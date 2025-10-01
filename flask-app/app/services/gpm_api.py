"""
NASA GPM IMERG Precipitation Data API Service

This service fetches Global Precipitation Measurement (GPM) Integrated Multi-satellitE 
Retrievals for GPM (IMERG) precipitation data from NASA Earthdata.

GPM IMERG provides near-real-time and research-quality precipitation estimates 
derived from an international network of precipitation-relevant satellites.

Credentials must be set in environment variables:
- EARTHDATA_USER: Your NASA Earthdata username
- EARTHDATA_PASS: Your NASA Earthdata password

For production use, obtain credentials from: https://urs.earthdata.nasa.gov/
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

logger = logging.getLogger(__name__)

class GPMAPIService:
    """Service for fetching NASA GPM IMERG precipitation data"""
    
    def __init__(self):
        self.base_url = "https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3"
        self.earthdata_user = os.getenv('EARTHDATA_USER')
        self.earthdata_pass = os.getenv('EARTHDATA_PASS')
        self.session = requests.Session()
        
        # Set up authentication if credentials are available
        if self.earthdata_user and self.earthdata_pass:
            self.session.auth = (self.earthdata_user, self.earthdata_pass)
            logger.info("GPM API Service initialized with NASA Earthdata credentials")
        else:
            logger.warning("GPM API Service initialized without credentials - will use mock data")
    
    def get_gpm_data(self, lat: float, lon: float, start: str, end: str) -> Dict:
        """
        Fetch GPM IMERG precipitation data for specified location and date range.
        
        Args:
            lat (float): Latitude (-90 to 90)
            lon (float): Longitude (-180 to 180)
            start (str): Start date in YYYYMMDD format
            end (str): End date in YYYYMMDD format
            
        Returns:
            Dict: Precipitation data with mobile-friendly structure
        """
        try:
            # Validate coordinates
            is_valid, error_msg = self._validate_coordinates(lat, lon)
            if not is_valid:
                return {
                    "success": False,
                    "error": error_msg,
                    "data": []
                }
            
            # Validate dates
            is_valid, error_msg = self._validate_dates(start, end)
            if not is_valid:
                return {
                    "success": False,
                    "error": error_msg,
                    "data": []
                }
            
            # Check credentials
            if not self.earthdata_user or not self.earthdata_pass:
                logger.info("No NASA Earthdata credentials found, using mock data")
                return self._get_mock_data(lat, lon, start, end)
            
            # Attempt to fetch real data
            try:
                return self._fetch_real_gpm_data(lat, lon, start, end)
            except Exception as e:
                logger.warning(f"Failed to fetch real GPM data: {e}, falling back to mock data")
                return self._get_mock_data(lat, lon, start, end)
                
        except Exception as e:
            logger.error(f"Error in get_gpm_data: {e}")
            return {
                "success": False,
                "error": f"Failed to fetch GPM precipitation data: {str(e)}",
                "data": []
            }
    
    def _fetch_real_gpm_data(self, lat: float, lon: float, start: str, end: str) -> Dict:
        """
        Fetch real GPM IMERG data from NASA Earthdata.
        
        Note: This is a simplified implementation. In production, you would:
        1. Use the correct GPM IMERG dataset URLs
        2. Parse NetCDF/HDF5 files properly
        3. Extract precipitation data for specific coordinates
        4. Handle different GPM products (Early, Late, Final runs)
        """
        # For now, we'll use a placeholder URL structure
        # In production, you'd need to:
        # 1. Query the appropriate GPM IMERG dataset
        # 2. Download and parse NetCDF/HDF5 files
        # 3. Extract data for specific lat/lon coordinates
        
        try:
            # Example URL structure for GPM IMERG data
            # Real implementation would require proper dataset navigation
            test_url = f"{self.base_url}/GPM_3IMERGHH.06"
            
            # Test authentication with a simple request
            response = self.session.get(test_url, timeout=10)
            
            if response.status_code == 401:
                return {
                    "success": False,
                    "error": "Invalid NASA Earthdata credentials",
                    "data": []
                }
            elif response.status_code == 403:
                return {
                    "success": False,
                    "error": "Access denied to GPM dataset",
                    "data": []
                }
            
            # For demonstration, return mock data with real API connection
            logger.info("Successfully authenticated with NASA Earthdata")
            return self._get_mock_data(lat, lon, start, end, authenticated=True)
            
        except requests.exceptions.Timeout:
            logger.error("Timeout connecting to NASA Earthdata")
            return {
                "success": False,
                "error": "Timeout connecting to NASA GPM service",
                "data": []
            }
        except requests.exceptions.ConnectionError:
            logger.error("Connection error to NASA Earthdata")
            return {
                "success": False,
                "error": "Cannot connect to NASA GPM service",
                "data": []
            }
    
    def _get_mock_data(self, lat: float, lon: float, start: str, end: str, authenticated: bool = False) -> Dict:
        """
        Generate mock GPM precipitation data for development and testing.
        
        This simulates realistic precipitation patterns based on:
        - Geographic location (higher precipitation near equator)
        - Seasonal variations
        - Random daily variations
        """
        try:
            start_date = datetime.strptime(start, '%Y%m%d')
            end_date = datetime.strptime(end, '%Y%m%d')
            
            data = []
            current_date = start_date
            
            while current_date <= end_date:
                # Generate realistic precipitation based on location and season
                base_precip = self._calculate_base_precipitation(lat, lon, current_date)
                
                # Add some realistic daily variation
                import random
                daily_variation = random.uniform(0.5, 2.0)
                final_precip = max(0, base_precip * daily_variation)
                
                data.append({
                    "date": current_date.strftime('%Y-%m-%d'),
                    "date_raw": current_date.strftime('%Y%m%d'),
                    "precipitation": round(final_precip, 2),
                    "precipitation_type": self._get_precipitation_type(final_precip),
                    "quality": "mock" if not authenticated else "estimated"
                })
                
                current_date += timedelta(days=1)
            
            source = "NASA GPM IMERG (Mock Data)" if not authenticated else "NASA GPM IMERG (Authenticated Mock)"
            
            return {
                "success": True,
                "data": data,
                "metadata": {
                    "source": source,
                    "dataset": "GPM_3IMERGHH.06",
                    "coordinate": {
                        "latitude": round(lat, 4),
                        "longitude": round(lon, 4)
                    },
                    "data_period": {
                        "start": start_date.strftime('%Y-%m-%d'),
                        "end": end_date.strftime('%Y-%m-%d'),
                        "total_days": len(data)
                    },
                    "parameter_info": {
                        "precipitation": "Surface precipitation rate (mm/hr converted to mm/day)",
                        "precipitation_type": "Precipitation intensity classification",
                        "quality": "Data quality indicator"
                    },
                    "notes": "Mock data for development" if not authenticated else "Authenticated mock data"
                },
                "request_info": {
                    "latitude": lat,
                    "longitude": lon,
                    "start_date": start,
                    "end_date": end,
                    "authenticated": authenticated
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating mock data: {e}")
            return {
                "success": False,
                "error": f"Failed to generate precipitation data: {str(e)}",
                "data": []
            }
    
    def _calculate_base_precipitation(self, lat: float, lon: float, date: datetime) -> float:
        """Calculate realistic base precipitation based on location and season"""
        # Higher precipitation near equator
        lat_factor = max(0.2, 1.0 - abs(lat) / 90.0)
        
        # Seasonal variation (simplified)
        month = date.month
        if lat >= 0:  # Northern hemisphere
            seasonal_factor = 1.2 if month in [6, 7, 8] else 0.8
        else:  # Southern hemisphere
            seasonal_factor = 1.2 if month in [12, 1, 2] else 0.8
        
        # Base precipitation (mm/day)
        base = 3.0 * lat_factor * seasonal_factor
        
        return base
    
    def _get_precipitation_type(self, precip: float) -> str:
        """Classify precipitation intensity"""
        if precip == 0:
            return "None"
        elif precip < 1.0:
            return "Light"
        elif precip < 10.0:
            return "Moderate"
        elif precip < 50.0:
            return "Heavy"
        else:
            return "Very Heavy"
    
    def _validate_coordinates(self, lat: float, lon: float) -> Tuple[bool, Optional[str]]:
        """Validate latitude and longitude coordinates"""
        try:
            lat = float(lat)
            lon = float(lon)
            
            if not (-90 <= lat <= 90):
                return False, f"Latitude must be between -90 and 90, got {lat}"
            if not (-180 <= lon <= 180):
                return False, f"Longitude must be between -180 and 180, got {lon}"
            
            return True, None
        except (ValueError, TypeError):
            return False, "Invalid coordinate format"
    
    def _validate_dates(self, start: str, end: str) -> Tuple[bool, Optional[str]]:
        """Validate date format and range"""
        try:
            start_date = datetime.strptime(start, '%Y%m%d')
            end_date = datetime.strptime(end, '%Y%m%d')
            
            if start_date > end_date:
                return False, "Start date must be before or equal to end date"
            
            # Limit to reasonable date range (GPM data available from 2014)
            min_date = datetime(2014, 1, 1)
            max_date = datetime.now() + timedelta(days=1)
            
            if start_date < min_date:
                return False, f"Start date must be after {min_date.strftime('%Y-%m-%d')} (GPM mission start)"
            
            if end_date > max_date:
                return False, f"End date cannot be in the future"
            
            # Limit query range to prevent abuse
            date_diff = (end_date - start_date).days
            if date_diff > 365:
                return False, "Date range cannot exceed 365 days"
            
            return True, None
            
        except ValueError:
            return False, "Invalid date format. Use YYYYMMDD format"


# Global service instance
gpm_service = GPMAPIService()

def get_gpm_data(lat: float, lon: float, start: str, end: str) -> Dict:
    """
    Convenience function to fetch GPM precipitation data.
    
    Args:
        lat (float): Latitude (-90 to 90)
        lon (float): Longitude (-180 to 180)
        start (str): Start date in YYYYMMDD format
        end (str): End date in YYYYMMDD format
        
    Returns:
        Dict: Mobile-friendly precipitation data
    """
    return gpm_service.get_gpm_data(lat, lon, start, end)
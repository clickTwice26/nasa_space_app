"""
NASA MODIS Aerosol Optical Depth (AOD) Air Quality Service

This service provides air quality data based on MODIS satellite observations
of Aerosol Optical Depth (AOD), which is a key indicator of atmospheric
aerosol loading and air quality conditions.

MODIS (Moderate Resolution Imaging Spectroradiometer) provides daily global
coverage of aerosol properties that can be used to assess air quality
and health impacts, particularly important for agricultural applications
where air quality affects crop health and worker safety.

Future integration points:
- NASA LAADS DAAC (Level-1 and Atmosphere Archive & Distribution System)
- NASA Giovanni (GES DISC Interactive Online Visualization ANd aNalysis Infrastructure)
- NASA Worldview for visualization
"""

import os
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import random

logger = logging.getLogger(__name__)

class MODISAirQualityService:
    """Service for fetching MODIS Aerosol Optical Depth and air quality data"""
    
    def __init__(self):
        self.laads_base_url = "https://ladsweb.modaps.eosdis.nasa.gov/api/v2"
        self.giovanni_base_url = "https://giovanni.gsfc.nasa.gov/giovanni"
        self.session = requests.Session()
        
        # Future: Add authentication for actual MODIS data access
        # self.earthdata_token = os.getenv('EARTHDATA_TOKEN')
        
        logger.info("MODIS Air Quality Service initialized")
    
    def get_modis_air_quality(self, lat: float, lon: float, start: str, end: str) -> Dict:
        """
        Fetch MODIS Aerosol Optical Depth data for air quality assessment.
        
        Args:
            lat (float): Latitude (-90 to 90)
            lon (float): Longitude (-180 to 180)
            start (str): Start date in YYYYMMDD format
            end (str): End date in YYYYMMDD format
            
        Returns:
            Dict: Air quality data with mobile-friendly structure
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
            
            # For now, generate realistic mock data
            # TODO: Replace with actual MODIS data fetching
            return self._get_mock_air_quality_data(lat, lon, start, end)
                
        except Exception as e:
            logger.error(f"Error in get_modis_air_quality: {e}")
            return {
                "success": False,
                "error": f"Failed to fetch MODIS air quality data: {str(e)}",
                "data": []
            }
    
    def _get_mock_air_quality_data(self, lat: float, lon: float, start: str, end: str) -> Dict:
        """
        Generate realistic mock MODIS AOD air quality data.
        
        This simulates realistic air quality patterns based on:
        - Geographic location (urban vs rural, industrial areas)
        - Seasonal variations (monsoon, dry season, burning season)
        - Day-to-day variations due to weather patterns
        """
        try:
            start_date = datetime.strptime(start, '%Y%m%d')
            end_date = datetime.strptime(end, '%Y%m%d')
            
            data = []
            current_date = start_date
            
            while current_date <= end_date:
                # Generate realistic AOD and air quality
                aod_value, air_quality_level, health_advisory = self._calculate_air_quality(lat, lon, current_date)
                
                data.append({
                    "date": current_date.strftime('%Y-%m-%d'),
                    "date_raw": current_date.strftime('%Y%m%d'),
                    "aerosol_index": round(aod_value, 3),
                    "air_quality_level": air_quality_level,
                    "health_advisory": health_advisory,
                    "visibility_km": self._calculate_visibility(aod_value),
                    "data_quality": "mock"
                })
                
                current_date += timedelta(days=1)
            
            return {
                "success": True,
                "data": data,
                "metadata": {
                    "source": "NASA MODIS (Mock Data)",
                    "instrument": "MODIS Terra/Aqua",
                    "parameter": "Aerosol Optical Depth at 550nm",
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
                        "aerosol_index": "Aerosol Optical Depth (dimensionless, 0-5 scale)",
                        "air_quality_level": "WHO/EPA based air quality classification",
                        "health_advisory": "Health recommendations based on air quality",
                        "visibility_km": "Estimated atmospheric visibility in kilometers"
                    },
                    "air_quality_scale": {
                        "Good": "AOD 0.0-0.1 (Green)",
                        "Moderate": "AOD 0.1-0.3 (Yellow)", 
                        "Unhealthy for Sensitive": "AOD 0.3-0.6 (Orange)",
                        "Unhealthy": "AOD 0.6-1.0 (Red)",
                        "Very Unhealthy": "AOD 1.0-1.5 (Purple)",
                        "Hazardous": "AOD >1.5 (Maroon)"
                    }
                },
                "request_info": {
                    "latitude": lat,
                    "longitude": lon,
                    "start_date": start,
                    "end_date": end,
                    "data_source": "mock"
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating mock air quality data: {e}")
            return {
                "success": False,
                "error": f"Failed to generate air quality data: {str(e)}",
                "data": []
            }
    
    def _calculate_air_quality(self, lat: float, lon: float, date: datetime) -> Tuple[float, str, str]:
        """Calculate realistic air quality based on location and season"""
        
        # Base AOD varies by geographic region
        base_aod = self._get_regional_base_aod(lat, lon)
        
        # Seasonal variation (dry season = higher AOD)
        seasonal_factor = self._get_seasonal_factor(lat, date)
        
        # Random daily variation
        daily_variation = random.uniform(0.7, 1.5)
        
        # Calculate final AOD
        aod_value = max(0.01, base_aod * seasonal_factor * daily_variation)
        
        # Determine air quality level and health advisory
        if aod_value <= 0.1:
            level = "Good"
            advisory = "Air quality is satisfactory. Ideal for outdoor activities."
        elif aod_value <= 0.3:
            level = "Moderate"
            advisory = "Air quality is acceptable. Sensitive individuals may experience minor issues."
        elif aod_value <= 0.6:
            level = "Unhealthy for Sensitive"
            advisory = "Sensitive groups should limit outdoor exposure."
        elif aod_value <= 1.0:
            level = "Unhealthy"
            advisory = "Everyone should limit outdoor activities. Wear masks if necessary."
        elif aod_value <= 1.5:
            level = "Very Unhealthy"
            advisory = "Avoid outdoor activities. Health warnings for all populations."
        else:
            level = "Hazardous"
            advisory = "Emergency conditions. Stay indoors and avoid outdoor exposure."
        
        return aod_value, level, advisory
    
    def _get_regional_base_aod(self, lat: float, lon: float) -> float:
        """Get base AOD values based on geographic region"""
        
        # High pollution regions (industrial areas, megacities)
        if (20 <= lat <= 40) and (70 <= lon <= 120):  # South/East Asia
            return 0.4
        elif (10 <= lat <= 30) and (-10 <= lon <= 50):  # North Africa/Middle East
            return 0.3
        elif (30 <= lat <= 50) and (100 <= lon <= 140):  # East Asia (China, Korea, Japan)
            return 0.35
        # Biomass burning regions
        elif (-20 <= lat <= 10) and (-80 <= lon <= -30):  # Amazon
            return 0.25
        elif (-10 <= lat <= 20) and (10 <= lon <= 50):  # Central Africa
            return 0.3
        # Clean regions (oceanic, polar)
        elif abs(lat) > 60:  # Polar regions
            return 0.05
        elif abs(lon) > 150 or abs(lon) < 30:  # Pacific/Atlantic
            return 0.08
        # Default continental
        else:
            return 0.15
    
    def _get_seasonal_factor(self, lat: float, date: datetime) -> float:
        """Calculate seasonal variation factor for AOD"""
        month = date.month
        
        # Northern hemisphere patterns
        if lat >= 0:
            # Higher AOD in spring/summer due to dust storms and biomass burning
            if month in [3, 4, 5]:  # Spring
                return 1.3
            elif month in [6, 7, 8]:  # Summer
                return 1.2
            elif month in [9, 10, 11]:  # Fall
                return 1.1
            else:  # Winter
                return 0.9
        # Southern hemisphere (seasons reversed)
        else:
            if month in [9, 10, 11]:  # Spring
                return 1.3
            elif month in [12, 1, 2]:  # Summer
                return 1.2
            elif month in [3, 4, 5]:  # Fall
                return 1.1
            else:  # Winter
                return 0.9
    
    def _calculate_visibility(self, aod_value: float) -> float:
        """Estimate visibility based on AOD value"""
        # Simplified relationship: higher AOD = lower visibility
        if aod_value <= 0.1:
            return round(random.uniform(15, 25), 1)  # Excellent visibility
        elif aod_value <= 0.3:
            return round(random.uniform(8, 15), 1)   # Good visibility
        elif aod_value <= 0.6:
            return round(random.uniform(4, 8), 1)    # Moderate visibility
        elif aod_value <= 1.0:
            return round(random.uniform(2, 4), 1)    # Poor visibility
        else:
            return round(random.uniform(0.5, 2), 1)  # Very poor visibility
    
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
            
            # MODIS data available from 2000
            min_date = datetime(2000, 1, 1)
            max_date = datetime.now() + timedelta(days=1)
            
            if start_date < min_date:
                return False, f"Start date must be after {min_date.strftime('%Y-%m-%d')} (MODIS data availability)"
            
            if end_date > max_date:
                return False, f"End date cannot be in the future"
            
            # Limit query range
            date_diff = (end_date - start_date).days
            if date_diff > 365:
                return False, "Date range cannot exceed 365 days"
            
            return True, None
            
        except ValueError:
            return False, "Invalid date format. Use YYYYMMDD format"


# Global service instance
modis_service = MODISAirQualityService()

def get_modis_air_quality(lat: float, lon: float, start: str, end: str) -> Dict:
    """
    Convenience function to fetch MODIS air quality data.
    
    Args:
        lat (float): Latitude (-90 to 90)
        lon (float): Longitude (-180 to 180)
        start (str): Start date in YYYYMMDD format
        end (str): End date in YYYYMMDD format
        
    Returns:
        Dict: Mobile-friendly air quality data
    """
    return modis_service.get_modis_air_quality(lat, lon, start, end)
"""
NASA POWER API Service
Provides access to NASA's POWER (Prediction Of Worldwide Energy Resources) API
for agricultural and meteorological data.
"""

import requests
import logging
from datetime import datetime
from typing import Dict, List, Optional, Union

logger = logging.getLogger(__name__)

class PowerAPIService:
    """Service for interacting with NASA POWER API"""
    
    BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    @staticmethod
    def get_power_data(lat: float, lon: float, start: str, end: str, 
                      parameters: Optional[str] = None) -> Dict[str, Union[List, str, bool]]:
        """
        Fetch NASA POWER API data for given coordinates and date range.
        
        Args:
            lat (float): Latitude (-90 to 90)
            lon (float): Longitude (-180 to 180)
            start (str): Start date in YYYYMMDD format
            end (str): End date in YYYYMMDD format
            parameters (str, optional): Comma-separated parameters. Defaults to 'T2M,PRECTOT'
        
        Returns:
            Dict containing:
            - success (bool): Whether the request was successful
            - data (list): List of daily records with date, temperature, precipitation
            - error (str): Error message if request failed
            - metadata (dict): Additional metadata about the request
        
        Example:
            >>> PowerAPIService.get_power_data(23.7, 90.4, '20231001', '20231031')
            {
                'success': True,
                'data': [
                    {'date': '2023-10-01', 'temperature': 25.4, 'precipitation': 0.0},
                    {'date': '2023-10-02', 'temperature': 26.1, 'precipitation': 2.3},
                    ...
                ],
                'metadata': {...}
            }
        """
        try:
            # Validate inputs
            if not PowerAPIService._validate_coordinates(lat, lon):
                return {
                    'success': False,
                    'error': 'Invalid coordinates. Latitude must be -90 to 90, longitude must be -180 to 180.',
                    'data': []
                }
            
            if not PowerAPIService._validate_dates(start, end):
                return {
                    'success': False,
                    'error': 'Invalid date format. Use YYYYMMDD format.',
                    'data': []
                }
            
            # Default parameters for agricultural community
            if parameters is None:
                parameters = 'T2M,PRECTOT'  # Temperature at 2m, Precipitation
            
            # Build API URL
            url = f"{PowerAPIService.BASE_URL}?parameters={parameters}&community=AG&longitude={lon}&latitude={lat}&start={start}&end={end}&format=JSON"
            
            logger.info(f"Requesting NASA POWER data for lat={lat}, lon={lon}, start={start}, end={end}")
            
            # Make API request with timeout
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Process the data into a mobile-friendly format
            processed_data = PowerAPIService._process_api_response(data)
            
            return {
                'success': True,
                'data': processed_data['daily_data'],
                'metadata': processed_data['metadata'],
                'request_info': {
                    'latitude': lat,
                    'longitude': lon,
                    'start_date': start,
                    'end_date': end,
                    'parameters': parameters
                }
            }
            
        except requests.exceptions.Timeout:
            logger.error("NASA POWER API request timed out")
            return {
                'success': False,
                'error': 'Request timed out. Please try again.',
                'data': []
            }
            
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to NASA POWER API")
            return {
                'success': False,
                'error': 'Unable to connect to NASA POWER API. Please check your internet connection.',
                'data': []
            }
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"NASA POWER API HTTP error: {e}")
            return {
                'success': False,
                'error': f'API request failed: {str(e)}',
                'data': []
            }
            
        except ValueError as e:
            logger.error(f"Invalid JSON response from NASA POWER API: {e}")
            return {
                'success': False,
                'error': 'Invalid response format from API.',
                'data': []
            }
            
        except Exception as e:
            logger.error(f"Unexpected error in NASA POWER API request: {e}")
            return {
                'success': False,
                'error': 'An unexpected error occurred while fetching data.',
                'data': []
            }
    
    @staticmethod
    def _validate_coordinates(lat: float, lon: float) -> bool:
        """Validate latitude and longitude values"""
        try:
            lat = float(lat)
            lon = float(lon)
            return -90 <= lat <= 90 and -180 <= lon <= 180
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def _validate_dates(start: str, end: str) -> bool:
        """Validate date format (YYYYMMDD)"""
        try:
            datetime.strptime(start, '%Y%m%d')
            datetime.strptime(end, '%Y%m%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def _process_api_response(raw_data: Dict) -> Dict:
        """
        Process NASA POWER API response into mobile-friendly format
        
        Args:
            raw_data: Raw JSON response from NASA POWER API
            
        Returns:
            Dict with processed daily data and metadata
        """
        try:
            # Extract parameters data
            parameters = raw_data.get('properties', {}).get('parameter', {})
            
            # Get temperature and precipitation data
            temp_data = parameters.get('T2M', {})
            precip_data = parameters.get('PRECTOT', {})
            
            # Process daily data
            daily_data = []
            
            # Get all available dates (should be same for both parameters)
            dates = set(temp_data.keys()) | set(precip_data.keys())
            
            for date_str in sorted(dates):
                # Convert YYYYMMDD to YYYY-MM-DD for better readability
                try:
                    formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
                except (IndexError, ValueError):
                    formatted_date = date_str
                
                # Get values, handling missing data
                temperature = temp_data.get(date_str)
                precipitation = precip_data.get(date_str)
                
                # Convert -999 (NASA's missing data indicator) to null
                if temperature == -999:
                    temperature = None
                if precipitation == -999:
                    precipitation = None
                
                daily_data.append({
                    'date': formatted_date,
                    'date_raw': date_str,
                    'temperature': round(temperature, 1) if temperature is not None else None,
                    'precipitation': round(precipitation, 2) if precipitation is not None else 0.0
                })
            
            # Extract metadata
            metadata = {
                'source': 'NASA POWER API',
                'data_version': raw_data.get('header', {}).get('api_version', 'Unknown'),
                'coordinate': {
                    'latitude': raw_data.get('geometry', {}).get('coordinates', [None, None])[1],
                    'longitude': raw_data.get('geometry', {}).get('coordinates', [None, None])[0]
                },
                'parameter_info': {
                    'T2M': 'Temperature at 2 Meters (°C)',
                    'PRECTOT': 'Precipitation (mm/day)'
                },
                'data_period': {
                    'start': daily_data[0]['date'] if daily_data else None,
                    'end': daily_data[-1]['date'] if daily_data else None,
                    'total_days': len(daily_data)
                }
            }
            
            return {
                'daily_data': daily_data,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Error processing NASA POWER API response: {e}")
            return {
                'daily_data': [],
                'metadata': {
                    'error': 'Failed to process API response',
                    'source': 'NASA POWER API'
                }
            }

# Convenience function for backward compatibility
def get_power_data(lat: float, lon: float, start: str, end: str) -> Dict:
    """
    Convenience function to get NASA POWER data.
    
    Args:
        lat: Latitude
        lon: Longitude  
        start: Start date in YYYYMMDD format
        end: End date in YYYYMMDD format
        
    Returns:
        Dict with success, data, and error fields
    """
    return PowerAPIService.get_power_data(lat, lon, start, end)
"""
NASA Worldview Snapshots API Service

This service provides access to NASA Worldview imagery through the Snapshots API,
allowing users to visualize satellite data for specific locations and dates.

NASA Worldview Snapshots API Documentation:
https://wiki.earthdata.nasa.gov/display/GIBS/GIBS+API+for+Developers
"""

import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode

logger = logging.getLogger(__name__)

class WorldviewService:
    """Service for interacting with NASA Worldview Snapshots API"""
    
    def __init__(self):
        self.base_url = "https://wvs.earthdata.nasa.gov/api/v1/snapshot"
        self.default_width = 1024
        self.default_height = 1024
        self.default_format = "png"
        logger.info("NASA Worldview Service initialized")
    
    def get_worldview_image(
        self, 
        lat: float, 
        lon: float, 
        date: str, 
        layers: str,
        bbox_size: float = 0.5
    ) -> Dict:
        """
        Get NASA Worldview satellite imagery for specified location and date.
        
        Args:
            lat (float): Latitude (-90 to 90)
            lon (float): Longitude (-180 to 180)
            date (str): Date in YYYY-MM-DD format
            layers (str): Comma-separated layer names (e.g., MODIS_Terra_CorrectedReflectance_TrueColor)
            bbox_size (float): Size of bounding box in degrees (default: 0.5)
            
        Returns:
            Dict: Result with image URL or error information
        """
        try:
            # Validate coordinates
            is_valid, error_msg = self._validate_coordinates(lat, lon)
            if not is_valid:
                return {
                    "success": False,
                    "error": error_msg,
                    "image_url": None
                }
            
            # Validate date
            is_valid, error_msg = self._validate_date(date)
            if not is_valid:
                return {
                    "success": False,
                    "error": error_msg,
                    "image_url": None
                }
            
            # Validate layers
            if not layers or not isinstance(layers, str):
                return {
                    "success": False,
                    "error": "Layers parameter is required and must be a string",
                    "image_url": None
                }
            
            # Calculate bounding box
            bbox = self._calculate_bbox(lat, lon, bbox_size)
            
            # Build API request parameters
            params = {
                "REQUEST": "GetSnapshot",
                "TIME": date,
                "BBOX": f"{bbox['west']},{bbox['south']},{bbox['east']},{bbox['north']}",
                "CRS": "EPSG:4326",
                "LAYERS": layers,
                "WRAP": "day",
                "FORMAT": self.default_format,
                "WIDTH": self.default_width,
                "HEIGHT": self.default_height
            }
            
            # Log the request
            logger.info(f"NASA Worldview API request: lat={lat}, lon={lon}, date={date}, layers={layers}")
            
            # Make the API request
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                # For successful requests, the API returns the image directly
                # We need to construct the URL that would generate this image
                image_url = f"{self.base_url}?{urlencode(params)}"
                
                return {
                    "success": True,
                    "date": date,
                    "layers": layers,
                    "image_url": image_url,
                    "bbox": bbox,
                    "location": {
                        "latitude": lat,
                        "longitude": lon
                    },
                    "metadata": {
                        "width": self.default_width,
                        "height": self.default_height,
                        "format": self.default_format,
                        "crs": "EPSG:4326",
                        "source": "NASA Worldview Snapshots API"
                    }
                }
            else:
                logger.error(f"NASA Worldview API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"NASA Worldview API returned status {response.status_code}",
                    "image_url": None
                }
                
        except requests.exceptions.Timeout:
            logger.error("NASA Worldview API request timed out")
            return {
                "success": False,
                "error": "Request to NASA Worldview API timed out",
                "image_url": None
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"NASA Worldview API request failed: {e}")
            return {
                "success": False,
                "error": f"Failed to connect to NASA Worldview API: {str(e)}",
                "image_url": None
            }
        except Exception as e:
            logger.error(f"Unexpected error in get_worldview_image: {e}")
            return {
                "success": False,
                "error": f"An unexpected error occurred: {str(e)}",
                "image_url": None
            }
    
    def _calculate_bbox(self, lat: float, lon: float, size: float) -> Dict[str, float]:
        """Calculate bounding box around the given coordinates"""
        half_size = size / 2
        return {
            "north": min(90.0, lat + half_size),
            "south": max(-90.0, lat - half_size),
            "east": min(180.0, lon + half_size),
            "west": max(-180.0, lon - half_size)
        }
    
    def _validate_coordinates(self, lat: float, lon: float) -> Tuple[bool, Optional[str]]:
        """Validate latitude and longitude values"""
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
    
    def _validate_date(self, date: str) -> Tuple[bool, Optional[str]]:
        """Validate date format and availability"""
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            
            # Check if date is not in the future
            if date_obj > datetime.now():
                return False, "Date cannot be in the future"
            
            # Check if date is not too far in the past (MODIS data starts around 2000)
            min_date = datetime(2000, 1, 1)
            if date_obj < min_date:
                return False, f"Date must be after {min_date.strftime('%Y-%m-%d')} (satellite data availability)"
            
            return True, None
            
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD format"
    
    def get_available_layers(self) -> Dict[str, str]:
        """Get a dictionary of commonly available layers"""
        return {
            "MODIS_Terra_CorrectedReflectance_TrueColor": "MODIS Terra True Color",
            "MODIS_Aqua_CorrectedReflectance_TrueColor": "MODIS Aqua True Color", 
            "MODIS_Terra_CorrectedReflectance_Bands721": "MODIS Terra False Color (721)",
            "MODIS_Aqua_CorrectedReflectance_Bands721": "MODIS Aqua False Color (721)",
            "VIIRS_SNPP_CorrectedReflectance_TrueColor": "VIIRS True Color",
            "VIIRS_SNPP_DayNightBand_ENCC": "VIIRS Day/Night Band",
            "MODIS_Terra_Aerosol": "MODIS Terra Aerosol Optical Depth",
            "MODIS_Aqua_Aerosol": "MODIS Aqua Aerosol Optical Depth",
            "MODIS_Terra_Land_Surface_Temp_Day": "MODIS Terra Land Surface Temperature (Day)",
            "MODIS_Terra_Snow_Cover": "MODIS Terra Snow Cover"
        }


# Global service instance
worldview_service = WorldviewService()

def get_worldview_image(lat: float, lon: float, date: str, layers: str, bbox_size: float = 0.5) -> Dict:
    """
    Convenience function to get NASA Worldview imagery.
    
    Args:
        lat (float): Latitude (-90 to 90)
        lon (float): Longitude (-180 to 180)
        date (str): Date in YYYY-MM-DD format
        layers (str): Comma-separated layer names
        bbox_size (float): Size of bounding box in degrees
        
    Returns:
        Dict: Result with image URL and metadata
    """
    return worldview_service.get_worldview_image(lat, lon, date, layers, bbox_size)

def get_available_layers() -> Dict[str, str]:
    """Get available NASA Worldview layers"""
    return worldview_service.get_available_layers()
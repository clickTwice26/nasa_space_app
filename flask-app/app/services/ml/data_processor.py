#!/usr/bin/env python3
"""
TerraPulse ML Data Processing Service
Data integration and feature engineering for agricultural ML models
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
import logging
import json
from dataclasses import dataclass, asdict
import requests
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

@dataclass
class LocationData:
    latitude: float
    longitude: float
    elevation: Optional[float] = None
    region: Optional[str] = None
    climate_zone: Optional[str] = None

@dataclass
class WeatherObservation:
    timestamp: datetime
    temperature: float
    humidity: float
    pressure: float
    rainfall: float
    wind_speed: float
    wind_direction: float
    cloud_cover: float
    solar_radiation: Optional[float] = None
    visibility: Optional[float] = None

@dataclass
class SatelliteData:
    timestamp: datetime
    location: LocationData
    precipitation: float
    ndvi: Optional[float] = None
    soil_moisture: Optional[float] = None
    land_surface_temperature: Optional[float] = None

class TerraPulseDataProcessor:
    """
    Data processing and feature engineering for agricultural ML models
    """
    
    def __init__(self):
        self.nasa_api_key = "DEMO_KEY"  # Using demo key for now
        self.base_urls = {
            'power': 'https://power.larc.nasa.gov/api/temporal/',
            'modis': 'https://modis.gsfc.nasa.gov/data/',
            'gpm': 'https://gpm.nasa.gov/data-access/'
        }
        
    def fetch_nasa_weather_data(self, location: LocationData, 
                               start_date: datetime = None,
                               end_date: datetime = None) -> Dict[str, Any]:
        """
        Fetch weather data from NASA POWER API
        """
        try:
            if start_date is None:
                start_date = datetime.now() - timedelta(days=30)
            if end_date is None:
                end_date = datetime.now()
            
            # Format dates for NASA API
            start_str = start_date.strftime('%Y%m%d')
            end_str = end_date.strftime('%Y%m%d')
            
            # NASA POWER API parameters
            parameters = [
                'T2M',      # Temperature at 2 meters
                'RH2M',     # Relative humidity at 2 meters
                'PS',       # Surface pressure
                'PRECTOTCORR',  # Precipitation corrected
                'WS2M',     # Wind speed at 2 meters
                'WD2M',     # Wind direction at 2 meters
                'CLRSKY_SFC_SW_DWN'  # Clear sky surface shortwave downward irradiance
            ]
            
            url = f"{self.base_urls['power']}daily/point"
            params = {
                'parameters': ','.join(parameters),
                'community': 'AG',
                'longitude': location.longitude,
                'latitude': location.latitude,
                'start': start_str,
                'end': end_str,
                'format': 'JSON'
            }
            
            # For demo purposes, generate synthetic data
            return self._generate_synthetic_nasa_data(location, start_date, end_date)
            
        except Exception as e:
            logger.error(f"Error fetching NASA weather data: {str(e)}")
            return self._generate_synthetic_nasa_data(location, start_date, end_date)
    
    def _generate_synthetic_nasa_data(self, location: LocationData,
                                    start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate synthetic NASA-like weather data for demo"""
        try:
            days = (end_date - start_date).days
            dates = [start_date + timedelta(days=i) for i in range(days)]
            
            # Generate realistic weather patterns based on location
            base_temp = 25 + (location.latitude - 20) * 0.5  # Temperature varies with latitude
            
            data = {
                'properties': {
                    'parameter': {
                        'T2M': {},      # Temperature
                        'RH2M': {},     # Humidity
                        'PS': {},       # Pressure
                        'PRECTOTCORR': {},  # Precipitation
                        'WS2M': {},     # Wind speed
                        'WD2M': {},     # Wind direction
                        'CLRSKY_SFC_SW_DWN': {}  # Solar radiation
                    }
                }
            }
            
            np.random.seed(int(location.latitude * 1000) % 10000)  # Consistent random seed
            
            for i, date in enumerate(dates):
                date_str = date.strftime('%Y%m%d')
                
                # Temperature with seasonal variation
                seasonal_factor = np.sin(2 * np.pi * date.timetuple().tm_yday / 365.25)
                temp = base_temp + seasonal_factor * 10 + np.random.normal(0, 3)
                
                # Humidity inversely related to temperature
                humidity = max(30, min(95, 80 - (temp - base_temp) * 2 + np.random.normal(0, 10)))
                
                # Pressure with small variations
                pressure = 1013 + np.random.normal(0, 15)
                
                # Precipitation with monsoon patterns
                monsoon_factor = max(0, np.sin(2 * np.pi * (date.timetuple().tm_yday - 150) / 365.25))
                precip = max(0, monsoon_factor * 15 + np.random.exponential(2))
                
                # Wind patterns
                wind_speed = max(0, np.random.normal(8, 4))
                wind_direction = np.random.uniform(0, 360)
                
                # Solar radiation
                solar = max(0, 20 + np.random.normal(0, 5))
                
                data['properties']['parameter']['T2M'][date_str] = round(temp, 2)
                data['properties']['parameter']['RH2M'][date_str] = round(humidity, 2)
                data['properties']['parameter']['PS'][date_str] = round(pressure, 2)
                data['properties']['parameter']['PRECTOTCORR'][date_str] = round(precip, 2)
                data['properties']['parameter']['WS2M'][date_str] = round(wind_speed, 2)
                data['properties']['parameter']['WD2M'][date_str] = round(wind_direction, 2)
                data['properties']['parameter']['CLRSKY_SFC_SW_DWN'][date_str] = round(solar, 2)
            
            return {
                'success': True,
                'data': data,
                'source': 'NASA POWER API (Synthetic)',
                'location': asdict(location),
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat(),
                    'days': days
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating synthetic NASA data: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def process_weather_observations(self, raw_data: Dict[str, Any]) -> List[WeatherObservation]:
        """
        Process raw weather data into structured observations
        """
        try:
            observations = []
            
            if not raw_data.get('success') or 'data' not in raw_data:
                return observations
            
            parameters = raw_data['data']['properties']['parameter']
            
            # Get all available dates
            dates = set()
            for param_data in parameters.values():
                dates.update(param_data.keys())
            
            dates = sorted(dates)
            
            for date_str in dates:
                try:
                    date = datetime.strptime(date_str, '%Y%m%d')
                    
                    # Extract parameters with defaults
                    temperature = parameters.get('T2M', {}).get(date_str, 25.0)
                    humidity = parameters.get('RH2M', {}).get(date_str, 65.0)
                    pressure = parameters.get('PS', {}).get(date_str, 1013.0)
                    rainfall = parameters.get('PRECTOTCORR', {}).get(date_str, 0.0)
                    wind_speed = parameters.get('WS2M', {}).get(date_str, 5.0)
                    wind_direction = parameters.get('WD2M', {}).get(date_str, 180.0)
                    solar_radiation = parameters.get('CLRSKY_SFC_SW_DWN', {}).get(date_str, 20.0)
                    
                    observation = WeatherObservation(
                        timestamp=date,
                        temperature=float(temperature),
                        humidity=float(humidity),
                        pressure=float(pressure),
                        rainfall=float(rainfall),
                        wind_speed=float(wind_speed),
                        wind_direction=float(wind_direction),
                        cloud_cover=max(0, min(100, 100 - float(humidity))),  # Estimated
                        solar_radiation=float(solar_radiation)
                    )
                    
                    observations.append(observation)
                    
                except (ValueError, KeyError) as e:
                    logger.warning(f"Error processing observation for {date_str}: {str(e)}")
                    continue
            
            logger.info(f"Processed {len(observations)} weather observations")
            return observations
            
        except Exception as e:
            logger.error(f"Error processing weather observations: {str(e)}")
            return []
    
    def extract_features(self, observations: List[WeatherObservation],
                        location: LocationData = None) -> pd.DataFrame:
        """
        Extract features for ML models from weather observations
        """
        try:
            if not observations:
                return pd.DataFrame()
            
            # Convert observations to DataFrame
            data = []
            for obs in observations:
                row = {
                    'timestamp': obs.timestamp,
                    'temperature': obs.temperature,
                    'humidity': obs.humidity,
                    'pressure': obs.pressure,
                    'rainfall': obs.rainfall,
                    'wind_speed': obs.wind_speed,
                    'wind_direction': obs.wind_direction,
                    'cloud_cover': obs.cloud_cover,
                    'solar_radiation': obs.solar_radiation or 20.0
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
            
            # Feature engineering
            features_df = self._engineer_features(df, location)
            
            return features_df
            
        except Exception as e:
            logger.error(f"Error extracting features: {str(e)}")
            return pd.DataFrame()
    
    def _engineer_features(self, df: pd.DataFrame, location: LocationData = None) -> pd.DataFrame:
        """
        Engineer features for ML models
        """
        try:
            features = df.copy()
            
            # Time-based features
            features['day_of_year'] = features.index.day_of_year
            features['month'] = features.index.month
            features['season'] = features['month'].apply(self._get_season)
            
            # Rolling statistics (3-day window)
            window = min(3, len(features))
            features['temp_rolling_mean'] = features['temperature'].rolling(window=window, min_periods=1).mean()
            features['temp_rolling_std'] = features['temperature'].rolling(window=window, min_periods=1).std().fillna(0)
            features['humidity_rolling_mean'] = features['humidity'].rolling(window=window, min_periods=1).mean()
            features['rainfall_rolling_sum'] = features['rainfall'].rolling(window=window, min_periods=1).sum()
            
            # Derived features
            features['heat_index'] = self._calculate_heat_index(features['temperature'], features['humidity'])
            features['dewpoint'] = self._calculate_dewpoint(features['temperature'], features['humidity'])
            features['vapor_pressure_deficit'] = self._calculate_vpd(features['temperature'], features['humidity'])
            
            # Weather change indicators
            features['temp_change'] = features['temperature'].diff().fillna(0)
            features['pressure_change'] = features['pressure'].diff().fillna(0)
            features['humidity_change'] = features['humidity'].diff().fillna(0)
            
            # Precipitation indicators
            features['is_rainy_day'] = (features['rainfall'] > 1.0).astype(int)
            features['consecutive_dry_days'] = self._calculate_consecutive_dry_days(features['rainfall'])
            
            # Wind-related features
            features['wind_u'] = features['wind_speed'] * np.cos(np.radians(features['wind_direction']))
            features['wind_v'] = features['wind_speed'] * np.sin(np.radians(features['wind_direction']))
            
            # Location-based features (if location provided)
            if location:
                features['latitude'] = location.latitude
                features['longitude'] = location.longitude
                features['elevation'] = location.elevation or 0
                
                # Distance from equator (affects temperature patterns)
                features['abs_latitude'] = abs(location.latitude)
            
            # Agricultural indices
            features['growing_degree_days'] = np.maximum(0, (features['temperature'] - 10))  # Base temp 10°C
            features['stress_temperature'] = np.maximum(0, features['temperature'] - 30)  # Heat stress
            features['cold_stress'] = np.maximum(0, 15 - features['temperature'])  # Cold stress
            
            # Evapotranspiration estimate (simplified Penman)
            features['potential_evapotranspiration'] = self._estimate_pet(
                features['temperature'], features['humidity'], features['wind_speed'], features['solar_radiation']
            )
            
            # Water balance
            features['water_balance'] = features['rainfall'] - features['potential_evapotranspiration']
            features['cumulative_water_balance'] = features['water_balance'].cumsum()
            
            # Lag features (previous day values)
            lag_columns = ['temperature', 'humidity', 'rainfall', 'pressure']
            for col in lag_columns:
                if col in features.columns:
                    features[f'{col}_lag1'] = features[col].shift(1).fillna(features[col].iloc[0])
                    if len(features) > 2:
                        features[f'{col}_lag2'] = features[col].shift(2).fillna(features[col].iloc[0])
            
            # Remove any infinite or NaN values
            features = features.replace([np.inf, -np.inf], np.nan)
            features = features.fillna(method='forward').fillna(method='backward').fillna(0)
            
            logger.info(f"Engineered {len(features.columns)} features from {len(features)} observations")
            return features
            
        except Exception as e:
            logger.error(f"Error in feature engineering: {str(e)}")
            return df
    
    def _get_season(self, month: int) -> str:
        """Get season from month"""
        if month in [12, 1, 2]:
            return 'winter'
        elif month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        else:
            return 'autumn'
    
    def _calculate_heat_index(self, temp: pd.Series, humidity: pd.Series) -> pd.Series:
        """Calculate heat index (apparent temperature)"""
        # Simplified heat index calculation
        hi = 0.5 * (temp + 61.0 + ((temp - 68.0) * 1.2) + (humidity * 0.094))
        return hi
    
    def _calculate_dewpoint(self, temp: pd.Series, humidity: pd.Series) -> pd.Series:
        """Calculate dewpoint temperature"""
        # Magnus formula approximation
        a = 17.27
        b = 237.7
        alpha = ((a * temp) / (b + temp)) + np.log(humidity / 100.0)
        dewpoint = (b * alpha) / (a - alpha)
        return dewpoint
    
    def _calculate_vpd(self, temp: pd.Series, humidity: pd.Series) -> pd.Series:
        """Calculate Vapor Pressure Deficit"""
        # Saturation vapor pressure
        es = 0.6108 * np.exp(17.27 * temp / (temp + 237.3))
        # Actual vapor pressure
        ea = es * humidity / 100
        # VPD
        vpd = es - ea
        return vpd
    
    def _calculate_consecutive_dry_days(self, rainfall: pd.Series) -> pd.Series:
        """Calculate consecutive dry days"""
        is_dry = rainfall <= 1.0
        consecutive = is_dry.groupby((~is_dry).cumsum()).cumsum()
        return consecutive * is_dry
    
    def _estimate_pet(self, temp: pd.Series, humidity: pd.Series, 
                     wind_speed: pd.Series, solar_radiation: pd.Series) -> pd.Series:
        """Estimate potential evapotranspiration using simplified Penman equation"""
        try:
            # Simplified PET calculation (mm/day)
            delta = 4098 * (0.6108 * np.exp(17.27 * temp / (temp + 237.3))) / ((temp + 237.3) ** 2)
            gamma = 0.665  # Psychrometric constant (kPa/°C)
            
            # Wind speed at 2m height
            u2 = wind_speed * 4.87 / np.log(67.8 * 10 - 5.42)
            
            # Saturation and actual vapor pressure
            es = 0.6108 * np.exp(17.27 * temp / (temp + 237.3))
            ea = es * humidity / 100
            
            # Net radiation (simplified)
            rn = solar_radiation * 0.0864  # Convert from W/m² to MJ/m²/day
            
            # Penman-Monteith equation (simplified)
            numerator = 0.408 * delta * rn + gamma * 900 / (temp + 273) * u2 * (es - ea)
            denominator = delta + gamma * (1 + 0.34 * u2)
            
            pet = numerator / denominator
            return np.maximum(0, pet)  # Ensure non-negative values
            
        except Exception as e:
            logger.warning(f"Error calculating PET, using simplified estimate: {str(e)}")
            # Fallback to simple temperature-based estimate
            return np.maximum(0, (temp - 5) * 0.2)
    
    def aggregate_to_features_dict(self, features_df: pd.DataFrame) -> Dict[str, float]:
        """
        Aggregate feature DataFrame to a single feature dictionary for prediction
        """
        try:
            if features_df.empty:
                return {}
            
            # Get the most recent values
            latest = features_df.iloc[-1]
            
            # Select key features for prediction
            key_features = [
                'temperature', 'humidity', 'pressure', 'rainfall', 'wind_speed',
                'cloud_cover', 'heat_index', 'dewpoint', 'vapor_pressure_deficit',
                'growing_degree_days', 'potential_evapotranspiration', 'water_balance',
                'temp_rolling_mean', 'humidity_rolling_mean', 'rainfall_rolling_sum'
            ]
            
            feature_dict = {}
            for feature in key_features:
                if feature in latest.index:
                    value = latest[feature]
                    if pd.notna(value) and np.isfinite(value):
                        feature_dict[feature] = float(value)
            
            return feature_dict
            
        except Exception as e:
            logger.error(f"Error aggregating features: {str(e)}")
            return {}
    
    def prepare_training_data(self, observations: List[WeatherObservation],
                            location: LocationData = None) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare training data for ML models
        """
        try:
            features_df = self.extract_features(observations, location)
            
            if features_df.empty:
                return pd.DataFrame(), pd.Series()
            
            # Create target variable (next day rainfall)
            target = features_df['rainfall'].shift(-1)
            
            # Remove the last row (no target available)
            features_df = features_df[:-1]
            target = target[:-1]
            
            # Remove rows with NaN targets
            mask = target.notna()
            features_df = features_df[mask]
            target = target[mask]
            
            return features_df, target
            
        except Exception as e:
            logger.error(f"Error preparing training data: {str(e)}")
            return pd.DataFrame(), pd.Series()

# Global instance for the Flask app
data_processor = TerraPulseDataProcessor()
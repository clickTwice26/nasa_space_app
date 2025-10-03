#!/usr/bin/env python3
"""
TRMM Precipitation Data Analyzer and Preprocessor
Handles NetCDF4 files and creates ML-ready datasets
"""

import os
import numpy as np
import pandas as pd
import xarray as xr
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class TRMMPrecipitationAnalyzer:
    """
    Analyzes TRMM precipitation data and creates features for ML models
    """
    
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.processed_dir = self.data_dir.parent / "processed"
        self.processed_dir.mkdir(exist_ok=True)
        
        # Coordinate bounds for different regions
        self.regions = {
            'global': {'lat': (-50, 50), 'lon': (-180, 180)},
            'usa': {'lat': (25, 50), 'lon': (-125, -66)},
            'europe': {'lat': (35, 70), 'lon': (-10, 40)},
            'asia': {'lat': (5, 55), 'lon': (60, 150)},
            'africa': {'lat': (-35, 35), 'lon': (-20, 55)},
            'south_america': {'lat': (-55, 15), 'lon': (-85, -35)}
        }
    
    def load_single_file(self, file_path: Path) -> xr.Dataset:
        """Load a single NetCDF file and return xarray Dataset"""
        try:
            ds = xr.open_dataset(file_path)
            return ds
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None
    
    def extract_date_from_filename(self, filename: str) -> datetime:
        """Extract date from TRMM filename format"""
        # Format: 3B42_Daily.YYYYMMDD.7.nc4
        date_str = filename.split('.')[1]
        return datetime.strptime(date_str, '%Y%m%d')
    
    def get_file_list(self, start_year: int = None, end_year: int = None) -> List[Tuple[Path, datetime]]:
        """Get sorted list of all NetCDF files with their dates"""
        files_with_dates = []
        
        for year_dir in sorted(self.data_dir.glob('*')):
            if not year_dir.is_dir():
                continue
                
            year = int(year_dir.name)
            if start_year and year < start_year:
                continue
            if end_year and year > end_year:
                continue
                
            for month_dir in sorted(year_dir.glob('*')):
                if not month_dir.is_dir():
                    continue
                    
                for file_path in sorted(month_dir.glob('*.nc4')):
                    try:
                        date = self.extract_date_from_filename(file_path.name)
                        files_with_dates.append((file_path, date))
                    except Exception as e:
                        print(f"Could not parse date from {file_path}: {e}")
        
        return sorted(files_with_dates, key=lambda x: x[1])
    
    def extract_regional_stats(self, ds: xr.Dataset, region: str = 'global') -> Dict:
        """Extract statistical features for a specific region"""
        if region not in self.regions:
            raise ValueError(f"Region {region} not supported. Available: {list(self.regions.keys())}")
        
        bounds = self.regions[region]
        
        # Select regional data
        regional_data = ds.sel(
            lat=slice(bounds['lat'][0], bounds['lat'][1]),
            lon=slice(bounds['lon'][0], bounds['lon'][1])
        )
        
        # Get precipitation data (usually called 'precipitation' or 'precip')
        precip_vars = ['precipitation', 'precip', 'PRECIP', 'rain']
        precip_data = None
        
        for var in precip_vars:
            if var in regional_data.data_vars:
                precip_data = regional_data[var]
                break
        
        if precip_data is None:
            # If no standard variable found, take the first data variable
            data_vars = list(regional_data.data_vars)
            if data_vars:
                precip_data = regional_data[data_vars[0]]
                print(f"Using variable: {data_vars[0]}")
            else:
                print("No data variables found!")
                return {}
        
        # Calculate statistics
        stats = {
            f'{region}_mean_precip': float(precip_data.mean().values),
            f'{region}_max_precip': float(precip_data.max().values),
            f'{region}_min_precip': float(precip_data.min().values),
            f'{region}_std_precip': float(precip_data.std().values),
            f'{region}_total_precip': float(precip_data.sum().values),
            f'{region}_precip_coverage': float((precip_data > 0.1).sum().values),  # Areas with > 0.1mm rain
            f'{region}_heavy_rain_coverage': float((precip_data > 10).sum().values),  # Areas with > 10mm rain
        }
        
        # Add percentiles
        for percentile in [25, 50, 75, 90, 95]:
            stats[f'{region}_p{percentile}_precip'] = float(precip_data.quantile(percentile/100).values)
        
        return stats
    
    def extract_temporal_features(self, date: datetime) -> Dict:
        """Extract temporal features from date"""
        return {
            'year': date.year,
            'month': date.month,
            'day': date.day,
            'day_of_year': date.timetuple().tm_yday,
            'week_of_year': date.isocalendar()[1],
            'quarter': (date.month - 1) // 3 + 1,
            'is_weekend': int(date.weekday() >= 5),
            'season': self._get_season(date.month),
            'month_sin': np.sin(2 * np.pi * date.month / 12),
            'month_cos': np.cos(2 * np.pi * date.month / 12),
            'day_sin': np.sin(2 * np.pi * date.timetuple().tm_yday / 365.25),
            'day_cos': np.cos(2 * np.pi * date.timetuple().tm_yday / 365.25),
        }
    
    def _get_season(self, month: int) -> int:
        """Convert month to season (0=Winter, 1=Spring, 2=Summer, 3=Fall)"""
        if month in [12, 1, 2]:
            return 0  # Winter
        elif month in [3, 4, 5]:
            return 1  # Spring
        elif month in [6, 7, 8]:
            return 2  # Summer
        else:
            return 3  # Fall
    
    def create_dataset(self, regions: List[str] = ['global'], 
                      start_year: int = None, end_year: int = None,
                      sample_size: int = None) -> pd.DataFrame:
        """Create ML-ready dataset with features from multiple regions"""
        print("Creating dataset...")
        
        files_with_dates = self.get_file_list(start_year, end_year)
        
        if sample_size:
            files_with_dates = files_with_dates[:sample_size]
        
        print(f"Processing {len(files_with_dates)} files...")
        
        all_features = []
        
        for i, (file_path, date) in enumerate(files_with_dates):
            if i % 50 == 0:
                print(f"Processing file {i+1}/{len(files_with_dates)}: {file_path.name}")
            
            try:
                # Load data
                ds = self.load_single_file(file_path)
                if ds is None:
                    continue
                
                # Extract features
                features = {'date': date}
                
                # Add temporal features
                features.update(self.extract_temporal_features(date))
                
                # Add regional features
                for region in regions:
                    regional_stats = self.extract_regional_stats(ds, region)
                    features.update(regional_stats)
                
                all_features.append(features)
                
                # Close dataset to free memory
                ds.close()
                
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                continue
        
        # Convert to DataFrame
        df = pd.DataFrame(all_features)
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date').reset_index(drop=True)
        
        print(f"Dataset created with {len(df)} records and {len(df.columns)} features")
        return df
    
    def add_lag_features(self, df: pd.DataFrame, target_cols: List[str], 
                        lags: List[int] = [1, 3, 7, 14, 30]) -> pd.DataFrame:
        """Add lagged features for time series prediction"""
        print("Adding lag features...")
        
        df_with_lags = df.copy()
        
        for col in target_cols:
            if col in df.columns:
                for lag in lags:
                    df_with_lags[f'{col}_lag_{lag}'] = df[col].shift(lag)
        
        # Drop rows with NaN values created by lagging
        df_with_lags = df_with_lags.dropna()
        
        print(f"Added lag features. Dataset now has {len(df_with_lags.columns)} features")
        return df_with_lags
    
    def add_rolling_features(self, df: pd.DataFrame, target_cols: List[str],
                           windows: List[int] = [7, 14, 30]) -> pd.DataFrame:
        """Add rolling window statistics"""
        print("Adding rolling features...")
        
        df_with_rolling = df.copy()
        
        for col in target_cols:
            if col in df.columns:
                for window in windows:
                    df_with_rolling[f'{col}_rolling_mean_{window}'] = df[col].rolling(window).mean()
                    df_with_rolling[f'{col}_rolling_std_{window}'] = df[col].rolling(window).std()
                    df_with_rolling[f'{col}_rolling_max_{window}'] = df[col].rolling(window).max()
                    df_with_rolling[f'{col}_rolling_min_{window}'] = df[col].rolling(window).min()
        
        # Drop rows with NaN values
        df_with_rolling = df_with_rolling.dropna()
        
        print(f"Added rolling features. Dataset now has {len(df_with_rolling.columns)} features")
        return df_with_rolling
    
    def save_dataset(self, df: pd.DataFrame, filename: str):
        """Save dataset to processed directory"""
        filepath = self.processed_dir / filename
        df.to_csv(filepath, index=False)
        print(f"Dataset saved to {filepath}")
        
        # Also save a summary
        summary_file = self.processed_dir / f"{filename.replace('.csv', '_summary.txt')}"
        with open(summary_file, 'w') as f:
            f.write(f"Dataset Summary\n")
            f.write(f"===============\n")
            f.write(f"Shape: {df.shape}\n")
            f.write(f"Date range: {df['date'].min()} to {df['date'].max()}\n")
            f.write(f"Columns: {list(df.columns)}\n")
            f.write(f"\nBasic Statistics:\n")
            f.write(str(df.describe()))
        
        print(f"Summary saved to {summary_file}")

def main():
    """Example usage"""
    # Initialize analyzer
    analyzer = TRMMPrecipitationAnalyzer("/home/raju/nasa_space_app/ml-project/data/raw")
    
    # Create a sample dataset (small for testing)
    print("Creating sample dataset...")
    df = analyzer.create_dataset(
        regions=['global', 'usa'],
        start_year=2011,
        end_year=2011,  # Just 2011 for quick testing
        sample_size=100  # First 100 files
    )
    
    # Add time series features
    target_columns = ['global_mean_precip', 'global_max_precip', 'usa_mean_precip']
    df_with_lags = analyzer.add_lag_features(df, target_columns, lags=[1, 3, 7])
    df_with_rolling = analyzer.add_rolling_features(df_with_lags, target_columns, windows=[7, 14])
    
    # Save the dataset
    analyzer.save_dataset(df_with_rolling, "precipitation_features_sample.csv")
    
    print("Data processing complete!")

if __name__ == "__main__":
    main()
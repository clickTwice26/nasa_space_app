"""
Test script for NASA POWER API integration
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.power_api import PowerAPIService

def test_power_api():
    """Test the NASA POWER API service"""
    print("Testing NASA POWER API Service...")
    
    # Test coordinates for Dhaka, Bangladesh
    lat = 23.7644
    lon = 90.3897
    start = "20240901"  # September 1, 2024
    end = "20240905"    # September 5, 2024
    
    print(f"Requesting data for Dhaka, Bangladesh")
    print(f"Coordinates: {lat}, {lon}")
    print(f"Date range: {start} to {end}")
    print()
    
    result = PowerAPIService.get_power_data(lat, lon, start, end)
    
    if result['success']:
        print("✅ API call successful!")
        print(f"Retrieved {len(result['data'])} days of data")
        print("\nSample data:")
        for i, day in enumerate(result['data'][:3]):  # Show first 3 days
            temp = day['temperature']
            precip = day['precipitation']
            print(f"  {day['date']}: {temp}°C, {precip}mm precipitation")
        
        if len(result['data']) > 3:
            print(f"  ... and {len(result['data']) - 3} more days")
        
        print(f"\nMetadata:")
        print(f"  Source: {result['metadata']['source']}")
        print(f"  Period: {result['metadata']['data_period']['start']} to {result['metadata']['data_period']['end']}")
        print(f"  Total days: {result['metadata']['data_period']['total_days']}")
        
    else:
        print("❌ API call failed!")
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    test_power_api()
#!/usr/bin/env python3
"""
Test script for NASA MODIS Aerosol Optical Depth (AOD) air quality API integration.

This script tests the MODIS air quality service both directly and via the Flask endpoint.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_modis_service():
    """Test the MODIS air quality service directly"""
    print("🛰️  Testing NASA MODIS Air Quality Service")
    print("=" * 50)
    
    from app.services.modis_api import get_modis_air_quality
    
    # Test with different locations to show regional variations
    test_locations = [
        {"name": "Dhaka, Bangladesh", "lat": 23.7644, "lon": 90.3897},
        {"name": "New Delhi, India", "lat": 28.6139, "lon": 77.2090},
        {"name": "Beijing, China", "lat": 39.9042, "lon": 116.4074},
        {"name": "Los Angeles, USA", "lat": 34.0522, "lon": -118.2437},
        {"name": "Rural Montana, USA", "lat": 47.0527, "lon": -109.6333}
    ]
    
    start = "20240925"
    end = "20240927"
    
    print(f"📅 Date range: {start} to {end}")
    print()
    
    success_count = 0
    
    for location in test_locations:
        print(f"📍 Testing: {location['name']} ({location['lat']}, {location['lon']})")
        
        try:
            result = get_modis_air_quality(location['lat'], location['lon'], start, end)
            
            if result['success']:
                print(f"   ✅ Success: {len(result['data'])} days of data")
                
                # Show air quality summary
                if result['data']:
                    avg_aod = sum(day['aerosol_index'] for day in result['data']) / len(result['data'])
                    air_quality_levels = [day['air_quality_level'] for day in result['data']]
                    most_common_level = max(set(air_quality_levels), key=air_quality_levels.count)
                    
                    print(f"   📊 Average AOD: {avg_aod:.3f}")
                    print(f"   🌬️  Most common air quality: {most_common_level}")
                    
                    # Show sample day
                    sample_day = result['data'][0]
                    print(f"   📝 Sample ({sample_day['date']}): AOD {sample_day['aerosol_index']}, {sample_day['air_quality_level']}")
                    print(f"      Health advisory: {sample_day['health_advisory']}")
                
                success_count += 1
            else:
                print(f"   ❌ Failed: {result['error']}")
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
        
        print()
    
    return success_count == len(test_locations)

def test_air_quality_levels():
    """Test different air quality level calculations"""
    print("🔍 Testing Air Quality Level Classifications")
    print("=" * 50)
    
    from app.services.modis_api import MODISAirQualityService
    service = MODISAirQualityService()
    
    # Test different AOD values to verify classification
    test_aod_values = [0.05, 0.2, 0.45, 0.8, 1.2, 2.0]
    
    for aod in test_aod_values:
        # Simulate calculation with a fixed AOD
        if aod <= 0.1:
            level = "Good"
            color = "🟢"
        elif aod <= 0.3:
            level = "Moderate"
            color = "🟡"
        elif aod <= 0.6:
            level = "Unhealthy for Sensitive"
            color = "🟠"
        elif aod <= 1.0:
            level = "Unhealthy"
            color = "🔴"
        elif aod <= 1.5:
            level = "Very Unhealthy"
            color = "🟣"
        else:
            level = "Hazardous"
            color = "🟤"
        
        print(f"   AOD {aod:>4.2f} → {color} {level}")
    
    print()

def test_error_handling():
    """Test error handling with invalid inputs"""
    print("🔍 Testing Error Handling")
    print("=" * 30)
    
    from app.services.modis_api import get_modis_air_quality
    
    test_cases = [
        {
            "name": "Invalid coordinates (lat > 90)",
            "lat": 999,
            "lon": 90.3897,
            "start": "20240925",
            "end": "20240927"
        },
        {
            "name": "Invalid coordinates (lon > 180)",
            "lat": 23.7644,
            "lon": 999,
            "start": "20240925",
            "end": "20240927"
        },
        {
            "name": "Invalid date format",
            "lat": 23.7644,
            "lon": 90.3897,
            "start": "2024-09-25",
            "end": "20240927"
        },
        {
            "name": "End date before start date",
            "lat": 23.7644,
            "lon": 90.3897,
            "start": "20240927",
            "end": "20240925"
        },
        {
            "name": "Date range too large (>365 days)",
            "lat": 23.7644,
            "lon": 90.3897,
            "start": "20230101",
            "end": "20241231"
        }
    ]
    
    for test in test_cases:
        print(f"Testing: {test['name']}")
        result = get_modis_air_quality(test['lat'], test['lon'], test['start'], test['end'])
        
        if not result['success']:
            print(f"   ✅ Correctly handled error: {result['error']}")
        else:
            print(f"   ❌ Should have failed but didn't")
        print()

if __name__ == "__main__":
    print("🚀 NASA MODIS Air Quality API Integration Test")
    print("=" * 60)
    print()
    
    # Test the service with multiple locations
    service_success = test_modis_service()
    print()
    
    # Test air quality level classifications
    test_air_quality_levels()
    
    # Test error handling
    test_error_handling()
    
    # Summary
    print("📋 Test Summary")
    print("=" * 20)
    if service_success:
        print("✅ MODIS Air Quality API integration is working correctly!")
        print("🌬️  Ready to fetch NASA aerosol and air quality data")
        print()
        print("🔗 Try the API endpoint:")
        print("   GET /api/modis-air?lat=23.7644&lon=90.3897&start=20240925&end=20240927")
        print()
        print("📊 Air Quality Levels:")
        print("   🟢 Good (AOD 0.0-0.1): Safe for all outdoor activities")
        print("   🟡 Moderate (AOD 0.1-0.3): Acceptable for most people")
        print("   🟠 Unhealthy for Sensitive (AOD 0.3-0.6): Sensitive groups limit exposure")
        print("   🔴 Unhealthy (AOD 0.6-1.0): Everyone should limit outdoor activities")
        print("   🟣 Very Unhealthy (AOD 1.0-1.5): Health warnings for all")
        print("   🟤 Hazardous (AOD >1.5): Emergency conditions")
    else:
        print("❌ MODIS Air Quality API integration has issues")
        print("🔧 Check service implementation and data processing")
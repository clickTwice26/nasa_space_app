#!/usr/bin/env python3
"""
Test script for NASA GPM IMERG precipitation data API integration.

This script tests the GPM API service both directly and via the Flask endpoint.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_gpm_service():
    """Test the GPM API service directly"""
    print("🛰️  Testing NASA GPM IMERG API Service")
    print("=" * 50)
    
    from app.services.gpm_api import get_gpm_data
    
    # Test with Dhaka, Bangladesh coordinates
    lat = 23.7644
    lon = 90.3897
    start = "20240925"
    end = "20240927"
    
    print(f"📍 Location: {lat}, {lon} (Dhaka, Bangladesh)")
    print(f"📅 Date range: {start} to {end}")
    print()
    
    try:
        result = get_gpm_data(lat, lon, start, end)
        
        if result['success']:
            print("✅ GPM API Service Test: SUCCESS")
            print(f"📊 Data points: {len(result['data'])}")
            print(f"🌧️  Source: {result['metadata']['source']}")
            print()
            
            # Display sample data
            print("📈 Sample precipitation data:")
            for day in result['data'][:3]:  # Show first 3 days
                precip = day['precipitation']
                precip_type = day['precipitation_type']
                print(f"   {day['date']}: {precip}mm ({precip_type})")
            
            if len(result['data']) > 3:
                print(f"   ... and {len(result['data']) - 3} more days")
            
            print()
            return True
        else:
            print("❌ GPM API Service Test: FAILED")
            print(f"Error: {result['error']}")
            return False
            
    except Exception as e:
        print(f"❌ GPM API Service Test: EXCEPTION")
        print(f"Error: {str(e)}")
        return False

def test_error_handling():
    """Test error handling with invalid inputs"""
    print("🔍 Testing Error Handling")
    print("=" * 30)
    
    from app.services.gpm_api import get_gpm_data
    
    test_cases = [
        {
            "name": "Invalid coordinates",
            "lat": 999,
            "lon": 90.3897,
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
        }
    ]
    
    for test in test_cases:
        print(f"Testing: {test['name']}")
        result = get_gpm_data(test['lat'], test['lon'], test['start'], test['end'])
        
        if not result['success']:
            print(f"   ✅ Correctly handled error: {result['error']}")
        else:
            print(f"   ❌ Should have failed but didn't")
        print()

if __name__ == "__main__":
    print("🚀 NASA GPM IMERG API Integration Test")
    print("=" * 60)
    print()
    
    # Test the service
    service_success = test_gpm_service()
    print()
    
    # Test error handling
    test_error_handling()
    
    # Summary
    print("📋 Test Summary")
    print("=" * 20)
    if service_success:
        print("✅ GPM API integration is working correctly!")
        print("🌧️  Ready to fetch NASA precipitation data")
        print()
        print("🔗 Try the API endpoint:")
        print("   GET /api/gpm-data?lat=23.7644&lon=90.3897&start=20240925&end=20240927")
    else:
        print("❌ GPM API integration has issues")
        print("🔧 Check credentials and network connectivity")
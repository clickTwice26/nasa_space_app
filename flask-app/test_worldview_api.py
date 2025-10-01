#!/usr/bin/env python3
"""
Test script for NASA Worldview Snapshots API integration.

This script tests the Worldview satellite imagery service both directly and via the Flask endpoint.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_worldview_service():
    """Test the Worldview service directly"""
    print("🛰️  Testing NASA Worldview Snapshots API Service")
    print("=" * 55)
    
    from app.services.worldview_api import get_worldview_image, get_available_layers
    
    # Test with different locations and layers
    test_cases = [
        {
            "name": "Dhaka, Bangladesh - True Color",
            "lat": 23.7644,
            "lon": 90.3897,
            "date": "2024-09-25",
            "layers": "MODIS_Terra_CorrectedReflectance_TrueColor"
        },
        {
            "name": "Amazon Rainforest - False Color",
            "lat": -3.4653,
            "lon": -62.2159,
            "date": "2024-09-20",
            "layers": "MODIS_Terra_CorrectedReflectance_Bands721"
        },
        {
            "name": "Arctic Ice - True Color",
            "lat": 75.0,
            "lon": -100.0,
            "date": "2024-09-15",
            "layers": "MODIS_Aqua_CorrectedReflectance_TrueColor"
        },
        {
            "name": "California Fires - Multiple Layers",
            "lat": 37.7749,
            "lon": -122.4194,
            "date": "2024-08-15",
            "layers": "MODIS_Terra_CorrectedReflectance_TrueColor,MODIS_Terra_Aerosol"
        }
    ]
    
    success_count = 0
    
    for test_case in test_cases:
        print(f"📍 Testing: {test_case['name']}")
        print(f"   Location: ({test_case['lat']}, {test_case['lon']})")
        print(f"   Date: {test_case['date']}")
        print(f"   Layers: {test_case['layers']}")
        
        try:
            result = get_worldview_image(
                test_case['lat'], 
                test_case['lon'], 
                test_case['date'], 
                test_case['layers']
            )
            
            if result['success']:
                print(f"   ✅ Success: Image URL generated")
                print(f"   🖼️  Image URL: {result['image_url'][:80]}...")
                print(f"   📦 Bounding box: {result['bbox']}")
                print(f"   📏 Image size: {result['metadata']['width']}x{result['metadata']['height']}")
                success_count += 1
            else:
                print(f"   ❌ Failed: {result['error']}")
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
        
        print()
    
    # Test available layers
    print("🗂️  Available Layers:")
    print("-" * 20)
    layers = get_available_layers()
    for layer_id, layer_name in layers.items():
        print(f"   • {layer_name}")
        print(f"     ID: {layer_id}")
    
    print()
    return success_count == len(test_cases)

def test_error_handling():
    """Test error handling with invalid inputs"""
    print("🔍 Testing Error Handling")
    print("=" * 30)
    
    from app.services.worldview_api import get_worldview_image
    
    test_cases = [
        {
            "name": "Invalid coordinates (lat > 90)",
            "lat": 999,
            "lon": 90.3897,
            "date": "2024-09-25",
            "layers": "MODIS_Terra_CorrectedReflectance_TrueColor"
        },
        {
            "name": "Invalid date format",
            "lat": 23.7644,
            "lon": 90.3897,
            "date": "2024-09-25T10:00:00",
            "layers": "MODIS_Terra_CorrectedReflectance_TrueColor"
        },
        {
            "name": "Future date",
            "lat": 23.7644,
            "lon": 90.3897,
            "date": "2025-12-31",
            "layers": "MODIS_Terra_CorrectedReflectance_TrueColor"
        },
        {
            "name": "Empty layers",
            "lat": 23.7644,
            "lon": 90.3897,
            "date": "2024-09-25",
            "layers": ""
        }
    ]
    
    for test in test_cases:
        print(f"Testing: {test['name']}")
        result = get_worldview_image(test['lat'], test['lon'], test['date'], test['layers'])
        
        if not result['success']:
            print(f"   ✅ Correctly handled error: {result['error']}")
        else:
            print(f"   ❌ Should have failed but didn't")
        print()

def test_flask_endpoints():
    """Test the Flask API endpoints"""
    print("🧪 Testing Flask API Endpoints")
    print("=" * 35)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Test successful request
            print("Testing /api/worldview-image endpoint:")
            response = client.get('/api/worldview-image?lat=23.7644&lon=90.3897&date=2024-09-25&layers=MODIS_Terra_CorrectedReflectance_TrueColor')
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                import json
                data = json.loads(response.data)
                print("   ✅ Successful response")
                print(f"   📅 Date: {data['date']}")
                print(f"   🗂️  Layers: {data['layers']}")
                print(f"   🖼️  Image URL: {data['image_url'][:60]}...")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                print(f"   Response: {response.data.decode()}")
            
            print()
            
            # Test layers endpoint
            print("Testing /api/worldview-layers endpoint:")
            response = client.get('/api/worldview-layers')
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = json.loads(response.data)
                print("   ✅ Successful response")
                print(f"   📊 Available layers: {data['layer_count']}")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
            
            print()
            
            # Test error handling
            print("Testing error handling:")
            response = client.get('/api/worldview-image?lat=999&lon=90.3897&date=2024-09-25&layers=MODIS_Terra_CorrectedReflectance_TrueColor')
            print(f"   Invalid coordinates - Status: {response.status_code}")
            if response.status_code == 400:
                print("   ✅ Correctly handled invalid coordinates")
    
    except Exception as e:
        print(f"   ❌ Flask test failed: {str(e)}")

if __name__ == "__main__":
    print("🚀 NASA Worldview Snapshots API Integration Test")
    print("=" * 60)
    print()
    
    # Test the service directly
    service_success = test_worldview_service()
    print()
    
    # Test error handling
    test_error_handling()
    
    # Test Flask endpoints
    test_flask_endpoints()
    
    # Summary
    print("📋 Test Summary")
    print("=" * 20)
    if service_success:
        print("✅ NASA Worldview Snapshots API integration is working correctly!")
        print("🖼️  Ready to generate satellite imagery URLs")
        print()
        print("🔗 Try the API endpoints:")
        print("   GET /api/worldview-image?lat=23.7644&lon=90.3897&date=2024-09-25&layers=MODIS_Terra_CorrectedReflectance_TrueColor")
        print("   GET /api/worldview-layers")
        print()
        print("🗂️  Popular Layers:")
        print("   • MODIS_Terra_CorrectedReflectance_TrueColor: Natural color satellite imagery")
        print("   • MODIS_Terra_CorrectedReflectance_Bands721: False color for vegetation analysis")
        print("   • MODIS_Terra_Aerosol: Aerosol optical depth visualization")
        print("   • VIIRS_SNPP_CorrectedReflectance_TrueColor: High-resolution VIIRS imagery")
    else:
        print("❌ NASA Worldview Snapshots API integration has issues")
        print("🔧 Check service implementation and API connectivity")
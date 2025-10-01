#!/usr/bin/env python3
"""
Test script for Agricultural Risk Engine integration.

This script tests the risk analysis service both directly and via Flask endpoints.
"""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_risk_engine_service():
    """Test the Risk Engine service directly"""
    print("🌾 Testing Agricultural Risk Engine Service")
    print("=" * 50)
    
    from app.services.risk_engine import crop_risk_analysis
    
    # Test with different crops and locations
    test_cases = [
        {
            "name": "Rice in Dhaka, Bangladesh",
            "lat": 23.7644,
            "lon": 90.3897,
            "crop": "rice",
            "start": "20240925",
            "end": "20241001"
        },
        {
            "name": "Wheat in Punjab, India",
            "lat": 30.7333,
            "lon": 76.7794,
            "crop": "wheat",
            "start": "20240920",
            "end": "20240927"
        },
        {
            "name": "Potato in Idaho, USA",
            "lat": 44.0682,
            "lon": -114.7420,
            "crop": "potato",
            "start": "20240915",
            "end": "20240922"
        },
        {
            "name": "Corn in Iowa, USA",
            "lat": 41.8780,
            "lon": -93.0977,
            "crop": "corn",
            "start": "20240910",
            "end": "20240917"
        }
    ]
    
    success_count = 0
    
    for test_case in test_cases:
        print(f"🌱 Testing: {test_case['name']}")
        print(f"   Location: ({test_case['lat']}, {test_case['lon']})")
        print(f"   Crop: {test_case['crop'].title()}")
        print(f"   Period: {test_case['start']} to {test_case['end']}")
        
        try:
            result = crop_risk_analysis(
                test_case['lat'],
                test_case['lon'],
                test_case['crop'],
                test_case['start'],
                test_case['end']
            )
            
            if result['success']:
                print(f"   ✅ Success: Risk level {result['risk_level']}")
                print(f"   📊 Alerts: {len(result['alerts'])} alerts identified")
                print(f"   💡 Recommendations: {len(result['recommendations'])} provided")
                
                # Show sample alerts and recommendations
                if result['alerts']:
                    print(f"   🚨 Sample alert: {result['alerts'][0]}")
                if result['recommendations']:
                    print(f"   💭 Sample recommendation: {result['recommendations'][0]}")
                
                print(f"   📝 Summary: {result['summary'][:80]}...")
                success_count += 1
            else:
                print(f"   ❌ Failed: {result['error']}")
        except Exception as e:
            print(f"   ❌ Exception: {str(e)}")
        
        print()
    
    return success_count == len(test_cases)

def test_risk_levels():
    """Test different risk level scenarios"""
    print("🔍 Testing Risk Level Classifications")
    print("=" * 40)
    
    from app.services.risk_engine import crop_risk_analysis
    
    # Test scenarios designed to trigger different risk levels
    scenarios = [
        {
            "name": "Low Risk Scenario",
            "location": "Moderate climate zone",
            "lat": 40.0,
            "lon": -95.0,
            "crop": "corn"
        },
        {
            "name": "High Risk Scenario",
            "location": "Tropical flood-prone area", 
            "lat": 10.0,
            "lon": 100.0,
            "crop": "rice"
        },
        {
            "name": "Cold Region Scenario",
            "location": "Northern temperate zone",
            "lat": 55.0,
            "lon": -105.0,
            "crop": "wheat"
        }
    ]
    
    for scenario in scenarios:
        print(f"📍 {scenario['name']} - {scenario['location']}")
        result = crop_risk_analysis(
            scenario['lat'], scenario['lon'], scenario['crop'], 
            "20240920", "20240927"
        )
        
        if result['success']:
            risk_emoji = {
                'low': '✅',
                'medium': '⚠️',
                'high': '🚨'
            }.get(result['risk_level'], '❓')
            
            print(f"   {risk_emoji} Risk Level: {result['risk_level'].upper()}")
            print(f"   📊 Alert Count: {len(result['alerts'])}")
        else:
            print(f"   ❌ Analysis failed")
        print()

def test_flask_endpoints():
    """Test the Flask API endpoints"""
    print("🧪 Testing Flask Risk API Endpoints")
    print("=" * 40)
    
    try:
        from app import create_app
        
        app = create_app()
        
        with app.test_client() as client:
            # Test risk-alerts endpoint
            print("Testing /api/risk-alerts endpoint:")
            response = client.get('/api/risk-alerts?lat=23.7644&lon=90.3897&crop=rice&start=20240925&end=20241001')
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                import json
                data = json.loads(response.data)
                print("   ✅ Successful response")
                print(f"   🌾 Crop: {data['crop']}")
                print(f"   📊 Risk Level: {data['risk_level']}")
                print(f"   🚨 Alerts: {len(data['alerts'])}")
                print(f"   💡 Recommendations: {len(data['recommendations'])}")
                print(f"   📱 Mobile-friendly: {data['mobile_friendly']['emoji_alerts']} emoji alerts")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
                print(f"   Response: {response.data.decode()[:200]}...")
            
            print()
            
            # Test risk-info endpoint
            print("Testing /api/risk-info endpoint:")
            response = client.get('/api/risk-info')
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = json.loads(response.data)
                print("   ✅ Successful response")
                print(f"   🌾 Supported crops: {len(data['supported_crops'])}")
                print(f"   📡 Data sources: {len(data['data_sources'])}")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
            
            print()
            
            # Test risk-test endpoint
            print("Testing /api/risk-test endpoint:")
            response = client.get('/api/risk-test')
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = json.loads(response.data)
                print("   ✅ Successful response")
                print(f"   🏠 Test location: {data['test_location']}")
                print(f"   🌾 Test crop: {data['test_crop']}")
                print(f"   ⚙️ Service status: {data['service_status']}")
            else:
                print(f"   ❌ Failed with status {response.status_code}")
            
            print()
            
            # Test error handling
            print("Testing error handling:")
            response = client.get('/api/risk-alerts?lat=999&lon=90.3897&crop=rice&start=20240925&end=20241001')
            print(f"   Invalid coordinates - Status: {response.status_code}")
            if response.status_code == 400:
                print("   ✅ Correctly handled invalid coordinates")
                
            response = client.get('/api/risk-alerts?lat=23.7644&lon=90.3897&crop=invalid&start=20240925&end=20241001')
            print(f"   Invalid crop - Status: {response.status_code}")
            if response.status_code == 400:
                print("   ✅ Correctly handled invalid crop")
    
    except Exception as e:
        print(f"   ❌ Flask test failed: {str(e)}")

def test_mobile_friendliness():
    """Test mobile-friendly features"""
    print("📱 Testing Mobile-Friendly Features")
    print("=" * 35)
    
    from app.services.risk_engine import crop_risk_analysis
    
    result = crop_risk_analysis(23.7644, 90.3897, "rice", "20240925", "20241001")
    
    if result['success']:
        # Count emojis in alerts
        emoji_count = 0
        emojis = ['🌧️', '🌡️', '🟠', '✅', '⚠️', '🌊', '🏜️', '🔥', '❄️', '🌱', '📊', '🚨']
        
        for alert in result['alerts']:
            for emoji in emojis:
                if emoji in alert:
                    emoji_count += 1
                    break
        
        print(f"   📊 Total alerts: {len(result['alerts'])}")
        print(f"   😀 Emoji alerts: {emoji_count}")
        print(f"   📝 Summary length: {len(result['summary'])} characters")
        print(f"   💡 Recommendations: {len(result['recommendations'])}")
        
        # Check if summary is mobile-friendly (not too long)
        if len(result['summary']) <= 150:
            print("   ✅ Summary is mobile-friendly length")
        else:
            print("   ⚠️ Summary might be too long for mobile")
        
        # Show sample content
        if result['alerts']:
            print(f"   📱 Sample alert: {result['alerts'][0]}")
        if result['recommendations']:
            print(f"   💭 Sample recommendation: {result['recommendations'][0]}")
    else:
        print("   ❌ Risk analysis failed")

if __name__ == "__main__":
    print("🚀 Agricultural Risk Engine Integration Test")
    print("=" * 60)
    print()
    
    # Test the service directly
    service_success = test_risk_engine_service()
    print()
    
    # Test risk level classifications
    test_risk_levels()
    
    # Test Flask endpoints
    test_flask_endpoints()
    
    # Test mobile-friendly features
    test_mobile_friendliness()
    
    # Summary
    print()
    print("📋 Test Summary")
    print("=" * 20)
    if service_success:
        print("✅ Agricultural Risk Engine integration is working correctly!")
        print("🌾 Ready to provide intelligent crop risk analysis")
        print()
        print("🔗 Try the API endpoints:")
        print("   GET /api/risk-alerts?lat=23.7644&lon=90.3897&crop=rice&start=20240925&end=20241001")
        print("   GET /api/risk-info")
        print("   GET /api/risk-test")
        print()
        print("🌱 Supported Crops:")
        print("   • Rice: High water needs, flood-prone")
        print("   • Wheat: Moderate water needs, heat-sensitive")
        print("   • Potato: Cool season crop, frost-sensitive")
        print("   • Jute: High water needs, warm climate")
        print("   • Corn: Moderate water needs, versatile")
        print()
        print("📱 Mobile Features:")
        print("   • Emoji-rich alerts for quick recognition")
        print("   • Farmer-friendly language and recommendations")
        print("   • Color-coded risk levels for visual clarity")
        print("   • Concise summaries optimized for mobile screens")
    else:
        print("❌ Agricultural Risk Engine integration has issues")
        print("🔧 Check service implementation and data connectivity")
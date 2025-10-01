# 🌾 TerraPulse Agricultural Risk Engine Documentation

## 🚀 Overview

The TerraPulse Agricultural Risk Engine is a comprehensive intelligent system that combines **4 NASA satellite data sources** to provide real-time crop risk analysis for farmers worldwide. This system transforms complex satellite data into actionable, mobile-friendly insights.

## 📡 Integrated NASA Data Sources

### 1. NASA POWER API
- **Purpose**: Weather monitoring (temperature, precipitation, humidity)
- **Coverage**: Global, daily data from 1981-present
- **Authentication**: None required
- **Risk Factors**: Heat stress, cold stress, drought, excessive rain

### 2. NASA GPM IMERG API
- **Purpose**: Advanced precipitation analysis
- **Coverage**: Global, 30-minute intervals, 2000-present  
- **Authentication**: NASA Earthdata credentials
- **Risk Factors**: Flooding, drought, irrigation planning

### 3. NASA MODIS API
- **Purpose**: Vegetation health and air quality
- **Coverage**: Global, daily data from 2000-present
- **Authentication**: None required
- **Risk Factors**: Vegetation stress, air quality impacts

### 4. NASA Worldview API
- **Purpose**: Satellite imagery visualization
- **Coverage**: Global, daily imagery from multiple satellites
- **Authentication**: None required
- **Risk Factors**: Visual field validation, storm tracking

## 🌾 Supported Crops & Risk Profiles

### Rice 🌾
- **Temperature Range**: 20-35°C (optimal: 25-30°C)
- **Water Needs**: High (5-7mm/day minimum)
- **Critical Periods**: Transplanting, flowering, grain filling
- **Key Risks**: Flooding, heat stress, insufficient water

### Wheat 🌾
- **Temperature Range**: 12-25°C (optimal: 15-20°C)
- **Water Needs**: Moderate (3-5mm/day)
- **Critical Periods**: Germination, tillering, grain development
- **Key Risks**: Heat stress, drought, frost damage

### Potato 🥔
- **Temperature Range**: 15-20°C (optimal: 17-19°C)
- **Water Needs**: Consistent (4-6mm/day)
- **Critical Periods**: Tuber initiation, bulking
- **Key Risks**: Cold stress, drought, excessive heat

### Jute 🌿
- **Temperature Range**: 24-35°C (optimal: 28-32°C)
- **Water Needs**: High (6-8mm/day)
- **Critical Periods**: Vegetative growth, flowering
- **Key Risks**: Water stress, temperature extremes

### Corn 🌽
- **Temperature Range**: 18-27°C (optimal: 21-24°C)
- **Water Needs**: High (5-7mm/day)
- **Critical Periods**: Tasseling, grain filling
- **Key Risks**: Heat stress, drought, flooding

## 🚨 Risk Assessment System

### Risk Levels
- **🚨 HIGH**: Critical risks requiring immediate attention
- **⚠️ MEDIUM**: Some concerns to monitor, take precautionary measures
- **✅ LOW**: Minimal risks, favorable conditions

### Alert Categories
- **🌡️ Temperature Alerts**: Heat stress, cold stress, frost warnings
- **💧 Water Alerts**: Drought conditions, excessive precipitation, irrigation needs
- **🌱 Vegetation Alerts**: Stress indicators, health decline, growth issues
- **🌍 Environmental Alerts**: Air quality, climate vulnerability, seasonal trends

## 📱 API Endpoints

### 1. Risk Analysis Endpoint
```
GET /api/risk-alerts
```

**Parameters:**
- `lat` (required): Latitude (-90 to 90)
- `lon` (required): Longitude (-180 to 180)
- `crop` (required): Crop type (rice, wheat, potato, jute, corn)
- `start` (required): Start date (YYYYMMDD)
- `end` (required): End date (YYYYMMDD)

**Example:**
```
GET /api/risk-alerts?lat=23.7644&lon=90.3897&crop=rice&start=20240925&end=20241001
```

**Response Format:**
```json
{
  "risk_level": "medium",
  "crop": "Rice",
  "location": {
    "latitude": 23.7644,
    "longitude": 90.3897
  },
  "period": {
    "start": "20240925",
    "end": "20241001"
  },
  "alerts": [
    "💧 Insufficient water for high-demand crop: 15.5mm",
    "🟡 Vegetation concern: NDVI 0.38 approaching stress level"
  ],
  "recommendations": [
    "💦 Monitor irrigation systems carefully",
    "📊 Keep detailed records of field conditions"
  ],
  "summary": "⚠️ Moderate risks identified for rice during Sep 25-Oct 01. 4 concerns to monitor.",
  "data_availability": {
    "power_api": true,
    "gpm_api": true,
    "modis_api": true,
    "worldview_api": true
  }
}
```

### 2. Service Information Endpoint
```
GET /api/risk-info
```

Returns service information, supported crops, and risk level definitions.

### 3. Service Test Endpoint
```
GET /api/risk-test
```

Quick validation endpoint to check if the Risk Engine is operational.

## 🔧 Technical Architecture

### Service Layer (`app/services/`)
- **`risk_engine.py`**: Core risk analysis logic combining all NASA APIs
- **`power_api.py`**: NASA POWER weather data service
- **`gpm_api.py`**: NASA GPM IMERG precipitation service
- **`modis_api.py`**: NASA MODIS vegetation/air quality service
- **`worldview_api.py`**: NASA Worldview imagery service

### API Layer (`app/routes/`)
- **`risk.py`**: Risk analysis endpoints
- **`api_routes.py`**: General API endpoints for individual NASA services

### Analysis Engine Features
- **Crop-Specific Profiles**: Customized thresholds for each crop type
- **Multi-Source Integration**: Combines 4 NASA APIs intelligently
- **Rule-Based Analysis**: Weather + precipitation + vegetation + historical trends
- **Mobile Optimization**: Emoji alerts, concise summaries, farmer-friendly language
- **Error Handling**: Graceful degradation when data sources are unavailable

## 🌍 Real-World Usage Examples

### Bangladesh Rice Farmer
```bash
curl "http://localhost:5000/api/risk-alerts?lat=23.7644&lon=90.3897&crop=rice&start=20240925&end=20241001"
```
**Typical Results:**
- Medium risk due to insufficient precipitation
- Vegetation stress indicators
- Recommendations for irrigation monitoring

### Indian Wheat Farmer
```bash
curl "http://localhost:5000/api/risk-alerts?lat=28.6139&lon=77.2090&crop=wheat&start=20240920&end=20240927"
```
**Typical Results:**
- High risk due to vegetation stress
- Temperature concerns for optimal growth
- Soil and pest management recommendations

### Idaho Potato Farmer
```bash
curl "http://localhost:5000/api/risk-alerts?lat=44.0682&lon=-114.7420&crop=potato&start=20240915&end=20240922"
```
**Typical Results:**
- Medium risk due to cold conditions
- Drought stress indicators
- Water conservation recommendations

## 📊 Data Flow Architecture

1. **Request Processing**: API receives location, crop, and date parameters
2. **Multi-Source Data Fetch**: Parallel requests to all 4 NASA APIs
3. **Crop Profile Loading**: Retrieves crop-specific thresholds and requirements
4. **Risk Analysis**: Rule-based analysis combining all data sources
5. **Alert Generation**: Creates farmer-friendly alerts with emojis and actions
6. **Response Formatting**: Mobile-optimized JSON with summary and recommendations

## 🔐 Authentication Requirements

### NASA Earthdata (for GPM IMERG API)
- **Username**: shagatoc
- **Password**: [Set in environment or config]
- **Registration**: https://urs.earthdata.nasa.gov/

### Other APIs
- NASA POWER, MODIS, and Worldview APIs require no authentication

## 🚀 Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   ```bash
   export NASA_EARTHDATA_USERNAME="shagatoc"
   export NASA_EARTHDATA_PASSWORD="your_password"
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```

4. **Test the Risk Engine**:
   ```bash
   curl "http://localhost:5000/api/risk-test"
   ```

## 🔍 Testing & Validation

### Automated Test Suite
Run the comprehensive test suite:
```bash
python test_risk_engine.py
```

**Test Coverage:**
- Individual NASA API integration tests
- Risk analysis algorithm validation
- Mobile response format verification
- Error handling and edge cases
- Multi-crop scenario testing

### Manual Testing Examples
```bash
# Rice in Bangladesh (monsoon season)
curl "http://localhost:5000/api/risk-alerts?lat=23.7644&lon=90.3897&crop=rice&start=20240925&end=20241001"

# Wheat in India (winter season)
curl "http://localhost:5000/api/risk-alerts?lat=28.6139&lon=77.2090&crop=wheat&start=20240920&end=20240927"

# Potato in Idaho (cool season)
curl "http://localhost:5000/api/risk-alerts?lat=44.0682&lon=-114.7420&crop=potato&start=20240915&end=20240922"
```

## 📱 Mobile Integration

### Response Optimization
- **Emoji Alerts**: Visual indicators for quick understanding
- **Concise Summaries**: ~110 characters for mobile display
- **Farmer-Friendly Language**: Avoiding technical jargon
- **Actionable Recommendations**: Specific steps farmers can take

### Example Mobile Card Display
```
🚨 HIGH RISK - Wheat
📍 Delhi, India
📅 Sep 20-27

⚠️ 3 critical issues:
• 🟠 Vegetation stress detected
• 📉 Plant health declining  
• 🌍 Climate vulnerability

💡 Actions:
• Check soil nutrients
• Inspect for pests
• Consider irrigation

Summary: High risk alert for wheat. 
Immediate attention recommended.
```

## 🔮 Future Enhancements

### Planned Features
- **AI/ML Predictions**: Machine learning models for yield forecasting
- **Historical Comparisons**: Multi-year trend analysis
- **Custom Alerts**: User-defined thresholds and notifications
- **Multi-Language Support**: Localized alerts in farmer's native language
- **Offline Capability**: Cached data for areas with poor connectivity

### Additional Crop Support
- **Sugarcane**: High water requirement crop
- **Cotton**: Fiber crop with specific temperature needs
- **Soybean**: Protein crop for diverse climates
- **Tomato**: High-value vegetable crop

## 📋 Troubleshooting

### Common Issues

1. **NASA Earthdata Authentication Failed**
   - Verify username/password in environment variables
   - Check account status at https://urs.earthdata.nasa.gov/

2. **API Timeout Errors**
   - NASA APIs may have temporary outages
   - Risk Engine gracefully handles missing data sources

3. **Invalid Coordinates**
   - Latitude must be between -90 and 90
   - Longitude must be between -180 and 180

4. **Unsupported Crop Type**
   - Use: rice, wheat, potato, jute, or corn
   - Case-insensitive input accepted

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

### Code Structure
- Follow PEP 8 style guidelines
- Add comprehensive docstrings
- Include unit tests for new features
- Update this documentation for changes

### Adding New Crops
1. Add crop profile to `risk_engine.py`
2. Define temperature and water thresholds
3. Create crop-specific risk analysis rules
4. Add test cases in `test_risk_engine.py`

## 📞 Support

For technical support or feature requests:
- Create issues in the project repository
- Include API request examples and error messages
- Specify crop type, location, and date range for reproduction

---

## 🎉 Success Metrics

**✅ Complete Integration**: 4 NASA APIs successfully combined
**✅ Mobile Optimization**: Emoji alerts and farmer-friendly responses  
**✅ Global Coverage**: Works worldwide with any coordinates
**✅ Real-Time Analysis**: Live satellite data processing
**✅ Actionable Insights**: Specific recommendations for farmers
**✅ Robust Testing**: Comprehensive validation across multiple scenarios

**🌾 TerraPulse Agricultural Risk Engine: Transforming satellite data into farmer success! 🚀**
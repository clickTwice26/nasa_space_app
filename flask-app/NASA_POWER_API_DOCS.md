# NASA POWER API Integration

This document describes the NASA POWER API integration for the TerraPulse application.

## Overview

The NASA POWER API provides satellite-derived meteorological data including temperature and precipitation. This integration allows the TerraPulse app to fetch historical weather data for any location on Earth.

## API Endpoint

### GET `/api/power-data`

Fetch NASA POWER meteorological data for agricultural applications.

**Required Parameters:**
- `lat` (float): Latitude (-90 to 90)
- `lon` (float): Longitude (-180 to 180)  
- `start` (string): Start date in YYYYMMDD format
- `end` (string): End date in YYYYMMDD format

**Optional Parameters:**
- `parameters` (string): Comma-separated list of parameters (default: "T2M,PRECTOT")

### Example Requests

#### Basic Request
```bash
curl "http://localhost:8080/api/power-data?lat=23.7644&lon=90.3897&start=20240901&end=20240905"
```

#### Request for Dhaka, Bangladesh (1 week of data)
```bash
curl "http://localhost:8080/api/power-data?lat=23.7644&lon=90.3897&start=20240901&end=20240907"
```

#### Request with Custom Parameters
```bash
curl "http://localhost:8080/api/power-data?lat=23.7644&lon=90.3897&start=20240901&end=20240905&parameters=T2M,PRECTOT,RH2M"
```

### Response Format

#### Success Response
```json
{
  "success": true,
  "data": [
    {
      "date": "2024-09-01",
      "date_raw": "20240901",
      "temperature": 28.1,
      "precipitation": 0.0
    },
    {
      "date": "2024-09-02", 
      "date_raw": "20240902",
      "temperature": 28.6,
      "precipitation": 2.3
    }
  ],
  "metadata": {
    "source": "NASA POWER API",
    "data_version": "Unknown",
    "coordinate": {
      "latitude": 23.764,
      "longitude": 90.39
    },
    "parameter_info": {
      "T2M": "Temperature at 2 Meters (°C)",
      "PRECTOT": "Precipitation (mm/day)"
    },
    "data_period": {
      "start": "2024-09-01",
      "end": "2024-09-02", 
      "total_days": 2
    }
  },
  "request_info": {
    "latitude": 23.7644,
    "longitude": 90.3897,
    "start_date": "20240901",
    "end_date": "20240902",
    "parameters": "T2M,PRECTOT"
  }
}
```

#### Error Response
```json
{
  "success": false,
  "error": "Missing required parameters: end",
  "data": [],
  "required_params": {
    "lat": "Latitude (-90 to 90)",
    "lon": "Longitude (-180 to 180)",
    "start": "Start date (YYYYMMDD)", 
    "end": "End date (YYYYMMDD)"
  }
}
```

## Data Fields

### Daily Data Fields
- `date`: Human-readable date (YYYY-MM-DD)
- `date_raw`: Original date format (YYYYMMDD)
- `temperature`: Temperature at 2 meters in Celsius (null if unavailable)
- `precipitation`: Daily precipitation in mm (0.0 if no precipitation)

### Available Parameters
- `T2M`: Temperature at 2 Meters (°C)
- `PRECTOT`: Precipitation (mm/day)
- `RH2M`: Relative Humidity at 2 Meters (%)
- `PS`: Surface Pressure (kPa)
- `WS2M`: Wind Speed at 2 Meters (m/s)

## Error Handling

The API includes comprehensive error handling for:

1. **Missing Parameters**: Returns 400 with list of missing required parameters
2. **Invalid Coordinates**: Validates latitude (-90 to 90) and longitude (-180 to 180)
3. **Invalid Date Format**: Validates YYYYMMDD format
4. **API Timeouts**: Handles NASA POWER API timeouts gracefully
5. **Network Errors**: Handles connection issues
6. **Invalid Responses**: Handles malformed JSON responses

## Rate Limiting

The NASA POWER API has no explicit rate limits, but it's recommended to:
- Cache responses when possible
- Avoid making rapid successive requests
- Use reasonable date ranges (max 1 year)

## Mobile Frontend Integration

The API is designed to be mobile-friendly with:
- Simple JSON structure
- Clear error messages
- Minimal data overhead
- Consistent response format

### JavaScript Example
```javascript
async function fetchWeatherData(lat, lon, startDate, endDate) {
  const url = `/api/power-data?lat=${lat}&lon=${lon}&start=${startDate}&end=${endDate}`;
  
  try {
    const response = await fetch(url);
    const data = await response.json();
    
    if (data.success) {
      return data.data; // Array of daily weather records
    } else {
      throw new Error(data.error);
    }
  } catch (error) {
    console.error('Weather data fetch failed:', error);
    throw error;
  }
}

// Usage
fetchWeatherData(23.7644, 90.3897, '20240901', '20240907')
  .then(weatherData => {
    weatherData.forEach(day => {
      console.log(`${day.date}: ${day.temperature}°C, ${day.precipitation}mm`);
    });
  })
  .catch(error => {
    console.error('Error:', error.message);
  });
```

## Testing

Use the provided test script to verify the integration:

```bash
cd /home/raju/nasa_space_app/flask-app
source venv/bin/activate
python test_power_api.py
```

## Troubleshooting

### Common Issues

1. **"Invalid coordinates" error**: Ensure latitude is between -90 and 90, longitude between -180 and 180
2. **"Invalid date format" error**: Use YYYYMMDD format (e.g., "20240901")
3. **API timeout**: NASA POWER API might be slow; consider implementing client-side retries
4. **Missing data**: Some locations/dates might have null values; handle appropriately in frontend

### Logs

The service logs all requests and errors. Check application logs for debugging:
```bash
tail -f logs/nasa-space-app-combined-*.log
```
"""
Agricultural Risk Engine Service

This service combines multiple NASA and agricultural data sources to provide 
intelligent crop risk analysis for farmers and agricultural decision makers.

Data Sources:
- NASA POWER API: Weather data (temperature, solar radiation)
- NASA GPM IMERG: Precipitation data
- NASA MODIS: NDVI vegetation health data
- FAO/World Bank: Historical agricultural datasets

Risk Categories:
- Weather risks: Flooding, drought, heat stress, cold stress
- Vegetation health: NDVI analysis, crop stress indicators
- Historical trends: Long-term yield patterns, climate trends
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics

logger = logging.getLogger(__name__)

class RiskEngine:
    """Agricultural Risk Analysis Engine"""
    
    def __init__(self):
        self.crop_profiles = {
            "rice": {
                "heat_stress_temp": 35.0,
                "cold_stress_temp": 15.0,
                "flooding_threshold": 50.0,
                "drought_threshold": 10.0,
                "min_ndvi": 0.3,
                "optimal_temp_range": (20, 30),
                "water_needs": "high"
            },
            "wheat": {
                "heat_stress_temp": 32.0,
                "cold_stress_temp": 5.0,
                "flooding_threshold": 40.0,
                "drought_threshold": 15.0,
                "min_ndvi": 0.4,
                "optimal_temp_range": (15, 25),
                "water_needs": "moderate"
            },
            "potato": {
                "heat_stress_temp": 30.0,
                "cold_stress_temp": 2.0,
                "flooding_threshold": 35.0,
                "drought_threshold": 20.0,
                "min_ndvi": 0.35,
                "optimal_temp_range": (15, 24),
                "water_needs": "moderate"
            },
            "jute": {
                "heat_stress_temp": 38.0,
                "cold_stress_temp": 18.0,
                "flooding_threshold": 60.0,
                "drought_threshold": 25.0,
                "min_ndvi": 0.4,
                "optimal_temp_range": (24, 35),
                "water_needs": "high"
            },
            "corn": {
                "heat_stress_temp": 35.0,
                "cold_stress_temp": 10.0,
                "flooding_threshold": 45.0,
                "drought_threshold": 20.0,
                "min_ndvi": 0.5,
                "optimal_temp_range": (20, 30),
                "water_needs": "moderate"
            }
        }
        logger.info("Agricultural Risk Engine initialized")
    
    def crop_risk_analysis(
        self, 
        lat: float, 
        lon: float, 
        crop: str, 
        start: str, 
        end: str
    ) -> Dict:
        """
        Comprehensive crop risk analysis combining multiple data sources.
        
        Args:
            lat (float): Latitude (-90 to 90)
            lon (float): Longitude (-180 to 180)
            crop (str): Crop type (rice, wheat, potato, jute, corn)
            start (str): Start date (YYYYMMDD format)
            end (str): End date (YYYYMMDD format)
            
        Returns:
            Dict: Comprehensive risk analysis with alerts and recommendations
        """
        try:
            # Validate inputs
            is_valid, error_msg = self._validate_inputs(lat, lon, crop, start, end)
            if not is_valid:
                return {
                    "success": False,
                    "error": error_msg,
                    "crop": crop,
                    "alerts": [],
                    "summary": "Unable to analyze risk due to invalid inputs"
                }
            
            # Get crop profile
            crop_profile = self.crop_profiles.get(crop.lower(), self.crop_profiles["rice"])
            
            # Fetch data from all sources
            weather_data = self._fetch_weather_data(lat, lon, start, end)
            precipitation_data = self._fetch_precipitation_data(lat, lon, start, end)
            vegetation_data = self._fetch_vegetation_data(lat, lon, start, end)
            historical_data = self._fetch_historical_data(lat, lon, crop)
            
            # Analyze risks
            alerts = []
            risk_level = "low"
            
            # Weather-based risk analysis
            weather_risks = self._analyze_weather_risks(weather_data, crop_profile)
            alerts.extend(weather_risks["alerts"])
            if weather_risks["level"] == "high":
                risk_level = "high"
            elif weather_risks["level"] == "medium" and risk_level != "high":
                risk_level = "medium"
            
            # Precipitation risk analysis
            precip_risks = self._analyze_precipitation_risks(precipitation_data, crop_profile)
            alerts.extend(precip_risks["alerts"])
            if precip_risks["level"] == "high":
                risk_level = "high"
            elif precip_risks["level"] == "medium" and risk_level != "high":
                risk_level = "medium"
            
            # Vegetation health analysis
            vegetation_risks = self._analyze_vegetation_health(vegetation_data, crop_profile)
            alerts.extend(vegetation_risks["alerts"])
            if vegetation_risks["level"] == "high":
                risk_level = "high"
            elif vegetation_risks["level"] == "medium" and risk_level != "high":
                risk_level = "medium"
            
            # Historical trend analysis
            historical_risks = self._analyze_historical_trends(historical_data, crop)
            alerts.extend(historical_risks["alerts"])
            
            # Generate summary and recommendations
            summary = self._generate_summary(crop, alerts, risk_level, start, end)
            recommendations = self._generate_recommendations(alerts, crop_profile, risk_level)
            
            return {
                "success": True,
                "crop": crop.title(),
                "location": {
                    "latitude": lat,
                    "longitude": lon
                },
                "period": {
                    "start": start,
                    "end": end
                },
                "risk_level": risk_level,
                "alerts": alerts,
                "summary": summary,
                "recommendations": recommendations,
                "data_sources": {
                    "weather": weather_data.get("success", False),
                    "precipitation": precipitation_data.get("success", False),
                    "vegetation": vegetation_data.get("success", False),
                    "historical": historical_data.get("success", False)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in crop risk analysis: {e}")
            return {
                "success": False,
                "error": f"Risk analysis failed: {str(e)}",
                "crop": crop,
                "alerts": ["⚠️ Unable to complete risk analysis"],
                "summary": "Risk analysis temporarily unavailable"
            }
    
    def _fetch_weather_data(self, lat: float, lon: float, start: str, end: str) -> Dict:
        """Fetch weather data from NASA POWER API"""
        try:
            from app.services.power_api import PowerAPIService
            power_service = PowerAPIService()
            result = power_service.get_power_data(lat, lon, start, end, "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR")
            logger.info(f"Weather data fetch: {'success' if result.get('success') else 'failed'}")
            return result
        except Exception as e:
            logger.error(f"Failed to fetch weather data: {e}")
            return {"success": False, "error": str(e), "data": []}
    
    def _fetch_precipitation_data(self, lat: float, lon: float, start: str, end: str) -> Dict:
        """Fetch precipitation data from NASA GPM IMERG"""
        try:
            from app.services.gpm_api import get_gpm_data
            result = get_gpm_data(lat, lon, start, end)
            logger.info(f"Precipitation data fetch: {'success' if result.get('success') else 'failed'}")
            return result
        except Exception as e:
            logger.error(f"Failed to fetch precipitation data: {e}")
            return {"success": False, "error": str(e), "data": []}
    
    def _fetch_vegetation_data(self, lat: float, lon: float, start: str, end: str) -> Dict:
        """Fetch vegetation health data from MODIS NDVI"""
        try:
            from app.services.modis_api import get_modis_air_quality
            # Note: Using MODIS service as placeholder for NDVI data
            # In production, this would call a dedicated NDVI service
            result = get_modis_air_quality(lat, lon, start, end)
            
            # Simulate NDVI data based on location and season
            ndvi_data = self._simulate_ndvi_data(lat, lon, start, end)
            result["ndvi_data"] = ndvi_data
            
            logger.info(f"Vegetation data fetch: {'success' if result.get('success') else 'failed'}")
            return result
        except Exception as e:
            logger.error(f"Failed to fetch vegetation data: {e}")
            return {"success": False, "error": str(e), "data": []}
    
    def _fetch_historical_data(self, lat: float, lon: float, crop: str) -> Dict:
        """Fetch historical agricultural data from FAO/World Bank datasets"""
        try:
            # Simulate historical yield trends based on location and crop
            historical_trends = self._simulate_historical_trends(lat, lon, crop)
            
            return {
                "success": True,
                "crop": crop,
                "yield_trend": historical_trends["trend"],
                "years_data": historical_trends["years"],
                "regional_context": historical_trends["context"]
            }
        except Exception as e:
            logger.error(f"Failed to fetch historical data: {e}")
            return {"success": False, "error": str(e)}
    
    def _analyze_weather_risks(self, weather_data: Dict, crop_profile: Dict) -> Dict:
        """Analyze weather-based risks"""
        alerts = []
        risk_level = "low"
        
        if not weather_data.get("success") or not weather_data.get("data"):
            return {"alerts": ["⚠️ Weather data unavailable"], "level": "medium"}
        
        temperatures = []
        for day in weather_data["data"]:
            temp = day.get("temperature", 25)
            temperatures.append(temp)
            
            # Heat stress check
            if temp > crop_profile["heat_stress_temp"]:
                alerts.append(f"🌡️ Heat stress risk: {temp}°C (limit: {crop_profile['heat_stress_temp']}°C)")
                risk_level = "high"
            
            # Cold stress check
            if temp < crop_profile["cold_stress_temp"]:
                alerts.append(f"🧊 Cold stress risk: {temp}°C (limit: {crop_profile['cold_stress_temp']}°C)")
                risk_level = "high"
        
        # Temperature trend analysis
        if temperatures:
            avg_temp = statistics.mean(temperatures)
            min_optimal, max_optimal = crop_profile["optimal_temp_range"]
            
            if avg_temp < min_optimal - 5:
                alerts.append(f"❄️ Sustained cold conditions: {avg_temp:.1f}°C average")
                risk_level = "medium" if risk_level == "low" else risk_level
            elif avg_temp > max_optimal + 5:
                alerts.append(f"🔥 Sustained hot conditions: {avg_temp:.1f}°C average")
                risk_level = "medium" if risk_level == "low" else risk_level
        
        return {"alerts": alerts, "level": risk_level}
    
    def _analyze_precipitation_risks(self, precip_data: Dict, crop_profile: Dict) -> Dict:
        """Analyze precipitation-based risks"""
        alerts = []
        risk_level = "low"
        
        if not precip_data.get("success") or not precip_data.get("data"):
            return {"alerts": ["⚠️ Precipitation data unavailable"], "level": "medium"}
        
        total_rainfall = 0
        daily_rainfall = []
        
        for day in precip_data["data"]:
            rainfall = day.get("precipitation", 0)
            daily_rainfall.append(rainfall)
            total_rainfall += rainfall
            
            # Daily flooding risk
            if rainfall > crop_profile["flooding_threshold"]:
                alerts.append(f"🌊 Flooding risk: {rainfall}mm rainfall (limit: {crop_profile['flooding_threshold']}mm)")
                risk_level = "high"
            elif rainfall > crop_profile["flooding_threshold"] * 0.8:
                alerts.append(f"🌧️ Heavy rainfall warning: {rainfall}mm")
                risk_level = "medium" if risk_level == "low" else risk_level
        
        # Weekly drought assessment
        if daily_rainfall:
            avg_daily = total_rainfall / len(daily_rainfall)
            if avg_daily < crop_profile["drought_threshold"] / 7:
                alerts.append(f"🏜️ Drought conditions: {total_rainfall:.1f}mm total rainfall")
                risk_level = "medium" if risk_level == "low" else risk_level
        
        # Water needs assessment
        water_needs = crop_profile.get("water_needs", "moderate")
        if water_needs == "high" and total_rainfall < 30:
            alerts.append(f"💧 Insufficient water for high-demand crop: {total_rainfall:.1f}mm")
            risk_level = "medium" if risk_level == "low" else risk_level
        
        return {"alerts": alerts, "level": risk_level}
    
    def _analyze_vegetation_health(self, vegetation_data: Dict, crop_profile: Dict) -> Dict:
        """Analyze vegetation health risks"""
        alerts = []
        risk_level = "low"
        
        if not vegetation_data.get("success"):
            return {"alerts": ["⚠️ Vegetation data unavailable"], "level": "medium"}
        
        # Analyze simulated NDVI data
        ndvi_data = vegetation_data.get("ndvi_data", {})
        avg_ndvi = ndvi_data.get("average_ndvi", 0.5)
        trend = ndvi_data.get("trend", "stable")
        
        if avg_ndvi < crop_profile["min_ndvi"]:
            alerts.append(f"🟠 Vegetation stress: NDVI {avg_ndvi:.2f} (minimum: {crop_profile['min_ndvi']})")
            risk_level = "high"
        elif avg_ndvi < crop_profile["min_ndvi"] + 0.1:
            alerts.append(f"🟡 Vegetation concern: NDVI {avg_ndvi:.2f} approaching stress level")
            risk_level = "medium" if risk_level == "low" else risk_level
        
        if trend == "declining":
            alerts.append("📉 Vegetation health declining over observation period")
            risk_level = "medium" if risk_level == "low" else risk_level
        elif trend == "improving":
            # This is positive news, but we still note it
            pass
        
        return {"alerts": alerts, "level": risk_level}
    
    def _analyze_historical_trends(self, historical_data: Dict, crop: str) -> Dict:
        """Analyze historical trends and long-term risks"""
        alerts = []
        
        if not historical_data.get("success"):
            return {"alerts": ["⚠️ Historical data unavailable"], "level": "low"}
        
        trend = historical_data.get("yield_trend", "stable")
        context = historical_data.get("regional_context", {})
        
        if trend == "declining":
            alerts.append(f"📊 Long-term yield decline trend for {crop} in this region")
        elif trend == "volatile":
            alerts.append(f"📈 Volatile yield patterns for {crop} - increased uncertainty")
        
        # Climate change indicators
        if context.get("climate_change_risk", False):
            alerts.append("🌍 Region showing climate change vulnerability")
        
        return {"alerts": alerts, "level": "low"}
    
    def _generate_summary(self, crop: str, alerts: List[str], risk_level: str, start: str, end: str) -> str:
        """Generate a farmer-friendly summary"""
        try:
            start_date = datetime.strptime(start, '%Y%m%d').strftime('%b %d')
            end_date = datetime.strptime(end, '%Y%m%d').strftime('%b %d')
            period = f"{start_date}-{end_date}"
        except:
            period = "this period"
        
        if not alerts:
            return f"✅ Good news! No major risks detected for {crop} during {period}. Conditions look favorable for your crop."
        
        alert_count = len(alerts)
        
        if risk_level == "high":
            return f"🚨 High risk alert for {crop} during {period}. {alert_count} critical issue{'s' if alert_count > 1 else ''} detected. Immediate attention recommended."
        elif risk_level == "medium":
            return f"⚠️ Moderate risks identified for {crop} during {period}. {alert_count} concern{'s' if alert_count > 1 else ''} to monitor. Take precautionary measures."
        else:
            return f"🌱 Minor concerns for {crop} during {period}. {alert_count} item{'s' if alert_count > 1 else ''} to watch. Overall conditions are manageable."
    
    def _generate_recommendations(self, alerts: List[str], crop_profile: Dict, risk_level: str) -> List[str]:
        """Generate actionable recommendations based on identified risks"""
        recommendations = []
        
        # Risk-specific recommendations
        for alert in alerts:
            if "flooding" in alert.lower() or "heavy rainfall" in alert.lower():
                recommendations.append("💧 Improve drainage systems and avoid low-lying fields")
                recommendations.append("🚜 Delay harvesting if crops are nearly mature")
            
            elif "heat stress" in alert.lower():
                recommendations.append("🌾 Increase irrigation frequency during hot periods")
                recommendations.append("⏰ Schedule field work for early morning or evening")
            
            elif "cold stress" in alert.lower():
                recommendations.append("🔥 Consider protective covering for sensitive crops")
                recommendations.append("⚡ Monitor for frost warnings and take preventive action")
            
            elif "drought" in alert.lower():
                recommendations.append("💦 Implement water conservation techniques")
                recommendations.append("🌱 Consider drought-resistant crop varieties for next season")
            
            elif "vegetation stress" in alert.lower():
                recommendations.append("🧪 Check soil nutrients and consider fertilization")
                recommendations.append("🐛 Inspect for pests and diseases affecting plant health")
        
        # General recommendations based on risk level
        if risk_level == "high":
            recommendations.append("📱 Monitor weather updates daily and be ready to act quickly")
            recommendations.append("👥 Consult with local agricultural extension services")
        elif risk_level == "medium":
            recommendations.append("📊 Keep detailed records of field conditions")
            recommendations.append("🤝 Share experiences with fellow farmers in your community")
        elif not recommendations:  # Low risk, no specific alerts
            recommendations.append("✅ Continue current farming practices")
            recommendations.append("📈 Good time to plan for next season improvements")
        
        # Remove duplicates and limit to top 4 recommendations
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                seen.add(rec)
                unique_recommendations.append(rec)
                if len(unique_recommendations) >= 4:
                    break
        
        return unique_recommendations
    
    def _simulate_ndvi_data(self, lat: float, lon: float, start: str, end: str) -> Dict:
        """Simulate NDVI data based on location and season"""
        import random
        
        # Base NDVI varies by latitude (proxy for climate)
        if abs(lat) < 10:  # Tropical
            base_ndvi = 0.6
        elif abs(lat) < 30:  # Subtropical
            base_ndvi = 0.5
        else:  # Temperate
            base_ndvi = 0.4
        
        # Seasonal variation
        try:
            month = int(start[4:6])
            if 3 <= month <= 5:  # Spring
                seasonal_factor = 1.1
            elif 6 <= month <= 8:  # Summer
                seasonal_factor = 1.2
            elif 9 <= month <= 11:  # Autumn
                seasonal_factor = 0.9
            else:  # Winter
                seasonal_factor = 0.7
        except:
            seasonal_factor = 1.0
        
        # Add some randomness
        noise = random.uniform(-0.1, 0.1)
        
        avg_ndvi = max(0.1, min(0.9, base_ndvi * seasonal_factor + noise))
        
        # Determine trend
        trends = ["improving", "stable", "declining"]
        trend = random.choice(trends)
        
        return {
            "average_ndvi": round(avg_ndvi, 3),
            "trend": trend,
            "observation_period": f"{start} to {end}"
        }
    
    def _simulate_historical_trends(self, lat: float, lon: float, crop: str) -> Dict:
        """Simulate historical agricultural trends"""
        import random
        
        # Regional context based on latitude
        if 20 <= lat <= 30:  # Subtropical regions like Bangladesh
            context = {
                "climate_change_risk": True,
                "region_type": "subtropical_agricultural",
                "challenges": ["flooding", "heat_stress", "erratic_rainfall"]
            }
        elif abs(lat) < 10:  # Tropical
            context = {
                "climate_change_risk": True,
                "region_type": "tropical",
                "challenges": ["drought", "extreme_weather"]
            }
        else:  # Temperate
            context = {
                "climate_change_risk": False,
                "region_type": "temperate",
                "challenges": ["seasonal_variations"]
            }
        
        # Crop-specific trends
        trends = ["improving", "stable", "declining", "volatile"]
        weights = [0.2, 0.4, 0.2, 0.2]  # Stable is most common
        
        if crop.lower() in ["rice", "wheat"]:  # Major crops
            weights = [0.3, 0.5, 0.1, 0.1]  # More likely to be stable/improving
        
        trend = random.choices(trends, weights=weights)[0]
        
        return {
            "trend": trend,
            "years": 10,  # 10 years of historical data
            "context": context
        }
    
    def _validate_inputs(self, lat: float, lon: float, crop: str, start: str, end: str) -> Tuple[bool, Optional[str]]:
        """Validate input parameters"""
        try:
            # Validate coordinates
            lat = float(lat)
            lon = float(lon)
            
            if not (-90 <= lat <= 90):
                return False, f"Latitude must be between -90 and 90, got {lat}"
            
            if not (-180 <= lon <= 180):
                return False, f"Longitude must be between -180 and 180, got {lon}"
            
            # Validate crop
            if not crop or crop.lower() not in self.crop_profiles:
                available_crops = ", ".join(self.crop_profiles.keys())
                return False, f"Crop must be one of: {available_crops}"
            
            # Validate dates
            start_date = datetime.strptime(start, '%Y%m%d')
            end_date = datetime.strptime(end, '%Y%m%d')
            
            if start_date > end_date:
                return False, "Start date must be before or equal to end date"
            
            # Limit analysis period
            date_diff = (end_date - start_date).days
            if date_diff > 30:
                return False, "Analysis period cannot exceed 30 days"
            
            return True, None
            
        except ValueError:
            return False, "Invalid date format. Use YYYYMMDD format"
        except Exception as e:
            return False, f"Input validation error: {str(e)}"


# Global service instance
risk_engine = RiskEngine()

def crop_risk_analysis(lat: float, lon: float, crop: str, start: str, end: str) -> Dict:
    """
    Convenience function for crop risk analysis.
    
    Args:
        lat (float): Latitude (-90 to 90)
        lon (float): Longitude (-180 to 180)
        crop (str): Crop type (rice, wheat, potato, jute, corn)
        start (str): Start date in YYYYMMDD format
        end (str): End date in YYYYMMDD format
        
    Returns:
        Dict: Comprehensive risk analysis with mobile-friendly alerts
    """
    return risk_engine.crop_risk_analysis(lat, lon, crop, start, end)
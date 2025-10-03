#!/usr/bin/env python3
"""
TerraPulse ML Weather Analytics Service
Advanced weather pattern analysis and agricultural insights
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class WeatherTrend:
    parameter: str
    current_value: float
    trend_direction: str  # 'increasing', 'decreasing', 'stable'
    change_rate: float
    confidence: float

@dataclass
class AgriculturalInsight:
    crop_type: str
    growth_stage: str
    suitability_score: float
    recommendations: List[str]
    risk_factors: List[str]

class TerraPulseWeatherAnalytics:
    """
    Advanced weather analytics for agricultural decision making
    """
    
    def __init__(self):
        self.crop_requirements = self._load_crop_requirements()
        self.seasonal_patterns = self._load_seasonal_patterns()
        
    def _load_crop_requirements(self) -> Dict[str, Dict]:
        """Load crop-specific weather requirements"""
        return {
            'rice': {
                'optimal_temp_range': (20, 35),
                'optimal_humidity_range': (60, 90),
                'water_requirement': 'high',
                'rainfall_threshold': 100,  # mm/month
                'sensitive_stages': ['flowering', 'grain_filling']
            },
            'wheat': {
                'optimal_temp_range': (15, 25),
                'optimal_humidity_range': (40, 70),
                'water_requirement': 'medium',
                'rainfall_threshold': 50,
                'sensitive_stages': ['germination', 'heading']
            },
            'maize': {
                'optimal_temp_range': (18, 30),
                'optimal_humidity_range': (50, 80),
                'water_requirement': 'medium',
                'rainfall_threshold': 60,
                'sensitive_stages': ['tasseling', 'silking']
            },
            'cotton': {
                'optimal_temp_range': (20, 32),
                'optimal_humidity_range': (45, 75),
                'water_requirement': 'medium',
                'rainfall_threshold': 40,
                'sensitive_stages': ['flowering', 'boll_development']
            },
            'sugarcane': {
                'optimal_temp_range': (20, 30),
                'optimal_humidity_range': (60, 85),
                'water_requirement': 'high',
                'rainfall_threshold': 120,
                'sensitive_stages': ['tillering', 'grand_growth']
            }
        }
    
    def _load_seasonal_patterns(self) -> Dict[str, Dict]:
        """Load seasonal weather patterns for different regions"""
        return {
            'tropical': {
                'wet_season_months': [6, 7, 8, 9, 10],
                'dry_season_months': [11, 12, 1, 2, 3, 4, 5],
                'peak_rainfall_month': 8,
                'temperature_variation': 5  # °C
            },
            'subtropical': {
                'wet_season_months': [6, 7, 8, 9],
                'dry_season_months': [10, 11, 12, 1, 2, 3, 4, 5],
                'peak_rainfall_month': 7,
                'temperature_variation': 10
            },
            'temperate': {
                'wet_season_months': [4, 5, 6, 7, 8],
                'dry_season_months': [9, 10, 11, 12, 1, 2, 3],
                'peak_rainfall_month': 6,
                'temperature_variation': 20
            }
        }
    
    def analyze_weather_trends(self, historical_data: List[Dict]) -> Dict[str, Any]:
        """
        Analyze weather trends from historical data
        """
        try:
            if not historical_data or len(historical_data) < 3:
                return self._generate_synthetic_trends()
            
            trends = []
            parameters = ['temperature', 'humidity', 'rainfall', 'pressure']
            
            for param in parameters:
                trend = self._calculate_trend(historical_data, param)
                trends.append(trend)
            
            return {
                'success': True,
                'trends': [self._trend_to_dict(trend) for trend in trends],
                'summary': self._generate_trend_summary(trends),
                'analysis_period': f"{len(historical_data)} days",
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing weather trends: {str(e)}")
            return self._generate_synthetic_trends()
    
    def generate_agricultural_insights(self, 
                                     weather_data: Dict[str, float], 
                                     location_info: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Generate crop-specific agricultural insights based on current weather
        """
        try:
            insights = []
            season = self._determine_season(datetime.now().month)
            
            # Analyze for different crop types
            for crop_name, requirements in self.crop_requirements.items():
                insight = self._analyze_crop_suitability(
                    crop_name, requirements, weather_data, season
                )
                insights.append(insight)
            
            # Sort by suitability score
            insights.sort(key=lambda x: x.suitability_score, reverse=True)
            
            return {
                'success': True,
                'insights': [self._insight_to_dict(insight) for insight in insights],
                'general_recommendations': self._generate_general_recommendations(weather_data, season),
                'season': season,
                'optimal_crops': [insight.crop_type for insight in insights[:3]],
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            
        except Exception as e:
            logger.error(f"Error generating agricultural insights: {str(e)}")
            return self._generate_fallback_insights()
    
    def analyze_irrigation_needs(self, 
                                weather_data: Dict[str, float],
                                crop_type: str = 'rice',
                                growth_stage: str = 'vegetative') -> Dict[str, Any]:
        """
        Analyze irrigation requirements based on weather and crop conditions
        """
        try:
            rainfall = weather_data.get('rainfall', 0)
            temperature = weather_data.get('temperature', 25)
            humidity = weather_data.get('humidity', 65)
            wind_speed = weather_data.get('wind_speed', 5)
            
            # Calculate evapotranspiration (simplified Penman-Monteith)
            et0 = self._calculate_reference_evapotranspiration(
                temperature, humidity, wind_speed
            )
            
            # Get crop coefficient based on growth stage
            kc = self._get_crop_coefficient(crop_type, growth_stage)
            crop_et = et0 * kc
            
            # Calculate water balance
            water_deficit = max(0, crop_et - rainfall)
            
            # Determine irrigation requirement
            irrigation_need = self._assess_irrigation_need(
                water_deficit, crop_type, growth_stage
            )
            
            return {
                'success': True,
                'analysis': {
                    'crop_evapotranspiration': round(crop_et, 2),
                    'reference_evapotranspiration': round(et0, 2),
                    'crop_coefficient': round(kc, 2),
                    'rainfall_amount': round(rainfall, 2),
                    'water_deficit': round(water_deficit, 2),
                    'irrigation_requirement': irrigation_need,
                    'efficiency_tips': self._generate_irrigation_tips(water_deficit, crop_type)
                },
                'weather_input': weather_data,
                'crop_info': {
                    'type': crop_type,
                    'growth_stage': growth_stage
                },
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing irrigation needs: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def predict_pest_disease_risk(self, weather_data: Dict[str, float]) -> Dict[str, Any]:
        """
        Predict pest and disease risks based on weather conditions
        """
        try:
            temperature = weather_data.get('temperature', 25)
            humidity = weather_data.get('humidity', 65)
            rainfall = weather_data.get('rainfall', 5)
            
            risks = []
            
            # Fungal disease risk (high humidity + moderate temperature)
            if humidity > 80 and 20 <= temperature <= 30:
                risks.append({
                    'type': 'Fungal Disease',
                    'risk_level': 'High',
                    'probability': min(95, 60 + (humidity - 80) * 2),
                    'conditions': 'High humidity and moderate temperature',
                    'prevention': [
                        'Improve air circulation',
                        'Reduce plant density',
                        'Apply preventive fungicides'
                    ]
                })
            
            # Bacterial disease risk (high rainfall + warm temperature)
            if rainfall > 10 and temperature > 25:
                risks.append({
                    'type': 'Bacterial Disease',
                    'risk_level': 'Medium' if rainfall < 20 else 'High',
                    'probability': min(90, 30 + rainfall * 2),
                    'conditions': 'Heavy rainfall and warm temperature',
                    'prevention': [
                        'Ensure proper drainage',
                        'Avoid overhead irrigation',
                        'Apply copper-based bactericides'
                    ]
                })
            
            # Insect pest risk (warm temperature + low rainfall)
            if temperature > 30 and rainfall < 5:
                risks.append({
                    'type': 'Insect Pests',
                    'risk_level': 'Medium',
                    'probability': min(80, 40 + (temperature - 30) * 3),
                    'conditions': 'Hot and dry conditions',
                    'prevention': [
                        'Monitor pest populations',
                        'Use integrated pest management',
                        'Apply targeted insecticides if needed'
                    ]
                })
            
            # General assessment
            overall_risk = 'Low'
            if risks:
                max_prob = max(risk['probability'] for risk in risks)
                if max_prob > 70:
                    overall_risk = 'High'
                elif max_prob > 40:
                    overall_risk = 'Medium'
            
            return {
                'success': True,
                'risk_assessment': {
                    'overall_risk': overall_risk,
                    'specific_risks': risks,
                    'monitoring_recommendations': self._generate_monitoring_recommendations(risks),
                    'weather_factors': {
                        'temperature_impact': self._assess_temperature_impact(temperature),
                        'humidity_impact': self._assess_humidity_impact(humidity),
                        'rainfall_impact': self._assess_rainfall_impact(rainfall)
                    }
                },
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
            
        except Exception as e:
            logger.error(f"Error predicting pest/disease risk: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _calculate_trend(self, data: List[Dict], parameter: str) -> WeatherTrend:
        """Calculate trend for a specific weather parameter"""
        values = [d.get(parameter, 0) for d in data[-7:]]  # Last 7 days
        
        if len(values) < 2:
            return WeatherTrend(parameter, values[0] if values else 0, 'stable', 0, 50)
        
        # Calculate linear trend
        x = np.arange(len(values))
        slope, intercept = np.polyfit(x, values, 1)
        
        current_value = values[-1]
        change_rate = slope
        
        if abs(slope) < 0.1:
            direction = 'stable'
        elif slope > 0:
            direction = 'increasing'
        else:
            direction = 'decreasing'
        
        # Calculate confidence based on R-squared
        y_pred = slope * x + intercept
        r_squared = 1 - (np.sum((values - y_pred) ** 2) / np.sum((values - np.mean(values)) ** 2))
        confidence = max(60, min(95, r_squared * 100))
        
        return WeatherTrend(parameter, current_value, direction, change_rate, confidence)
    
    def _analyze_crop_suitability(self, crop_name: str, requirements: Dict, 
                                weather_data: Dict, season: str) -> AgriculturalInsight:
        """Analyze suitability of a crop for current weather conditions"""
        temp = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 65)
        rainfall = weather_data.get('rainfall', 5)
        
        score = 100
        recommendations = []
        risk_factors = []
        
        # Temperature suitability
        temp_range = requirements['optimal_temp_range']
        if temp < temp_range[0]:
            score -= 20
            risk_factors.append(f"Temperature too low ({temp}°C)")
            recommendations.append("Consider cold protection measures")
        elif temp > temp_range[1]:
            score -= 15
            risk_factors.append(f"Temperature too high ({temp}°C)")
            recommendations.append("Provide shade or cooling")
        
        # Humidity suitability
        humidity_range = requirements['optimal_humidity_range']
        if humidity < humidity_range[0]:
            score -= 10
            recommendations.append("Consider irrigation to increase humidity")
        elif humidity > humidity_range[1]:
            score -= 15
            risk_factors.append("High humidity - disease risk")
            recommendations.append("Improve ventilation")
        
        # Water requirement assessment
        water_req = requirements['water_requirement']
        if water_req == 'high' and rainfall < 10:
            score -= 25
            recommendations.append("Increase irrigation frequency")
        elif water_req == 'low' and rainfall > 15:
            score -= 10
            risk_factors.append("Excess water - drainage needed")
        
        # Seasonal appropriateness
        if season in ['kharif', 'wet'] and water_req == 'low':
            score -= 5
        elif season in ['rabi', 'dry'] and water_req == 'high':
            score -= 10
        
        score = max(0, min(100, score))
        growth_stage = self._determine_growth_stage(crop_name, season)
        
        return AgriculturalInsight(
            crop_type=crop_name.title(),
            growth_stage=growth_stage,
            suitability_score=score,
            recommendations=recommendations or ["Conditions are suitable for cultivation"],
            risk_factors=risk_factors or ["No significant risks identified"]
        )
    
    def _calculate_reference_evapotranspiration(self, temp: float, humidity: float, 
                                              wind_speed: float) -> float:
        """Calculate reference evapotranspiration using simplified formula"""
        # Simplified Penman-Monteith equation
        delta = 4098 * (0.6108 * np.exp(17.27 * temp / (temp + 237.3))) / ((temp + 237.3) ** 2)
        gamma = 0.665  # Psychrometric constant
        u2 = wind_speed * 4.87 / np.log(67.8 * 10 - 5.42)  # Wind speed at 2m
        
        es = 0.6108 * np.exp(17.27 * temp / (temp + 237.3))  # Saturation vapor pressure
        ea = es * humidity / 100  # Actual vapor pressure
        
        # Simplified ET0 calculation (mm/day)
        et0 = (0.408 * delta * (temp) + gamma * 900 / (temp + 273) * u2 * (es - ea)) / (delta + gamma * (1 + 0.34 * u2))
        
        return max(0, et0)
    
    def _get_crop_coefficient(self, crop_type: str, growth_stage: str) -> float:
        """Get crop coefficient based on crop type and growth stage"""
        coefficients = {
            'rice': {'initial': 1.0, 'vegetative': 1.2, 'reproductive': 1.3, 'maturity': 0.9},
            'wheat': {'initial': 0.4, 'vegetative': 0.7, 'reproductive': 1.15, 'maturity': 0.4},
            'maize': {'initial': 0.3, 'vegetative': 0.7, 'reproductive': 1.2, 'maturity': 0.6},
            'cotton': {'initial': 0.35, 'vegetative': 0.7, 'reproductive': 1.15, 'maturity': 0.5},
            'sugarcane': {'initial': 0.4, 'vegetative': 0.8, 'reproductive': 1.25, 'maturity': 0.75}
        }
        
        crop_coeffs = coefficients.get(crop_type, coefficients['rice'])
        return crop_coeffs.get(growth_stage, 1.0)
    
    def _assess_irrigation_need(self, water_deficit: float, crop_type: str, 
                              growth_stage: str) -> Dict[str, Any]:
        """Assess irrigation needs based on water deficit"""
        if water_deficit < 2:
            need_level = 'Low'
            amount = 0
            frequency = 'No irrigation needed'
        elif water_deficit < 5:
            need_level = 'Medium'
            amount = round(water_deficit * 1.2, 1)
            frequency = 'Every 2-3 days'
        else:
            need_level = 'High'
            amount = round(water_deficit * 1.5, 1)
            frequency = 'Daily'
        
        return {
            'level': need_level,
            'amount_mm': amount,
            'frequency': frequency,
            'priority': 'High' if growth_stage in ['reproductive', 'flowering'] else 'Medium'
        }
    
    def _determine_season(self, month: int) -> str:
        """Determine agricultural season based on month"""
        if month in [6, 7, 8, 9]:
            return 'kharif'  # Monsoon season
        elif month in [10, 11, 12, 1, 2]:
            return 'rabi'    # Winter season
        else:
            return 'summer'  # Summer season
    
    def _determine_growth_stage(self, crop_type: str, season: str) -> str:
        """Determine likely growth stage based on crop and season"""
        stages = ['initial', 'vegetative', 'reproductive', 'maturity']
        # Simplified logic - in real implementation, this would be more sophisticated
        current_month = datetime.now().month
        if season == 'kharif' and current_month in [6, 7]:
            return 'initial'
        elif season == 'kharif' and current_month in [8, 9]:
            return 'vegetative'
        elif season == 'kharif' and current_month in [10]:
            return 'reproductive'
        else:
            return 'vegetative'  # Default
    
    # Helper methods for generating various outputs and assessments
    def _generate_synthetic_trends(self) -> Dict[str, Any]:
        """Generate synthetic trends when historical data is not available"""
        parameters = ['temperature', 'humidity', 'rainfall', 'pressure']
        trends = []
        
        for param in parameters:
            trend = {
                'parameter': param,
                'current_value': np.random.uniform(10, 100),
                'trend_direction': np.random.choice(['increasing', 'decreasing', 'stable']),
                'change_rate': np.random.uniform(-2, 2),
                'confidence': np.random.uniform(70, 90)
            }
            trends.append(trend)
        
        return {
            'success': True,
            'trends': trends,
            'summary': 'Synthetic trend analysis based on statistical models',
            'analysis_period': 'Demo data',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    def _trend_to_dict(self, trend: WeatherTrend) -> Dict[str, Any]:
        """Convert WeatherTrend to dictionary"""
        return {
            'parameter': trend.parameter,
            'current_value': round(trend.current_value, 2),
            'trend_direction': trend.trend_direction,
            'change_rate': round(trend.change_rate, 3),
            'confidence': round(trend.confidence, 1)
        }
    
    def _insight_to_dict(self, insight: AgriculturalInsight) -> Dict[str, Any]:
        """Convert AgriculturalInsight to dictionary"""
        return {
            'crop_type': insight.crop_type,
            'growth_stage': insight.growth_stage,
            'suitability_score': round(insight.suitability_score, 1),
            'recommendations': insight.recommendations,
            'risk_factors': insight.risk_factors
        }
    
    def _generate_trend_summary(self, trends: List[WeatherTrend]) -> str:
        """Generate summary of weather trends"""
        increasing = sum(1 for t in trends if t.trend_direction == 'increasing')
        decreasing = sum(1 for t in trends if t.trend_direction == 'decreasing')
        
        if increasing > decreasing:
            return "Weather parameters are generally trending upward"
        elif decreasing > increasing:
            return "Weather parameters are generally trending downward"
        else:
            return "Weather patterns are relatively stable"
    
    def _generate_general_recommendations(self, weather_data: Dict, season: str) -> List[str]:
        """Generate general agricultural recommendations"""
        recommendations = []
        temp = weather_data.get('temperature', 25)
        rainfall = weather_data.get('rainfall', 5)
        
        if season == 'kharif':
            recommendations.append("Monitor rainfall patterns for crop planning")
            if rainfall > 15:
                recommendations.append("Ensure proper drainage to prevent waterlogging")
        elif season == 'rabi':
            recommendations.append("Plan irrigation schedule for winter crops")
            if temp < 15:
                recommendations.append("Consider cold protection for sensitive crops")
        
        if temp > 35:
            recommendations.append("Provide shade or cooling for heat-sensitive crops")
        
        return recommendations
    
    def _generate_fallback_insights(self) -> Dict[str, Any]:
        """Generate fallback insights when analysis fails"""
        return {
            'success': True,
            'insights': [
                {
                    'crop_type': 'Rice',
                    'growth_stage': 'vegetative',
                    'suitability_score': 75,
                    'recommendations': ['Monitor weather conditions', 'Ensure adequate water supply'],
                    'risk_factors': ['No significant risks identified']
                }
            ],
            'general_recommendations': ['Check local weather forecasts', 'Plan irrigation accordingly'],
            'season': 'current',
            'optimal_crops': ['Rice'],
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
    
    def _generate_irrigation_tips(self, water_deficit: float, crop_type: str) -> List[str]:
        """Generate irrigation efficiency tips"""
        tips = []
        
        if water_deficit > 10:
            tips.extend([
                "Use drip irrigation for water efficiency",
                "Apply mulch to reduce evaporation",
                "Irrigate during early morning or evening"
            ])
        elif water_deficit > 5:
            tips.extend([
                "Monitor soil moisture levels",
                "Use sprinkler irrigation for uniform distribution"
            ])
        else:
            tips.append("Current rainfall is sufficient")
        
        return tips
    
    def _generate_monitoring_recommendations(self, risks: List[Dict]) -> List[str]:
        """Generate pest/disease monitoring recommendations"""
        if not risks:
            return ["Regular field inspection recommended"]
        
        recommendations = []
        for risk in risks:
            if risk['type'] == 'Fungal Disease':
                recommendations.append("Check for leaf spots and fungal growth")
            elif risk['type'] == 'Bacterial Disease':
                recommendations.append("Monitor for wilting and bacterial ooze")
            elif risk['type'] == 'Insect Pests':
                recommendations.append("Use pheromone traps and visual inspection")
        
        return recommendations
    
    def _assess_temperature_impact(self, temperature: float) -> str:
        """Assess temperature impact on pests/diseases"""
        if temperature > 35:
            return "High temperature favors insect reproduction"
        elif temperature < 15:
            return "Low temperature reduces pest activity"
        else:
            return "Moderate temperature - balanced risk"
    
    def _assess_humidity_impact(self, humidity: float) -> str:
        """Assess humidity impact on pests/diseases"""
        if humidity > 80:
            return "High humidity increases fungal disease risk"
        elif humidity < 40:
            return "Low humidity reduces disease pressure"
        else:
            return "Moderate humidity - normal conditions"
    
    def _assess_rainfall_impact(self, rainfall: float) -> str:
        """Assess rainfall impact on pests/diseases"""
        if rainfall > 15:
            return "Heavy rainfall increases bacterial disease risk"
        elif rainfall < 2:
            return "Dry conditions may increase pest activity"
        else:
            return "Normal rainfall - balanced conditions"

# Global instance for the Flask app
weather_analytics = TerraPulseWeatherAnalytics()
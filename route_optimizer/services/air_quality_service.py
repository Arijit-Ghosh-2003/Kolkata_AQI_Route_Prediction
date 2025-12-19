import requests
from django.conf import settings
from typing import Dict, List, Optional
import time

class AirQualityService:
    """Service to fetch air quality data from WAQI API"""
    
    BASE_URL = "https://api.waqi.info"
    
    def __init__(self):
        self.api_key = settings.WAQI_API_KEY
    
    def get_aqi_by_coordinates(self, lat: float, lng: float) -> Optional[Dict]:
        """
        Get AQI data for specific coordinates
        """
        url = f"{self.BASE_URL}/feed/geo:{lat};{lng}/"
        params = {'token': self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                return self._parse_aqi_data(data['data'])
            return None
        except Exception as e:
            print(f"Error fetching AQI data: {e}")
            return None
    
    def get_aqi_by_city(self, city_name: str) -> Optional[Dict]:
        """
        Get AQI data for specific city
        """
        url = f"{self.BASE_URL}/feed/{city_name}/"
        params = {'token': self.api_key}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                return self._parse_aqi_data(data['data'])
            return None
        except Exception as e:
            print(f"Error fetching AQI data: {e}")
            return None
    
    def get_multiple_aqi_for_route(self, coordinates: List[tuple]) -> List[Dict]:
        """
        Get AQI data for multiple coordinates along a route
        """
        aqi_data = []
        for lat, lng in coordinates:
            data = self.get_aqi_by_coordinates(lat, lng)
            if data:
                aqi_data.append(data)
            time.sleep(0.1)  # Rate limiting
        
        return aqi_data
    
    def _parse_aqi_data(self, data: Dict) -> Dict:
        """
        Parse and structure AQI data
        """
        iaqi = data.get('iaqi', {})
        
        return {
            'aqi': data.get('aqi', 0),
            'pm25': iaqi.get('pm25', {}).get('v', 0),
            'pm10': iaqi.get('pm10', {}).get('v', 0),
            'no2': iaqi.get('no2', {}).get('v', 0),
            'co': iaqi.get('co', {}).get('v', 0),
            'o3': iaqi.get('o3', {}).get('v', 0),
            'location': {
                'lat': data.get('city', {}).get('geo', [0, 0])[0],
                'lng': data.get('city', {}).get('geo', [0, 0])[1],
                'name': data.get('city', {}).get('name', 'Unknown')
            },
            'time': data.get('time', {}).get('s', ''),
        }
    
    def calculate_weighted_aqi(self, aqi_data: Dict) -> float:
        """
        Calculate weighted AQI based on multiple pollutants
        """
        weights = {
            'pm25': 0.35,
            'pm10': 0.25,
            'no2': 0.20,
            'co': 0.10,
            'o3': 0.10
        }
        
        weighted_sum = 0
        total_weight = 0
        
        for pollutant, weight in weights.items():
            value = aqi_data.get(pollutant, 0)
            if value > 0:
                weighted_sum += value * weight
                total_weight += weight
        
        if total_weight > 0:
            return weighted_sum / total_weight
        
        return aqi_data.get('aqi', 0)

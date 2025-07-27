import requests
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
#WEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"
WEATHER_BASE_URL = os.getenv('WEATHER_BASE_URL', 'http://api.openweathermap.org/data/2.5')

def get_current_weather(location):
    """Get current weather data for a location"""
    try:
        if not WEATHER_API_KEY:
            print("Weather API key not set, returning mock data")
            # Return mock data if no API key
            return {
                'location': location,
                'temperature': 25.0,
                'humidity': 65.0,
                'wind_speed': 5.2,
                'description': 'Partly cloudy',
                'source': 'mock_data'
            }
        
        url = f"{WEATHER_BASE_URL}/weather"
        params = {
            'q': location,
            'appid': WEATHER_API_KEY,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        return {
            'location': location,
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'wind_speed': data['wind']['speed'],
            'description': data['weather'][0]['description'],
            'source': 'openweathermap'
        }
        
    except Exception as e:
        print(f"Weather API failed: {e}")
        return {
            'location': location,
            'temperature': 20.0,
            'humidity': 60.0,
            'wind_speed': 3.0,
            'description': 'Weather data unavailable',
            'source': 'fallback'
        }

def get_weather_forecast(location, days=7):
    """Get weather forecast for a location"""
    try:
        if not WEATHER_API_KEY:
            # Return mock forecast data with current date
            print("Weather API key not set, returning mock forecast data")
            current_date = datetime.now()
            return [
                {
                    'date': (current_date + timedelta(days=i)).strftime('%Y-%m-%d'),
                    'temperature_max': 25 + i,
                    'temperature_min': 15 + i,
                    'humidity': 60 + i,
                    'description': 'Partly cloudy'
                }
                for i in range(days)
            ]
        
        url = f"{WEATHER_BASE_URL}/forecast"
        params = {
            'q': location,
            'appid': WEATHER_API_KEY,
            'units': 'metric',
            'cnt': days * 8  # 8 forecasts per day (3-hour intervals)
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        # Process forecast data (simplified)
        forecast = []
        for item in data['list'][::8]:  # Take one forecast per day
            forecast.append({
                'date': item['dt_txt'].split(' ')[0],
                'temperature_max': item['main']['temp_max'],
                'temperature_min': item['main']['temp_min'],
                'humidity': item['main']['humidity'],
                'description': item['weather'][0]['description']
            })
        
        return forecast[:days]
        
    except Exception as e:
        print(f"Weather forecast failed: {e}")
        # Return fallback data with current dates
        current_date = datetime.now()
        return [
            {
                'date': (current_date + timedelta(days=i)).strftime('%Y-%m-%d'),
                'temperature_max': 20 + i,
                'temperature_min': 10 + i,
                'humidity': 65,
                'description': 'Weather data unavailable'
            }
            for i in range(days)
        ]

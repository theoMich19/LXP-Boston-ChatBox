"""
LXP - Advanced AI development Workshop: Chatbot tools

WARNING: LangChain ConversationalAgent only accepts single input parameters for tool calling.
Use create_string_input_tool() to wrap multi-parameter functions.
"""

import requests
from langchain_core.tools import tool
from utils import create_string_input_tool

@tool
def geocode_city(city: str) -> str:
    """Convert a city name to latitude and longitude coordinates using Open-Meteo geocoding API.
    
    Args:
        city: The name of the city to geocode
        
    Returns:
        A formatted string with coordinates and location information
    """
    try:
        # Geocode the city name to get coordinates
        geocode_url = "https://geocoding-api.open-meteo.com/v1/search"
        geocode_params = {
            'name': city,
            'count': 1,
            'language': 'en',
            'format': 'json'
        }
        
        response = requests.get(geocode_url, params=geocode_params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if not data.get('results'):
            return f"Error: City '{city}' not found. Please check the spelling and try again."
        
        # Extract coordinates and location info
        location = data['results'][0]
        latitude = location['latitude']
        longitude = location['longitude']
        location_name = location['name']
        country = location.get('country', 'Unknown')
        admin1 = location.get('admin1', '')
        
        # Build location display name
        display_name = f"{location_name}"
        if admin1:
            display_name += f", {admin1}"
        if country:
            display_name += f", {country}"
        
        return f"📍 {display_name}\nLatitude: {latitude}\nLongitude: {longitude}"
        
    except Exception as e:
        return f"Error: {str(e)}"

def get_temperature_by_coordinates(latitude: float, longitude: float) -> str:
    """Get current temperature data for specific coordinates.
    
    Args:
        latitude: The latitude coordinate (e.g., 40.7128)
        longitude: The longitude coordinate (e.g., -74.0060)
        
    Returns:
        JSON string with temperature data including current, feels_like, and daily min/max
    """
    try:
        # Get current and daily temperature data
        weather_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'current': ['temperature_2m', 'apparent_temperature'],
            'daily': ['temperature_2m_max', 'temperature_2m_min'],
            'timezone': 'auto',
            'forecast_days': 1
        }
        
        response = requests.get(weather_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        result = {
            'current_temperature': data['current']['temperature_2m'],
            'feels_like': data['current']['apparent_temperature'],
            'daily_max': data['daily']['temperature_2m_max'][0],
            'daily_min': data['daily']['temperature_2m_min'][0],
            'unit': data['current_units']['temperature_2m']
        }
        
        return str(result)
        
    except Exception as e:
        return f"Error: {str(e)}"

def get_precipitation_by_coordinates(latitude: float, longitude: float) -> str:
    """Get current precipitation data for specific coordinates.
    
    Args:
        latitude: The latitude coordinate (e.g., 40.7128)
        longitude: The longitude coordinate (e.g., -74.0060)
        
    Returns:
        JSON string with precipitation data including current, rain, snow, and daily totals
    """
    try:
        # Get precipitation data
        weather_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'current': ['precipitation', 'rain', 'showers', 'snowfall', 'weather_code'],
            'daily': ['precipitation_sum', 'rain_sum', 'snowfall_sum', 'precipitation_probability_max'],
            'timezone': 'auto',
            'forecast_days': 1
        }
        
        response = requests.get(weather_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Weather code descriptions
        weather_descriptions = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Fog", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            56: "Light freezing drizzle", 57: "Dense freezing drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            66: "Light freezing rain", 67: "Heavy freezing rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
            77: "Snow grains",
            80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
            85: "Slight snow showers", 86: "Heavy snow showers",
            95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
        }
        
        weather_code = data['current']['weather_code']
        
        result = {
            'current': {
                'total_precipitation': data['current']['precipitation'],
                'rain': data['current']['rain'],
                'showers': data['current']['showers'], 
                'snowfall': data['current']['snowfall'],
                'weather_condition': weather_descriptions.get(weather_code, f"Unknown ({weather_code})")
            },
            'daily': {
                'precipitation_sum': data['daily']['precipitation_sum'][0],
                'rain_sum': data['daily']['rain_sum'][0],
                'snowfall_sum': data['daily']['snowfall_sum'][0],
                'precipitation_probability': data['daily']['precipitation_probability_max'][0]
            },
            'unit': data['current_units']['precipitation']
        }
        
        return str(result)
        
    except Exception as e:
        return f"Error: {str(e)}"

def get_wind_by_coordinates(latitude: float, longitude: float) -> str:
    """Get current wind data for specific coordinates.
    
    Args:
        latitude: The latitude coordinate (e.g., 40.7128)
        longitude: The longitude coordinate (e.g., -74.0060)
        
    Returns:
        JSON string with wind data including speed, direction, gusts
    """
    try:
        # Get wind data
        weather_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'current': ['wind_speed_10m', 'wind_direction_10m', 'wind_gusts_10m'],
            'daily': ['wind_speed_10m_max', 'wind_gusts_10m_max', 'wind_direction_10m_dominant'],
            'timezone': 'auto',
            'forecast_days': 1
        }
        
        response = requests.get(weather_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        def wind_direction_to_compass(degrees):
            if degrees is None:
                return "N/A"
            directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
                         "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
            index = round(degrees / 22.5) % 16
            return directions[index]
        
        current_direction = data['current']['wind_direction_10m']
        daily_direction = data['daily']['wind_direction_10m_dominant'][0]
        
        result = {
            'current': {
                'wind_speed': data['current']['wind_speed_10m'],
                'wind_direction_degrees': current_direction,
                'wind_direction_compass': wind_direction_to_compass(current_direction),
                'wind_gusts': data['current']['wind_gusts_10m']
            },
            'daily': {
                'max_wind_speed': data['daily']['wind_speed_10m_max'][0],
                'max_wind_gusts': data['daily']['wind_gusts_10m_max'][0],
                'dominant_direction_degrees': daily_direction,
                'dominant_direction_compass': wind_direction_to_compass(daily_direction)
            },
            'unit': data['current_units']['wind_speed_10m']
        }
        
        return str(result)
        
    except Exception as e:
        return f"Error: {str(e)}"

def get_wind_forecast_by_coordinates(latitude: float, longitude: float) -> str:
    """Get 7-day wind forecast for specific coordinates.
    
    Args:
        latitude: The latitude coordinate (e.g., 40.7128)
        longitude: The longitude coordinate (e.g., -74.0060)
        
    Returns:
        JSON string with 7-day wind forecast data
    """
    try:
        # Get wind forecast data
        weather_url = "https://api.open-meteo.com/v1/forecast"
        params = {
            'latitude': latitude,
            'longitude': longitude,
            'daily': [
                'wind_speed_10m_max',
                'wind_gusts_10m_max', 
                'wind_direction_10m_dominant'
            ],
            'timezone': 'auto',
            'forecast_days': 7
        }
        
        response = requests.get(weather_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        def wind_direction_to_compass(degrees):
            if degrees is None:
                return "N/A"
            directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
                         "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
            index = round(degrees / 22.5) % 16
            return directions[index]
        
        # Build forecast array
        forecast = []
        for i in range(len(data['daily']['time'])):
            direction_degrees = data['daily']['wind_direction_10m_dominant'][i]
            forecast.append({
                'date': data['daily']['time'][i],
                'max_wind_speed': data['daily']['wind_speed_10m_max'][i],
                'max_wind_gusts': data['daily']['wind_gusts_10m_max'][i],
                'dominant_direction_degrees': direction_degrees,
                'dominant_direction_compass': wind_direction_to_compass(direction_degrees)
            })
        
        result = {
            'forecast': forecast,
            'unit': data['daily_units']['wind_speed_10m_max']
        }
        
        return str(result)
        
    except Exception as e:
        return f"Error: {str(e)}"

# Create the string input tool versions for LangChain
get_city_temperature = create_string_input_tool(get_temperature_by_coordinates, "get_city_temperature")
get_city_precipitation = create_string_input_tool(get_precipitation_by_coordinates, "get_city_precipitation") 
get_city_wind = create_string_input_tool(get_wind_by_coordinates, "get_city_wind")
get_city_wind_forecast = create_string_input_tool(get_wind_forecast_by_coordinates, "get_city_wind_forecast")
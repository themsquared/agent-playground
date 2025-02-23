import os
import aiohttp
from typing import Dict, Any
from ..base import BaseAction, ActionResult, ActionExample


class WeatherAction(BaseAction):
    """Action to get current weather information"""
    name = "get_weather"
    description = "Get current weather information for a location"
    required_parameters = {
        "location": "Name of the city or location (optionally include state/country code, e.g., 'London,UK' or 'New York,US')",
        "units": "Temperature units (metric/imperial), defaults to imperial"
    }
    examples = [
        ActionExample(
            query="What's the weather in London?",
            response={
                "actions": [{
                    "name": "get_weather",
                    "parameters": {
                        "location": "London,UK",
                        "units": "imperial"
                    }
                }]
            },
            description="Basic weather query with country code"
        ),
        ActionExample(
            query="Get the temperature in New York in Celsius",
            response={
                "actions": [{
                    "name": "get_weather",
                    "parameters": {
                        "location": "New York,US",
                        "units": "metric"
                    }
                }]
            },
            description="Weather query with country code and metric units"
        ),
        ActionExample(
            query="How's the weather in NYC?",
            response={
                "actions": [{
                    "name": "get_weather",
                    "parameters": {
                        "location": "New York,US",
                        "units": "imperial"
                    }
                }]
            },
            description="Weather query with city abbreviation"
        )
    ]

    # Common city name mappings
    CITY_MAPPINGS = {
        "NYC": "New York,US",
        "LA": "Los Angeles,US",
        "SF": "San Francisco,US",
        "DC": "Washington,US",
        "LONDON": "London,UK",
        "PARIS": "Paris,FR",
        "TOKYO": "Tokyo,JP",
    }

    def __init__(self):
        super().__init__()
        self.api_key = os.getenv("OPENWEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"

    def _format_location(self, location: str) -> str:
        """Format location name for OpenWeather API"""
        # Check common abbreviations first
        location_upper = location.upper().strip()
        if location_upper in self.CITY_MAPPINGS:
            return self.CITY_MAPPINGS[location_upper]

        # If location already contains a comma, assume it's properly formatted
        if "," in location:
            return location

        # For US cities, append US country code
        common_us_cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia",
                          "San Antonio", "San Diego", "Dallas", "San Jose"]
        if any(city.lower() == location.lower() for city in common_us_cities):
            return f"{location},US"

        # For other major world cities, add country codes
        world_cities = {
            "london": "UK",
            "paris": "FR",
            "tokyo": "JP",
            "berlin": "DE",
            "rome": "IT",
            "madrid": "ES",
            "moscow": "RU",
            "beijing": "CN",
            "seoul": "KR",
            "sydney": "AU"
        }
        location_lower = location.lower()
        if location_lower in world_cities:
            return f"{location},{world_cities[location_lower]}"

        # If no specific mapping, return as is
        return location

    async def execute(self, parameters: Dict[str, Any]) -> ActionResult:
        """Execute the weather action"""
        print(f"Executing weather action with parameters: {parameters}")
        
        if not self.api_key:
            print("Weather action failed: No API key configured")
            return ActionResult(
                success=False,
                message="OpenWeather API key not configured",
                error="OpenWeather API key is required. Set OPENWEATHER_API_KEY environment variable."
            )

        try:
            location = self._format_location(parameters["location"])
            units = parameters.get("units", "imperial")

            if units not in ["metric", "imperial"]:
                print(f"Weather action failed: Invalid units parameter: {units}")
                return ActionResult(
                    success=False,
                    message="Invalid units parameter",
                    error="Units must be either 'metric' or 'imperial'"
                )

            print(f"Making API request to OpenWeatherMap for location: {location}")
            # Make API request to OpenWeatherMap
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/weather",
                    params={
                        "q": location,
                        "appid": self.api_key,
                        "units": units
                    }
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        error_message = error_data.get('message', 'Unknown error')
                        print(f"Weather API request failed: {error_data}")
                        return ActionResult(
                            success=False,
                            message=f"Failed to get weather data: {error_message}",
                            error=error_message
                        )

                    data = await response.json()
                    print(f"Received weather data: {data}")

                    # Format the weather information
                    temp_unit = "°C" if units == "metric" else "°F"
                    speed_unit = "m/s" if units == "metric" else "mph"
                    
                    weather_info = {
                        "location": f"{data['name']}, {data.get('sys', {}).get('country', '')}",
                        "temperature": f"{data['main']['temp']}{temp_unit}",
                        "feels_like": f"{data['main']['feels_like']}{temp_unit}",
                        "humidity": f"{data['main']['humidity']}%",
                        "pressure": f"{data['main']['pressure']} hPa",
                        "wind_speed": f"{data['wind']['speed']} {speed_unit}",
                        "description": data['weather'][0]['description'].capitalize(),
                        "units": units
                    }

                    result = ActionResult(
                        success=True,
                        message=(
                            f"Current weather in {weather_info['location']}: "
                            f"{weather_info['description']}, "
                            f"Temperature: {weather_info['temperature']} "
                            f"(feels like {weather_info['feels_like']}), "
                            f"Humidity: {weather_info['humidity']}, "
                            f"Wind: {weather_info['wind_speed']}"
                        ),
                        data=weather_info
                    )
                    print(f"Weather action completed successfully: {result.message}")
                    return result

        except KeyError as e:
            print(f"Weather action failed: Missing parameter: {e}")
            return ActionResult(
                success=False,
                message="Missing required parameter",
                error=f"Missing parameter: {str(e)}"
            )
        except Exception as e:
            print(f"Weather action failed with unexpected error: {e}")
            return ActionResult(
                success=False,
                message="Failed to get weather information",
                error=str(e)
            ) 
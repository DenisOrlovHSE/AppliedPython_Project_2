from typing import Literal
import aiohttp

from .constants import OWM_API_URL
from .models import WeatherData


class OWMClient:

    def __init__(self, api_key: str) -> None:
        self.base_url = OWM_API_URL
        self.api_key = api_key

    async def get_weather(
        self,
        city: str,
        units: Literal["standard", "metric", "imperial"] = "metric"
    ) -> WeatherData | None:
        try:
            endpoint = f"{self.base_url}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": units
            }
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params) as response:
                    response.raise_for_status()
                    return WeatherData.model_validate(await response.json())
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None
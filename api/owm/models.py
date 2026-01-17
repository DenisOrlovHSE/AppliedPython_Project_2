from pydantic import BaseModel, Field
from typing import Optional, List


class Coordinates(BaseModel):
    lon: float
    lat: float


class WeatherCondition(BaseModel):
    id: int
    main: str
    description: str
    icon: str


class MainWeatherData(BaseModel):
    temp: float
    feels_like: float
    temp_min: float
    temp_max: float
    pressure: int
    humidity: int
    sea_level: Optional[int] = None
    grnd_level: Optional[int] = None


class Wind(BaseModel):
    speed: float
    deg: int
    gust: Optional[float] = None


class Rain(BaseModel):
    one_hour: Optional[float] = Field(None, alias="1h")


class Clouds(BaseModel):
    all: int


class SystemData(BaseModel):
    type: int
    id: int
    country: str
    sunrise: int
    sunset: int


class WeatherData(BaseModel):
    coord: Coordinates
    weather: List[WeatherCondition]
    base: str
    main: MainWeatherData
    visibility: int
    wind: Wind
    rain: Optional[Rain] = None
    clouds: Clouds
    dt: int
    sys: SystemData
    timezone: int
    id: int
    name: str
    cod: int

    class Config:
        populate_by_name = True
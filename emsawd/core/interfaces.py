from abc import ABC, abstractmethod
from datetime import date
from typing import List, Tuple
from .models import WeatherRecord

class IGeocodingRepository(ABC):
    """
    Interface for a geocoding repository that converts location names to coordinates.
    """
    @abstractmethod
    def get_coordinates(self, location_name: str) -> Tuple[float, float]:
        """
        Gets the latitude and longitude for a given location name.
        Returns a tuple of (latitude, longitude).
        """
        pass

class IWeatherRepository(ABC):
    """
    Interface for a weather repository that fetches historical weather data.
    """
    @abstractmethod
    def get_historical_weather(
        self, latitude: float, longitude: float, start_date: date, end_date: date
    ) -> List[WeatherRecord]:
        """
        Fetches historical weather data for a given location and date range.
        """
        pass

class IWeatherService(ABC):
    """
    Interface for the main weather service that handles business logic.
    """
    @abstractmethod
    def fetch_weather_for_range(
        self, location: str, start_date: date, end_date: date, years_past: int
    ) -> List[WeatherRecord]:
        """
        Fetches and aggregates historical weather data for a specific date range
        across a number of past years.
        """
        pass
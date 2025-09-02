from dataclasses import dataclass
from datetime import date

@dataclass
class WeatherRecord:
    """
    Represents a single record of historical weather data for a specific day.
    """
    record_date: date
    year: int
    location: str
    max_temp_c: float
    min_temp_c: float
    precipitation_mm: float

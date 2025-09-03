from datetime import date
from dataclasses import dataclass

@dataclass
class WeatherRecord:
    """
    Represents a weather record from a historical weather source.
    """
    record_date: date
    year: int
    location: str
    max_temp_c: float
    min_temp_c: float
    precipitation_mm: float

    def __post_init__(self):
        """Validate that max_temp_c >= min_temp_c"""
        if self.max_temp_c < self.min_temp_c:
            raise ValueError(f"Maximum temperature ({self.max_temp_c}°C) cannot be less than minimum temperature ({self.min_temp_c}°C)")
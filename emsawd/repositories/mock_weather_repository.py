from datetime import date, timedelta
from typing import List
from emsawd.core.interfaces import IWeatherRepository
from emsawd.core.models import WeatherRecord

class MockWeatherRepository(IWeatherRepository):
    """
    A mock weather repository that returns dummy data for testing.
    """
    def get_historical_weather(
        self, latitude: float, longitude: float, start_date: date, end_date: date
    ) -> List[WeatherRecord]:
        """
        Returns a list of dummy weather records.
        """
        records = []
        current_date = start_date
        while current_date <= end_date:
            records.append(
                WeatherRecord(
                    record_date=current_date,
                    year=current_date.year,
                    location="Mock Location",
                    max_temp_c=20 + (current_date.day % 10),
                    min_temp_c=10 + (current_date.day % 5),
                    precipitation_mm=current_date.day % 5,
                )
            )
            current_date += timedelta(days=1)
        return records

from datetime import date
from typing import List
from .interfaces import IWeatherService, IGeocodingRepository, IWeatherRepository
from .models import WeatherRecord

class WeatherService(IWeatherService):
    """
    Implements the core business logic for fetching and processing weather data.
    """
    def __init__(
        self,
        geocoding_repo: IGeocodingRepository,
        weather_repo: IWeatherRepository,
    ):
        self._geocoding_repo = geocoding_repo
        self._weather_repo = weather_repo

    def fetch_weather_for_range(
        self, location: str, start_date: date, end_date: date, years_past: int
    ) -> List[WeatherRecord]:
        """
        Fetches and aggregates historical weather data for a specific date range
        across a number of past years.

        Args:
            location: The name of the location (e.g., city).
            start_date: The start of the date range of interest.
            end_date: The end of the date range of interest.
            years_past: The number of past years to query.

        Returns:
            A list of WeatherRecord objects containing the aggregated data.
        """
        print(f"Fetching coordinates for {location}...")
        latitude, longitude = self._geocoding_repo.get_coordinates(location)

        all_records: List[WeatherRecord] = []

        for year_offset in range(1, years_past + 1):
            try:
                # Calculate the historical date range for the current iteration
                hist_start_date = start_date.replace(year=start_date.year - year_offset)
                hist_end_date = end_date.replace(year=end_date.year - year_offset)

                print(
                    f"Fetching data for year {hist_start_date.year}, "
                    f"range: {hist_start_date} to {hist_end_date}"
                )

                # Fetch data for the historical range
                records = self._weather_repo.get_historical_weather(
                    latitude, longitude, hist_start_date, hist_end_date
                )
                all_records.extend(records)

            except Exception as e:
                # Log the error and continue to the next year
                print(f"Error fetching data for year offset {year_offset}: {e}")
                # In a real app, this would use the logging service
                continue

        print(f"Successfully fetched and aggregated {len(all_records)} records.")
        return all_records

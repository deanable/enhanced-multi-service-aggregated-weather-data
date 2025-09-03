import logging
from datetime import date, timedelta
from typing import List
from .interfaces import IWeatherRepository, IGeocodingRepository
from .models import WeatherRecord

logger = logging.getLogger(__name__)

class WeatherService:
    """
    Main weather service that handles business logic for weather data aggregation.
    """

    def __init__(self, geocoding_repo: IGeocodingRepository, weather_repo: IWeatherRepository):
        """
        Initialize the WeatherService with geocoding and weather repositories.

        Args:
            geocoding_repo: The geocoding repository implementation
            weather_repo: The weather repository implementation
        """
        self.geocoding_repo = geocoding_repo
        self.weather_repo = weather_repo

    def fetch_weather_for_range(
        self, location: str, start_date: date, end_date: date, years_past: int
    ) -> List[WeatherRecord]:
        """
        Fetches and aggregates historical weather data for a specific date range
        across a number of past years.

        Args:
            location: The location name
            start_date: The start of the date range
            end_date: The end of the date range
            years_past: Number of past years to include (0 means just the current period)

        Returns:
            List of WeatherRecord objects
        """
        logger.info(f"Fetching weather data for {location}, period: {start_date} to {end_date}, years: {years_past}")

        # Get coordinates
        try:
            latitude, longitude = self.geocoding_repo.get_coordinates(location)
            logger.info(f"Coordinates for {location}: lat={latitude}, lon={longitude}")
        except Exception as e:
            logger.error(f"Failed to get coordinates for {location}: {e}")
            raise ValueError(f"Could not find location: {location}") from e

        all_records = []

        # Fetch data for each offset year
        for year_offset in range(years_past + 1):
            # Calculate the offset date range
            date_offset = timedelta(days=365 * year_offset)
            current_start = start_date - date_offset
            current_end = end_date - date_offset
            current_year = current_start.year

            logger.info(f"Fetching data for year offset {year_offset} ({current_year}): {current_start} to {current_end}")

            try:
                # Fetch records for this period
                period_records = self.weather_repo.get_historical_weather(
                    latitude, longitude, current_start, current_end
                )

                logger.info(f"Fetched {len(period_records)} records for {current_year}")

                # Add to collection
                all_records.extend(period_records)

            except Exception as e:
                logger.error(f"Failed to fetch data for {current_year}: {e}")
                # Continue with other years even if one fails
                continue

        logger.info(f"Total records collected: {len(all_records)}")
        return all_records
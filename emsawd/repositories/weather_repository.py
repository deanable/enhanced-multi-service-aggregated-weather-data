import requests
import logging
from datetime import date, datetime
from typing import List
from emsawd.core.interfaces import IWeatherRepository
from emsawd.core.models import WeatherRecord

logger = logging.getLogger(__name__)

class WeatherRepository(IWeatherRepository):
    """
    An implementation of the weather repository using the Open-Meteo Historical Weather API.
    """
    API_URL = "https://archive-api.open-meteo.com/v1/archive"

    def get_historical_weather(
        self, latitude: float, longitude: float, start_date: date, end_date: date
    ) -> List[WeatherRecord]:
        """
        Fetches historical weather data for a given location and date range.

        Args:
            latitude: The latitude of the location.
            longitude: The longitude of the location.
            start_date: The start of the date range.
            end_date: The end of the date range.

        Returns:
            A list of WeatherRecord objects.

        Raises:
            ValueError: If the API returns an error or the data is malformed.
        """
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
            "timezone": "auto"
        }
        try:
            logger.info(f"Requesting historical weather for lat={latitude}, lon={longitude}")
            logger.debug(f"Request params: {params}")
            response = requests.get(self.API_URL, params=params, timeout=30)
            response.raise_for_status()
            logger.info(f"API response status: {response.status_code}")

            data = response.json()
            daily_data = data.get("daily")

            if not daily_data:
                logger.warning("API response is missing the 'daily' data object.")
                raise ValueError("API response did not contain 'daily' data.")

            # Unpack the daily data arrays
            dates = daily_data.get("time", [])
            max_temps = daily_data.get("temperature_2m_max", [])
            min_temps = daily_data.get("temperature_2m_min", [])
            precipitations = daily_data.get("precipitation_sum", [])

            # The API might return null for some values if data is missing.
            # We need to handle this gracefully. We'll use a default value (e.g., 0.0)
            # or skip the record if essential data is missing.

            records = []
            for i, record_date_str in enumerate(dates):
                record_date = datetime.fromisoformat(record_date_str).date()

                # Check for None values and provide defaults if necessary
                max_temp = max_temps[i] if max_temps[i] is not None else 0.0
                min_temp = min_temps[i] if min_temps[i] is not None else 0.0
                precipitation = precipitations[i] if precipitations[i] is not None else 0.0

                records.append(
                    WeatherRecord(
                        record_date=record_date,
                        year=record_date.year,
                        # Location is not part of the response, it's known by the caller
                        location="",
                        max_temp_c=max_temp,
                        min_temp_c=min_temp,
                        precipitation_mm=precipitation,
                    )
                )

            logger.info(f"Successfully parsed {len(records)} records from API response.")
            return records

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while fetching weather data: {e}", exc_info=True)
            raise ValueError(f"Network error while fetching weather data: {e}")
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing weather API response: {e}", exc_info=True)
            raise ValueError(f"Error parsing weather API response: {e}")

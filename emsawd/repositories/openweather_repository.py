import requests
import logging
from datetime import date, datetime, timedelta
from typing import List
from emsawd.core.interfaces import IWeatherRepository
from emsawd.core.models import WeatherRecord

logger = logging.getLogger(__name__)

class OpenWeatherRepository(IWeatherRepository):
    """
    An implementation of the weather repository using OpenWeatherMap API.
    Requires API key.
    """
    BASE_URL = "https://api.openweathermap.org/data/3.0/onecall/timemachine"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_historical_weather(
        self, latitude: float, longitude: float, start_date: date, end_date: date
    ) -> List[WeatherRecord]:
        """
        Fetches historical weather data for a given location and date range.
        Uses OpenWeatherMap One Call Timemachine API.

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
        records = []
        current_date = start_date
        while current_date <= end_date:
            # Use noon timestamp for the day
            timestamp = int(datetime.combine(current_date, datetime.min.time()).timestamp() + 12 * 3600)

            try:
                logger.info(f"Requesting OpenWeather for {current_date} at lat={latitude}, lon={longitude}")
                params = {
                    "lat": latitude,
                    "lon": longitude,
                    "dt": timestamp,
                    "appid": self.api_key
                }
                response = requests.get(self.BASE_URL, params=params, timeout=30)
                response.raise_for_status()
                logger.info(f"API response status: {response.status_code}")

                data = response.json()
                current_data = data.get("data", [])[0] if data.get("data") else None

                if not current_data:
                    logger.warning(f"No current data for {current_date}")
                    current_date += timedelta(days=1)
                    continue

                # Extract data from current (daily equivalent)
                temp = current_data.get("temp", 0)
                humidity = current_data.get("humidity", 0)
                precipitation = current_data.get("rain", {}).get("1h", 0) if "rain" in current_data else 0
                pressure = current_data.get("pressure", 0)
                wind_speed = current_data.get("wind_speed", 0)

                # Convert temp from Kelvin to Celsius
                temp_c = temp - 273.15 if temp > 200 else temp  # Check if Kelvin

                # Max/min might not be available, approximate
                max_temp = temp_c
                min_temp = temp_c

                records.append(
                    WeatherRecord(
                        record_date=current_date,
                        year=current_date.year,
                        location="",  # To be filled by caller
                        max_temp_c=max_temp,
                        min_temp_c=min_temp,
                        precipitation_mm=precipitation,
                    )
                )

            except requests.exceptions.RequestException as e:
                logger.error(f"Network error for {current_date}: {e}", exc_info=True)
                raise ValueError(f"Network error while fetching weather data: {e}")
            except (KeyError, IndexError, ValueError) as e:
                logger.error(f"Error parsing weather API response for {current_date}: {e}", exc_info=True)
                raise ValueError(f"Error parsing weather API response: {e}")

            current_date += timedelta(days=1)

        logger.info(f"Successfully parsed {len(records)} records from OpenWeather API.")
        return records
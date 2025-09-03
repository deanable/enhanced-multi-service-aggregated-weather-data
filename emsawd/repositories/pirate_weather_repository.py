import requests
import logging
from datetime import date, datetime, timedelta
from typing import List
from emsawd.core.interfaces import IWeatherRepository
from emsawd.core.models import WeatherRecord

logger = logging.getLogger(__name__)

class PirateWeatherRepository(IWeatherRepository):
    """
    An implementation of the weather repository using the Pirate Weather API (free, no key).
    Uses ERA5 historical reanalysis data.
    """
    BASE_URL = "https://timemachine.pirateweather.net/forecast/free"

    def get_historical_weather(
        self, latitude: float, longitude: float, start_date: date, end_date: date
    ) -> List[WeatherRecord]:
        """
        Fetches historical weather data for a given location and date range.
        Uses Pirate Weather API with ERA5 reanalysis.

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
            timestamp = int(datetime.combine(current_date, datetime.min.time()).timestamp() + 12 * 3600)  # Noon
            
            try:
                logger.info(f"Requesting Pirate Weather for {current_date} at lat={latitude}, lon={longitude}")
                url = f"{self.BASE_URL}/{latitude},{longitude},{timestamp}"
                response = requests.get(url)
                response.raise_for_status()
                logger.info(f"API response status: {response.status_code}")

                data = response.json()
                daily_data = data.get("daily", {}).get("data", [])
                
                if not daily_data:
                    logger.warning(f"No daily data for {current_date}")
                    current_date += timedelta(days=1)
                    continue

                # For historical, the API returns daily block with entries
                # But since we query per day, take the first daily entry
                day_data = daily_data[0]

                # Extract data
                max_temp = day_data.get("temperatureHigh", 0.0)
                min_temp = day_data.get("temperatureLow", 0.0)
                precipitation = day_data.get("precipAccumulation", 0.0)
                
                timestamp_date = datetime.fromtimestamp(day_data.get("time", 0)).date()
                if timestamp_date != current_date:
                    logger.warning(f"Date mismatch: requested {current_date}, got {timestamp_date}")
                    # Use the returned date
                    record_date = timestamp_date
                else:
                    record_date = current_date

                records.append(
                    WeatherRecord(
                        record_date=record_date,
                        year=record_date.year,
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

        logger.info(f"Successfully parsed {len(records)} records from Pirate Weather API.")
        return records
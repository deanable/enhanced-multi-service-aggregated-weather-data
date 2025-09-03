import requests
import logging
from datetime import date, datetime, timedelta
from typing import List
from emsawd.core.interfaces import IWeatherRepository
from emsawd.core.models import WeatherRecord

logger = logging.getLogger(__name__)

class AccuWeatherRepository(IWeatherRepository):
    """
    An implementation of the weather repository using AccuWeather API.
    Requires API key.
    """
    BASE_URL_HISTORICAL = "https://historical.accuweather.com/v1/daily/historical"
    GEOPOSITION_URL = "http://api.accuweather.com/locations/v1/cities/geoposition/search"

    def __init__(self, api_key):
        self.api_key = api_key

    def _get_location_key(self, latitude: float, longitude: float) -> str:
        """Get location key from lat/lon."""
        params = {
            "apikey": self.api_key,
            "q": f"{latitude},{longitude}",
            "language": "en-us"
        }
        response = requests.get(self.GEOPOSITION_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("Key", "")

    def get_historical_weather(
        self, latitude: float, longitude: float, start_date: date, end_date: date
    ) -> List[WeatherRecord]:
        """
        Fetches historical weather data for a given location and date range.
        Uses AccuWeather historical API.

        Args:
            latitude: The latitude of the location.
            longitude: The longitude of the location.
            start_date: The start of the date range.
            end_date: The end of the date range.

        Returns:
            A list of WeatherRecord objects.

        Raises:
            ValueError: If the API返回 returns an error or the data is malformed.
        """
        # Get location key
        location_key = self._get_location_key(latitude, longitude)
        if not location_key:
            raise ValueError("Could not get location key from AccuWeather")

        records = []
        # For daily historical, request per day or small range
        current_date = start_date
        while current_date <= end_date:
            start_dt = datetime.combine(current_date, datetime.min.time()).isoformat() + "Z"
            end_dt = datetime.combine(current_date, datetime.max.time()).isoformat() + "Z"

            try:
                logger.info(f"Requesting AccuWeather for {current_date} location {location_key}")
                url = f"{self.BASE_URL_HISTORICAL}/{location_key}"
                params = {
                    "apikey": self.api_key,
                    "startDateTime": start_dt,
                    "endDateTime": end_dt
                }
                response = requests.get(url, params=params)
                response.raise_for_status()
                logger.info(f"API response status: {response.status_code}")

                data = response.json()
                if not data:
                    logger.warning(f"No data for {current_date}")
                    current_date += timedelta(days=1)
                    continue

                # Daily data
                day_data = data[0]
                max_temp = day_data.get("Temperature", {}).get("Maximum", {}).get("Value", 0)
                min_temp = day_data.get("Temperature", {}).get("Minimum", {}).get("Value", 0)
                precipitation = day_data.get("Day", {}).get("Rain", {}).get("Value", 0)

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
                logger.error(f"Error parsing AccuWeather API response for {current_date}: {e}", exc_info=True)
                raise ValueError(f"Error parsing weather API response: {e}")

            current_date += timedelta(days=1)

        logger.info(f"Successfully parsed {len(records)} records from AccuWeather.")
        return records
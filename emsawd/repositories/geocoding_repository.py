import requests
import logging
from typing import Tuple
from emsawd.core.interfaces import IGeocodingRepository

logger = logging.getLogger(__name__)

class GeocodingRepository(IGeocodingRepository):
    """
    An implementation of the geocoding repository using the Open-Meteo Geocoding API.
    """
    API_URL = "https://geocoding-api.open-meteo.com/v1/search"

    def get_coordinates(self, location_name: str) -> Tuple[float, float]:
        """
        Gets the latitude and longitude for a given location name.

        Args:
            location_name: The name of the city or location to search for.

        Returns:
            A tuple containing the latitude and longitude of the first search result.

        Raises:
            ValueError: If the location cannot be found or the API returns an error.
        """
        params = {
            "name": location_name,
            "count": 1
        }
        try:
            logger.info(f"Requesting coordinates for '{location_name}' from {self.API_URL}")
            logger.debug(f"Request params: {params}")
            response = requests.get(self.API_URL, params=params)
            response.raise_for_status()
            logger.info(f"API response status: {response.status_code}")

            data = response.json()

            if not data.get("results"):
                logger.warning(f"Location '{location_name}' not found in API response.")
                raise ValueError(f"Location '{location_name}' not found.")

            result = data["results"][0]
            latitude = result["latitude"]
            longitude = result["longitude"]

            logger.info(f"Successfully found coordinates for '{location_name}': ({latitude}, {longitude})")
            return (latitude, longitude)

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while fetching coordinates for '{location_name}': {e}", exc_info=True)
            raise ValueError(f"Network error while fetching coordinates: {e}")
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing API response for '{location_name}': {e}", exc_info=True)
            raise ValueError(f"Error parsing API response: {e}")

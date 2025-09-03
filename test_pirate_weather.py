from datetime import date, timedelta
from emsawd.repositories.pirate_weather_repository import PirateWeatherRepository

print("Starting test script")
import sys
sys.stdout.flush()

def test_pirate_weather():
    print("Creating repo")
    sys.stdout.flush()
    repo = PirateWeatherRepository()
    latitude = 51.5  # London
    longitude = -0.12
    start_date = date(2023, 1, 1)
    end_date = date(2023, 1, 3)  # Small range for testing

    print(f"Testing Pirate Weather for London, {start_date} to {end_date}")
    sys.stdout.flush()
    try:
        records = repo.get_historical_weather(latitude, longitude, start_date, end_date)
        print(f"Successfully fetched {len(records)} records:")
        for record in records:
            print(f"Date: {record.record_date}, Max Temp: {record.max_temp_c}°C, Min Temp: {record.min_temp_c}°C, Precip: {record.precipitation_mm}mm")
        print("Done")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pirate_weather()
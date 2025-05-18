import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import json

# Setup Open-Meteo API client with cache and retry
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Define API endpoint and parameters
url = "https://archive-api.open-meteo.com/v1/archive"

# Define locations
locations = [
    {"name": "Karachi", "latitude": 24.8608, "longitude": 67.0104},
    {"name": "Islamabad", "latitude": 33.7215, "longitude": 73.0433}
]

# API request parameters common to all locations
base_params = {
    "start_date": "2024-05-18",
    "end_date": "2025-05-16",
    "daily": ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min"]
}

all_weather_data = {}

# Fetch data for each location
for loc in locations:
    print(f"\nProcessing data for {loc['name']}")

    params = {
        "latitude": loc["latitude"],
        "longitude": loc["longitude"],
        **base_params
    }

    try:
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]

        print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation: {response.Elevation()} m asl")
        print(f"Timezone: {response.Timezone()} {response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()} s")

        # Extract daily data
        daily = response.Daily()

        # Generate date range based on metadata
        date_range = pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        )
        formatted_dates = [dt.strftime('%Y-%m-%d') for dt in date_range]

        # Read temperature values
        temp_mean = daily.Variables(0).ValuesAsNumpy()
        temp_max = daily.Variables(1).ValuesAsNumpy()
        temp_min = daily.Variables(2).ValuesAsNumpy()

        # Create DataFrame
        daily_data = {
            "date": formatted_dates,
            "temperature_2m_mean": temp_mean,
            "temperature_2m_max": temp_max,
            "temperature_2m_min": temp_min
        }

        df = pd.DataFrame(daily_data)
        all_weather_data[loc["name"]] = df.to_dict(orient="records")

    except Exception as e:
        print(f"Error fetching data for {loc['name']}: {e}")

# Save all data to JSON file
output_file = "all_weather_data.json"
try:
    with open(output_file, "w") as f:
        json.dump(all_weather_data, f, indent=4)
    print(f"Data successfully saved to '{output_file}'")
except Exception as e:
    print(f"Failed to save data: {e}")

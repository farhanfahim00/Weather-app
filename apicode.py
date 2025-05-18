import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import json
from datetime import datetime, timedelta

# Setup Open-Meteo API client
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)  # Cache for 1 hour
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

url = "https://archive-api.open-meteo.com/v1/archive"

locations = [
    {"name": "Islamabad", "latitude": 33.738045, "longitude": 73.084488},
    {"name": "Karachi", "latitude": 24.860966, "longitude": 66.990501}
]

all_data = {}

# Dynamic date range (1 year of data, ending yesterday)
end_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

print(f"Fetching data from {start_date} to {end_date}")

for location in locations:
    print(f"\nProcessing data for {location['name']}")

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "start_date": start_date,
        "end_date": end_date,
        "daily": ["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean"],
        "timezone": "Asia/Karachi"  # Force timezone to avoid issues
    }

    print(params)

    try:
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]

        print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation: {response.Elevation()} m asl")
        print(f"Timezone: {response.Timezone()} {response.TimezoneAbbreviation()}")

        daily = response.Daily()
        time_array = daily.Time()  # Should be an array of timestamps
        temp_max = daily.Variables(0).ValuesAsNumpy()
        temp_min = daily.Variables(1).ValuesAsNumpy()
        temp_mean = daily.Variables(2).ValuesAsNumpy()

        # Check if data exists
        if len(time_array) == 0:
            print(f"No data available for {location['name']}!")
            continue

        # Convert timestamps to dates
        dates = pd.to_datetime(time_array, unit='s', utc=True).strftime('%Y-%m-%d')

        # Create DataFrame
        df = pd.DataFrame({
            "date": dates,
            "temperature_max": temp_max,
            "temperature_min": temp_min,
            "temperature_mean": temp_mean
        })

        all_data[location["name"]] = df

        print(f"\nFirst 5 rows for {location['name']}:")
        print(df.head())

    except Exception as e:
        print(f"🚨 Error for {location['name']}: {str(e)}")
        # Generate empty DataFrame if API fails
        all_data[location["name"]] = pd.DataFrame(
            columns=["date", "temperature_max", "temperature_min", "temperature_mean"])

# Save data to JSON
output_filename = "all_weather_data.json"
with open(output_filename, "w") as outfile:
    json.dump({city: df.to_dict("records") for city, df in all_data.items()}, outfile, indent=4)

print(f"\n✅ Weather data saved to {output_filename}")
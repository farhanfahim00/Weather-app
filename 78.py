import openmeteo_requests
import pandas as pd
import requests_cache
from retry_requests import retry
import json

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Base URL for the historical API
url = "https://archive-api.open-meteo.com/v1/archive"

# Define the locations you want data for
locations = [
    {"name": "Islamabad", "latitude": 33.738045, "longitude": 73.084488},
    {"name": "Karachi", "latitude": 24.860966, "longitude": 66.990501}
]

all_data = {}

for location in locations:
    print(f"Processing data for {location['name']}")
    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "start_date": "2024-05-18",
        "end_date": "2025-05-17",
        "daily": ["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean"]
    }

    print(params)

    try:
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]  # Assuming one response per location
        print(responses)

        print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
        print(f"Elevation: {response.Elevation()} m asl")
        print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
        print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()} s")

        # Process daily data
        daily = response.Daily()
        daily_time = daily.Time()
        daily_temperature_2m = daily.Variables(0).ValuesAsNumpy()

        daily_data = {"date": pd.to_datetime(daily_time, unit="s", utc=True).strftime('%Y-%m-%d'), #converted to string and take first 10 characters since we dont need time
                      "temperature_2m": daily_temperature_2m}

        daily_dataframe = pd.DataFrame(data=daily_data)
        all_data[location["name"]] = daily_dataframe

    except Exception as e:
        print(f"Error fetching data for {location['name']}: {e}")

# Now 'all_data' dictionary contains the Pandas DataFrames for each city
print("\n--- Data for all locations ---")
for city, df in all_data.items():
    print(f"\nData for {city}:")
    print(df)

filename = "locations_data.json"
try:
       with open(filename, 'w') as json_file:
              json.dump(locations, json_file, indent=4)
except Exception as e:
		print(f"An error occurred while writing to '{filename}': {e}")
              

# Convert all DataFrames to dictionaries
combined_data = {city: df.to_dict(orient="records") for city, df in all_data.items()}

# Save to one JSON file
with open("all_weather_data.json", "w") as outfile:
    json.dump(combined_data, outfile, indent=4)


import json
import pandas as pd
import matplotlib.pyplot as plt

#Load the JSON file
with open("all_weather_data.json", "r") as f:
    weather_data = json.load(f)

#Creating DataFrames for each city
karachi_data = pd.DataFrame(weather_data["Karachi"])
islamabad_data = pd.DataFrame(weather_data["Islamabad"])

#Converting 'date' column to datetime objects
karachi_data["date"] = pd.to_datetime(karachi_data["date"])
islamabad_data["date"] = pd.to_datetime(islamabad_data["date"])

# Plotting
plt.figure(figsize=(14, 6))
plt.plot(karachi_data["date"], karachi_data["temperature_2m_mean"], label="Karachi", color="orange")
plt.plot(islamabad_data["date"], islamabad_data["temperature_2m_mean"], label="Islamabad", color="blue")

# Customize plot
plt.title("Daily Mean Temperature for Karachi and Islamabad (Last 365 Days)")
plt.xlabel("Date")
plt.ylabel("Mean Temperature (°C)")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Show the plot
plt.show()

import requests
import pandas as pd


def main():

    url = (
        "https://archive-api.open-meteo.com/v1/archive?"
        "latitude=57.0488&"
        "longitude=9.9217&"
        "start_date=2025-01-01&"
        "end_date=2025-12-31&"
        "hourly=wind_speed_100m,temperature_2m&"
        "timezone=Europe%2FBerlin"
    )

    response = requests.get(url)

    data = response.json()

    df = pd.DataFrame({
        "time": data["hourly"]["time"],
        "wind_speed_100m": data["hourly"]["wind_speed_100m"],
        "temperature_2m": data["hourly"]["temperature_2m"]
    })
    df["wind_speed_100m"] = df["wind_speed_100m"] / 3.6
    df.to_csv("data/weather_data.csv", index=False)

    print(df.head())
    print("Weather data stored successfully")


if __name__ == "__main__":
    main()

import pandas as pd
import numpy as np


ANNUAL_CONSUMPTION_MWH = 266770

AVERAGE_LOAD_MW = ANNUAL_CONSUMPTION_MWH / 8760


def main():

    weather_df = pd.read_csv("data/weather_data.csv")

    weather_df["time"] = pd.to_datetime(weather_df["time"])

    demand = []

    for timestamp in weather_df["time"]:

        hour = timestamp.hour
        weekday = timestamp.weekday()

        load = AVERAGE_LOAD_MW

        # Lower demand during night
        if hour >= 0 and hour <= 5:
            load *= 0.92

        # Higher demand during daytime
        elif hour >= 8 and hour <= 18:
            load *= 1.05

        # Lower demand during weekends
        if weekday >= 5:
            load *= 0.90

        # Small random variability
        load *= np.random.normal(1, 0.02)

        demand.append(load)

    demand_df = pd.DataFrame({
        "time": weather_df["time"],
        "demand_mw": demand
    })

    demand_df.to_csv("data/demand_profile.csv", index=False)

    print(demand_df.head())
    print("Synthetic demand profile generated successfully")


if __name__ == "__main__":
    main()

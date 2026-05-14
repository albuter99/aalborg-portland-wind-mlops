import pandas as pd


TURBINES = {
    "Vestas V136 4.5 MW": {
        "rated_power_mw": 4.5,
        "cut_in": 3,
        "rated_speed": 12,
        "cut_out": 25
    },
    "Siemens Gamesa SG 5.0-145": {
        "rated_power_mw": 5.0,
        "cut_in": 3,
        "rated_speed": 12,
        "cut_out": 25
    },
    "Nordex N149 5.X": {
        "rated_power_mw": 5.5,
        "cut_in": 3,
        "rated_speed": 12,
        "cut_out": 26
    },
    "Enercon E-138 EP3": {
        "rated_power_mw": 4.26,
        "cut_in": 3,
        "rated_speed": 12,
        "cut_out": 25
    }
}


def estimate_power(wind_speed, turbine):
    cut_in = turbine["cut_in"]
    rated_speed = turbine["rated_speed"]
    cut_out = turbine["cut_out"]
    rated_power = turbine["rated_power_mw"]

    if wind_speed < cut_in:
        return 0

    if wind_speed >= cut_out:
        return 0

    if wind_speed >= rated_speed:
        return rated_power

    power = rated_power * ((wind_speed - cut_in) / (rated_speed - cut_in)) ** 3
    return power


def main():
    weather_df = pd.read_csv("data/weather_data.csv")
    demand_df = pd.read_csv("data/demand_profile.csv")

    weather_df["time"] = pd.to_datetime(weather_df["time"])
    demand_df["time"] = pd.to_datetime(demand_df["time"])

    df = weather_df.merge(demand_df, on="time")

    for turbine_name, turbine_specs in TURBINES.items():
        df[turbine_name + " generation_mw"] = df["wind_speed_100m"].apply(
            lambda x: estimate_power(x, turbine_specs)
        )

        df[turbine_name + " coverage_ratio"] = (
            df[turbine_name + " generation_mw"] / df["demand_mw"]
        )

    df.to_csv("data/turbine_simulation_results.csv", index=False)

    print(df.head())
    print("Turbine simulation completed successfully")


if __name__ == "__main__":
    main()

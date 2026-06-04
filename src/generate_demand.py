import pandas as pd
import numpy as np


ANNUAL_CONSUMPTION_MWH = 256211

AVERAGE_LOAD_MW = ANNUAL_CONSUMPTION_MWH / 8760

RANDOM_SEED = 42


def generate_hourly_demand(weather_df):

    demand = []

    for timestamp in weather_df["time"]:

        hour = timestamp.hour
        weekday = timestamp.weekday()

        load = AVERAGE_LOAD_MW

        # Lower demand during night
        if 0 <= hour <= 5:
            load *= 0.92

        # Higher demand during working hours
        elif 8 <= hour <= 18:
            load *= 1.05

        # Lower demand during weekends
        if weekday >= 5:
            load *= 0.90

        # Small random variability
        load *= np.random.normal(1, 0.02)

        demand.append(load)

    return demand


def calibrate_to_annual_consumption(demand_df):

    synthetic_total = demand_df["demand_mw"].sum()

    scaling_factor = ANNUAL_CONSUMPTION_MWH / synthetic_total

    demand_df["demand_mw"] *= scaling_factor

    calibrated_total = demand_df["demand_mw"].sum()

    calibration_error = (
        abs(calibrated_total - ANNUAL_CONSUMPTION_MWH)
        / ANNUAL_CONSUMPTION_MWH
        * 100
    )

    return demand_df, calibrated_total, calibration_error


def export_validation_metrics(demand_df, calibrated_total, calibration_error):

    monthly_profile = (
        demand_df
        .assign(month=demand_df["time"].dt.month_name())
        .groupby("month")["demand_mw"]
        .sum()
        .reset_index()
    )

    monthly_profile.to_csv(
        "artifacts/monthly_demand_profile.csv",
        index=False
    )

    validation_df = pd.DataFrame([{
        "reported_annual_demand_mwh": ANNUAL_CONSUMPTION_MWH,
        "synthetic_annual_demand_mwh": round(calibrated_total, 2),
        "calibration_error_percent": round(calibration_error, 4)
    }])

    validation_df.to_csv(
        "artifacts/demand_model_validation.csv",
        index=False
    )


def main():

    np.random.seed(RANDOM_SEED)

    weather_df = pd.read_csv("data/weather_data.csv")

    weather_df["time"] = pd.to_datetime(weather_df["time"])

    demand_values = generate_hourly_demand(weather_df)

    demand_df = pd.DataFrame({
        "time": weather_df["time"],
        "demand_mw": demand_values
    })

    demand_df, calibrated_total, calibration_error = (
        calibrate_to_annual_consumption(demand_df)
    )

    demand_df.to_csv(
        "data/demand_profile.csv",
        index=False
    )

    export_validation_metrics(
        demand_df,
        calibrated_total,
        calibration_error
    )

    print()
    print("Demand profile generated successfully")
    print(f"Reported annual demand: {ANNUAL_CONSUMPTION_MWH:,.0f} MWh")
    print(f"Synthetic annual demand: {calibrated_total:,.2f} MWh")
    print(f"Calibration error: {calibration_error:.6f}%")
    print()


if __name__ == "__main__":
    main()

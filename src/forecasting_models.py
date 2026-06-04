import os
import requests
import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:
    from xgboost import XGBRegressor
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False


TURBINES = {
    "Vestas V136 4.5 MW": {
        "rated_power_mw": 4.5,
        "cut_in": 3.0,
        "rated_speed": 11.3,
        "cut_out": 25.0
    },
    "Siemens Gamesa SG 5.0-145": {
        "rated_power_mw": 5.0,
        "cut_in": 3.0,
        "rated_speed": 11.0,
        "cut_out": 27.0
    },
    "Nordex N149 5.X": {
        "rated_power_mw": 5.7,
        "cut_in": 3.0,
        "rated_speed": 12.0,
        "cut_out": 26.0
    },
    "Enercon E-138 EP3": {
        "rated_power_mw": 4.26,
        "cut_in": 2.5,
        "rated_speed": 12.1,
        "cut_out": 28.0
    }
}


def estimate_power(wind_speed_ms, turbine):
    cut_in = turbine["cut_in"]
    rated_speed = turbine["rated_speed"]
    cut_out = turbine["cut_out"]
    rated_power = turbine["rated_power_mw"]

    if wind_speed_ms < cut_in:
        return 0.0

    if wind_speed_ms >= cut_out:
        return 0.0

    if wind_speed_ms >= rated_speed:
        return rated_power

    return rated_power * ((wind_speed_ms - cut_in) / (rated_speed - cut_in)) ** 3


def fetch_7_day_forecast():
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        "latitude=57.0488&"
        "longitude=9.9217&"
        "hourly=wind_speed_100m,temperature_2m&"
        "forecast_days=7&"
        "wind_speed_unit=ms&"
        "timezone=Europe%2FBerlin"
    )

    response = requests.get(url, timeout=60)
    response.raise_for_status()
    data = response.json()

    forecast_df = pd.DataFrame({
        "time": data["hourly"]["time"],
        "wind_speed_100m": data["hourly"]["wind_speed_100m"],
        "temperature_2m": data["hourly"]["temperature_2m"]
    })

    forecast_df["time"] = pd.to_datetime(forecast_df["time"])

    os.makedirs("data", exist_ok=True)
    forecast_df.to_csv("data/forecast_weather_7d.csv", index=False)

    return forecast_df


def build_features(df):
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])

    df["hour"] = df["time"].dt.hour
    df["dayofyear"] = df["time"].dt.dayofyear
    df["month"] = df["time"].dt.month
    df["weekday"] = df["time"].dt.weekday

    if "wind_speed_100m" in df.columns:
        wind_col = "wind_speed_100m"
    elif "wind_speed_100m_ms" in df.columns:
        wind_col = "wind_speed_100m_ms"
    else:
        raise ValueError("No wind speed column found.")

    df["wind_speed"] = df[wind_col]

    return df


def get_ml_features():
    return [
        "wind_speed",
        "temperature_2m",
        "hour",
        "dayofyear",
        "month",
        "weekday"
    ]


def evaluate_model(model, X, y):
    predictions = model.predict(X)
    predictions = np.maximum(predictions, 0)

    mae = mean_absolute_error(y, predictions)
    rmse = np.sqrt(mean_squared_error(y, predictions))
    r2 = r2_score(y, predictions)

    return mae, rmse, r2


def train_and_compare_models():
    df = pd.read_csv("data/turbine_simulation_results.csv")
    df = build_features(df)

    target_col = "Nordex N149 5.X generation_mw"
    features = get_ml_features()

    df = df.dropna(subset=features + [target_col]).reset_index(drop=True)

    train_end = int(len(df) * 0.70)
    validation_end = int(len(df) * 0.85)

    train_df = df.iloc[:train_end]
    validation_df = df.iloc[train_end:validation_end]
    test_df = df.iloc[validation_end:]

    X_train = train_df[features]
    y_train = train_df[target_col]

    X_validation = validation_df[features]
    y_validation = validation_df[target_col]

    X_test = test_df[features]
    y_test = test_df[target_col]

    models = {
        "Linear Regression": LinearRegression(),
        "Random Forest": RandomForestRegressor(
            n_estimators=150,
            random_state=42,
            max_depth=8
        )
    }

    if XGBOOST_AVAILABLE:
        models["XGBoost"] = XGBRegressor(
            n_estimators=150,
            max_depth=3,
            learning_rate=0.05,
            objective="reg:squarederror",
            random_state=42
        )

    validation_results = []
    fitted_models = {}

    for name, model in models.items():
        model.fit(X_train, y_train)

        val_mae, val_rmse, val_r2 = evaluate_model(
            model,
            X_validation,
            y_validation
        )

        fitted_models[name] = model

        validation_results.append({
            "model": name,
            "validation_mae_mw": val_mae,
            "validation_rmse_mw": val_rmse,
            "validation_r2_score": val_r2
        })

    validation_results_df = pd.DataFrame(validation_results)

    best_model_name = validation_results_df.sort_values(
        "validation_mae_mw"
    ).iloc[0]["model"]

    best_model = models[best_model_name]

    X_train_validation = pd.concat([X_train, X_validation])
    y_train_validation = pd.concat([y_train, y_validation])

    final_results = []

    for name, model in models.items():
        model.fit(X_train_validation, y_train_validation)

        test_mae, test_rmse, test_r2 = evaluate_model(
            model,
            X_test,
            y_test
        )

        validation_row = validation_results_df[
            validation_results_df["model"] == name
        ].iloc[0]

        final_results.append({
            "model": name,
            "mae_mw": round(test_mae, 4),
            "rmse_mw": round(test_rmse, 4),
            "r2_score": round(test_r2, 4),
            "validation_mae_mw": round(validation_row["validation_mae_mw"], 4),
            "validation_rmse_mw": round(validation_row["validation_rmse_mw"], 4),
            "validation_r2_score": round(validation_row["validation_r2_score"], 4),
            "test_mae_mw": round(test_mae, 4),
            "test_rmse_mw": round(test_rmse, 4),
            "test_r2_score": round(test_r2, 4),
            "evaluation_type": "Surrogate model approximation",
            "target_type": "Simulated turbine generation from physical power curve"
        })

    results_df = pd.DataFrame(final_results)

    os.makedirs("artifacts", exist_ok=True)
    results_df.to_csv("artifacts/forecast_model_comparison.csv", index=False)

    model_note_df = pd.DataFrame([{
        "forecasting_method": "Physical power-curve forecast",
        "ml_role": "Machine learning models are evaluated as surrogate models.",
        "evaluation_note": (
            "The target variable is simulated turbine generation derived from a "
            "physical power curve, not measured turbine production. Very high R² "
            "values are therefore expected and should be interpreted as approximation "
            "accuracy rather than real-world forecasting accuracy."
        ),
        "split_strategy": "Chronological split: 70% train, 15% validation, 15% test",
        "selected_model": best_model_name
    }])

    model_note_df.to_csv("artifacts/forecast_model_note.csv", index=False)

    best_model.fit(X_train_validation, y_train_validation)

    return best_model_name, best_model, features


def generate_hourly_profile(
    forecast_output,
    seven_day_demand_mwh,
    reference_turbine,
    reference_turbine_count
):
    hourly_demand_mwh = seven_day_demand_mwh / len(forecast_output)

    generation_col = f"{reference_turbine} generation_mw"

    hourly_profile = forecast_output[[
        "time",
        generation_col
    ]].copy()

    hourly_profile = hourly_profile.rename(columns={
        "time": "timestamp",
        generation_col: "forecast_generation_mwh"
    })

    hourly_profile["forecast_generation_mwh"] *= reference_turbine_count
    hourly_profile["estimated_demand_mwh"] = hourly_demand_mwh

    hourly_profile["coverage_percent"] = (
        hourly_profile["forecast_generation_mwh"] /
        hourly_profile["estimated_demand_mwh"] * 100
    )

    hourly_profile["grid_required_mwh"] = (
        hourly_profile["estimated_demand_mwh"] -
        hourly_profile["forecast_generation_mwh"]
    ).clip(lower=0)

    hourly_profile["reference_turbine"] = reference_turbine
    hourly_profile["reference_turbine_count"] = reference_turbine_count
    hourly_profile["forecast_method"] = "Physical turbine power curve"

    hourly_profile["forecast_generation_mwh"] = hourly_profile[
        "forecast_generation_mwh"
    ].round(4)

    hourly_profile["estimated_demand_mwh"] = hourly_profile[
        "estimated_demand_mwh"
    ].round(4)

    hourly_profile["coverage_percent"] = hourly_profile[
        "coverage_percent"
    ].round(2)

    hourly_profile["grid_required_mwh"] = hourly_profile[
        "grid_required_mwh"
    ].round(4)

    hourly_profile.to_csv(
        "artifacts/forecast_hourly_profile.csv",
        index=False
    )


def generate_7_day_forecast():
    best_model_name, best_model, features = train_and_compare_models()

    forecast_weather_df = fetch_7_day_forecast()
    forecast_features_df = build_features(forecast_weather_df)

    X_forecast = forecast_features_df[features]

    forecast_features_df["best_model_generation_mw"] = np.maximum(
        best_model.predict(X_forecast),
        0
    )

    for turbine_name, turbine_specs in TURBINES.items():
        generation_col = f"{turbine_name} generation_mw"

        forecast_features_df[generation_col] = forecast_features_df["wind_speed"].apply(
            lambda wind_speed: estimate_power(wind_speed, turbine_specs)
        )

    output_columns = [
        "time",
        "wind_speed",
        "temperature_2m",
        "best_model_generation_mw"
    ]

    for turbine_name in TURBINES:
        output_columns.append(f"{turbine_name} generation_mw")

    forecast_output = forecast_features_df[output_columns].copy()
    forecast_output["best_model"] = best_model_name
    forecast_output["operational_forecast_method"] = "Physical turbine power curve"
    forecast_output["ml_model_role"] = "Surrogate model approximation"

    forecast_output.to_csv("artifacts/forecast_7d_generation.csv", index=False)

    annual_demand_df = pd.read_csv("data/turbine_simulation_results.csv")
    annual_demand_mwh = annual_demand_df["demand_mw"].sum()
    seven_day_demand_mwh = annual_demand_mwh / 365 * 7

    stakeholder_rows = []

    for turbine_name in TURBINES:
        generation_col = f"{turbine_name} generation_mw"
        one_turbine_generation = forecast_output[generation_col].sum()

        for turbine_count in [1, 2, 3, 5, 10]:
            total_generation = one_turbine_generation * turbine_count
            coverage = total_generation / seven_day_demand_mwh * 100
            grid_required = max(seven_day_demand_mwh - total_generation, 0)

            stakeholder_rows.append({
                "turbine": turbine_name,
                "number_of_turbines": turbine_count,
                "forecast_generation_mwh": round(total_generation, 2),
                "estimated_7d_demand_mwh": round(seven_day_demand_mwh, 2),
                "grid_required_mwh": round(grid_required, 2),
                "coverage_percent": round(coverage, 2),
                "forecast_method": "Physical turbine power curve"
            })

    stakeholder_df = pd.DataFrame(stakeholder_rows)
    stakeholder_df.to_csv(
        "artifacts/forecast_stakeholder_scenarios.csv",
        index=False
    )

    best_scenario = stakeholder_df.sort_values(
        "forecast_generation_mwh",
        ascending=False
    ).iloc[0]

    generate_hourly_profile(
        forecast_output=forecast_output,
        seven_day_demand_mwh=seven_day_demand_mwh,
        reference_turbine=best_scenario["turbine"],
        reference_turbine_count=int(best_scenario["number_of_turbines"])
    )

    print("7-day forecasting module completed successfully")
    print("Operational forecast method: physical turbine power curve")
    print(f"ML model selected as surrogate approximation: {best_model_name}")
    print("Hourly forecast profile generated successfully")


def main():
    generate_7_day_forecast()


if __name__ == "__main__":
    main()

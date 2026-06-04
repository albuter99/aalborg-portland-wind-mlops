import pandas as pd


TURBINES = [
    "Vestas V136 4.5 MW",
    "Siemens Gamesa SG 5.0-145",
    "Nordex N149 5.X",
    "Enercon E-138 EP3",
]


def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    if month in [3, 4, 5]:
        return "Spring"
    if month in [6, 7, 8]:
        return "Summer"
    return "Autumn"


def main():
    df = pd.read_csv("data/turbine_simulation_results.csv")
    df["time"] = pd.to_datetime(df["time"])
    df["season"] = df["time"].dt.month.apply(get_season)

    results = []

    for season, group in df.groupby("season"):
        seasonal_demand = group["demand_mw"].sum()

        for turbine in TURBINES:
            generation_col = f"{turbine} generation_mw"

            if generation_col not in group.columns:
                continue

            seasonal_generation = group[generation_col].sum()
            seasonal_coverage = seasonal_generation / seasonal_demand * 100

            results.append({
                "season": season,
                "turbine": turbine,
                "seasonal_demand_mwh": round(seasonal_demand, 2),
                "seasonal_generation_mwh": round(seasonal_generation, 2),
                "seasonal_coverage_percent": round(seasonal_coverage, 2),
            })

    results_df = pd.DataFrame(results)
    results_df.to_csv("artifacts/seasonal_analysis.csv", index=False)

    print(results_df)
    print("Seasonal analysis completed successfully")


if __name__ == "__main__":
    main()

import pandas as pd


TURBINES = [
    "Vestas V136 4.5 MW",
    "Siemens Gamesa SG 5.0-145",
    "Nordex N149 5.X",
    "Enercon E-138 EP3"
]


def main():

    df = pd.read_csv("data/turbine_simulation_results.csv")

    results = []

    annual_demand = df["demand_mw"].sum()

    for turbine in TURBINES:

        generation_col = turbine + " generation_mw"

        annual_generation = df[generation_col].sum()

        coverage_ratio = annual_generation / annual_demand

        capacity_factor = annual_generation / (
            len(df) * df[generation_col].max()
        )

        surplus_hours = (
            df[generation_col] > df["demand_mw"]
        ).sum()

        results.append({
            "turbine": turbine,
            "annual_generation_mwh": round(annual_generation, 2),
            "coverage_ratio_percent": round(coverage_ratio * 100, 2),
            "capacity_factor_percent": round(capacity_factor * 100, 2),
            "surplus_hours": surplus_hours
        })

    results_df = pd.DataFrame(results)

    results_df.to_csv("artifacts/turbine_summary.csv", index=False)

    print(results_df)

    print("Analysis completed successfully")


if __name__ == "__main__":
    main()

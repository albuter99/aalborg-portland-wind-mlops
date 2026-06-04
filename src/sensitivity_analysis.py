import pandas as pd


def main():
    simulation_df = pd.read_csv("data/turbine_simulation_results.csv")
    summary_df = pd.read_csv("artifacts/turbine_summary.csv")

    base_annual_demand = simulation_df["demand_mw"].sum()

    scenarios = {
        "Low demand (-10%)": 0.90,
        "Base demand": 1.00,
        "High demand (+10%)": 1.10,
    }

    results = []

    for _, row in summary_df.iterrows():
        turbine = row["turbine"]
        annual_generation = row["annual_generation_mwh"]

        for scenario_name, multiplier in scenarios.items():
            scenario_demand = base_annual_demand * multiplier
            coverage = annual_generation / scenario_demand * 100

            results.append({
                "scenario": scenario_name,
                "turbine": turbine,
                "annual_generation_mwh": round(annual_generation, 2),
                "scenario_demand_mwh": round(scenario_demand, 2),
                "coverage_percent": round(coverage, 2),
            })

    results_df = pd.DataFrame(results)
    results_df.to_csv("artifacts/sensitivity_analysis.csv", index=False)

    print(results_df)
    print("Sensitivity analysis completed successfully")


if __name__ == "__main__":
    main()

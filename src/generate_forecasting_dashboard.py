import pandas as pd


BRAND_COLOR = "#a0003f"
ACCENT_COLOR = "#e4005a"
LIGHT_BG = "#f7f5f6"


def format_number(value):
    return f"{value:,.0f}".replace(",", ".")


def main():
    model_df = pd.read_csv("artifacts/forecast_model_comparison.csv")
    scenario_df = pd.read_csv("artifacts/forecast_stakeholder_scenarios.csv")

    best_model = model_df.sort_values("mae_mw").iloc[0]

    best_scenario = scenario_df.sort_values(
        "forecast_generation_mwh",
        ascending=False
    ).iloc[0]

    average_coverage = scenario_df["coverage_percent"].mean()

    model_rows = ""
    for _, row in model_df.iterrows():
        highlight = "highlight" if row["model"] == best_model["model"] else ""

        model_rows += f"""
        <tr class="{highlight}">
            <td>{row["model"]}</td>
            <td>{row["mae_mw"]:.4f}</td>
            <td>{row["rmse_mw"]:.4f}</td>
            <td>{row["r2_score"]:.4f}</td>
        </tr>
        """

    turbine_options = ""
    turbine_table_rows = ""

    for turbine in scenario_df["turbine"].unique():
        turbine_options += f'<option value="{turbine}">{turbine}</option>'

        one_turbine = scenario_df[
            (scenario_df["turbine"] == turbine)
            & (scenario_df["number_of_turbines"] == 1)
        ].iloc[0]

        turbine_table_rows += f"""
        <tr>
            <td><strong>{turbine}</strong></td>
            <td>{format_number(one_turbine["forecast_generation_mwh"])} MWh</td>
            <td>{one_turbine["coverage_percent"]:.2f}%</td>
        </tr>
        """

    scenario_json = scenario_df.to_json(orient="records")

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Aalborg Portland Forecasting</title>

    <style>
        :root {{
            --brand: {BRAND_COLOR};
            --accent: {ACCENT_COLOR};
            --light: {LIGHT_BG};
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: Arial, Helvetica, sans-serif;
            background: var(--light);
            color: #222;
        }}

        .top-brand {{
            background: linear-gradient(90deg, #78002e, #b00046);
            color: white;
            padding: 22px 60px;
        }}

        .brand-name {{
            font-size: 34px;
            font-weight: 700;
            letter-spacing: -1px;
        }}

        .brand-name span {{
            font-weight: 300;
        }}

        .brand-subtitle {{
            font-size: 11px;
            letter-spacing: 1.8px;
            margin-top: 2px;
            opacity: 0.9;
        }}

        .nav-bar {{
            background: #5c0026;
            padding: 14px 60px;
            display: flex;
            gap: 40px;
        }}

        .nav-bar a {{
            color: white;
            text-decoration: none;
            font-weight: 600;
            letter-spacing: 0.3px;
        }}

        .nav-bar a:hover,
        .nav-bar a.active {{
            color: #ff2b7a;
        }}

        .page-hero {{
            background:
                radial-gradient(circle at 80% 20%, rgba(255,255,255,0.12), transparent 26%),
                linear-gradient(135deg, #70002e, #b00046);
            color: white;
            padding: 58px 70px 105px 70px;
        }}

        .page-hero-grid {{
            max-width: 1500px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 1.3fr 0.7fr;
            gap: 48px;
            align-items: center;
        }}

        .page-hero h1 {{
            font-size: 56px;
            line-height: 1.04;
            margin: 0 0 18px 0;
            letter-spacing: -2px;
        }}

        .page-hero p {{
            font-size: 21px;
            line-height: 1.42;
            margin: 0;
            max-width: 760px;
        }}

        .hero-panel {{
            background: rgba(18, 0, 10, 0.72);
            border-radius: 14px;
            padding: 32px;
            box-shadow: 0 18px 40px rgba(0,0,0,0.25);
        }}

        .hero-panel small {{
            display: block;
            font-size: 14px;
            margin-bottom: 10px;
        }}

        .hero-panel h2 {{
            color: white;
            font-size: 30px;
            margin: 0 0 8px 0;
        }}

        .hero-panel .big {{
            font-size: 58px;
            font-weight: 900;
            margin: 8px 0;
            color: #ff2b7a;
        }}

        .container {{
            max-width: 1500px;
            margin: -58px auto 0 auto;
            padding: 0 28px 44px 28px;
        }}

        .card {{
            background: white;
            border-radius: 10px;
            padding: 24px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 24px;
        }}

        .kpi-value {{
            font-size: 29px;
            font-weight: 900;
            margin-top: 8px;
        }}

        .kpi-label {{
            color: #555;
            font-size: 15px;
        }}

        .kpi-note {{
            color: #777;
            font-size: 12px;
            margin-top: 8px;
        }}

        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 24px;
        }}

        h2 {{
            margin-top: 0;
            font-size: 24px;
        }}

        .sub {{
            margin-top: -8px;
            color: #666;
            font-size: 14px;
            margin-bottom: 20px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}

        th {{
            background: #f0ecee;
            text-align: left;
            padding: 13px 10px;
        }}

        td {{
            padding: 14px 10px;
            border-bottom: 1px solid #eee;
        }}

        tr.highlight td {{
            color: var(--brand);
            font-weight: 900;
        }}

        .interactive-box {{
            background: #faf7f8;
            border: 1px solid #eee;
            border-radius: 12px;
            padding: 24px;
        }}

        label {{
            font-weight: 800;
            display: block;
            margin-bottom: 8px;
        }}

        select,
        input {{
            width: 100%;
            padding: 13px;
            border-radius: 8px;
            border: 1px solid #ddd;
            margin-bottom: 18px;
            font-size: 15px;
        }}

        .result {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-top: 18px;
        }}

        .result-card {{
            background: white;
            border-radius: 10px;
            padding: 18px;
        }}

        .result-card strong {{
            display: block;
            color: var(--brand);
            font-size: 26px;
            margin-top: 6px;
        }}

        .tag {{
            display: inline-block;
            background: #faf7f8;
            border: 1px solid #eee;
            color: var(--brand);
            font-weight: 800;
            padding: 7px 10px;
            border-radius: 999px;
            font-size: 12px;
            margin: 4px 4px 0 0;
        }}

        .footer {{
            background: linear-gradient(90deg, #78002e, #b00046);
            color: white;
            padding: 28px 70px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .footer .logo {{
            font-size: 28px;
            font-weight: 700;
        }}

        .footer .logo span {{
            font-weight: 300;
        }}

        @media (max-width: 1100px) {{
            .page-hero-grid,
            .kpi-grid,
            .grid,
            .result {{
                grid-template-columns: 1fr;
            }}

            .container {{
                margin-top: 20px;
            }}
        }}

        @media (max-width: 900px) {{
            .top-brand {{
                padding: 22px 30px;
            }}

            .page-hero {{
                padding: 46px 30px 70px 30px;
            }}

            .page-hero h1 {{
                font-size: 42px;
            }}

            .page-hero p {{
                font-size: 18px;
            }}

            .nav-bar {{
                padding: 14px 30px;
                gap: 20px;
                flex-wrap: wrap;
            }}

            .footer {{
                padding: 28px 30px;
                flex-direction: column;
                gap: 16px;
                align-items: flex-start;
            }}
        }}
    </style>
</head>

<body>

    <section class="top-brand">
        <div class="brand-name">aalborg<span>portland</span></div>
        <div class="brand-subtitle">CEMENTIR HOLDING</div>
    </section>

    <section class="nav-bar">
        <a href="index.html">Overview</a>
        <a href="advanced.html">Advanced Analytics</a>
        <a href="forecasting.html" class="active">Forecasting</a>
        <a href="economics.html">Economics</a>
    </section>

    <section class="page-hero">
        <div class="page-hero-grid">
            <div>
                <h1>7-day wind<br>generation forecast</h1>
                <p>
                    Estimate the electricity Aalborg Portland could generate over the next 7 days
                    under different turbine models and turbine-count scenarios.
                </p>
            </div>

            <div class="hero-panel">
                <small>Expected 7-day generation</small>
                <h2>{best_scenario["turbine"]}</h2>
                <small>{int(best_scenario["number_of_turbines"])} turbines</small>
                <div class="big">{format_number(best_scenario["forecast_generation_mwh"])}</div>
                <small>MWh in the maximum generation scenario</small>
            </div>
        </div>
    </section>

    <main class="container">

        <section class="kpi-grid">
            <div class="card">
                <div class="kpi-label">Best generation scenario</div>
                <div class="kpi-value">{format_number(best_scenario["forecast_generation_mwh"])} MWh</div>
                <div class="kpi-note">
                    {int(best_scenario["number_of_turbines"])} turbines, {best_scenario["turbine"]}
                </div>
            </div>

            <div class="card">
                <div class="kpi-label">Average scenario coverage</div>
                <div class="kpi-value">{average_coverage:.2f}%</div>
                <div class="kpi-note">Across all turbine and deployment scenarios</div>
            </div>

            <div class="card">
                <div class="kpi-label">Forecast horizon</div>
                <div class="kpi-value">7 days</div>
                <div class="kpi-note">168 hourly forecast observations</div>
            </div>
        </section>

        <section class="card" style="margin-bottom: 24px;">
            <h2>Turbine forecast comparison</h2>
            <div class="sub">
                Expected 7-day generation and demand coverage for one installed turbine.
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Turbine model</th>
                        <th>7-day generation</th>
                        <th>7-day demand coverage</th>
                    </tr>
                </thead>
                <tbody>
                    {turbine_table_rows}
                </tbody>
            </table>
        </section>

        <section class="grid">
            <div class="card">
                <h2>Interactive stakeholder calculator</h2>
                <div class="sub">Estimate 7-day generation, demand coverage and remaining grid dependency</div>

                <div class="interactive-box">
                    <label for="turbineSelect">Turbine model</label>
                    <select id="turbineSelect">
                        {turbine_options}
                    </select>

                    <label for="turbineCount">Number of turbines</label>
                    <input id="turbineCount" type="number" min="1" max="50" value="1">

                    <div class="result">
                        <div class="result-card">
                            <span>Forecast generation</span>
                            <strong id="generationResult">-</strong>
                        </div>

                        <div class="result-card">
                            <span>7-day demand coverage</span>
                            <strong id="coverageResult">-</strong>
                        </div>

                        <div class="result-card">
                            <span>Grid electricity required</span>
                            <strong id="gridResult">-</strong>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>Model comparison</h2>
                <div class="sub">Forecasting models evaluated on historical turbine generation</div>

                <table>
                    <thead>
                        <tr>
                            <th>Model</th>
                            <th>MAE MW</th>
                            <th>RMSE MW</th>
                            <th>R²</th>
                        </tr>
                    </thead>
                    <tbody>
                        {model_rows}
                    </tbody>
                </table>

                <p class="sub" style="margin-top: 18px;">
                    Best model: <strong>{best_model["model"]}</strong>. Model quality is reported separately from
                    the business KPIs to keep the page focused on industrial decision support.
                </p>
            </div>
        </section>

        <section class="grid">
            <div class="card">
                <h2>Academic interpretation</h2>
                <p>
                    The forecasting module transforms the project from a descriptive dashboard into an operational
                    decision-support tool. Instead of only reporting annual generation, stakeholders can estimate
                    expected short-term production under different deployment scenarios.
                </p>
                <span class="tag">Forecasting</span>
                <span class="tag">Decision support</span>
                <span class="tag">Industrial planning</span>
            </div>

            <div class="card">
                <h2>LSTM feasibility</h2>
                <p>
                    LSTM models are widely used for sequential forecasting, but they require heavier dependencies
                    and more careful training. For this lightweight GitHub Actions pipeline, Linear Regression,
                    Random Forest and XGBoost provide a more stable implementation.
                </p>
                <span class="tag">LSTM considered</span>
                <span class="tag">GitHub Actions constraint</span>
                <span class="tag">Future work</span>
            </div>
        </section>

    </main>

    <footer class="footer">
        <div>Aalborg Portland 7-day forecasting and decision-support tool</div>
        <div class="logo">aalborg<span>portland</span></div>
    </footer>

    <script>
        const scenarios = {scenario_json};

        function formatNumber(value) {{
            return Math.round(value).toLocaleString("de-DE");
        }}

        function updateCalculator() {{
            const turbine = document.getElementById("turbineSelect").value;
            const count = Number(document.getElementById("turbineCount").value);

            const oneTurbineScenario = scenarios.find(row =>
                row.turbine === turbine && row.number_of_turbines === 1
            );

            const generation = oneTurbineScenario.forecast_generation_mwh * count;
            const demand = oneTurbineScenario.estimated_7d_demand_mwh;
            const coverage = generation / demand * 100;
            const gridRequired = Math.max(demand - generation, 0);

            document.getElementById("generationResult").textContent =
                formatNumber(generation) + " MWh";

            document.getElementById("coverageResult").textContent =
                coverage.toFixed(2) + "%";

            document.getElementById("gridResult").textContent =
                formatNumber(gridRequired) + " MWh";
        }}

        document.getElementById("turbineSelect").addEventListener("change", updateCalculator);
        document.getElementById("turbineCount").addEventListener("input", updateCalculator);

        updateCalculator();
    </script>

</body>
</html>
    """

    with open("docs/forecasting.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Forecasting dashboard generated successfully")


if __name__ == "__main__":
    main()

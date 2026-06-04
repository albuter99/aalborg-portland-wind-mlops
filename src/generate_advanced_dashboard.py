import pandas as pd


BRAND_COLOR = "#a0003f"
DARK_COLOR = "#2b0014"
ACCENT_COLOR = "#e4005a"
LIGHT_BG = "#f7f5f6"


def format_number(value):
    return f"{value:,.0f}".replace(",", ".")


def main():
    seasonal_df = pd.read_csv("artifacts/seasonal_analysis.csv")
    sensitivity_df = pd.read_csv("artifacts/sensitivity_analysis.csv")

    best_season_row = seasonal_df.sort_values(
        "seasonal_coverage_percent",
        ascending=False
    ).iloc[0]

    best_season = best_season_row["season"]
    best_season_turbine = best_season_row["turbine"]
    best_season_coverage = best_season_row["seasonal_coverage_percent"]

    seasonal_rows = ""
    for _, row in seasonal_df.iterrows():
        highlight = "highlight" if (
            row["season"] == best_season and row["turbine"] == best_season_turbine
        ) else ""

        seasonal_rows += f"""
        <tr class="{highlight}">
            <td>{row["season"]}</td>
            <td>{row["turbine"]}</td>
            <td>{format_number(row["seasonal_generation_mwh"])} MWh</td>
            <td>{row["seasonal_coverage_percent"]:.2f}%</td>
        </tr>
        """

    sensitivity_rows = ""
    for _, row in sensitivity_df.iterrows():
        highlight = "highlight" if "Base" in row["scenario"] else ""

        sensitivity_rows += f"""
        <tr class="{highlight}">
            <td>{row["scenario"]}</td>
            <td>{row["turbine"]}</td>
            <td>{format_number(row["scenario_demand_mwh"])} MWh</td>
            <td>{row["coverage_percent"]:.2f}%</td>
        </tr>
        """

    season_order = ["Winter", "Spring", "Summer", "Autumn"]
    season_summary = (
        seasonal_df
        .groupby("season")["seasonal_coverage_percent"]
        .mean()
        .reindex(season_order)
        .reset_index()
    )

    max_season_coverage = season_summary["seasonal_coverage_percent"].max()

    seasonal_bars = ""
    for _, row in season_summary.iterrows():
        height = max(8, row["seasonal_coverage_percent"] / max_season_coverage * 180)
        seasonal_bars += f"""
        <div class="bar-item">
            <div class="bar-value">{row["seasonal_coverage_percent"]:.2f}%</div>
            <div class="bar" style="height:{height}px;"></div>
            <div class="bar-label">{row["season"]}</div>
        </div>
        """

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Aalborg Portland Advanced Analytics</title>
    <style>
        :root {{
            --brand: {BRAND_COLOR};
            --dark: {DARK_COLOR};
            --accent: {ACCENT_COLOR};
            --light: {LIGHT_BG};
        }}

        * {{ box-sizing: border-box; }}

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

        .brand-name span {{ font-weight: 300; }}

        .brand-subtitle {{
            font-size: 11px;
            letter-spacing: 1.8px;
            margin-top: 2px;
            opacity: 0.9;
        }}

        .nav-bar {{
            background:#5c0026;
            padding:14px 60px;
            display:flex;
            gap:40px;
        }}

        .nav-bar a {{
            color:white;
            text-decoration:none;
            font-weight:600;
            letter-spacing:0.3px;
        }}

        .nav-bar a:hover,
        .nav-bar a.active {{
            color:#ff2b7a;
        }}

        .hero {{
            min-height: 390px;
            padding: 70px 70px 92px 70px;
            color: white;
            background:
                linear-gradient(rgba(92, 0, 38, 0.76), rgba(92, 0, 38, 0.84)),
                url("wind-hero.jpg");
            background-size: cover;
            background-position: center;
            display: grid;
            grid-template-columns: 1.35fr 0.8fr;
            gap: 42px;
            align-items: center;
        }}

        .hero h1 {{
            font-size: 58px;
            line-height: 1.05;
            margin: 0 0 22px 0;
            letter-spacing: -2px;
        }}

        .hero p {{
            font-size: 22px;
            line-height: 1.4;
            margin: 0;
            max-width: 760px;
        }}

        .hero-subtitle {{
            margin-top: 18px !important;
            font-size: 17px !important;
            opacity: 0.9;
            font-weight: 600;
        }}

        .hero-card {{
            background: rgba(18, 0, 10, 0.74);
            border-radius: 12px;
            padding: 34px;
            box-shadow: 0 18px 40px rgba(0,0,0,0.25);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.08);
        }}

        .hero-card small {{
            display: block;
            font-size: 14px;
            margin-bottom: 10px;
        }}

        .hero-card h2 {{
            font-size: 34px;
            margin: 0 0 8px 0;
        }}

        .hero-card .big {{
            font-size: 58px;
            font-weight: 850;
            margin: 10px 0;
            color: #ff2b7a;
        }}

        .container {{
            max-width: 1500px;
            margin: -50px auto 0 auto;
            padding: 0 28px 40px 28px;
        }}

        .card {{
            background: white;
            border-radius: 8px;
            padding: 24px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 24px;
        }}

        .kpi {{
            display: flex;
            gap: 18px;
            align-items: center;
            min-height: 118px;
        }}

        .icon {{
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: var(--brand);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 25px;
            font-weight: bold;
            flex-shrink: 0;
        }}

        .kpi-label {{
            font-size: 15px;
            color: #555;
            margin-bottom: 6px;
        }}

        .kpi-value {{
            font-size: 28px;
            font-weight: 850;
            line-height: 1.05;
            letter-spacing: -0.5px;
        }}

        .kpi-note {{
            font-size: 12px;
            color: #777;
            margin-top: 6px;
        }}

        .advanced-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 24px;
        }}

        .three-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 24px;
            margin-bottom: 24px;
        }}

        h2 {{
            margin-top: 0;
            font-size: 23px;
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
            font-weight: 700;
        }}

        td {{
            padding: 14px 10px;
            border-bottom: 1px solid #eee;
        }}

        tr.highlight td {{
            color: var(--brand);
            font-weight: 800;
        }}

        .bars {{
            height: 250px;
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
            border-left: 1px solid #ddd;
            border-bottom: 1px solid #ddd;
            padding: 0 12px 10px 12px;
        }}

        .bar-item {{
            width: 22%;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-end;
        }}

        .bar {{
            width: 58px;
            background: linear-gradient(180deg, #e4005a, #8b0037);
            border-radius: 6px 6px 0 0;
        }}

        .bar-value {{
            font-weight: 800;
            color: var(--brand);
            margin-bottom: 8px;
            font-size: 14px;
        }}

        .bar-label {{
            font-size: 11px;
            color: #555;
            margin-top: 10px;
            line-height: 1.25;
        }}

        .method-card p,
        .extension-card p,
        .text-card p {{
            color: #555;
            line-height: 1.45;
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

        .footer .logo span {{ font-weight: 300; }}

        @media (max-width: 1100px) {{
            .kpi-grid,
            .advanced-grid,
            .three-grid {{
                grid-template-columns: 1fr;
            }}

            .container {{
                margin-top: 20px;
            }}
        }}

        @media (max-width: 900px) {{
            .hero {{
                grid-template-columns: 1fr;
                padding: 50px 30px;
            }}

            .hero h1 {{
                font-size: 42px;
            }}

            .nav-bar {{
                padding: 14px 30px;
                gap: 20px;
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
        <a href="advanced.html" class="active">Advanced Analytics</a>
        <a href="economics.html">Economics</a>
    </section>

    <section class="hero">
        <div>
            <h1>Advanced wind<br>energy analytics</h1>
            <p>
                Seasonal performance, demand sensitivity and future forecasting scenarios
                for Aalborg Portland.
            </p>
            <p class="hero-subtitle">
                Additional analytical modules built on top of the automated wind-energy pipeline.
            </p>
        </div>

        <div class="hero-card">
            <small>Best seasonal scenario</small>
            <h2>{best_season_turbine}</h2>
            <small>{best_season}</small>
            <div class="big">{best_season_coverage:.2f}%</div>
            <small>seasonal electricity coverage</small>
        </div>
    </section>

    <main class="container">

        <section class="kpi-grid">
            <div class="card kpi">
                <div class="icon">❄</div>
                <div>
                    <div class="kpi-label">Best season</div>
                    <div class="kpi-value">{best_season}</div>
                    <div class="kpi-note">{best_season_turbine}</div>
                </div>
            </div>

            <div class="card kpi">
                <div class="icon">±</div>
                <div>
                    <div class="kpi-label">Demand sensitivity</div>
                    <div class="kpi-value">±10%</div>
                    <div class="kpi-note">Low, base and high demand scenarios</div>
                </div>
            </div>

            <div class="card kpi">
                <div class="icon">▥</div>
                <div>
                    <div class="kpi-label">Generated artifacts</div>
                    <div class="kpi-value">2 CSV</div>
                    <div class="kpi-note">Seasonal and sensitivity outputs</div>
                </div>
            </div>

            <div class="card kpi">
                <div class="icon">↗</div>
                <div>
                    <div class="kpi-label">Forecasting module</div>
                    <div class="kpi-value">Next</div>
                    <div class="kpi-note">7-day forecast and model comparison</div>
                </div>
            </div>
        </section>

        <section class="advanced-grid">
            <div class="card">
                <h2>Seasonal analysis</h2>
                <div class="sub">Estimated turbine performance across winter, spring, summer and autumn</div>

                <table>
                    <thead>
                        <tr>
                            <th>Season</th>
                            <th>Turbine</th>
                            <th>Generation</th>
                            <th>Coverage</th>
                        </tr>
                    </thead>
                    <tbody>
                        {seasonal_rows}
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h2>Seasonal coverage comparison</h2>
                <div class="sub">Average coverage across all turbine models by season</div>

                <div class="bars">
                    {seasonal_bars}
                </div>
            </div>
        </section>

        <section class="advanced-grid">
            <div class="card">
                <h2>Sensitivity analysis</h2>
                <div class="sub">Impact of industrial demand uncertainty on wind-energy coverage</div>

                <table>
                    <thead>
                        <tr>
                            <th>Scenario</th>
                            <th>Turbine</th>
                            <th>Demand</th>
                            <th>Coverage</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sensitivity_rows}
                    </tbody>
                </table>
            </div>

            <div class="card text-card">
                <h2>Scenario robustness</h2>
                <div class="sub">Why sensitivity analysis improves the academic quality of the project</div>

                <p>
                    The demand profile is synthetic because plant-level hourly electricity consumption is not publicly available.
                    Sensitivity analysis tests whether the conclusions remain reasonable under alternative demand assumptions.
                </p>

                <span class="tag">Demand uncertainty</span>
                <span class="tag">Scenario analysis</span>
                <span class="tag">Industrial robustness</span>
                <span class="tag">Decision support</span>
            </div>
        </section>

        <section class="three-grid">
            <div class="card method-card">
                <h2>Methodology extension</h2>
                <p>
                    The advanced analytics page extends the original pipeline from annual coverage estimation
                    to scenario-based industrial energy analysis.
                </p>
                <span class="tag">Seasonality</span>
                <span class="tag">Sensitivity</span>
                <span class="tag">Artifacts</span>
            </div>

            <div class="card extension-card">
                <h2>Future forecasting</h2>
                <p>
                    A future module can use 7-day weather forecasts to estimate expected wind generation
                    and short-term electricity demand coverage.
                </p>
                <span class="tag">7-day forecast</span>
                <span class="tag">Weather prediction</span>
                <span class="tag">Planning</span>
            </div>

            <div class="card extension-card">
                <h2>Model comparison</h2>
                <p>
                    Linear Regression, Random Forest and XGBoost can be compared to evaluate whether
                    machine learning improves generation forecasting.
                </p>
                <span class="tag">Baseline model</span>
                <span class="tag">Random Forest</span>
                <span class="tag">XGBoost</span>
            </div>
        </section>

    </main>

    <footer class="footer">
        <div>Aalborg Portland advanced wind-energy analytics</div>
        <div class="logo">aalborg<span>portland</span></div>
    </footer>

</body>
</html>
    """

    with open("docs/advanced.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Advanced dashboard generated successfully")


if __name__ == "__main__":
    main()

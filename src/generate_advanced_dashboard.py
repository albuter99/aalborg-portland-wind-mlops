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

    best_sensitivity_row = sensitivity_df.sort_values(
        "coverage_percent",
        ascending=False
    ).iloc[0]

    min_sensitivity = sensitivity_df["coverage_percent"].min()
    max_sensitivity = sensitivity_df["coverage_percent"].max()

    season_order = ["Winter", "Spring", "Summer", "Autumn"]

    season_summary = (
        seasonal_df
        .groupby("season")
        .agg(
            average_coverage=("seasonal_coverage_percent", "mean"),
            total_generation=("seasonal_generation_mwh", "sum")
        )
        .reindex(season_order)
        .reset_index()
    )

    best_turbine_seasonal = seasonal_df[
        seasonal_df["turbine"] == best_season_turbine
    ].set_index("season").reindex(season_order).reset_index()

    seasonal_summary_rows = ""
    for _, row in season_summary.iterrows():
        highlight = "highlight" if row["season"] == best_season else ""

        seasonal_summary_rows += f"""
        <tr class="{highlight}">
            <td>{row["season"]}</td>
            <td>{format_number(row["total_generation"])} MWh</td>
            <td>{row["average_coverage"]:.2f}%</td>
        </tr>
        """

    best_turbine_rows = ""
    for _, row in best_turbine_seasonal.iterrows():
        highlight = "highlight" if row["season"] == best_season else ""

        best_turbine_rows += f"""
        <tr class="{highlight}">
            <td>{row["season"]}</td>
            <td>{format_number(row["seasonal_generation_mwh"])} MWh</td>
            <td>{row["seasonal_coverage_percent"]:.2f}%</td>
        </tr>
        """

    max_season_coverage = season_summary["average_coverage"].max()

    seasonal_bars = ""
    for _, row in season_summary.iterrows():
        height = max(10, row["average_coverage"] / max_season_coverage * 190)

        seasonal_bars += f"""
        <div class="bar-item">
            <div class="bar-value">{row["average_coverage"]:.2f}%</div>
            <div class="bar" style="height:{height}px;"></div>
            <div class="bar-label">{row["season"]}</div>
        </div>
        """

    best_turbine_sensitivity = sensitivity_df[
        sensitivity_df["turbine"] == best_season_turbine
    ]

    sensitivity_rows = ""
    sensitivity_bars = ""

    max_sensitivity_for_best = best_turbine_sensitivity["coverage_percent"].max()

    for _, row in best_turbine_sensitivity.iterrows():
        highlight = "highlight" if "Base" in row["scenario"] else ""

        sensitivity_rows += f"""
        <tr class="{highlight}">
            <td>{row["scenario"]}</td>
            <td>{format_number(row["scenario_demand_mwh"])} MWh</td>
            <td>{row["coverage_percent"]:.2f}%</td>
        </tr>
        """

        height = max(10, row["coverage_percent"] / max_sensitivity_for_best * 190)

        sensitivity_bars += f"""
        <div class="bar-item">
            <div class="bar-value">{row["coverage_percent"]:.2f}%</div>
            <div class="bar" style="height:{height}px;"></div>
            <div class="bar-label">{row["scenario"].replace(" ", "<br>")}</div>
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

        .-bar {{
            background:#5c0026;
            padding:14px 60px;
            display:flex;
            gap:40px;
        }}

        .-bar a {{
            color:white;
            text-decoration:none;
            font-weight:600;
            letter-spacing:0.3px;
        }}

        .-bar a:hover,
        .-bar a.active {{
            color:#ff2b7a;
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

        .hero-note {{
            margin-top: 16px !important;
            font-size: 16px !important;
            font-weight: 700;
            opacity: 0.9;
        }}

        .hero-panel {{
            background: rgba(18, 0, 10, 0.72);
            border-radius: 14px;
            padding: 32px;
            box-shadow: 0 18px 40px rgba(0,0,0,0.25);
            border: 1px solid rgba(255,255,255,0.08);
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
            font-size: 29px;
            font-weight: 900;
            line-height: 1.05;
            letter-spacing: -0.5px;
        }}

        .kpi-note {{
            font-size: 12px;
            color: #777;
            margin-top: 6px;
        }}

        .section-title {{
            margin: 34px 0 16px 0;
            display: flex;
            align-items: end;
            justify-content: space-between;
            gap: 20px;
        }}

        .section-title h2 {{
            margin: 0;
            font-size: 28px;
        }}

        .section-title p {{
            margin: 6px 0 0 0;
            color: #666;
            max-width: 780px;
        }}

        .analysis-grid {{
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
            font-weight: 900;
        }}

        .bars {{
            height: 270px;
            display: flex;
            align-items: flex-end;
            justify-content: space-around;
            border-left: 1px solid #ddd;
            border-bottom: 1px solid #ddd;
            padding: 0 12px 12px 12px;
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
            width: 62px;
            background: linear-gradient(180deg, #e4005a, #8b0037);
            border-radius: 7px 7px 0 0;
        }}

        .bar-value {{
            font-weight: 900;
            color: var(--brand);
            margin-bottom: 8px;
            font-size: 15px;
        }}

        .bar-label {{
            font-size: 11px;
            color: #555;
            margin-top: 10px;
            line-height: 1.25;
        }}

        .insight-box {{
            background: #faf7f8;
            border-left: 5px solid var(--brand);
            padding: 18px 20px;
            border-radius: 10px;
            margin-top: 20px;
        }}

        .insight-box strong {{
            color: var(--brand);
        }}

        .module-card {{
            min-height: 215px;
        }}

        .module-card p {{
            color: #555;
            line-height: 1.5;
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

        .status-pill {{
            display: inline-block;
            background: rgba(228,0,90,0.10);
            color: var(--brand);
            font-weight: 900;
            padding: 8px 12px;
            border-radius: 999px;
            font-size: 13px;
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
            .analysis-grid,
            .three-grid {{
                grid-template-columns: 1fr;
            }}

            .container {{
                margin-top: 20px;
            }}
        }}

        @media (max-width: 900px) {{
            .page-hero {{
                padding: 46px 30px 70px 30px;
            }}

            .page-hero h1 {{
                font-size: 42px;
            }}

            .-bar {{
                padding: 14px 30px;
                gap: 20px;
                flex-wrap: wrap;
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
        <a href="forecasting.html">Forecasting</a>
        <a href="economics.html">Economics</a>
    </section>

    <section class="page-hero">
        <div class="page-hero-grid">
            <div>
                <h1>Advanced wind<br>energy analytics</h1>
                <p>
                    Seasonal performance, demand sensitivity and forecasting roadmap
                    for Aalborg Portland's wind-energy self-sufficiency assessment.
                </p>
                <p class="hero-note">
                    This page extends the main dashboard from annual reporting to scenario-based industrial decision support.
                </p>
            </div>

            <div class="hero-panel">
                <small>Best seasonal scenario</small>
                <h2>{best_season_turbine}</h2>
                <small>{best_season}</small>
                <div class="big">{best_season_coverage:.2f}%</div>
                <small>seasonal electricity coverage</small>
            </div>
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
                <div class="icon">↕</div>
                <div>
                    <div class="kpi-label">Coverage range</div>
                    <div class="kpi-value">{min_sensitivity:.2f}% - {max_sensitivity:.2f}%</div>
                    <div class="kpi-note">Across demand sensitivity scenarios</div>
                </div>
            </div>

            <div class="card kpi">
                <div class="icon">±</div>
                <div>
                    <div class="kpi-label">Demand sensitivity</div>
                    <div class="kpi-value">±10%</div>
                    <div class="kpi-note">Low, base and high demand</div>
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

        <div class="section-title">
            <div>
                <h2>Seasonal performance</h2>
                <p>
                    Wind generation is not constant throughout the year. This section compares seasonal production
                    and identifies when on-site wind is most valuable for industrial electricity coverage.
                </p>
            </div>
            <span class="status-pill">Seasonal analysis active</span>
        </div>

        <section class="analysis-grid">
            <div class="card">
                <h2>Season summary</h2>
                <div class="sub">Average coverage across all turbine models</div>

                <table>
                    <thead>
                        <tr>
                            <th>Season</th>
                            <th>Total generation</th>
                            <th>Average coverage</th>
                        </tr>
                    </thead>
                    <tbody>
                        {seasonal_summary_rows}
                    </tbody>
                </table>

                <div class="insight-box">
                    <strong>Interpretation:</strong>
                    Winter shows the strongest seasonal performance, while summer is weaker.
                    This supports the need for seasonal analysis instead of relying only on annual averages.
                </div>
            </div>

            <div class="card">
                <h2>Seasonal coverage comparison</h2>
                <div class="sub">Average coverage by season</div>

                <div class="bars">
                    {seasonal_bars}
                </div>
            </div>
        </section>

        <section class="analysis-grid">
            <div class="card">
                <h2>Best turbine by season</h2>
                <div class="sub">{best_season_turbine} seasonal behaviour</div>

                <table>
                    <thead>
                        <tr>
                            <th>Season</th>
                            <th>Generation</th>
                            <th>Coverage</th>
                        </tr>
                    </thead>
                    <tbody>
                        {best_turbine_rows}
                    </tbody>
                </table>
            </div>

            <div class="card module-card">
                <h2>Why this matters</h2>
                <p>
                    A cement facility operates continuously, but wind generation varies strongly by season.
                    Seasonal analysis helps identify periods where on-site wind generation is more likely to
                    reduce grid dependency and periods where complementary solutions may be required.
                </p>

                <span class="tag">Industrial demand</span>
                <span class="tag">Seasonality</span>
                <span class="tag">Renewable variability</span>
                <span class="tag">Decision support</span>
            </div>
        </section>

        <div class="section-title">
            <div>
                <h2>Demand sensitivity</h2>
                <p>
                    Since the hourly load profile is synthetic, sensitivity analysis tests how robust the conclusions are
                    when industrial electricity demand is lower or higher than the baseline assumption.
                </p>
            </div>
            <span class="status-pill">±10% demand tested</span>
        </div>

        <section class="analysis-grid">
            <div class="card">
                <h2>{best_season_turbine} sensitivity</h2>
                <div class="sub">Coverage under low, base and high demand assumptions</div>

                <table>
                    <thead>
                        <tr>
                            <th>Scenario</th>
                            <th>Demand</th>
                            <th>Coverage</th>
                        </tr>
                    </thead>
                    <tbody>
                        {sensitivity_rows}
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h2>Sensitivity comparison</h2>
                <div class="sub">Coverage variation for the selected turbine</div>

                <div class="bars">
                    {sensitivity_bars}
                </div>
            </div>
        </section>

        <section class="three-grid">
            <div class="card module-card">
                <h2>Methodology value</h2>
                <p>
                    The advanced analytics layer improves the project by moving beyond single annual KPIs
                    and introducing scenario-based assessment.
                </p>
                <span class="tag">Scenario analysis</span>
                <span class="tag">Robustness</span>
                <span class="tag">Academic value</span>
            </div>

            <div class="card module-card">
                <h2>Future forecasting</h2>
                <p>
                    The next extension can use 7-day weather forecasts to estimate short-term wind generation
                    and expected industrial coverage.
                </p>
                <span class="tag">7-day forecast</span>
                <span class="tag">Operational planning</span>
                <span class="tag">Weather API</span>
            </div>

            <div class="card module-card">
                <h2>Model comparison</h2>
                <p>
                    Linear Regression, Random Forest and XGBoost can be compared to assess whether machine learning
                    improves short-term wind generation forecasting.
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

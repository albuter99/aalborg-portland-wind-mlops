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

    min_sensitivity = sensitivity_df["coverage_percent"].min()
    max_sensitivity = sensitivity_df["coverage_percent"].max()

    season_order = ["Winter", "Spring", "Summer", "Autumn"]

    season_summary = (
        seasonal_df
        .groupby("season")
        .agg(
            average_coverage=("seasonal_coverage_percent", "mean"),
            min_coverage=("seasonal_coverage_percent", "min"),
            max_coverage=("seasonal_coverage_percent", "max"),
            std_coverage=("seasonal_coverage_percent", "std"),
            total_generation=("seasonal_generation_mwh", "sum")
        )
        .reindex(season_order)
        .reset_index()
    )

    best_turbine_seasonal = (
        seasonal_df[seasonal_df["turbine"] == best_season_turbine]
        .set_index("season")
        .reindex(season_order)
        .reset_index()
    )

    seasonal_summary_rows = ""
    for _, row in season_summary.iterrows():
        highlight = "highlight" if row["season"] == best_season else ""

        seasonal_summary_rows += f"""
        <tr class="{highlight}">
            <td>{row["season"]}</td>
            <td>{format_number(row["total_generation"])} MWh</td>
            <td>{row["average_coverage"]:.2f}%</td>
            <td>{row["min_coverage"]:.2f}%</td>
            <td>{row["max_coverage"]:.2f}%</td>
            <td>{row["std_coverage"]:.2f}%</td>
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

    seasonal_ranges = ""
    max_range_value = season_summary["max_coverage"].max()

    for _, row in season_summary.iterrows():
        left = row["min_coverage"] / max_range_value * 100
        width = (
            (row["max_coverage"] - row["min_coverage"])
            / max_range_value * 100
        )
        avg_position = row["average_coverage"] / max_range_value * 100

        seasonal_ranges += f"""
        <div class="range-row">
            <div class="range-header">
                <strong>{row["season"]}</strong>
                <span>
                    min {row["min_coverage"]:.2f}% ·
                    avg {row["average_coverage"]:.2f}% ·
                    max {row["max_coverage"]:.2f}%
                </span>
            </div>

            <div class="range-track">
                <div
                    class="range-bar"
                    style="left:{left:.2f}%; width:{width:.2f}%;">
                </div>

                <div
                    class="range-average"
                    style="left:{avg_position:.2f}%;">
                </div>
            </div>
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
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 28px;
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

        .range-card {{
            min-height: 360px;
        }}

        .range-row {{
            margin-bottom: 26px;
        }}

        .range-header {{
            display: flex;
            justify-content: space-between;
            gap: 16px;
            font-size: 13px;
            margin-bottom: 8px;
        }}

        .range-header strong {{
            color: var(--dark);
            font-size: 14px;
        }}

        .range-header span {{
            color: #666;
            text-align: right;
        }}

        .range-track {{
            position: relative;
            height: 17px;
            background: #eee;
            border-radius: 999px;
            overflow: visible;
        }}

        .range-bar {{
            position: absolute;
            top: 0;
            height: 100%;
            background: rgba(228, 0, 90, 0.34);
            border-radius: 999px;
        }}

        .range-average {{
            position: absolute;
            top: -5px;
            width: 5px;
            height: 27px;
            background: #8b0037;
            border-radius: 999px;
            box-shadow: 0 0 0 4px rgba(139, 0, 55, 0.12);
        }}

        .range-legend {{
            display: flex;
            gap: 18px;
            flex-wrap: wrap;
            margin-top: 18px;
            font-size: 12px;
            color: #666;
        }}

        .range-legend span {{
            display: inline-flex;
            align-items: center;
            gap: 7px;
        }}

        .legend-range-box {{
            width: 22px;
            height: 10px;
            background: rgba(228, 0, 90, 0.34);
            border-radius: 999px;
            display: inline-block;
        }}

        .legend-average-box {{
            width: 5px;
            height: 18px;
            background: #8b0037;
            border-radius: 999px;
            display: inline-block;
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
        <a href="advanced.html" class="active">Advanced Analytics</a>
        <a href="forecasting.html">Forecasting</a>
        <a href="economics.html">Economics</a>
    </section>

    <section class="page-hero">
        <div class="page-hero-grid">
            <div>
                <h1>Advanced wind<br>energy analytics</h1>
                <p>
                    Seasonal performance and demand sensitivity analysis for Aalborg Portland's
                    wind-energy self-sufficiency assessment.
                </p>
                <p class="hero-note">
                    This page moves the project beyond annual averages and supports scenario-based industrial planning.
                </p>
            </div>

            <div class="hero-panel">
                <small>Maximum seasonal coverage</small>
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
                    <div class="kpi-label">Demand sensitivity range</div>
                    <div class="kpi-value">{min_sensitivity:.2f}% - {max_sensitivity:.2f}%</div>
                    <div class="kpi-note">Across low, base and high demand scenarios</div>
                </div>
            </div>

            <div class="card kpi">
                <div class="icon">±</div>
                <div>
                    <div class="kpi-label">Demand sensitivity</div>
                    <div class="kpi-value">±10%</div>
                    <div class="kpi-note">Low, base and high demand assumptions</div>
                </div>
            </div>
        </section>

        <div class="section-title">
            <div>
                <h2>Seasonal performance</h2>
                <p>
                    Wind generation is not constant throughout the year. This section compares average seasonal production,
                    the minimum and maximum turbine outcomes, and the uncertainty range across turbine models.
                </p>
            </div>
            <span class="status-pill">Seasonal uncertainty active</span>
        </div>

        <section class="analysis-grid">
            <div class="card">
                <h2>Season summary</h2>
                <div class="sub">Average, minimum, maximum and standard deviation across turbine models</div>

                <table>
                    <thead>
                        <tr>
                            <th>Season</th>
                            <th>Total generation</th>
                            <th>Average</th>
                            <th>Min</th>
                            <th>Max</th>
                            <th>Std</th>
                        </tr>
                    </thead>
                    <tbody>
                        {seasonal_summary_rows}
                    </tbody>
                </table>

                <div class="insight-box">
                    <strong>Interpretation:</strong>
                    The seasonal averages show the central tendency, while the min-max range captures the variation
                    across turbine models. This makes the seasonal analysis more transparent than reporting averages alone.
                </div>
            </div>

            <div class="card range-card">
                <h2>Seasonal uncertainty range</h2>
                <div class="sub">Minimum, average and maximum coverage by season</div>

                {seasonal_ranges}

                <div class="range-legend">
                    <span><i class="legend-range-box"></i>Min-max range</span>
                    <span><i class="legend-average-box"></i>Average coverage</span>
                </div>
            </div>
        </section>

        <section class="analysis-grid">
            <div class="card">
                <h2>Seasonal coverage comparison</h2>
                <div class="sub">Average seasonal coverage across turbine models</div>

                <div class="bars">
                    {seasonal_bars}
                </div>
            </div>

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
        </section>

        <section class="analysis-grid">
            <div class="card module-card">
                <h2>Why this matters</h2>
                <p>
                    A cement facility operates continuously, but wind generation varies strongly by season.
                    Adding minimum, average and maximum seasonal coverage makes the analysis more robust and
                    shows how dependent the conclusions are on turbine selection.
                </p>

                <span class="tag">Industrial demand</span>
                <span class="tag">Seasonality</span>
                <span class="tag">Uncertainty</span>
                <span class="tag">Decision support</span>
            </div>

            <div class="card module-card">
                <h2>Robustness interpretation</h2>
                <p>
                    The range chart should be read as a model-comparison interval. A narrow range means turbine models
                    behave similarly during that season, while a wider range indicates stronger turbine-specific variation.
                </p>

                <span class="tag">Min-max range</span>
                <span class="tag">Average coverage</span>
                <span class="tag">Model comparison</span>
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
                    and introducing seasonal uncertainty, sensitivity testing and scenario-based assessment.
                </p>
                <span class="tag">Scenario analysis</span>
                <span class="tag">Robustness</span>
                <span class="tag">Academic value</span>
            </div>

            <div class="card module-card">
                <h2>Forecasting connection</h2>
                <p>
                    The seasonal and sensitivity results provide context for the forecasting module,
                    where short-term wind generation is estimated using weather forecasts and physical power curves.
                </p>
                <span class="tag">7-day forecast</span>
                <span class="tag">Operational planning</span>
                <span class="tag">Weather API</span>
            </div>

            <div class="card module-card">
                <h2>Decision-support role</h2>
                <p>
                    The analysis helps stakeholders understand when wind generation performs best,
                    how sensitive the conclusions are to demand assumptions, and where additional energy planning is needed.
                </p>
                <span class="tag">Industrial planning</span>
                <span class="tag">Risk awareness</span>
                <span class="tag">Grid dependency</span>
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

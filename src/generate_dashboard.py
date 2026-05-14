import pandas as pd


BRAND_COLOR = "#a0003f"
DARK_COLOR = "#2b0014"
ACCENT_COLOR = "#e4005a"
LIGHT_BG = "#f7f5f6"


def format_number(value):
    return f"{value:,.0f}".replace(",", ".")


def main():
    summary_df = pd.read_csv("artifacts/turbine_summary.csv")
    simulation_df = pd.read_csv("data/turbine_simulation_results.csv")

    simulation_df["time"] = pd.to_datetime(simulation_df["time"])

    best = summary_df.sort_values(
        "coverage_ratio_percent",
        ascending=False
    ).iloc[0]

    annual_demand_mwh = simulation_df["demand_mw"].sum()
    best_turbine = best["turbine"]
    best_generation = best["annual_generation_mwh"]
    best_coverage = best["coverage_ratio_percent"]

    best_generation_col = best_turbine + " generation_mw"

    table_rows = ""
    bar_items = ""
    chart_points = ""

    max_coverage = summary_df["coverage_ratio_percent"].max()

    for _, row in summary_df.iterrows():
        turbine = row["turbine"]
        coverage = row["coverage_ratio_percent"]
        generation = row["annual_generation_mwh"]
        capacity = row["capacity_factor_percent"]
        surplus = row["surplus_hours"]

        highlight = "highlight" if turbine == best_turbine else ""

        table_rows += f"""
        <tr class="{highlight}">
            <td>{turbine}</td>
            <td>{format_number(generation)} MWh</td>
            <td>{coverage:.1f}%</td>
            <td>{capacity:.1f}%</td>
            <td>{surplus}</td>
        </tr>
        """

        height = max(8, (coverage / max_coverage) * 170)

        bar_items += f"""
        <div class="bar-item">
            <div class="bar-value">{coverage:.1f}%</div>
            <div class="bar" style="height:{height}px;"></div>
            <div class="bar-label">{turbine.replace(" ", "<br>")}</div>
        </div>
        """

    chart_df = simulation_df.head(24 * 14).copy()
    max_value = max(
        chart_df["demand_mw"].max(),
        chart_df[best_generation_col].max(),
        1
    )

    for i, row in chart_df.iterrows():
        x = (i / (len(chart_df) - 1)) * 100
        demand_y = 100 - ((row["demand_mw"] / max_value) * 100)
        generation_y = 100 - ((row[best_generation_col] / max_value) * 100)

        chart_points += f"""
        <circle class="demand-point" cx="{x:.2f}%" cy="{demand_y:.2f}%" r="1.2"></circle>
        <circle class="generation-point" cx="{x:.2f}%" cy="{generation_y:.2f}%" r="1.2"></circle>
        """

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Aalborg Portland Wind Energy Dashboard</title>
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
            max-width: 720px;
        }}

        .hero-subtitle {{
            margin-top: 18px !important;
            font-size: 17px !important;
            opacity: 0.9;
            max-width: 760px;
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
            font-size: 68px;
            font-weight: 850;
            margin: 10px 0;
            color: #ff2b7a;
        }}

        .container {{
            max-width: 1500px;
            margin: -50px auto 0 auto;
            padding: 0 28px 40px 28px;
        }}

        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 24px;
        }}

        .card {{
            background: white;
            border-radius: 8px;
            padding: 24px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
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
            margin-top: 4px;
        }}

        .kpi-note {{
            font-size: 12px;
            color: #777;
            margin-top: 6px;
        }}

        .main-grid {{
            display: grid;
            grid-template-columns: 1.35fr 0.85fr 1.1fr;
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

        .time-chart {{
            height: 250px;
            border-left: 1px solid #ddd;
            border-bottom: 1px solid #ddd;
            position: relative;
            background:
                linear-gradient(to top, rgba(0,0,0,0.05) 1px, transparent 1px);
            background-size: 100% 50px;
        }}

        .time-chart svg {{
            width: 100%;
            height: 100%;
            overflow: visible;
        }}

        .demand-point {{
            fill: var(--brand);
            opacity: 0.9;
        }}

        .generation-point {{
            fill: #9a9a9a;
            opacity: 0.65;
        }}

        .legend {{
            display: flex;
            gap: 16px;
            font-size: 12px;
            margin-bottom: 14px;
            color: #555;
        }}

        .legend span::before {{
            content: "";
            display: inline-block;
            width: 18px;
            height: 3px;
            margin-right: 6px;
            vertical-align: middle;
            background: var(--brand);
        }}

        .legend .generation::before {{
            background: #9a9a9a;
        }}

        .pipeline-card {{
            margin-bottom: 24px;
        }}

        .pipeline-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
        }}

        .pipeline-step {{
            background: #faf7f8;
            border: 1px solid #eee;
            border-radius: 10px;
            padding: 18px;
        }}

        .pipeline-step strong {{
            display: block;
            font-size: 15px;
            margin: 10px 0 6px 0;
        }}

        .pipeline-step p {{
            margin: 0;
            color: var(--brand);
            font-weight: 800;
        }}

        .status-dot {{
            width: 13px;
            height: 13px;
            background: #1fa463;
            border-radius: 50%;
            display: inline-block;
            box-shadow: 0 0 0 5px rgba(31,164,99,0.12);
        }}

        .status-dot.automated {{
            background: var(--accent);
            box-shadow: 0 0 0 5px rgba(228,0,90,0.12);
        }}

        .info-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 24px;
        }}

        .info-card {{
            display: flex;
            gap: 18px;
            align-items: flex-start;
            min-height: 140px;
        }}

        .outline-icon {{
            width: 58px;
            height: 58px;
            border-radius: 50%;
            border: 2px solid var(--brand);
            color: var(--brand);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 26px;
            flex-shrink: 0;
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
            .kpi-grid,
            .main-grid,
            .pipeline-grid,
            .info-grid {{
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
        }}
    </style>
</head>
<body>

    <section class="top-brand">
        <div class="brand-name">aalborg<span>portland</span></div>
        <div class="brand-subtitle">CEMENTIR HOLDING</div>
    </section>

    <section class="hero">
        <div>
            <h1>Wind energy for<br>Aalborg Portland</h1>
            <p>
                How much of Aalborg Portland's electricity demand could be supplied
                by individual wind turbine scenarios?
            </p>
            <p class="hero-subtitle">
                Wind-energy self-sufficiency estimation using real weather data
                and synthetic industrial demand modelling.
            </p>
        </div>

        <div class="hero-card">
            <small>Single-turbine contribution</small>
            <h2>{best_turbine}</h2>
            <small>can supply up to</small>
            <div class="big">{best_coverage:.1f}%</div>
            <small>of annual electricity demand</small>
        </div>
    </section>

    <main class="container">

        <section class="kpi-grid">
            <div class="card kpi">
                <div class="icon">⚡</div>
                <div>
                    <div class="kpi-label">Annual electricity demand</div>
                    <div class="kpi-value">{format_number(annual_demand_mwh)} MWh</div>
                    <div class="kpi-note">Synthetic hourly profile calibrated to public annual data</div>
                </div>
            </div>

            <div class="card kpi">
                <div class="icon">≈</div>
                <div>
                    <div class="kpi-label">Single-turbine contribution</div>
                    <div class="kpi-value">{best_coverage:.1f}%</div>
                    <div class="kpi-note">{best_turbine}</div>
                </div>
            </div>

            <div class="card kpi">
                <div class="icon">▥</div>
                <div>
                    <div class="kpi-label">Annual generation</div>
                    <div class="kpi-value">{format_number(best_generation)} MWh</div>
                    <div class="kpi-note">Best turbine scenario</div>
                </div>
            </div>

            <div class="card kpi">
                <div class="icon">◷</div>
                <div>
                    <div class="kpi-label">Analysis period</div>
                    <div class="kpi-value">2025</div>
                    <div class="kpi-note">8760 hourly observations</div>
                </div>
            </div>
        </section>

        <section class="main-grid">
            <div class="card">
                <h2>Turbine comparison</h2>
                <div class="sub">Annual production, demand coverage and operating indicators</div>
                <table>
                    <thead>
                        <tr>
                            <th>Turbine</th>
                            <th>Annual production</th>
                            <th>Coverage</th>
                            <th>Capacity factor</th>
                            <th>Surplus hours</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>

            <div class="card">
                <h2>Coverage comparison</h2>
                <div class="sub">Share of annual electricity demand covered by each turbine</div>
                <div class="bars">
                    {bar_items}
                </div>
            </div>

            <div class="card">
                <h2>Demand vs wind generation</h2>
                <div class="sub">Hourly comparison for the first 14 days of 2025</div>
                <div class="legend">
                    <span>Demand MW</span>
                    <span class="generation">{best_turbine} MW</span>
                </div>
                <div class="time-chart">
                    <svg>
                        {chart_points}
                    </svg>
                </div>
            </div>
        </section>

        <section class="card pipeline-card">
            <h2>Pipeline status</h2>
            <div class="sub">Automated MLOps workflow generated through GitHub Actions</div>

            <div class="pipeline-grid">
                <div class="pipeline-step">
                    <span class="status-dot"></span>
                    <strong>Weather API</strong>
                    <p>Active</p>
                </div>

                <div class="pipeline-step">
                    <span class="status-dot"></span>
                    <strong>Demand modelling</strong>
                    <p>Active</p>
                </div>

                <div class="pipeline-step">
                    <span class="status-dot"></span>
                    <strong>Turbine simulation</strong>
                    <p>Active</p>
                </div>

                <div class="pipeline-step">
                    <span class="status-dot"></span>
                    <strong>Dashboard generation</strong>
                    <p>Active</p>
                </div>

                <div class="pipeline-step">
                    <span class="status-dot automated"></span>
                    <strong>GitHub Actions</strong>
                    <p>Automated</p>
                </div>
            </div>
        </section>

        <section class="info-grid">
            <div class="card info-card">
                <div class="outline-icon">▤</div>
                <div>
                    <h2>About the analysis</h2>
                    <p>
                        This dashboard estimates physical on-site electricity coverage using
                        real hourly wind data and a synthetic industrial demand profile.
                    </p>
                </div>
            </div>

            <div class="card info-card">
                <div class="outline-icon">◌</div>
                <div>
                    <h2>Method</h2>
                    <p>
                        The hourly demand profile is synthetic, but calibrated to Aalborg
                        Portland's publicly reported annual electricity consumption.
                    </p>
                </div>
            </div>

            <div class="card info-card">
                <div class="outline-icon">↓</div>
                <div>
                    <h2>Data product</h2>
                    <p>
                        The page is generated automatically from pipeline outputs and published
                        as a static GitHub Pages dashboard.
                    </p>
                </div>
            </div>
        </section>

    </main>

    <footer class="footer">
        <div>Aalborg Portland wind-energy self-sufficiency analysis</div>
        <div class="logo">aalborg<span>portland</span></div>
    </footer>

</body>
</html>
    """

    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Branded dashboard generated successfully")


if __name__ == "__main__":
    main()

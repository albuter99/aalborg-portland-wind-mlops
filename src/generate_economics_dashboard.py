import pandas as pd


BRAND_COLOR = "#a0003f"
DARK_COLOR = "#2b0014"
ACCENT_COLOR = "#e4005a"
LIGHT_BG = "#f7f5f6"


ELECTRICITY_PRICE_DKK_PER_MWH = 1470
FIXED_INFRASTRUCTURE_COST_DKK = 15_000_000
OPEX_PERCENT_OF_CAPEX = 0.025
PROJECT_LIFETIME_YEARS = 20


TURBINE_CAPEX_DKK = {
    "Vestas V136 4.5 MW": 42_000_000,
    "Siemens Gamesa SG 5.0-145": 47_000_000,
    "Nordex N149 5.X": 52_000_000,
    "Enercon E-138 EP3": 40_000_000
}


def format_number(value):
    return f"{value:,.0f}".replace(",", ".")


def calculate_lcoe(total_capex, annual_opex, annual_generation_mwh):
    lifetime_cost = total_capex + annual_opex * PROJECT_LIFETIME_YEARS
    lifetime_generation = annual_generation_mwh * PROJECT_LIFETIME_YEARS

    if lifetime_generation <= 0:
        return 0

    return lifetime_cost / lifetime_generation


def main():
    summary_df = pd.read_csv("artifacts/turbine_summary.csv")
    simulation_df = pd.read_csv("data/turbine_simulation_results.csv")

    annual_demand_mwh = simulation_df["demand_mw"].sum()

    economics_rows = []

    for _, row in summary_df.iterrows():
        turbine = row["turbine"]
        annual_generation_one_turbine = row["annual_generation_mwh"]

        for turbine_count in [1, 3, 5, 10]:
            annual_generation = annual_generation_one_turbine * turbine_count
            coverage = annual_generation / annual_demand_mwh * 100
            grid_required = max(annual_demand_mwh - annual_generation, 0)

            turbine_capex = TURBINE_CAPEX_DKK[turbine] * turbine_count
            total_capex = turbine_capex + FIXED_INFRASTRUCTURE_COST_DKK
            annual_opex = turbine_capex * OPEX_PERCENT_OF_CAPEX

            annual_savings = annual_generation * ELECTRICITY_PRICE_DKK_PER_MWH
            net_annual_savings = annual_savings - annual_opex

            if net_annual_savings > 0:
                payback = total_capex / net_annual_savings
            else:
                payback = 0

            lcoe = calculate_lcoe(
                total_capex=total_capex,
                annual_opex=annual_opex,
                annual_generation_mwh=annual_generation
            )

            economics_rows.append({
                "turbine": turbine,
                "number_of_turbines": turbine_count,
                "annual_generation_mwh": round(annual_generation, 2),
                "annual_demand_mwh": round(annual_demand_mwh, 2),
                "coverage_percent": round(coverage, 2),
                "grid_required_mwh": round(grid_required, 2),
                "total_capex_dkk": round(total_capex, 2),
                "annual_opex_dkk": round(annual_opex, 2),
                "annual_savings_dkk": round(annual_savings, 2),
                "net_annual_savings_dkk": round(net_annual_savings, 2),
                "payback_years": round(payback, 2),
                "lcoe_dkk_per_mwh": round(lcoe, 2)
            })

    economics_df = pd.DataFrame(economics_rows)
    economics_df.to_csv("artifacts/economics_scenarios.csv", index=False)

    best_payback = economics_df[
        economics_df["net_annual_savings_dkk"] > 0
    ].sort_values("payback_years").iloc[0]

    scenario_rows = ""
    for _, row in economics_df[
        economics_df["number_of_turbines"].isin([1, 3, 5, 10])
    ].iterrows():
        highlight = "highlight" if (
            row["turbine"] == best_payback["turbine"]
            and row["number_of_turbines"] == best_payback["number_of_turbines"]
        ) else ""

        scenario_rows += f"""
        <tr class="{highlight}">
            <td>{row["turbine"]}</td>
            <td>{int(row["number_of_turbines"])}</td>
            <td>{format_number(row["annual_generation_mwh"])} MWh</td>
            <td>{row["coverage_percent"]:.2f}%</td>
            <td>{format_number(row["total_capex_dkk"])} DKK</td>
            <td>{row["payback_years"]:.2f} years</td>
            <td>{format_number(row["lcoe_dkk_per_mwh"])} DKK/MWh</td>
        </tr>
        """

    turbine_options = ""
    for turbine in summary_df["turbine"].unique():
        turbine_options += f'<option value="{turbine}">{turbine}</option>'

    economics_json = economics_df.to_json(orient="records")

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Aalborg Portland Economics</title>

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
            margin-top: 18px !important;
            font-size: 16px !important;
            font-weight: 700;
            opacity: 0.9;
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
            font-size: 24px;
            margin: 18px 0 8px 0;
            line-height: 1.25;
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

        .kpi-value {{
            font-size: 28px;
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
            grid-template-columns: 0.95fr 1.05fr;
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

        .planner-box {{
            background: #faf7f8;
            border: 1px solid #eee;
            border-radius: 12px;
            padding: 24px;
        }}

        .planner-results {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 14px;
            margin-top: 18px;
        }}

        .result-card {{
            background: white;
            border-radius: 10px;
            padding: 16px;
        }}

        .result-card span {{
            color: #555;
            font-size: 13px;
        }}

        .result-card strong {{
            display: block;
            color: var(--brand);
            font-size: 24px;
            margin-top: 6px;
        }}

        .chart-box {{
            background: #faf7f8;
            border-radius: 12px;
            padding: 22px;
            border: 1px solid #eee;
            min-height: 420px;
        }}

        .savings-row {{
            margin-bottom: 20px;
        }}

        .savings-header {{
            display: flex;
            justify-content: space-between;
            gap: 16px;
            font-size: 13px;
            margin-bottom: 7px;
        }}

        .bar-track {{
            height: 18px;
            background: #eee;
            border-radius: 999px;
            overflow: hidden;
        }}

        .bar-fill {{
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #8b0037, #e4005a);
            border-radius: 999px;
            transition: width 0.25s ease;
        }}

        .method-note {{
            background: #faf7f8;
            border-left: 5px solid var(--brand);
            padding: 18px 20px;
            border-radius: 10px;
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
            .planner-results {{
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
        <a href="forecasting.html">Forecasting</a>
        <a href="economics.html" class="active">Economics</a>
    </section>

    <section class="page-hero">
        <div class="page-hero-grid">
            <div>
                <h1>Wind deployment<br>economics</h1>
                <p>
                    Translate turbine generation, demand coverage and grid dependency into
                    financial decision-support indicators.
                </p>
                <p class="hero-note">
                    Economics completes the dashboard story: technical feasibility, forecasting and financial viability.
                </p>
            </div>

            <div class="hero-panel">
                <small>Fastest payback scenario</small>
                <h2>{best_payback["turbine"]}</h2>
                <small>{int(best_payback["number_of_turbines"])} turbines</small>
                <div class="big">{best_payback["payback_years"]:.1f}</div>
                <small>years estimated payback</small>
            </div>
        </div>
    </section>

    <main class="container">

        <section class="kpi-grid">
            <div class="card">
                <div class="kpi-label">Electricity price assumption</div>
                <div class="kpi-value">{format_number(ELECTRICITY_PRICE_DKK_PER_MWH)} DKK/MWh</div>
                <div class="kpi-note">Based on invoice variable electricity price proxy</div>
            </div>

            <div class="card">
                <div class="kpi-label">Fixed infrastructure cost</div>
                <div class="kpi-value">{format_number(FIXED_INFRASTRUCTURE_COST_DKK)} DKK</div>
                <div class="kpi-note">Transformer, connection and integration proxy</div>
            </div>

            <div class="card">
                <div class="kpi-label">OPEX assumption</div>
                <div class="kpi-value">{OPEX_PERCENT_OF_CAPEX * 100:.1f}%</div>
                <div class="kpi-note">Annual share of turbine CAPEX</div>
            </div>

            <div class="card">
                <div class="kpi-label">Project lifetime</div>
                <div class="kpi-value">{PROJECT_LIFETIME_YEARS} years</div>
                <div class="kpi-note">Used for LCOE calculation</div>
            </div>
        </section>

        <section class="grid">
            <div class="card">
                <h2>Interactive deployment planner</h2>
                <div class="sub">
                    Select turbine model and deployment size to estimate energy and economic outcomes.
                </div>

                <div class="planner-box">
                    <label for="turbineSelect">Turbine model</label>
                    <select id="turbineSelect">
                        {turbine_options}
                    </select>

                    <label for="turbineCount">Number of turbines</label>
                    <input id="turbineCount" type="number" min="1" max="20" value="1">

                    <div class="planner-results">
                        <div class="result-card">
                            <span>Annual generation</span>
                            <strong id="generationResult">-</strong>
                        </div>

                        <div class="result-card">
                            <span>Demand coverage</span>
                            <strong id="coverageResult">-</strong>
                        </div>

                        <div class="result-card">
                            <span>Grid dependency</span>
                            <strong id="gridResult">-</strong>
                        </div>

                        <div class="result-card">
                            <span>Total CAPEX</span>
                            <strong id="capexResult">-</strong>
                        </div>

                        <div class="result-card">
                            <span>Annual net savings</span>
                            <strong id="savingsResult">-</strong>
                        </div>

                        <div class="result-card">
                            <span>Payback period</span>
                            <strong id="paybackResult">-</strong>
                        </div>

                        <div class="result-card">
                            <span>LCOE</span>
                            <strong id="lcoeResult">-</strong>
                        </div>

                        <div class="result-card">
                            <span>Cost per covered MWh</span>
                            <strong id="costCoveredResult">-</strong>
                        </div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>Savings versus investment</h2>
                <div class="sub">
                    Visual comparison of CAPEX and estimated annual net savings for the selected deployment.
                </div>

                <div class="chart-box" id="savingsChart"></div>
            </div>
        </section>

        <section class="card" style="margin-bottom: 24px;">
            <h2>Scenario comparison</h2>
            <div class="sub">
                Standard deployment sizes for comparison across turbine models.
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Turbine</th>
                        <th>Units</th>
                        <th>Annual generation</th>
                        <th>Coverage</th>
                        <th>CAPEX</th>
                        <th>Payback</th>
                        <th>LCOE</th>
                    </tr>
                </thead>
                <tbody>
                    {scenario_rows}
                </tbody>
            </table>
        </section>

        <section class="grid">
            <div class="card">
                <h2>Economic methodology</h2>
                <div class="method-note">
                    The model estimates avoided electricity purchases by multiplying annual wind generation by
                    the assumed electricity price. CAPEX includes turbine investment plus a fixed infrastructure
                    proxy for grid connection, transformer and integration. OPEX is modelled as a fixed annual
                    percentage of turbine CAPEX.
                </div>
            </div>

            <div class="card">
                <h2>Decision-support value</h2>
                <p>
                    This page converts the project from a descriptive energy assessment into an interactive
                    deployment planner. Stakeholders can compare turbine choices, deployment sizes, grid dependency,
                    payback and LCOE under transparent assumptions.
                </p>
                <span class="tag">CAPEX</span>
                <span class="tag">Payback</span>
                <span class="tag">LCOE</span>
                <span class="tag">Decision support</span>
            </div>
        </section>

    </main>

    <footer class="footer">
        <div>Aalborg Portland wind deployment economics</div>
        <div class="logo">aalborg<span>portland</span></div>
    </footer>

    <script>
        const economicsScenarios = {economics_json};

        function formatNumber(value) {{
            return Math.round(value).toLocaleString("de-DE");
        }}

        function getOneTurbineScenario(turbine) {{
            return economicsScenarios.find(row =>
                row.turbine === turbine && row.number_of_turbines === 1
            );
        }}

        function updatePlanner() {{
            const turbine = document.getElementById("turbineSelect").value;
            const count = Number(document.getElementById("turbineCount").value) || 1;

            const oneTurbineScenario = getOneTurbineScenario(turbine);

            const annualGeneration = oneTurbineScenario.annual_generation_mwh * count;
            const annualDemand = oneTurbineScenario.annual_demand_mwh;
            const coverage = annualGeneration / annualDemand * 100;
            const gridRequired = Math.max(annualDemand - annualGeneration, 0);

            const turbineCapexPerUnit = (
                (oneTurbineScenario.total_capex_dkk - {FIXED_INFRASTRUCTURE_COST_DKK})
                / oneTurbineScenario.number_of_turbines
            );

            const turbineCapex = turbineCapexPerUnit * count;
            const totalCapex = turbineCapex + {FIXED_INFRASTRUCTURE_COST_DKK};
            const annualOpex = turbineCapex * {OPEX_PERCENT_OF_CAPEX};
            const annualSavings = annualGeneration * {ELECTRICITY_PRICE_DKK_PER_MWH};
            const netAnnualSavings = annualSavings - annualOpex;

            const payback = netAnnualSavings > 0
                ? totalCapex / netAnnualSavings
                : 0;

            const lcoe = annualGeneration > 0
                ? (totalCapex + annualOpex * {PROJECT_LIFETIME_YEARS}) /
                  (annualGeneration * {PROJECT_LIFETIME_YEARS})
                : 0;

            const costPerCoveredMwh = annualGeneration > 0
                ? totalCapex / annualGeneration
                : 0;

            document.getElementById("generationResult").textContent =
                formatNumber(annualGeneration) + " MWh";

            document.getElementById("coverageResult").textContent =
                coverage.toFixed(2) + "%";

            document.getElementById("gridResult").textContent =
                formatNumber(gridRequired) + " MWh";

            document.getElementById("capexResult").textContent =
                formatNumber(totalCapex) + " DKK";

            document.getElementById("savingsResult").textContent =
                formatNumber(netAnnualSavings) + " DKK";

            document.getElementById("paybackResult").textContent =
                payback.toFixed(2) + " years";

            document.getElementById("lcoeResult").textContent =
                formatNumber(lcoe) + " DKK/MWh";

            document.getElementById("costCoveredResult").textContent =
                formatNumber(costPerCoveredMwh) + " DKK/MWh";

            updateSavingsChart(totalCapex, netAnnualSavings, annualSavings, annualOpex);
        }}

        function updateSavingsChart(totalCapex, netAnnualSavings, annualSavings, annualOpex) {{
            const chart = document.getElementById("savingsChart");

            const maxValue = Math.max(totalCapex, annualSavings, annualOpex, Math.abs(netAnnualSavings), 1);

            const items = [
                ["Total CAPEX", totalCapex],
                ["Annual gross savings", annualSavings],
                ["Annual OPEX", annualOpex],
                ["Annual net savings", netAnnualSavings]
            ];

            let html = "";

            items.forEach(item => {{
                const label = item[0];
                const value = item[1];
                const width = Math.max(Math.abs(value) / maxValue * 100, 2);

                html += `
                    <div class="savings-row">
                        <div class="savings-header">
                            <strong>${{label}}</strong>
                            <span>${{formatNumber(value)}} DKK</span>
                        </div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width:${{width}}%;"></div>
                        </div>
                    </div>
                `;
            }});

            chart.innerHTML = html;
        }}

        document.getElementById("turbineSelect").addEventListener("change", updatePlanner);
        document.getElementById("turbineCount").addEventListener("input", updatePlanner);

        updatePlanner();
    </script>

</body>
</html>
    """

    with open("docs/economics.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Economics dashboard generated successfully")


if __name__ == "__main__":
    main()

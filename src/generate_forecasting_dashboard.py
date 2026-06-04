import pandas as pd


BRAND_COLOR = "#a0003f"
ACCENT_COLOR = "#e4005a"
LIGHT_BG = "#f7f5f6"


def format_number(value):
    return f"{value:,.0f}".replace(",", ".")


def main():
    model_df = pd.read_csv("artifacts/forecast_model_comparison.csv")
    scenario_df = pd.read_csv("artifacts/forecast_stakeholder_scenarios.csv")
    hourly_df = pd.read_csv("artifacts/forecast_hourly_profile.csv")

    hourly_df["timestamp"] = pd.to_datetime(hourly_df["timestamp"])
    hourly_df["label"] = hourly_df["timestamp"].dt.strftime("%d %b %H:%M")

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

    turbine_table_rows = ""
    turbine_mix_inputs = ""

    for turbine in scenario_df["turbine"].unique():
        one_turbine = scenario_df[
            (scenario_df["turbine"] == turbine)
            & (scenario_df["number_of_turbines"] == 1)
        ].iloc[0]

        safe_id = (
            turbine
            .replace(" ", "_")
            .replace(".", "")
            .replace("-", "_")
            .replace("/", "_")
        )

        turbine_table_rows += f"""
        <tr>
            <td><strong>{turbine}</strong></td>
            <td>{format_number(one_turbine["forecast_generation_mwh"])} MWh</td>
            <td>{one_turbine["coverage_percent"]:.2f}%</td>
        </tr>
        """

        turbine_mix_inputs += f"""
        <div class="mix-row">
            <div>
                <label for="{safe_id}">{turbine}</label>
                <small>{format_number(one_turbine["forecast_generation_mwh"])} MWh per turbine</small>
            </div>
            <input
                id="{safe_id}"
                class="turbine-count"
                type="number"
                min="0"
                max="50"
                value="0"
                data-turbine="{turbine}"
            >
        </div>
        """

    scenario_json = scenario_df.to_json(orient="records")
    hourly_profile_json = hourly_df[
        [
            "label",
            "forecast_generation_mwh",
            "estimated_demand_mwh",
            "grid_required_mwh"
        ]
    ].to_json(orient="records")

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Aalborg Portland Forecasting</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

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
            margin-bottom: 4px;
        }}

        select,
        input {{
            width: 100%;
            padding: 13px;
            border-radius: 8px;
            border: 1px solid #ddd;
            font-size: 15px;
        }}

        .mix-row {{
            display: grid;
            grid-template-columns: 1fr 110px;
            gap: 18px;
            align-items: center;
            margin-bottom: 16px;
        }}

        .mix-row small {{
            color: #777;
            font-size: 12px;
        }}

        .result {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-top: 22px;
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

        .chart-box {{
            background: #faf7f8;
            border-radius: 12px;
            padding: 22px;
            border: 1px solid #eee;
            min-height: 365px;
        }}

        .line-chart-wrapper {{
            height: 420px;
            background: #faf7f8;
            border: 1px solid #eee;
            border-radius: 12px;
            padding: 20px;
        }}

        .bar-row {{
            margin-bottom: 18px;
        }}

        .bar-row-header {{
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

        .placeholder-chart {{
            height: 250px;
            border-left: 1px solid #ddd;
            border-bottom: 1px solid #ddd;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #777;
            text-align: center;
            padding: 24px;
            background:
                linear-gradient(to right, rgba(160,0,63,0.06) 1px, transparent 1px),
                linear-gradient(to bottom, rgba(160,0,63,0.06) 1px, transparent 1px);
            background-size: 42px 42px;
            border-radius: 10px;
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

            .mix-row {{
                grid-template-columns: 1fr;
                gap: 8px;
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
                    under different turbine deployment scenarios.
                </p>
                <p class="hero-note">
                    Forecast generated using {best_model["model"]} and translated into industrial energy-planning indicators.
                </p>
            </div>

            <div class="hero-panel">
                <small>Expected 7-day generation</small>
                <div class="big">{format_number(best_scenario["forecast_generation_mwh"])}</div>
                <small>MWh under the maximum generation scenario</small>

                <h2>Forecast generated using {best_model["model"]}</h2>
                <small>
                    Model quality is reported below, but the main dashboard focuses on energy planning,
                    demand coverage and grid dependency.
                </small>
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
            <h2>7-day forecast profile</h2>
            <div class="sub">
                Hourly wind generation forecast compared with estimated industrial electricity demand.
            </div>

            <div class="line-chart-wrapper">
                <canvas id="forecastProfileChart"></canvas>
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
                <div class="sub">
                    Combine several turbine models and estimate generation, demand coverage and grid dependency.
                </div>

                <div class="interactive-box">
                    {turbine_mix_inputs}

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
                <h2>Generation mix contribution</h2>
                <div class="sub">
                    Visual contribution of each selected turbine model to the total forecasted wind generation.
                </div>

                <div class="chart-box" id="mixChart">
                    <div class="placeholder-chart">
                        Select turbine quantities in the calculator to display the generation contribution by turbine model.
                    </div>
                </div>
            </div>
        </section>

        <section class="grid">
            <div class="card">
                <h2>Forecast methodology</h2>
                <div class="sub">
                    Machine-learning models evaluated on historical turbine generation.
                </div>

                <p>
                    The operational forecast is generated using <strong>{best_model["model"]}</strong>,
                    which achieved the lowest forecasting error among the tested models. The model comparison is kept
                    separate from the business KPIs so that the dashboard remains focused on industrial decision support.
                </p>

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
            </div>

            <div class="card">
                <h2>Academic interpretation</h2>
                <p>
                    The forecasting module transforms the project from a descriptive dashboard into an operational
                    decision-support tool. Instead of only reporting annual generation, stakeholders can estimate
                    expected short-term production under single-turbine and mixed-turbine deployment scenarios.
                </p>
                <span class="tag">Forecasting</span>
                <span class="tag">Decision support</span>
                <span class="tag">Industrial planning</span>
                <span class="tag">Grid dependency</span>
            </div>
        </section>

        <section class="grid">
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

            <div class="card">
                <h2>Operational value</h2>
                <p>
                    The 168-hour forecast profile makes the dashboard more useful for planning because it shows when
                    wind generation is expected to be closer to or further from industrial electricity demand.
                </p>
                <span class="tag">168-hour profile</span>
                <span class="tag">Demand comparison</span>
                <span class="tag">Operational dashboard</span>
            </div>
        </section>

    </main>

    <footer class="footer">
        <div>Aalborg Portland 7-day forecasting and decision-support tool</div>
        <div class="logo">aalborg<span>portland</span></div>
    </footer>

    <script>
        const scenarios = {scenario_json};
        const hourlyProfile = {hourly_profile_json};

        function formatNumber(value) {{
            return Math.round(value).toLocaleString("de-DE");
        }}

        function getOneTurbineScenario(turbine) {{
            return scenarios.find(row =>
                row.turbine === turbine && row.number_of_turbines === 1
            );
        }}

        function updateCalculator() {{
            const inputs = document.querySelectorAll(".turbine-count");

            let totalGeneration = 0;
            let demand = null;
            let contributions = [];

            inputs.forEach(input => {{
                const turbine = input.dataset.turbine;
                const count = Number(input.value) || 0;
                const scenario = getOneTurbineScenario(turbine);

                if (!scenario) {{
                    return;
                }}

                if (demand === null) {{
                    demand = scenario.estimated_7d_demand_mwh;
                }}

                const generation = scenario.forecast_generation_mwh * count;
                totalGeneration += generation;

                contributions.push({{
                    turbine: turbine,
                    count: count,
                    generation: generation
                }});
            }});

            if (demand === null) {{
                demand = 0;
            }}

            const coverage = demand > 0 ? totalGeneration / demand * 100 : 0;
            const gridRequired = Math.max(demand - totalGeneration, 0);

            document.getElementById("generationResult").textContent =
                formatNumber(totalGeneration) + " MWh";

            document.getElementById("coverageResult").textContent =
                coverage.toFixed(2) + "%";

            document.getElementById("gridResult").textContent =
                formatNumber(gridRequired) + " MWh";

            updateMixChart(contributions, totalGeneration);
        }}

        function updateMixChart(contributions, totalGeneration) {{
            const chart = document.getElementById("mixChart");

            if (totalGeneration <= 0) {{
                chart.innerHTML = `
                    <div class="placeholder-chart">
                        Select turbine quantities in the calculator to display the generation contribution by turbine model.
                    </div>
                `;
                return;
            }}

            let html = "";

            contributions.forEach(item => {{
                const share = totalGeneration > 0 ? item.generation / totalGeneration * 100 : 0;
                const width = Math.max(share, item.generation > 0 ? 3 : 0);

                html += `
                    <div class="bar-row">
                        <div class="bar-row-header">
                            <strong>${{item.turbine}}</strong>
                            <span>${{item.count}} turbines · ${{formatNumber(item.generation)}} MWh · ${{share.toFixed(1)}}%</span>
                        </div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width:${{width}}%;"></div>
                        </div>
                    </div>
                `;
            }});

            chart.innerHTML = html;
        }}

                function renderForecastProfileChart() {{
            const ctx = document.getElementById("forecastProfileChart");

            const labels = hourlyProfile.map(row => row.label);
            const demand = hourlyProfile.map(row => row.estimated_demand_mwh);
            const generation = hourlyProfile.map(row => row.forecast_generation_mwh);

            const windCovered = hourlyProfile.map(row =>
                Math.min(row.forecast_generation_mwh, row.estimated_demand_mwh)
            );

            new Chart(ctx, {{
                type: "line",
                data: {{
                    labels: labels,
                    datasets: [
                        {{
                            label: "Demand not covered by wind",
                            data: demand,
                            borderColor: "rgba(0, 0, 0, 0)",
                            backgroundColor: "rgba(228, 0, 90, 0.12)",
                            pointRadius: 0,
                            fill: "origin",
                            tension: 0.25,
                            order: 4
                        }},
                        {{
                            label: "Wind-covered demand",
                            data: windCovered,
                            borderColor: "rgba(0, 0, 0, 0)",
                            backgroundColor: "rgba(46, 160, 67, 0.22)",
                            pointRadius: 0,
                            fill: "origin",
                            tension: 0.25,
                            order: 3
                        }},
                        {{
                            label: "Estimated industrial demand",
                            data: demand,
                            borderColor: "#2b0014",
                            backgroundColor: "rgba(43, 0, 20, 0.08)",
                            borderWidth: 2.5,
                            pointRadius: 0,
                            tension: 0.25,
                            fill: false,
                            order: 1
                        }},
                        {{
                            label: "Forecast wind generation",
                            data: generation,
                            borderColor: "#e4005a",
                            backgroundColor: "rgba(228, 0, 90, 0.10)",
                            borderWidth: 2.5,
                            pointRadius: 0,
                            tension: 0.25,
                            fill: false,
                            order: 0
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        mode: "index",
                        intersect: false
                    }},
                    plugins: {{
                        legend: {{
                            position: "top",
                            labels: {{
                                filter: function(item) {{
                                    return item.text !== "Demand not covered by wind";
                                }}
                            }}
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    const index = context.dataIndex;
                                    const row = hourlyProfile[index];

                                    if (context.dataset.label === "Demand not covered by wind") {{
                                        const value = Math.max(
                                            row.estimated_demand_mwh - row.forecast_generation_mwh,
                                            0
                                        );
                                        return "Grid required: " + value.toFixed(2) + " MWh";
                                    }}

                                    if (context.dataset.label === "Wind-covered demand") {{
                                        const value = Math.min(
                                            row.forecast_generation_mwh,
                                            row.estimated_demand_mwh
                                        );
                                        return "Wind-covered demand: " + value.toFixed(2) + " MWh";
                                    }}

                                    return context.dataset.label + ": " +
                                        context.parsed.y.toFixed(2) + " MWh";
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            ticks: {{
                                maxTicksLimit: 12
                            }},
                            grid: {{
                                display: false
                            }}
                        }},
                        y: {{
                            title: {{
                                display: true,
                                text: "MWh per hour"
                            }},
                            beginAtZero: true
                        }}
                    }}
                }}
            }});
        }}

        document.querySelectorAll(".turbine-count").forEach(input => {{
            input.addEventListener("input", updateCalculator);
        }});

        updateCalculator();
        renderForecastProfileChart();
    </script>

</body>
</html>
    """

    with open("docs/forecasting.html", "w", encoding="utf-8") as f:
        f.write(html)

    print("Forecasting dashboard generated successfully")


if __name__ == "__main__":
    main()

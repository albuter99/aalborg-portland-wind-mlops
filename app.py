import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="Aalborg Portland Wind MLOps",
    layout="wide"
)

st.title("Aalborg Portland Wind Energy Self-Sufficiency Dashboard")

st.write(
    "This dashboard estimates how much of Aalborg Portland's electricity demand "
    "could be covered by different wind turbine models using real hourly wind data "
    "and a synthetic hourly demand profile calibrated to public annual electricity consumption."
)

summary_df = pd.read_csv("artifacts/turbine_summary.csv")
simulation_df = pd.read_csv("data/turbine_simulation_results.csv")

simulation_df["time"] = pd.to_datetime(simulation_df["time"])

st.header("Turbine comparison")

st.dataframe(summary_df)

best_turbine = summary_df.sort_values(
    "coverage_ratio_percent",
    ascending=False
).iloc[0]

col1, col2, col3 = st.columns(3)

col1.metric("Best turbine", best_turbine["turbine"])
col2.metric("Demand covered", f"{best_turbine['coverage_ratio_percent']}%")
col3.metric("Annual generation", f"{best_turbine['annual_generation_mwh']:,.0f} MWh")

st.header("Coverage comparison")

fig, ax = plt.subplots()
ax.bar(summary_df["turbine"], summary_df["coverage_ratio_percent"])
ax.set_ylabel("Demand coverage (%)")
ax.set_xlabel("Turbine model")
ax.set_title("Annual electricity demand coverage by turbine")
plt.xticks(rotation=30, ha="right")
st.pyplot(fig)

st.header("Hourly demand vs generation")

turbine_options = [
    "Vestas V136 4.5 MW",
    "Siemens Gamesa SG 5.0-145",
    "Nordex N149 5.X",
    "Enercon E-138 EP3"
]

selected_turbine = st.selectbox(
    "Select turbine model",
    turbine_options
)

generation_col = selected_turbine + " generation_mw"

sample_df = simulation_df.head(24 * 14)

fig2, ax2 = plt.subplots()
ax2.plot(sample_df["time"], sample_df["demand_mw"], label="Demand MW")
ax2.plot(sample_df["time"], sample_df[generation_col], label="Wind generation MW")
ax2.set_ylabel("MW")
ax2.set_xlabel("Time")
ax2.set_title(f"Demand vs generation for {selected_turbine}")
ax2.legend()
plt.xticks(rotation=30, ha="right")
st.pyplot(fig2)

st.header("Project interpretation")

st.write(
    "The results should be interpreted as physical on-site electricity coverage, "
    "not full plant energy autonomy. Cement production has very large thermal energy "
    "requirements, so this model focuses only on electricity demand."
)

st.header("Methodological limitation")

st.write(
    "Public plant-level hourly electricity demand is not available. Therefore, the hourly "
    "demand profile is synthetic but calibrated to Aalborg Portland's publicly reported "
    "annual electricity consumption."
)

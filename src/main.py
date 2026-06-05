from fetch_weather import main as fetch_weather_main
from generate_demand import main as generate_demand_main
from simulate_turbines import main as simulate_turbines_main
from analyze_results import main as analyze_results_main
from seasonal_analysis import main as seasonal_analysis_main
from sensitivity_analysis import main as sensitivity_analysis_main
from generate_dashboard import main as generate_dashboard_main
from generate_advanced_dashboard import main as generate_advanced_dashboard_main
from forecasting_models import main as forecasting_models_main
from generate_forecasting_dashboard import main as generate_forecasting_dashboard_main
from generate_economics_dashboard import main as generate_economics_dashboard_main


if __name__ == "__main__":
    fetch_weather_main()
    generate_demand_main()
    simulate_turbines_main()
    analyze_results_main()
    seasonal_analysis_main()
    sensitivity_analysis_main()
    forecasting_models_main()
    generate_dashboard_main()
    generate_advanced_dashboard_main()
    generate_forecasting_dashboard_main()
    generate_economics_dashboard_main()

    print("Full pipeline completed successfully")

from fetch_weather import main as fetch_weather_main
from generate_demand import main as generate_demand_main
from simulate_turbines import main as simulate_turbines_main
from analyze_results import main as analyze_results_main
from generate_dashboard import main as generate_dashboard_main

if __name__ == "__main__":
    fetch_weather_main()
    generate_demand_main()
    simulate_turbines_main()
    analyze_results_main()
    generate_dashboard_main()

    print("Full pipeline completed successfully")

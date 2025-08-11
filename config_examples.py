#!/usr/bin/env python3
"""
Configuration Examples and Usage Guide for Employee Simulation System

This script demonstrates how to use the configuration system and scenarios.
"""

from config_manager import ConfigurationManager
import json


def show_usage_examples():
    """Show examples of how to use the configuration system."""
    print("=== Employee Simulation System - Configuration Examples ===\n")
    
    # Initialize configuration manager
    config_manager = ConfigurationManager("config.json")
    
    print("1. LIST AVAILABLE SCENARIOS:")
    scenarios = config_manager.list_scenarios()
    for i, scenario in enumerate(scenarios, 1):
        print(f"   {i}. {scenario}")
    
    print(f"\n2. SHOW SCENARIO DETAILS:")
    if scenarios:
        example_scenario = scenarios[0]
        print(f"   Example: {example_scenario}")
        config_manager.print_scenario_info(example_scenario)
    
    print(f"\n3. COMMAND LINE USAGE EXAMPLES:")
    print("   # Use default configuration (config.json):")
    print("   python employee_simulation_orchestrator.py --mode advanced-analysis-only")
    print()
    print("   # Use a specific scenario:")
    print("   python employee_simulation_orchestrator.py --scenario quick_test")
    print()
    print("   # Override population size with scenario:")
    print("   python employee_simulation_orchestrator.py --scenario gender_gap_analysis --population-size 500")
    print()
    print("   # Use custom config file:")
    print("   python employee_simulation_orchestrator.py --config my_custom_config.json")
    
    print(f"\n4. CONFIGURATION MANAGER CLI USAGE:")
    print("   # List all scenarios:")
    print("   python config_manager.py list")
    print()
    print("   # Show scenario details:")
    print("   python config_manager.py show comprehensive_analysis")
    print()
    print("   # Create custom config file:")
    print("   python config_manager.py create my_config.json --scenario quick_test --population-size 300")
    print()
    print("   # Test scenario configuration:")
    print("   python config_manager.py test gender_gap_analysis")


def demonstrate_programmatic_usage():
    """Show how to use configuration manager programmatically."""
    print("\n=== PROGRAMMATIC CONFIGURATION USAGE ===\n")
    
    config_manager = ConfigurationManager("config.json")
    
    print("1. Get default configuration:")
    default_config = config_manager.get_orchestrator_config()
    print(f"   Population size: {default_config.get('population_size')}")
    print(f"   Advanced analysis enabled: {default_config.get('enable_advanced_analysis')}")
    
    print("\n2. Get scenario configuration:")
    scenario_config = config_manager.get_orchestrator_config(scenario="gender_gap_analysis")
    print(f"   Scenario population size: {scenario_config.get('population_size')}")
    print(f"   Gender pay gap: {scenario_config.get('gender_pay_gap_percent')}%")
    print(f"   Story tracking: {scenario_config.get('enable_story_tracking')}")
    
    print("\n3. Configuration with overrides:")
    override_config = config_manager.get_orchestrator_config(
        scenario="quick_test",
        overrides={
            "population_size": 150,
            "enable_advanced_analysis": True,
            "log_level": "DEBUG"
        }
    )
    print(f"   Final population size: {override_config.get('population_size')}")
    print(f"   Advanced analysis: {override_config.get('enable_advanced_analysis')}")
    print(f"   Log level: {override_config.get('log_level')}")


def create_custom_scenario_example():
    """Example of creating a custom scenario."""
    print("\n=== CREATING CUSTOM SCENARIOS ===\n")
    
    config_manager = ConfigurationManager("config.json")
    
    # Example custom scenario
    custom_scenario = {
        "population_size": 300,
        "gender_pay_gap_percent": 20.0,
        "enable_advanced_analysis": True,
        "run_individual_progression_analysis": True,
        "run_median_convergence_analysis": True,
        "enable_story_tracking": True,
        "story_categories": ["gender_gap", "high_performer"],
        "progression_analysis_years": 3,
        "log_level": "DEBUG"
    }
    
    print("Custom scenario configuration:")
    print(json.dumps(custom_scenario, indent=2))
    
    # Note: Uncomment the line below to actually save the scenario
    # config_manager.save_scenario("my_custom_analysis", custom_scenario)
    print("\n(To save this scenario, uncomment the save_scenario line in the code)")


def show_advanced_configuration_options():
    """Show advanced configuration options available."""
    print("\n=== ADVANCED CONFIGURATION OPTIONS ===\n")
    
    config_manager = ConfigurationManager("config.json")
    
    print("Key configuration categories:")
    print("• population: population_size, random_seed, level_distribution, gender_pay_gap_percent, salary_constraints")
    print("• simulation: max_cycles, convergence_threshold") 
    print("• export: export_formats, generate_visualizations, export_individual_files, export_comprehensive_report")
    print("• story_tracking: enable_story_tracking, tracked_employee_count, story_categories, story_export_formats")
    print("• logging: log_level, enable_progress_bar, enable_file_logging, generate_summary_report")
    print("• advanced_analysis: enable_advanced_analysis, run_*_analysis, progression_analysis_years, etc.")
    
    print(f"\nFor detailed configuration structure, see config.json")
    
    # Show actual config structure
    base_config = config_manager.base_config
    print(f"\nMain configuration sections available:")
    for section in base_config.keys():
        if section not in ["meta", "user_stories", "customization_examples"]:
            print(f"  • {section}")


if __name__ == "__main__":
    show_usage_examples()
    demonstrate_programmatic_usage()
    create_custom_scenario_example()
    show_advanced_configuration_options()
    
    print(f"\n=== NEXT STEPS ===")
    print("1. Try running with default config: python employee_simulation_orchestrator.py --mode advanced-analysis-only")
    print("2. Experiment with scenarios: python employee_simulation_orchestrator.py --scenario quick_test")
    print("3. Customize config.json for your needs")
    print("4. Create new scenarios using config_manager.py")
    print("5. Use programmatic configuration in your own scripts")
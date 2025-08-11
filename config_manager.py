#!/usr/bin/env python3
"""Configuration Manager for Employee Simulation System.

Handles loading, merging, and managing configuration files and user scenarios.
"""

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional


class ConfigurationManager:
    """Manages configuration loading and scenario application for the simulation system."""

    def __init__(self, config_path: str = "config.json"):
        """Initialize configuration manager.

        Args:
            config_path: Path to the main configuration file
        """
        self.config_path = Path(config_path)
        self.base_config = self._load_base_config()

    def _load_base_config(self) -> Dict[str, Any]:
        """Load the base configuration file."""
        try:
            if self.config_path.exists():
                with open(self.config_path, "r") as f:
                    return json.load(f)
            else:
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return self._get_fallback_config()

    def _get_fallback_config(self) -> Dict[str, Any]:
        """Provide fallback configuration if file loading fails."""
        return {
            "population": {"population_size": 1000, "random_seed": 42},
            "simulation": {"max_cycles": 15, "convergence_threshold": 0.001},
            "export": {"export_formats": ["csv", "json"], "generate_visualizations": True},
            "story_tracking": {"enable_story_tracking": False},
            "logging": {"log_level": "INFO"},
            "advanced_analysis": {"enable_advanced_analysis": False},
        }

    def get_orchestrator_config(
        self, scenario: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Get configuration formatted for EmployeeSimulationOrchestrator.

        Args:
            scenario: Name of predefined scenario to apply
            overrides: Additional configuration overrides

        Returns:
            Configuration dictionary compatible with orchestrator
        """
        # Start with flattened base configuration
        config = self._flatten_config(self.base_config)

        # Apply scenario if specified
        if scenario:
            scenario_config = self.get_scenario_config(scenario)
            if scenario_config:
                # Handle salary constraints in scenario config
                if "salary_constraints" in scenario_config and isinstance(scenario_config["salary_constraints"], dict):
                    scenario_config["salary_constraints"] = {
                        int(k): v for k, v in scenario_config["salary_constraints"].items()
                    }
                config.update(scenario_config)

        # Apply any overrides
        if overrides:
            config.update(overrides)

        return config

    def _flatten_config(self, nested_config: Dict[str, Any]) -> Dict[str, Any]:
        """Flatten nested configuration into format expected by orchestrator.

        Args:
            nested_config: Nested configuration dictionary

        Returns:
            Flattened configuration dictionary
        """
        flat_config = {}

        # Population settings
        pop_config = nested_config.get("population", {})

        # Convert salary constraints string keys to integers if present
        salary_constraints = pop_config.get("salary_constraints")
        if salary_constraints and isinstance(salary_constraints, dict):
            salary_constraints = {int(k): v for k, v in salary_constraints.items()}

        flat_config.update(
            {
                "population_size": pop_config.get("population_size", 1000),
                "random_seed": pop_config.get("random_seed", 42),
                "level_distribution": pop_config.get("level_distribution"),
                "gender_pay_gap_percent": pop_config.get("gender_pay_gap_percent"),
                "salary_constraints": salary_constraints,
            }
        )

        # Simulation settings
        sim_config = nested_config.get("simulation", {})
        flat_config.update(
            {
                "max_cycles": sim_config.get("max_cycles", 15),
                "convergence_threshold": sim_config.get("convergence_threshold", 0.001),
            }
        )

        # Export settings
        export_config = nested_config.get("export", {})
        flat_config.update(
            {
                "export_formats": export_config.get("export_formats", ["csv", "json"]),
                "generate_visualizations": export_config.get("generate_visualizations", True),
                "export_individual_files": export_config.get("export_individual_files", True),
                "export_comprehensive_report": export_config.get("export_comprehensive_report", True),
            }
        )

        # Story tracking settings
        story_config = nested_config.get("story_tracking", {})
        flat_config.update(
            {
                "enable_story_tracking": story_config.get("enable_story_tracking", False),
                "tracked_employee_count": story_config.get("tracked_employee_count", 20),
                "story_categories": story_config.get(
                    "story_categories", ["gender_gap", "above_range", "high_performer"]
                ),
                "story_export_formats": story_config.get("story_export_formats", ["json", "csv", "excel", "markdown"]),
                "generate_interactive_dashboard": story_config.get("generate_interactive_dashboard", False),
                "create_individual_story_charts": story_config.get("create_individual_story_charts", False),
                "export_story_data": story_config.get("export_story_data", True),
            }
        )

        # Logging settings
        log_config = nested_config.get("logging", {})
        flat_config.update(
            {
                "log_level": log_config.get("log_level", "INFO"),
                "enable_progress_bar": log_config.get("enable_progress_bar", True),
                "enable_file_logging": log_config.get("enable_file_logging", False),
                "generate_summary_report": log_config.get("generate_summary_report", True),
            }
        )

        # Advanced analysis settings
        analysis_config = nested_config.get("advanced_analysis", {})
        flat_config.update(
            {
                "enable_advanced_analysis": analysis_config.get("enable_advanced_analysis", False),
                "run_individual_progression_analysis": analysis_config.get(
                    "run_individual_progression_analysis", False
                ),
                "run_median_convergence_analysis": analysis_config.get("run_median_convergence_analysis", False),
                "run_intervention_strategy_analysis": analysis_config.get("run_intervention_strategy_analysis", False),
                "export_advanced_analysis_reports": analysis_config.get("export_advanced_analysis_reports", True),
                "progression_analysis_years": analysis_config.get("progression_analysis_years", 5),
                "convergence_threshold_years": analysis_config.get("convergence_threshold_years", 5),
                "acceptable_gap_percent": analysis_config.get("acceptable_gap_percent", 5.0),
                "intervention_budget_constraint": analysis_config.get("intervention_budget_constraint", 0.005),
                "target_gender_gap_percent": analysis_config.get("target_gender_gap_percent", 0.0),
            }
        )

        return flat_config

    def get_scenario_config(self, scenario_name: str) -> Optional[Dict[str, Any]]:
        """Get configuration for a specific scenario.

        Args:
            scenario_name: Name of the scenario

        Returns:
            Configuration dictionary for the scenario, or None if not found
        """
        scenarios = self.base_config.get("user_stories", {}).get("scenarios", {})
        if scenario_name in scenarios:
            return scenarios[scenario_name]

        # Also check customization examples
        examples = self.base_config.get("customization_examples", {})
        if scenario_name in examples:
            return examples[scenario_name]

        return None

    def list_scenarios(self) -> List[str]:
        """Get list of available scenario names."""
        scenarios = list(self.base_config.get("user_stories", {}).get("scenarios", {}).keys())
        examples = list(self.base_config.get("customization_examples", {}).keys())
        return scenarios + [name for name in examples if name != "description"]

    def save_scenario(self, scenario_name: str, config: Dict[str, Any]) -> None:
        """Save a new scenario to the configuration file.

        Args:
            scenario_name: Name for the new scenario
            config: Configuration for the scenario
        """
        if "user_stories" not in self.base_config:
            self.base_config["user_stories"] = {"scenarios": {}}
        elif "scenarios" not in self.base_config["user_stories"]:
            self.base_config["user_stories"]["scenarios"] = {}

        self.base_config["user_stories"]["scenarios"][scenario_name] = config

        # Save updated configuration
        with open(self.config_path, "w") as f:
            json.dump(self.base_config, f, indent=2)

    def print_scenario_info(self, scenario_name: str) -> None:
        """Print detailed information about a scenario."""
        scenario_config = self.get_scenario_config(scenario_name)
        if not scenario_config:
            print(f"Scenario '{scenario_name}' not found.")
            return

        print(f"\n=== Scenario: {scenario_name} ===")
        for key, value in scenario_config.items():
            if isinstance(value, (dict, list)):
                print(f"{key}: {json.dumps(value, indent=2)}")
            else:
                print(f"{key}: {value}")

    def create_config_file(
        self, output_path: str, scenario: Optional[str] = None, overrides: Optional[Dict[str, Any]] = None
    ) -> None:
        """Create a standalone configuration file.

        Args:
            output_path: Path where to save the configuration file
            scenario: Scenario to use as base
            overrides: Additional overrides to apply
        """
        config = self.get_orchestrator_config(scenario=scenario, overrides=overrides)

        with open(output_path, "w") as f:
            json.dump(config, f, indent=2)

        print(f"Configuration saved to: {output_path}")


def main():
    """Command-line interface for configuration management."""
    parser = argparse.ArgumentParser(description="Employee Simulation Configuration Manager")
    parser.add_argument("--config", default="config.json", help="Path to configuration file")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # List scenarios command
    _ = subparsers.add_parser("list", help="List available scenarios")

    # Show scenario command
    show_parser = subparsers.add_parser("show", help="Show scenario configuration")
    show_parser.add_argument("scenario", help="Scenario name to show")

    # Create config command
    create_parser = subparsers.add_parser("create", help="Create configuration file")
    create_parser.add_argument("output", help="Output file path")
    create_parser.add_argument("--scenario", help="Base scenario to use")
    create_parser.add_argument("--population-size", type=int, help="Override population size")
    create_parser.add_argument("--enable-stories", action="store_true", help="Enable story tracking")
    create_parser.add_argument("--enable-analysis", action="store_true", help="Enable advanced analysis")

    # Test scenario command
    test_parser = subparsers.add_parser("test", help="Test configuration with scenario")
    test_parser.add_argument("scenario", help="Scenario name to test")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        config_manager = ConfigurationManager(args.config)
    except Exception as e:
        print(f"Error initializing configuration manager: {e}")
        sys.exit(1)

    if args.command == "list":
        scenarios = config_manager.list_scenarios()
        print(f"\nAvailable scenarios ({len(scenarios)}):")
        for scenario in scenarios:
            print(f"  - {scenario}")

    elif args.command == "show":
        config_manager.print_scenario_info(args.scenario)

    elif args.command == "create":
        overrides = {}
        if args.population_size:
            overrides["population_size"] = args.population_size
        if args.enable_stories:
            overrides["enable_story_tracking"] = True
        if args.enable_analysis:
            overrides["enable_advanced_analysis"] = True
            overrides["run_individual_progression_analysis"] = True
            overrides["run_median_convergence_analysis"] = True

        config_manager.create_config_file(args.output, scenario=args.scenario, overrides=overrides)

    elif args.command == "test":
        config = config_manager.get_orchestrator_config(scenario=args.scenario)
        print(f"\n=== Configuration for scenario '{args.scenario}' ===")
        print(json.dumps(config, indent=2))


if __name__ == "__main__":
    main()

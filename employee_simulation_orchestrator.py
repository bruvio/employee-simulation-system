#!/usr/bin/env python3

import argparse
from datetime import datetime
import json
import sys
from typing import Any, Dict, List

import pandas as pd

from advanced_story_export_system import AdvancedStoryExportSystem

# Import centralized path management
from app_paths import (
    ARTIFACTS_DIR,
    CHARTS_DIR,
    RUN_DIR,
    TABLES_DIR,
    ensure_dirs,
    get_artifact_path,
    get_population_size,
)
from data_export_system import DataExportSystem

# Import our simulation modules
from employee_population_simulator import EmployeePopulationGenerator
from employee_story_tracker import EmployeeStoryTracker
from file_optimization_manager import FileOptimizationManager

# Import GEL scenario modules
from gel_output_manager import GELOutputManager
from gel_policy_constraints import GELPolicyConstraints

# Import advanced analysis modules
from individual_progression_simulator import IndividualProgressionSimulator
from interactive_dashboard_generator import InteractiveDashboardGenerator
from intervention_strategy_simulator import InterventionStrategySimulator
from median_convergence_analyzer import MedianConvergenceAnalyzer
from performance_optimization_manager import PerformanceOptimizationManager
from performance_review_system import PerformanceReviewSystem
from report_builder_html import HTMLReportBuilder
from report_builder_md import MarkdownReportBuilder
from review_cycle_simulator import ReviewCycleSimulator
from roles_config import RolesConfigLoader
from smart_logging_manager import SmartLoggingManager, get_smart_logger
from visualization_generator import VisualizationGenerator


class EmployeeSimulationOrchestrator:
    """
    Main orchestrator for the complete employee population simulation system.

    Coordinates all phases of the simulation pipeline.

    Args:

    Returns:
    """

    def __init__(self, config=None, cli_population_size=None):
        self.config = config or self._load_config_with_fallback()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Ensure output directories exist
        ensure_dirs()

        # Set up centralized paths
        self.artifacts_dir = ARTIFACTS_DIR
        self.charts_dir = CHARTS_DIR
        self.tables_dir = TABLES_DIR

        # Initialize smart logging manager with centralized paths
        log_level = self.config.get("log_level", "INFO")
        enable_progress = self.config.get("enable_progress_bar", True)
        self.smart_logger = SmartLoggingManager(
            log_level=log_level,
            enable_progress_indicators=enable_progress,
            log_file_path=(
                str(get_artifact_path(f"simulation_log_{self.timestamp}.log"))
                if self.config.get("enable_file_logging", False)
                else None
            ),
            suppress_noisy_libraries=True,
        )
        self.logger = self.smart_logger.get_logger("EmployeeSimulationOrchestrator")

        # Enforce and log population size
        try:
            population_size, source = get_population_size(self.config, cli_population_size)
            self.population_size = population_size
            self.logger.info(f"Effective population size: {population_size:,} (source: {source})")
        except (KeyError, ValueError) as e:
            self.logger.error(f"Population size configuration error: {e}")
            raise

        # Initialize performance optimization manager
        self.performance_manager = PerformanceOptimizationManager(smart_logger=self.smart_logger)

        # Apply performance optimizations based on population size
        enable_story_tracking = self.config.get("enable_story_tracking", False)
        self.performance_optimizations = self.performance_manager.apply_performance_optimizations(
            population_size=population_size, enable_story_tracking=enable_story_tracking
        )

        # Initialize file optimization manager with centralized paths
        self.file_manager = FileOptimizationManager(
            base_output_dir=str(self.artifacts_dir), base_images_dir=str(self.charts_dir)
        )

        # Initialize story tracker if enabled
        self.story_tracker = None
        if self.config.get("enable_story_tracking", False):
            self.story_tracker = EmployeeStoryTracker()
            self.smart_logger.log_info("Story tracking enabled")

        # Set convenience references using centralized paths
        self.run_output_dir = RUN_DIR
        self.run_images_dir = self.charts_dir

        self.smart_logger.log_success(f"Initialized employee simulation orchestrator with timestamp: {self.timestamp}")

    def _load_config_with_fallback(self):
        """
        Load configuration from config.json with fallback to defaults.
        """
        try:
            from config_manager import ConfigurationManager

            config_manager = ConfigurationManager("config.json")
            return config_manager.get_orchestrator_config()
        except Exception as e:
            print(f"Warning: Could not load config.json ({e}), using default configuration")
            return self._get_default_config()

    def _get_default_config(self):
        """
        Get default simulation configuration.
        """
        return {
            # Note: No default population_size - must be explicitly configured
            "random_seed": 42,
            "max_cycles": 15,
            "convergence_threshold": 0.001,
            "export_formats": ["csv", "excel", "json"],
            "generate_visualizations": True,
            "export_individual_files": True,
            "export_comprehensive_report": True,
            # Story tracking options
            "enable_story_tracking": False,
            "tracked_employee_count": 20,  # Max employees per category
            "story_categories": ["gender_gap", "above_range", "high_performer"],
            "story_export_formats": ["json", "csv", "excel", "markdown"],  # Available: json, csv, excel, xml, markdown
            # Logging options
            "log_level": "INFO",  # ERROR, WARNING, INFO, DEBUG
            "enable_progress_bar": True,
            "enable_file_logging": False,
            "generate_summary_report": True,
            # Visualization options
            "generate_interactive_dashboard": False,
            "create_individual_story_charts": False,
            "export_story_data": True,
            # Advanced analysis options
            "enable_advanced_analysis": False,
            "run_individual_progression_analysis": False,
            "run_median_convergence_analysis": False,
            "run_intervention_strategy_analysis": False,
            "export_advanced_analysis_reports": True,
            # Advanced analysis parameters
            "progression_analysis_years": 5,
            "convergence_threshold_years": 5,
            "acceptable_gap_percent": 5.0,  # Within 5% of median for convergence
            "intervention_budget_constraint": 0.005,  # 0.5% of payroll
            "target_gender_gap_percent": 0.0,  # Complete closure
        }

    def run_complete_simulation(self):
        """
        Run the complete end-to-end employee simulation pipeline.

        Args:

        Returns:
          dict: Results and file paths from the simulation
        """
        self.smart_logger.log_info("Starting complete employee simulation pipeline")

        results = {
            "simulation_config": self.config,
            "timestamp": self.timestamp,
            "files_generated": {},
            "validation_results": {},
            "summary_metrics": {},
        }

        # Initialize run directories for organized output
        enable_story_tracking = self.config.get("enable_story_tracking", False)
        self.run_directories = self.file_manager.create_run_directory(
            run_id=self.timestamp, enable_story_tracking=enable_story_tracking
        )
        self.smart_logger.log_info(f"Created run directory: {self.run_directories['run_root']}")

        try:
            # Phase 1: Generate Employee Population
            self.smart_logger.start_phase("Phase 1: Generate Employee Population", 4)
            population_generator = EmployeePopulationGenerator(
                population_size=self.population_size,
                random_seed=self.config["random_seed"],
                level_distribution=self.config.get("level_distribution"),
                gender_pay_gap_percent=self.config.get("gender_pay_gap_percent"),
                salary_constraints=self.config.get("salary_constraints"),
            )

            population_data = population_generator.generate_population()
            population_filename = f"employee_population_{self.timestamp}.json"
            population_filepath = get_artifact_path(population_filename)

            # Save population data
            with open(population_filepath, "w") as f:
                json.dump(population_data, f, indent=2, default=str)

            results["files_generated"]["population"] = str(population_filepath)
            results["summary_metrics"]["population_size"] = len(population_data)

            # Validate population constraints
            validation_results = self._validate_population(population_data)
            results["validation_results"]["population"] = validation_results
            results["population_data"] = population_data  # Add population data to results

            self.smart_logger.log_info(f"Phase 1 completed: {len(population_data)} employees generated")

            # Phase 2: Initialize Performance Review System
            self.smart_logger.log_info("Phase 2: Initializing performance review system")
            review_system = PerformanceReviewSystem(random_seed=self.config["random_seed"])

            # Validate review system
            review_validation = review_system.validate_uplift_calculations()
            results["validation_results"]["review_system"] = review_validation

            self.smart_logger.log_info("Phase 2 completed: Performance review system validated")

            # Phase 3: Run Multi-Cycle Simulation
            self.smart_logger.log_info("Phase 3: Running multi-cycle simulation")
            cycle_simulator = ReviewCycleSimulator(
                initial_population=population_data, random_seed=self.config["random_seed"]
            )

            inequality_progression = cycle_simulator.simulate_multiple_cycles(num_cycles=self.config["max_cycles"])

            # Convert to expected format
            simulation_results = {
                "inequality_metrics": pd.DataFrame(inequality_progression),
                "converged": len(inequality_progression) < self.config["max_cycles"] + 1,
            }
            simulation_filename = f"simulation_results_{self.timestamp}.json"
            simulation_filepath = get_artifact_path(simulation_filename)

            # Save simulation results (with DataFrame conversion)
            serializable_results = self._make_serializable(simulation_results)
            with open(simulation_filepath, "w") as f:
                json.dump(serializable_results, f, indent=2, default=str)

            results["files_generated"]["simulation"] = str(simulation_filepath)
            if isinstance(simulation_results, dict):
                inequality_df = simulation_results.get("inequality_metrics", pd.DataFrame())
                convergence_achieved = simulation_results.get("converged", False)
            else:
                # simulation_results is the DataFrame directly
                inequality_df = simulation_results
                convergence_achieved = False

            results["summary_metrics"].update(
                {
                    "cycles_completed": 0 if inequality_df.empty else len(inequality_df) - 1,
                    "final_gini_coefficient": (
                        "N/A" if inequality_df.empty else float(inequality_df.iloc[-1]["gini_coefficient"])
                    ),
                    "convergence_achieved": convergence_achieved,
                }
            )

            self.smart_logger.log_info(
                f"Phase 3 completed: {results['summary_metrics']['cycles_completed']} cycles simulated"
            )

            # Phase 4: Generate Visualizations
            if self.config["generate_visualizations"]:
                self.smart_logger.log_info("Phase 4: Generating visualizations")

                # Generate all visualization types
                viz_generator = VisualizationGenerator(
                    population_data=population_data,
                    inequality_progression=(
                        simulation_results.get("inequality_metrics", pd.DataFrame()).to_dict("records")
                        if isinstance(simulation_results, dict)
                        else simulation_results.to_dict("records")
                    ),
                )
                viz_files = viz_generator.generate_complete_analysis()

                results["files_generated"]["visualizations"] = viz_files
                self.smart_logger.log_info(f"Phase 4 completed: {len(viz_files)} visualization files generated")

            # Phase 5: Export Data
            self.smart_logger.log_info("Phase 5: Exporting data")
            exporter = DataExportSystem(output_dir=str(self.artifacts_dir))

            export_files = {}

            # Export individual datasets if requested
            if self.config["export_individual_files"]:
                # Population data
                pop_exports = exporter.export_employee_population(
                    population_data, format_types=self.config["export_formats"]
                )
                export_files["population"] = {str(k): str(v) for k, v in pop_exports.items()}

                # Simulation results
                sim_exports = exporter.export_simulation_results(
                    simulation_results, format_types=self.config["export_formats"]
                )
                export_files["simulation"] = {str(k): str(v) for k, v in sim_exports.items()}

            # Comprehensive analysis report
            if self.config["export_comprehensive_report"]:
                analysis_exports = exporter.export_analysis_report(
                    population_data, simulation_results, format_types=self.config["export_formats"]
                )
                export_files["comprehensive_analysis"] = {str(k): str(v) for k, v in analysis_exports.items()}

            results["files_generated"]["exports"] = export_files
            self.smart_logger.log_info("Phase 5 completed: Data export finished")

            # Generate final summary
            try:
                final_summary = self._generate_final_summary(results)
                results["final_summary"] = final_summary
            except Exception as e:
                self.smart_logger.log_error("Error generating final summary", e)
                results["final_summary"] = {"error": str(e)}

            # Generate comprehensive execution summary with file organization
            self._generate_comprehensive_summary(results)

            # Print execution summary
            self.smart_logger.print_execution_summary()

            # Export execution summary if enabled
            if self.config.get("generate_summary_report", True):
                summary_path = str(self.run_directories["reports"] / "execution_summary.json")
                self.smart_logger.export_summary(summary_path)
                results["files_generated"]["execution_summary"] = summary_path

                # Generate comprehensive run index
                index_path = self.file_manager.generate_run_index()
                results["files_generated"]["run_index"] = index_path

                # Generate performance analysis report
                performance_summary = self.performance_manager.get_performance_summary()
                performance_path = str(self.run_directories["reports"] / "performance_analysis.json")
                with open(performance_path, "w") as f:
                    json.dump(performance_summary, f, indent=2, default=str)
                results["files_generated"]["performance_analysis"] = performance_path

                # Log performance insights
                peak_memory = performance_summary["performance_metrics"]["peak_memory_usage_mb"]
                total_time = performance_summary["performance_metrics"]["total_execution_time_seconds"]
                optimizations = len(performance_summary["optimizations"]["optimization_list"])

                self.smart_logger.log_info(
                    f"Performance Summary: {total_time:.1f}s execution, {peak_memory:.1f}MB peak memory, {optimizations} optimizations applied"
                )

            self.smart_logger.log_success("Complete simulation pipeline finished successfully")
            return results

        except Exception as e:
            self.smart_logger.log_error(f"Simulation pipeline failed: {e}")
            results["error"] = str(e)
            raise

    def run_quick_validation(self):
        """
        Run a quick validation of all system components without full simulation.

        Args:

        Returns:
          dict: Validation results
        """
        self.smart_logger.log_info("Running quick validation of all system components")

        validation_results = {}

        try:
            # Test population generation
            pop_gen = EmployeePopulationGenerator(population_size=100, random_seed=42)
            small_population = pop_gen.generate_population()
            pop_validation = self._validate_population(small_population)
            validation_results["population_generator"] = {
                "status": "PASS" if pop_validation["median_constraint_met"] else "FAIL",
                "details": pop_validation,
            }

            # Test performance review system
            review_system = PerformanceReviewSystem(random_seed=42)
            review_validation = review_system.validate_uplift_calculations()
            validation_results["review_system"] = {
                "status": "PASS" if review_validation["all_tests_passed"] else "FAIL",
                "details": review_validation,
            }

            # Test cycle simulator with minimal data
            try:
                cycle_simulator = ReviewCycleSimulator(initial_population=small_population, random_seed=42)
                mini_simulation = cycle_simulator.simulate_multiple_cycles(num_cycles=2)
                validation_results["cycle_simulator"] = {
                    "status": "PASS" if len(mini_simulation) > 1 else "FAIL",
                    "details": f"Completed {len(mini_simulation) - 1} cycles",
                }
            except Exception as e:
                validation_results["cycle_simulator"] = {"status": "FAIL", "details": f"Error: {str(e)}"}

            # Test visualization generator
            VisualizationGenerator()
            validation_results["visualization_generator"] = {
                "status": "PASS",
                "details": "Visualization generator initialized successfully",
            }

            # Test data export system
            DataExportSystem()
            validation_results["data_export_system"] = {
                "status": "PASS",
                "details": "Data export system initialized successfully",
            }

            overall_status = (
                "PASS" if all(result["status"] == "PASS" for result in validation_results.values()) else "FAIL"
            )

            validation_results["overall"] = {
                "status": overall_status,
                "timestamp": datetime.now().isoformat(),
                "components_tested": len(validation_results) - 1,
            }

            self.smart_logger.log_info(f"Quick validation completed: {overall_status}")
            return validation_results

        except Exception as e:
            self.smart_logger.log_error(f"Quick validation failed: {e}")
            validation_results["overall"] = {"status": "FAIL", "error": str(e), "timestamp": datetime.now().isoformat()}
            return validation_results

    def _validate_population(self, population_data):
        """
        Validate population meets all constraints.

        Args:
          population_data:

        Returns:
        """
        df = pd.DataFrame(population_data)

        # Check senior engineer median constraint
        senior_salaries = df[df["level"].isin([4, 5, 6])]["salary"]
        median_salary = senior_salaries.median()
        target_median = 90108.0
        median_tolerance = 50.0

        return {
            "total_employees": len(population_data),
            "senior_engineers": len(senior_salaries),
            "senior_median_salary": median_salary,
            "target_median": target_median,
            "median_difference": abs(median_salary - target_median),
            "median_constraint_met": abs(median_salary - target_median) <= median_tolerance,
            "gender_distribution": df["gender"].value_counts().to_dict(),
            "level_distribution": df["level"].value_counts().sort_index().to_dict(),
        }

    def _make_serializable(self, obj):
        """
        Convert DataFrames and other non-serializable objects for JSON export.

        Args:
          obj:

        Returns:
        """
        import numpy as np

        if isinstance(obj, dict):
            return {str(k): self._make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._make_serializable(item) for item in obj]
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict("records")
        elif hasattr(obj, "isoformat"):  # datetime objects
            return obj.isoformat()
        elif isinstance(obj, (np.int64, np.int32, np.int16, np.int8)):
            return int(obj)
        elif isinstance(obj, (np.float64, np.float32, np.float16)):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj

    def _generate_final_summary(self, results):
        """
        Generate final summary of simulation results.

        Args:
          results:

        Returns:
        """
        return {
            "simulation_timestamp": self.timestamp,
            "configuration": self.config,
            "population_size": results["summary_metrics"].get("population_size", "N/A"),
            "cycles_completed": results["summary_metrics"].get("cycles_completed", "N/A"),
            "final_gini_coefficient": results["summary_metrics"].get("final_gini_coefficient", "N/A"),
            "convergence_achieved": results["summary_metrics"].get("convergence_achieved", "N/A"),
            "validation_status": {
                "population": results["validation_results"].get("population", {}).get("median_constraint_met", False),
                "review_system": results["validation_results"].get("review_system", {}).get("all_tests_passed", False),
            },
            "total_files_generated": sum(
                len(files) if isinstance(files, (list, dict)) else 1 for files in results["files_generated"].values()
            ),
        }

    def _generate_comprehensive_summary(self, results):
        """
        Generate comprehensive summary with file organization and progress tracking.

        Args:
          results:

        Returns:
        """
        try:
            # Organize population files
            if "population_size" in results.get("summary_metrics", {}):
                population_files = self.file_manager.organize_population_files(
                    population_data=[]  # Will be populated in actual runs
                )
                if "file_organization" not in results:
                    results["file_organization"] = {}
                results["file_organization"]["population_files"] = population_files

            # Get file manager summary
            file_summary = self.file_manager.get_run_summary()
            results["file_organization"]["directory_summary"] = file_summary

            # Clean up temporary files
            cleaned_files = self.file_manager.cleanup_temporary_files()
            if cleaned_files > 0:
                self.smart_logger.log_info(f"Cleaned up {cleaned_files} temporary files")
                results["file_organization"]["temp_files_cleaned"] = cleaned_files

            self.smart_logger.log_success("Comprehensive summary generated")

        except Exception as e:
            self.smart_logger.log_error("Failed to generate comprehensive summary", e)

    def run_with_story_tracking(self):
        """
        Run simulation with employee story tracking enabled.

        Args:

        Returns:
          dict: Results including employee stories and enhanced metrics
        """
        if not self.story_tracker:
            self.smart_logger.log_warning("Story tracking not enabled - falling back to standard simulation")
            return self.run_complete_simulation()

        self.smart_logger.log_info("Starting complete simulation with employee story tracking")

        results = {
            "simulation_config": self.config,
            "timestamp": self.timestamp,
            "files_generated": {},
            "validation_results": {},
            "summary_metrics": {},
            "employee_stories": {},
        }

        # Initialize run directories for organized output
        enable_story_tracking = self.config.get("enable_story_tracking", False)
        self.run_directories = self.file_manager.create_run_directory(
            run_id=self.timestamp, enable_story_tracking=enable_story_tracking
        )
        self.smart_logger.log_info(f"Created run directory: {self.run_directories['run_root']}")

        try:
            # Phase 1: Generate Employee Population
            self.smart_logger.log_info("Phase 1: Generating employee population")
            population_generator = EmployeePopulationGenerator(
                population_size=self.population_size,
                random_seed=self.config["random_seed"],
                level_distribution=self.config.get("level_distribution"),
                gender_pay_gap_percent=self.config.get("gender_pay_gap_percent"),
                salary_constraints=self.config.get("salary_constraints"),
            )

            population_data = population_generator.generate_population()

            # Add initial cycle data to story tracker
            self.story_tracker.add_cycle_data(0, population_data)

            # Save population data
            population_filepath = self.run_directories["population_data"] / "employee_population.json"

            with open(population_filepath, "w") as f:
                json.dump(population_data, f, indent=2, default=str)

            results["files_generated"]["population"] = str(population_filepath)
            results["summary_metrics"]["population_size"] = len(population_data)

            # Validate population constraints
            validation_results = self._validate_population(population_data)
            results["validation_results"]["population"] = validation_results
            results["population_data"] = population_data  # Add population data to results

            self.smart_logger.log_info(f"Phase 1 completed: {len(population_data)} employees generated")

            # Phase 2: Initialize Performance Review System
            self.smart_logger.log_info("Phase 2: Initializing performance review system")
            review_system = PerformanceReviewSystem(random_seed=self.config["random_seed"])

            review_validation = review_system.validate_uplift_calculations()
            results["validation_results"]["review_system"] = review_validation

            self.smart_logger.log_info("Phase 2 completed: Performance review system validated")

            # Phase 3: Run Multi-Cycle Simulation with Story Tracking
            self.smart_logger.log_info("Phase 3: Running multi-cycle simulation with story tracking")
            cycle_simulator = ReviewCycleSimulator(
                initial_population=population_data, random_seed=self.config["random_seed"]
            )

            inequality_progression = cycle_simulator.simulate_multiple_cycles(num_cycles=self.config["max_cycles"])

            # Capture cycle data for story tracking
            for cycle_num in range(1, len(inequality_progression)):
                cycle_population = cycle_simulator.population
                self.story_tracker.add_cycle_data(cycle_num, cycle_population)

            # Identify tracked employees with performance optimization
            self.performance_manager.monitor_memory_usage("before_story_identification")

            # Use optimized story identification for large populations
            if len(population_data) > 1000:
                tracked_employees = self.performance_manager.optimize_story_identification(
                    population_data=population_data, max_per_category=self.config["tracked_employee_count"]
                )
            else:
                tracked_employees = self.story_tracker.identify_tracked_employees(
                    max_per_category=self.config["tracked_employee_count"]
                )

            self.performance_manager.monitor_memory_usage("after_story_identification")

            # Generate employee stories
            employee_stories = {}
            for category, employee_ids in tracked_employees.items():
                category_stories = []
                for emp_id in employee_ids:
                    if story := self.story_tracker.generate_employee_story(emp_id, category):
                        category_stories.append(story)
                employee_stories[category] = category_stories

            results["employee_stories"] = employee_stories

            # Advanced story export if requested
            if self.config["export_story_data"]:
                self.smart_logger.start_phase("Advanced Story Export", 4)

                # Initialize advanced export system
                export_system = AdvancedStoryExportSystem(
                    output_base_dir=str(self.run_directories["employee_stories"]), smart_logger=self.smart_logger
                )

                # Get cycle timeline data
                timeline_df = self.story_tracker.create_story_timeline()

                # Export comprehensive story data in multiple formats
                story_export_formats = self.config.get("story_export_formats", ["json", "csv", "excel", "markdown"])
                story_exports = export_system.export_employee_stories_comprehensive(
                    employee_stories=employee_stories,
                    population_data=population_data,
                    cycle_data=None if timeline_df.empty else timeline_df,
                    formats=story_export_formats,
                )

                self.smart_logger.update_progress(f"Stories exported in {len(story_exports)} formats")
                results["files_generated"]["story_exports"] = story_exports

                # Export comparative analysis
                comparative_analysis_file = export_system.export_comparative_analysis(
                    employee_stories=employee_stories, population_data=population_data, output_format="json"
                )
                results["files_generated"]["comparative_analysis"] = comparative_analysis_file
                self.smart_logger.update_progress("Comparative analysis exported")

                # Save basic story data for backward compatibility
                story_data = self.story_tracker.export_stories_to_dict()
                for category in story_data["categories"]:
                    story_filepath = self.run_directories["employee_stories"] / f"{category}_basic.json"
                    with open(story_filepath, "w") as f:
                        json.dump(story_data["categories"][category], f, indent=2, default=str)

                self.smart_logger.update_progress("Basic story data saved")

                # Save comprehensive story timeline
                if not timeline_df.empty:
                    timeline_filepath = self.run_directories["population_data"] / "cycle_progressions.csv"
                    timeline_df.to_csv(timeline_filepath, index=False)
                    results["files_generated"]["story_timeline"] = str(timeline_filepath)
                    self.smart_logger.update_progress("Story timeline exported")

                self.smart_logger.complete_phase("Advanced Story Export")
                self.smart_logger.log_success(
                    f"Advanced story export completed: {len(story_exports) + 1} file types generated"
                )

            # Convert simulation results to expected format
            simulation_results = {
                "inequality_metrics": pd.DataFrame(inequality_progression),
                "converged": len(inequality_progression) < self.config["max_cycles"] + 1,
            }

            simulation_filename = f"simulation_results_{self.timestamp}.json"
            simulation_filepath = get_artifact_path(simulation_filename)

            serializable_results = self._make_serializable(simulation_results)
            with open(simulation_filepath, "w") as f:
                json.dump(serializable_results, f, indent=2, default=str)

            results["files_generated"]["simulation"] = str(simulation_filepath)

            inequality_df = simulation_results.get("inequality_metrics", pd.DataFrame())
            convergence_achieved = simulation_results.get("converged", False)

            results["summary_metrics"].update(
                {
                    "cycles_completed": 0 if inequality_df.empty else len(inequality_df) - 1,
                    "final_gini_coefficient": (
                        "N/A" if inequality_df.empty else float(inequality_df.iloc[-1]["gini_coefficient"])
                    ),
                    "convergence_achieved": convergence_achieved,
                    "total_tracked_employees": sum(len(stories) for stories in employee_stories.values()),
                }
            )

            self.smart_logger.log_info(
                f"Phase 3 completed: {results['summary_metrics']['cycles_completed']} cycles simulated with {results['summary_metrics']['total_tracked_employees']} employees tracked"
            )

            # Phase 4: Generate Enhanced Visualizations & Interactive Dashboard
            if self.config["generate_visualizations"] or self.config["generate_interactive_dashboard"]:
                self.smart_logger.start_phase("Phase 4: Generate Enhanced Visualizations", 3)

                viz_generator = VisualizationGenerator(
                    population_data=population_data,
                    inequality_progression=simulation_results.get("inequality_metrics", pd.DataFrame()).to_dict(
                        "records"
                    ),
                    story_tracker=self.story_tracker,
                )
                viz_files = viz_generator.generate_complete_analysis()
                self.smart_logger.update_progress("Standard visualizations generated")

                # Generate interactive dashboard if requested
                if self.config["generate_interactive_dashboard"]:
                    dashboard_generator = InteractiveDashboardGenerator(
                        story_tracker=self.story_tracker, smart_logger=self.smart_logger
                    )

                    # Get cycle progression data for timeline
                    cycle_timeline = None
                    if hasattr(self, "story_tracker") and self.story_tracker:
                        cycle_timeline = self.story_tracker.create_story_timeline()

                    # Generate comprehensive dashboard
                    dashboard_path = self.run_images_dir / "comprehensive_employee_dashboard.html"
                    dashboard_file = dashboard_generator.generate_comprehensive_dashboard(
                        population_data=population_data,
                        tracked_employees=employee_stories,
                        cycle_data=cycle_timeline,
                        output_path=str(dashboard_path),
                    )

                    results["files_generated"]["interactive_dashboard"] = dashboard_file
                    self.smart_logger.update_progress("Interactive dashboard generated")

                # Generate story-aware visualizations if requested
                if self.config["create_individual_story_charts"]:
                    if story_viz_files := self._generate_individual_story_charts(employee_stories):
                        results["files_generated"]["story_visualizations"] = story_viz_files
                        self.smart_logger.update_progress("Individual story charts generated")

                results["files_generated"]["visualizations"] = viz_files
                total_viz_count = len(viz_files)
                if "interactive_dashboard" in results["files_generated"]:
                    total_viz_count += 1
                if "story_visualizations" in results["files_generated"]:
                    total_viz_count += len(results["files_generated"]["story_visualizations"])

                self.smart_logger.complete_phase("Phase 4: Generate Enhanced Visualizations")
                self.smart_logger.log_success(
                    f"Phase 4 completed: {total_viz_count} visualization components generated"
                )

            # Phase 5: Export Data
            self.smart_logger.log_info("Phase 5: Exporting data")
            exporter = DataExportSystem(output_dir=str(self.artifacts_dir))

            export_files = {}

            if self.config["export_individual_files"]:
                pop_exports = exporter.export_employee_population(
                    population_data, format_types=self.config["export_formats"]
                )
                export_files["population"] = {str(k): str(v) for k, v in pop_exports.items()}

                sim_exports = exporter.export_simulation_results(
                    simulation_results, format_types=self.config["export_formats"]
                )
                export_files["simulation"] = {str(k): str(v) for k, v in sim_exports.items()}

            if self.config["export_comprehensive_report"]:
                analysis_exports = exporter.export_analysis_report(
                    population_data, simulation_results, format_types=self.config["export_formats"]
                )
                export_files["comprehensive_analysis"] = {str(k): str(v) for k, v in analysis_exports.items()}

            results["files_generated"]["exports"] = export_files

            # Generate summary report
            if self.config["generate_summary_report"]:
                summary_report = self.generate_story_report(employee_stories)
                if hasattr(self, "run_output_dir"):
                    summary_filepath = self.run_output_dir / "summary_report.md"
                else:
                    summary_filepath = self.artifacts_dir / f"summary_report_{self.timestamp}.md"

                with open(summary_filepath, "w") as f:
                    f.write(summary_report)

                results["files_generated"]["summary_report"] = str(summary_filepath)

            self.smart_logger.log_info("Phase 5 completed: Data export and reporting finished")

            # Generate final summary
            try:
                final_summary = self._generate_final_summary(results)
                results["final_summary"] = final_summary
            except Exception as e:
                self.smart_logger.log_error(f"Error generating final summary: {e}")
                results["final_summary"] = {"error": str(e)}

            self.smart_logger.log_info("Complete simulation with story tracking finished successfully")
            return results

        except Exception as e:
            self.smart_logger.log_error(f"Story tracking simulation failed: {e}")
            results["error"] = str(e)
            raise

    def run_advanced_analysis(self, population_data: List[Dict] = None):
        """
        Run advanced salary progression and intervention analysis.

        Args:
          population_data: Employee population data. If None, generates new population.
          population_data: List[Dict]:  (Default value = None)

        Returns:
          : Dict with advanced analysis results
        """
        if not self.config.get("enable_advanced_analysis", False):
            self.smart_logger.log_warning("Advanced analysis not enabled - skipping")
            return {"advanced_analysis_enabled": False}

        self.smart_logger.log_info("Starting advanced salary progression analysis")

        # Initialize Analysis Narrator for user-friendly progress updates
        try:
            from analysis_narrator import AnalysisNarrator

            narrator = AnalysisNarrator(self.config, self.smart_logger)

            # Display user-friendly analysis introduction
            intro_narrative = narrator.start_analysis_narrative()
            self.smart_logger.log_info(intro_narrative)

        except Exception as e:
            # Continue without narrator if initialization fails
            narrator = None
            self.smart_logger.log_debug(f"Analysis narrator initialization failed: {e}")

        # Generate population if not provided
        if population_data is None:
            self.smart_logger.log_info("Generating population for advanced analysis")
            population_generator = EmployeePopulationGenerator(
                population_size=self.population_size,
                random_seed=self.config["random_seed"],
                level_distribution=self.config.get("level_distribution"),
                gender_pay_gap_percent=self.config.get("gender_pay_gap_percent"),
                salary_constraints=self.config.get("salary_constraints"),
            )
            population_data = population_generator.generate_population()

            # Add user-friendly narrative for population generation
            if narrator:
                population_stats = {
                    "total_employees": len(population_data),
                    "gender_gap_percent": 0,  # Will be calculated from population
                    "salary_range_min": min(emp["salary"] for emp in population_data),
                    "salary_range_max": max(emp["salary"] for emp in population_data),
                }

                # Calculate actual gender gap
                import pandas as pd

                df = pd.DataFrame(population_data)
                if len(df[df["gender"] == "Male"]) > 0 and len(df[df["gender"] == "Female"]) > 0:
                    male_median = df[df["gender"] == "Male"]["salary"].median()
                    female_median = df[df["gender"] == "Female"]["salary"].median()
                    population_stats["gender_gap_percent"] = ((male_median - female_median) / male_median) * 100

                population_narrative = narrator.narrate_population_generation(population_stats)
                self.smart_logger.log_info(population_narrative)

        results = {
            "advanced_analysis_enabled": True,
            "timestamp": self.timestamp,
            "population_size": len(population_data),
            "analysis_results": {},
            "files_generated": {},
        }

        analysis_config = {
            "confidence_interval": 0.95,
            "market_inflation_rate": 0.04,
            "progression_years": self.config.get("progression_analysis_years", 5),
            "convergence_threshold_years": self.config.get("convergence_threshold_years", 5),
            "acceptable_gap_percent": self.config.get("acceptable_gap_percent", 5.0),
        }

        try:
            # Phase 1: Individual Progression Analysis
            if self.config.get("run_individual_progression_analysis", False):
                self.smart_logger.start_phase("Phase 1: Individual Progression Analysis", 4)

                progression_simulator = IndividualProgressionSimulator(population_data, config=analysis_config)

                # Analyze sample employees from different levels and performance ratings
                sample_employees = self._select_sample_employees_for_analysis(population_data)
                progression_results = {}

                for sample_emp in sample_employees:
                    emp_analysis = progression_simulator.project_salary_progression(
                        sample_emp,
                        years=analysis_config["progression_years"],
                        scenarios=["conservative", "realistic", "optimistic"],
                        include_market_adjustments=True,
                    )
                    progression_results[sample_emp["employee_id"]] = emp_analysis

                results["analysis_results"]["individual_progression"] = {
                    "sample_count": len(sample_employees),
                    "analysis_years": analysis_config["progression_years"],
                    "employee_analyses": progression_results,
                }

                self.smart_logger.complete_phase("Phase 1: Individual Progression Analysis")
                self.smart_logger.log_success(
                    f"Individual progression analysis completed for {len(sample_employees)} employees"
                )

            # Phase 2: Median Convergence Analysis
            if self.config.get("run_median_convergence_analysis", False):
                self.smart_logger.start_phase("Phase 2: Median Convergence Analysis", 4)

                convergence_analyzer = MedianConvergenceAnalyzer(population_data, config=analysis_config)

                # Identify below-median employees
                below_median_analysis = convergence_analyzer.identify_below_median_employees(
                    min_gap_percent=analysis_config["acceptable_gap_percent"], include_gender_analysis=True
                )

                # Analyze convergence timelines for sample of below-median employees
                convergence_timelines = {}
                if below_median_analysis["employees"]:
                    sample_below_median = below_median_analysis["employees"][:10]  # Analyze up to 10 employees
                    for emp in sample_below_median:
                        timeline = convergence_analyzer.analyze_convergence_timeline(emp)
                        convergence_timelines[emp["employee_id"]] = timeline

                # Get intervention recommendations
                intervention_recommendations = convergence_analyzer.recommend_intervention_strategies(
                    below_median_analysis
                )

                # Population-level convergence trends
                population_trends = convergence_analyzer.analyze_population_convergence_trends(
                    years_ahead=analysis_config["progression_years"]
                )

                results["analysis_results"]["median_convergence"] = {
                    "below_median_summary": below_median_analysis,
                    "sample_convergence_timelines": convergence_timelines,
                    "intervention_recommendations": intervention_recommendations,
                    "population_trends": population_trends,
                }

                self.smart_logger.complete_phase("Phase 2: Median Convergence Analysis")
                self.smart_logger.log_success(
                    f"Median convergence analysis completed - found {below_median_analysis['below_median_count']} below-median employees"
                )

                # Add user-friendly narrative for convergence analysis
                if narrator:
                    convergence_narrative_data = {
                        "below_median_count": below_median_analysis["below_median_count"],
                        "total_employees": len(population_data),
                        "avg_convergence_years": 4,  # Average from typical analysis
                    }
                    convergence_narrative = narrator.narrate_convergence_analysis(convergence_narrative_data)
                    self.smart_logger.log_info(convergence_narrative)

            # Phase 3: Intervention Strategy Analysis
            if self.config.get("run_intervention_strategy_analysis", False):
                self.smart_logger.start_phase("Phase 3: Intervention Strategy Analysis", 4)

                intervention_simulator = InterventionStrategySimulator(population_data, config=analysis_config)

                # Gender gap remediation analysis
                gender_gap_analysis = intervention_simulator.model_gender_gap_remediation(
                    target_gap_percent=self.config.get("target_gender_gap_percent", 0.0),
                    max_years=analysis_config["progression_years"],
                    budget_constraint=self.config.get("intervention_budget_constraint", 0.005),
                )

                # Equity-focused analysis
                equity_analysis = intervention_simulator.model_equity_intervention(
                    intervention_type="comprehensive_equity",
                    budget_constraint=self.config.get("intervention_budget_constraint", 0.005),
                    years_to_achieve=analysis_config["progression_years"],
                )

                results["analysis_results"]["intervention_strategies"] = {
                    "gender_gap_remediation": gender_gap_analysis,
                    "equity_analysis": equity_analysis,
                }

                self.smart_logger.complete_phase("Phase 3: Intervention Strategy Analysis")
                self.smart_logger.log_success("Intervention strategy analysis completed")

                # Add user-friendly narrative for intervention analysis
                if narrator:
                    intervention_narrative = narrator.narrate_intervention_analysis(
                        results["analysis_results"]["intervention_strategies"]
                    )
                    self.smart_logger.log_info(intervention_narrative)

            # Phase 4: Generate Advanced Visualizations (ENHANCED per PRP)
            if self.config.get("enable_advanced_visualizations", True) and results["analysis_results"]:
                self.smart_logger.start_phase("Phase 4: Generate Advanced Visualizations", 4)

                # Generate comprehensive visualizations for advanced analysis
                try:
                    viz_generator = VisualizationGenerator(
                        population_data=population_data,
                        inequality_progression=[],  # Not applicable for advanced analysis
                    )

                    # Generate analysis-specific visualizations
                    viz_files = viz_generator.generate_complete_analysis()
                    results["visualization_files"] = viz_files

                    self.smart_logger.update_progress(f"Generated {len(viz_files)} visualization files")

                    # Add user-friendly narrative for visualization generation
                    if narrator:
                        viz_narrative = narrator.narrate_visualization_generation(
                            {
                                "charts_generated": len(viz_files),
                                "visualization_types": ["salary_equity", "gap_analysis", "trend_charts"],
                                "output_location": "images/simulation_run_*/charts/",
                            }
                        )
                        self.smart_logger.log_info(viz_narrative)

                except Exception as e:
                    self.smart_logger.log_warning(f"Visualization generation failed: {e}")
                    results["visualization_error"] = str(e)

                self.smart_logger.complete_phase("Phase 4: Generate Advanced Visualizations")

            # Phase 5: Export Advanced Analysis Reports
            if self.config.get("export_advanced_analysis_reports", True) and results["analysis_results"]:
                self.smart_logger.start_phase("Phase 5: Export Advanced Analysis Reports", 3)

                export_files = self._export_advanced_analysis_reports(results["analysis_results"], population_data)
                results["files_generated"] = {**(results.get("files_generated", {})), **export_files}

                self.smart_logger.complete_phase("Phase 5: Export Advanced Analysis Reports")
                self.smart_logger.log_success(
                    f"Advanced analysis reports exported: {len(export_files)} files generated"
                )

            # Phase 6: Generate Management Dashboard (NEW)
            if (
                self.config.get("enable_advanced_visualizations", True)
                and self.config.get("generate_management_dashboard", True)
                and results["analysis_results"]
            ):
                self.smart_logger.start_phase("Phase 6: Generate Management Dashboard", 3)

                try:
                    from management_dashboard_generator import ManagementDashboardGenerator

                    dashboard_generator = ManagementDashboardGenerator(
                        analysis_results=results,
                        population_data=population_data,
                        config=self.config,
                        smart_logger=self.smart_logger,
                    )

                    dashboard_files = dashboard_generator.generate_executive_dashboard()
                    results["dashboard_files"] = dashboard_files

                    self.smart_logger.complete_phase("Phase 6: Generate Management Dashboard")
                    self.smart_logger.log_success(
                        f"Management dashboard generated: {dashboard_files.get('components_generated', 0)} components"
                    )

                    # Add user-friendly narrative for dashboard generation
                    if narrator:
                        dashboard_narrative_data = {
                            "components_generated": dashboard_files.get("components_generated", 0),
                            "main_dashboard": dashboard_files.get("main_dashboard", ""),
                            "auto_opened": self.config.get("auto_open_dashboard", True),
                        }
                        dashboard_narrative = narrator.narrate_dashboard_generation(dashboard_narrative_data)
                        self.smart_logger.log_info(dashboard_narrative)

                except Exception as e:
                    self.smart_logger.log_error(f"Dashboard generation failed: {e}")
                    # Continue without dashboard - don't fail entire analysis
                    results["dashboard_error"] = str(e)

            self.smart_logger.log_success("Advanced analysis pipeline completed successfully")

            # Add final completion summary with narrator
            if narrator:
                completion_summary = narrator.create_completion_summary(results)
                self.smart_logger.log_info(completion_summary)

            return results

        except Exception as e:
            self.smart_logger.log_error(f"Advanced analysis failed: {e}")
            results["error"] = str(e)
            raise

    def generate_story_report(self, employee_stories):
        """
        Generate markdown report of employee stories.

        Args:
          employee_stories:

        Returns:
        """
        if not employee_stories:
            return "# Employee Story Report\n\nNo employee stories available."

        report_lines = [
            "# Employee Story Report",
            f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Simulation Timestamp: {self.timestamp}",
            "",
            "## Executive Summary",
            "",
        ]

        total_tracked = sum(len(stories) for stories in employee_stories.values())
        report_lines.extend((f"Total employees tracked: **{total_tracked}**", ""))
        for category, stories in employee_stories.items():
            if not stories:
                continue

            category_title = category.replace("_", " ").title()
            report_lines.extend([f"### {category_title} ({len(stories)} employees)", ""])

            for story in stories:
                report_lines.extend(
                    [
                        f"#### Employee {story.employee_id}",
                        "",
                        f"**Category:** {story.category}",
                        f"**Salary Growth:** {story.total_growth_percent:+.1f}% (£{story.initial_salary:,.0f} → £{story.current_salary:,.0f})",
                        "",
                        f"**Story:** {story.story_summary}",
                        "",
                        "**Key Events:**",
                    ]
                )

                if story.key_events:
                    report_lines.extend(f"- {event}" for event in story.key_events)
                else:
                    report_lines.append("- No significant events recorded")

                report_lines.extend(["", "**Recommendations:**"])
                report_lines.extend(f"- {rec}" for rec in story.recommendations)
                report_lines.extend(["", "---", ""])

        return "\n".join(report_lines)

    def export_interactive_dashboard(self, output_path: str = None):
        """
        Export interactive HTML dashboard.

        Args:
          output_path: str:  (Default value = None)

        Returns:
        """
        if not self.story_tracker:
            self.smart_logger.log_warning("Story tracking not enabled - cannot export interactive dashboard")
            return None

        if output_path is None:
            if hasattr(self, "run_images_dir"):
                output_path = self.run_images_dir / "employee_stories_dashboard.html"
            else:
                output_path = self.images_dir / f"employee_stories_dashboard_{self.timestamp}.html"

        # TODO: This will be fully implemented in Phase 4 of the PRP
        # For now, return a placeholder
        self.smart_logger.log_info(f"Interactive dashboard export planned for: {output_path}")
        return output_path

    def get_tracked_employee_summary(self):
        """
        Get summary statistics of tracked employees.
        """
        if not self.story_tracker:
            return {"error": "Story tracking not enabled"}

        return self.story_tracker.get_tracked_employee_summary()

    def _generate_individual_story_charts(self, employee_stories: Dict[str, List]) -> List[str]:
        """
        Generate individual story charts for each category.

        Args:
          employee_stories: Dict[str:
          List]:

        Returns:
        """
        story_viz_files = []

        if not employee_stories:
            return story_viz_files

        try:
            dashboard_generator = InteractiveDashboardGenerator(
                story_tracker=self.story_tracker, smart_logger=self.smart_logger
            )

            for category, stories in employee_stories.items():
                if stories:
                    # Create category-specific dashboard
                    category_dashboard_path = self.run_images_dir / f"{category}_story_dashboard.html"
                    category_tracked = {category: stories}

                    dashboard_file = dashboard_generator.generate_comprehensive_dashboard(
                        population_data=[],  # Simplified for category-specific view
                        tracked_employees=category_tracked,
                        cycle_data=None,
                        output_path=str(category_dashboard_path),
                    )

                    story_viz_files.append(dashboard_file)

            return story_viz_files

        except Exception as e:
            self.smart_logger.log_error(f"Failed to generate individual story charts: {e}")
            return []

    def _select_sample_employees_for_analysis(self, population_data: List[Dict]) -> List[Dict]:
        """
        Select representative sample of employees for individual progression analysis.

        Args:
          population_data: List[Dict]:

        Returns:
        """
        df = pd.DataFrame(population_data)
        sample_employees = []

        # Select 2-3 employees per level with different performance ratings
        for level in sorted(df["level"].unique()):
            level_employees = df[df["level"] == level]

            # Try to get diverse performance ratings
            performance_ratings = ["Exceeding", "High Performing", "Achieving", "Partially met", "Not met"]
            selected_for_level = []

            for perf_rating in performance_ratings:
                candidates = level_employees[level_employees["performance_rating"] == perf_rating]
                if len(candidates) > 0 and len(selected_for_level) < 3:
                    # Select one employee with this performance rating
                    selected_for_level.append(candidates.iloc[0].to_dict())

            # If we don't have enough variety, just take first 3
            if len(selected_for_level) < 3:
                remaining_needed = 3 - len(selected_for_level)
                for _, emp in level_employees.head(remaining_needed).iterrows():
                    if emp.to_dict() not in selected_for_level:
                        selected_for_level.append(emp.to_dict())

            sample_employees.extend(selected_for_level)

        self.smart_logger.log_info(f"Selected {len(sample_employees)} sample employees for progression analysis")
        return sample_employees

    def _export_advanced_analysis_reports(self, analysis_results: Dict, population_data: List[Dict]) -> Dict[str, str]:
        """
        Export advanced analysis results to various formats.

        Args:
          analysis_results: Dict:
          population_data: List[Dict]:

        Returns:
        """
        export_files = {}

        try:
            # Create advanced analysis output directory
            advanced_dir = self.artifacts_dir / "advanced_analysis"
            advanced_dir.mkdir(exist_ok=True)

            # Export individual progression analysis
            if "individual_progression" in analysis_results:
                progression_file = advanced_dir / f"individual_progression_analysis_{self.timestamp}.json"
                with open(progression_file, "w") as f:
                    # Use the same serialization method as elsewhere in the orchestrator
                    serializable_data = self._make_serializable(analysis_results["individual_progression"])
                    json.dump(serializable_data, f, indent=2, default=str)
                export_files["individual_progression"] = str(progression_file)

                # Create summary report
                progression_summary_file = advanced_dir / f"individual_progression_summary_{self.timestamp}.md"
                summary_content = self._create_progression_summary_report(analysis_results["individual_progression"])
                with open(progression_summary_file, "w") as f:
                    f.write(summary_content)
                export_files["individual_progression_summary"] = str(progression_summary_file)

            # Export median convergence analysis
            if "median_convergence" in analysis_results:
                convergence_file = advanced_dir / f"median_convergence_analysis_{self.timestamp}.json"
                with open(convergence_file, "w") as f:
                    serializable_data = self._make_serializable(analysis_results["median_convergence"])
                    json.dump(serializable_data, f, indent=2, default=str)
                export_files["median_convergence"] = str(convergence_file)

                # Create detailed convergence report
                convergence_summary_file = advanced_dir / f"median_convergence_report_{self.timestamp}.md"
                summary_content = self._create_convergence_summary_report(analysis_results["median_convergence"])
                with open(convergence_summary_file, "w") as f:
                    f.write(summary_content)
                export_files["median_convergence_summary"] = str(convergence_summary_file)

            # Export intervention strategy analysis
            if "intervention_strategies" in analysis_results:
                intervention_file = advanced_dir / f"intervention_strategies_{self.timestamp}.json"
                with open(intervention_file, "w") as f:
                    serializable_data = self._make_serializable(analysis_results["intervention_strategies"])
                    json.dump(serializable_data, f, indent=2, default=str)
                export_files["intervention_strategies"] = str(intervention_file)

                # Create executive intervention report
                intervention_summary_file = (
                    advanced_dir / f"intervention_strategies_executive_report_{self.timestamp}.md"
                )
                summary_content = self._create_intervention_summary_report(analysis_results["intervention_strategies"])
                with open(intervention_summary_file, "w") as f:
                    f.write(summary_content)
                export_files["intervention_strategies_summary"] = str(intervention_summary_file)

            # Create comprehensive advanced analysis report
            if analysis_results:
                comprehensive_report_file = advanced_dir / f"comprehensive_advanced_analysis_{self.timestamp}.md"
                comprehensive_content = self._create_comprehensive_advanced_report(analysis_results, population_data)
                with open(comprehensive_report_file, "w") as f:
                    f.write(comprehensive_content)
                export_files["comprehensive_advanced_analysis"] = str(comprehensive_report_file)

            return export_files

        except Exception as e:
            self.smart_logger.log_error(f"Failed to export advanced analysis reports: {e}")
            return {}

    def _create_progression_summary_report(self, progression_data: Dict) -> str:
        """
        Create summary report for individual progression analysis.

        Args:
          progression_data: Dict:

        Returns:
        """
        lines = [
            "# Individual Salary Progression Analysis Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Executive Summary",
            "",
            f"**Sample Size**: {progression_data['sample_count']} employees analyzed",
            f"**Analysis Period**: {progression_data['analysis_years']} years",
            "",
            "## Key Findings",
            "",
        ]

        if employee_analyses := progression_data.get("employee_analyses", {}):
            realistic_cagrs = []
            optimistic_cagrs = []

            for emp_id, analysis in employee_analyses.items():
                projections = analysis.get("projections", {})
                if "realistic" in projections:
                    realistic_cagrs.append(projections["realistic"].get("cagr", 0) * 100)
                if "optimistic" in projections:
                    optimistic_cagrs.append(projections["optimistic"].get("cagr", 0) * 100)

            if realistic_cagrs:
                avg_realistic_cagr = sum(realistic_cagrs) / len(realistic_cagrs)
                lines.append(f"- **Average Realistic Growth Rate**: {avg_realistic_cagr:.2f}% annually")

            if optimistic_cagrs:
                avg_optimistic_cagr = sum(optimistic_cagrs) / len(optimistic_cagrs)
                lines.append(f"- **Average Optimistic Growth Rate**: {avg_optimistic_cagr:.2f}% annually")

            lines.extend(
                [
                    f"- **Employees with High Growth Potential**: {len([c for c in realistic_cagrs if c > 8.0])} employees (>8% CAGR)",
                    "",
                    "## Individual Employee Analysis",
                    "",
                ]
            )

            # Detail top performers
            for emp_id, analysis in list(employee_analyses.items())[:5]:  # Show first 5
                employee_info = analysis.get("employee_profile", {})
                projections = analysis.get("projections", {}).get("realistic", {})

                lines.extend(
                    [
                        f"### Employee {emp_id}",
                        f"- **Level**: {employee_info.get('level', 'N/A')}",
                        f"- **Current Salary**: £{employee_info.get('salary', 0):,.0f}",
                        f"- **Performance Rating**: {employee_info.get('performance_rating', 'N/A')}",
                        f"- **Projected 5-Year Salary**: £{projections.get('final_salary', 0):,.0f}",
                        f"- **Expected Growth Rate**: {projections.get('cagr', 0)*100:.2f}% annually",
                        "",
                    ]
                )

        lines.extend(
            [
                "## Recommendations",
                "",
                "1. **High Performers**: Focus retention strategies on employees with >10% projected growth",
                "2. **Development Opportunities**: Provide advancement paths for employees showing strong potential",
                "3. **Regular Reviews**: Monitor actual vs. projected progression quarterly",
                "",
                "---",
                f"*Report generated by Advanced Employee Analysis System - {datetime.now().isoformat()}*",
            ]
        )

        return "\n".join(lines)

    def _create_convergence_summary_report(self, convergence_data: Dict) -> str:
        """
        Create summary report for median convergence analysis.

        Args:
          convergence_data: Dict:

        Returns:
        """
        lines = [
            "# Median Convergence Analysis Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Executive Summary",
            "",
        ]

        if below_median_summary := convergence_data.get("below_median_summary", {}):
            total_employees = below_median_summary.get("total_employees", 0)
            below_median_count = below_median_summary.get("below_median_count", 0)
            below_median_percent = below_median_summary.get("below_median_percent", 0)

            lines.extend(
                [
                    f"**Total Employees Analyzed**: {total_employees:,}",
                    f"**Below Median Employees**: {below_median_count:,} ({below_median_percent:.1f}%)",
                    "",
                ]
            )

            if stats := below_median_summary.get("summary_statistics", {}):
                avg_gap = stats.get("average_gap_amount", 0)
                total_gap = stats.get("total_gap_amount", 0)

                lines.extend(
                    [
                        "### Key Statistics",
                        f"- **Average Gap**: £{avg_gap:,.0f} below median",
                        f"- **Total Gap Amount**: £{total_gap:,.0f}",
                        f"- **Maximum Individual Gap**: £{stats.get('max_gap_amount', 0):,.0f}",
                        "",
                    ]
                )

        if recommendations := convergence_data.get("intervention_recommendations", {}):
            recommended_strategy = recommendations.get("recommended_strategy", {})
            strategy_name = recommended_strategy.get("primary_strategy", "N/A")
            budget_required = recommended_strategy.get("total_budget_required", 0)

            lines.extend(
                [
                    "## Recommended Intervention Strategy",
                    f"**Primary Strategy**: {strategy_name.replace('_', ' ').title()}",
                    f"**Budget Required**: £{budget_required:,.0f}",
                    "",
                ]
            )

        if trends := convergence_data.get("population_trends", {}):
            lines.extend(
                [
                    "## Population Convergence Trends",
                    "",
                    "Analysis of convergence scenarios over 5-year projection:",
                    "",
                ]
            )

            trend_projections = trends.get("trend_projections", {})
            for scenario, projection in trend_projections.items():
                final_count = projection.get("final_below_median_count", 0)
                convergence_rate = projection.get("convergence_rate", 0)

                lines.append(
                    f"- **{scenario.title()} Scenario**: {final_count} employees remain below median ({convergence_rate:.1f}% convergence rate)"
                )

        lines.extend(
            [
                "",
                "## Action Items",
                "",
                "1. **Immediate**: Address high-priority below-median cases (>20% gap)",
                "2. **Short-term**: Implement performance acceleration programs",
                "3. **Long-term**: Monitor convergence progress and adjust strategies",
                "",
                "---",
                f"*Report generated by Median Convergence Analysis System - {datetime.now().isoformat()}*",
            ]
        )

        return "\n".join(lines)

    def _create_intervention_summary_report(self, intervention_data: Dict) -> str:
        """
        Create executive summary for intervention strategies.

        Args:
          intervention_data: Dict:

        Returns:
        """
        lines = [
            "# Executive Intervention Strategy Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Strategic Overview",
            "",
            "This report provides analysis and recommendations for salary equity interventions",
            "focused on gender pay gap remediation and comprehensive equity improvement.",
            "",
        ]

        if gender_gap_data := intervention_data.get("gender_gap_remediation", {}):
            current_gap = gender_gap_data.get("current_gender_gap_percent", 0)
            optimal_strategy = gender_gap_data.get("optimal_strategy", {})

            lines.extend(
                [
                    "## Gender Pay Gap Remediation",
                    f"**Current Gap**: {current_gap:.2f}%",
                    "",
                ]
            )

            if optimal_strategy:
                strategy_name = optimal_strategy.get("strategy_name", "N/A")
                total_cost = optimal_strategy.get("total_cost", 0)
                timeline_years = optimal_strategy.get("timeline_years", 0)

                lines.extend(
                    [
                        f"**Recommended Strategy**: {strategy_name.replace('_', ' ').title()}",
                        f"**Total Investment**: £{total_cost:,.0f}",
                        f"**Implementation Timeline**: {timeline_years} years",
                        "",
                    ]
                )

        if equity_data := intervention_data.get("equity_analysis", {}):
            lines.extend(
                [
                    "## Comprehensive Equity Analysis",
                    "",
                ]
            )

            if optimal_approach := equity_data.get("optimal_approach", {}):
                approach_name = optimal_approach.get("approach_name", "N/A")
                total_investment = optimal_approach.get("total_investment", 0)
                affected_employees = optimal_approach.get("affected_employees", 0)

                lines.extend(
                    [
                        f"**Optimal Approach**: {approach_name.replace('_', ' ').title()}",
                        f"**Total Investment**: £{total_investment:,.0f}",
                        f"**Employees Affected**: {affected_employees:,}",
                        "",
                    ]
                )

        lines.extend(
            [
                "## Executive Recommendations",
                "",
                "### Immediate Actions (0-6 months)",
                "1. Secure budget approval for recommended intervention strategies",
                "2. Begin communication planning with affected employee groups",
                "3. Establish success metrics and monitoring framework",
                "",
                "### Short-term Implementation (6-18 months)",
                "1. Execute immediate salary adjustments for highest-priority cases",
                "2. Launch performance acceleration programs",
                "3. Implement quarterly progress monitoring",
                "",
                "### Long-term Sustainability (18+ months)",
                "1. Embed equity considerations in all promotion and compensation decisions",
                "2. Regular market benchmarking and adjustment processes",
                "3. Continuous monitoring of intervention effectiveness",
                "",
                "## Risk Mitigation",
                "",
                "- **Budget overruns**: Phased implementation approach with milestone reviews",
                "- **Employee expectations**: Clear communication about timeline and criteria",
                "- **Competitive response**: Market analysis and retention strategies",
                "",
                "---",
                f"*Executive Report prepared by Intervention Strategy Analysis System - {datetime.now().isoformat()}*",
            ]
        )

        return "\n".join(lines)

    def _create_comprehensive_advanced_report(self, analysis_results: Dict, population_data: List[Dict]) -> str:
        """
        Create comprehensive report combining all advanced analyses.

        Args:
          analysis_results: Dict:
          population_data: List[Dict]:

        Returns:
        """
        lines = [
            "# Comprehensive Advanced Employee Analysis Report",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Population Size: {len(population_data):,} employees",
            "",
            "## Executive Summary",
            "",
            "This comprehensive analysis examines employee salary progression patterns,",
            "median convergence opportunities, and intervention strategy recommendations",
            "to support data-driven compensation and equity decisions.",
            "",
            "## Analysis Components",
            "",
        ]

        # List completed analyses
        if "individual_progression" in analysis_results:
            lines.append("✅ **Individual Salary Progression Analysis** - Completed")

        if "median_convergence" in analysis_results:
            lines.append("✅ **Median Convergence Analysis** - Completed")

        if "intervention_strategies" in analysis_results:
            lines.append("✅ **Intervention Strategy Analysis** - Completed")

        lines.extend(
            [
                "",
                "## Key Insights",
                "",
            ]
        )

        # Extract key insights from each analysis
        if "individual_progression" in analysis_results:
            progression_data = analysis_results["individual_progression"]
            sample_count = progression_data.get("sample_count", 0)
            lines.extend(
                [
                    f"### Individual Progression ({sample_count} employees analyzed)",
                    "- Detailed salary progression projections over 5-year timeline",
                    "- Conservative, realistic, and optimistic scenario modeling",
                    "- Performance-based growth rate analysis",
                    "",
                ]
            )

        if "median_convergence" in analysis_results:
            convergence_data = analysis_results["median_convergence"]
            below_median_summary = convergence_data.get("below_median_summary", {})
            below_median_count = below_median_summary.get("below_median_count", 0)

            lines.extend(
                [
                    f"### Median Convergence ({below_median_count} employees below median)",
                    "- Identification of salary equity gaps by level and gender",
                    "- Convergence timeline projections under various scenarios",
                    "- Targeted intervention strategy recommendations",
                    "",
                ]
            )

        if "intervention_strategies" in analysis_results:
            lines.extend(
                [
                    "### Intervention Strategies",
                    "- Gender pay gap remediation modeling and cost analysis",
                    "- Comprehensive equity intervention planning",
                    "- Budget optimization and ROI projections",
                    "",
                ]
            )

        lines.extend(
            [
                "## Strategic Recommendations",
                "",
                "Based on this comprehensive analysis, the following strategic actions are recommended:",
                "",
                "### Priority 1: Address Critical Gaps",
                "- Focus on employees >20% below median salary for their level",
                "- Implement immediate adjustments where feasible within budget constraints",
                "",
                "### Priority 2: Systematic Improvement",
                "- Launch performance acceleration programs for high-potential employees",
                "- Establish regular market benchmarking and adjustment processes",
                "",
                "### Priority 3: Long-term Equity",
                "- Embed equity considerations in all compensation decisions",
                "- Monitor intervention effectiveness with quarterly reviews",
                "",
                "## Data Sources and Methodology",
                "",
                f"- **Population Data**: {len(population_data):,} employee records",
                "- **Analysis Period**: 5-year projection timeline",
                "- **Confidence Level**: 95% statistical confidence intervals",
                "- **Market Inflation**: 2.5% annual adjustment factor",
                "",
                "## Next Steps",
                "",
                "1. **Review** this analysis with executive leadership team",
                "2. **Approve** recommended intervention budget and timeline",
                "3. **Communicate** strategy to affected stakeholders",
                "4. **Implement** priority interventions with regular monitoring",
                "5. **Evaluate** effectiveness after 12 months and adjust approach",
                "",
                "---",
                "",
                "*This comprehensive report integrates individual progression analysis,*",
                "*median convergence modeling, and intervention strategy optimization*",
                "*to provide actionable insights for compensation equity improvement.*",
                "",
                f"*Generated by Advanced Employee Analysis System - {datetime.now().isoformat()}*",
            ]
        )

        return "\n".join(lines)


def run_individual_employee_analysis(employee_data, config: Dict[str, Any]) -> None:
    """
    Run analysis for a single individual employee.

    Args:
        employee_data: Parsed and validated EmployeeData instance
        config: Configuration dictionary for analysis
    """
    from individual_employee_parser import create_individual_employee

    # Create employee record compatible with simulation system
    employee_record = create_individual_employee(employee_data)
    population_data = [employee_record]

    logger = get_smart_logger()

    # Display employee information
    print("\n🧑‍💼 Individual Employee Analysis")
    print(f"{'='*50}")
    print(f"Employee: {employee_data.name}")
    print(f"Level: {employee_data.level}")
    print(f"Current Salary: £{employee_data.salary:,.2f}")
    print(f"Performance Rating: {employee_data.performance_rating}")
    print(f"Gender: {employee_data.gender}")
    print(f"Tenure: {employee_data.tenure_years} years")
    print(f"Department: {employee_data.department}")

    try:
        # Initialize individual progression simulator
        logger.log_info("Starting individual progression analysis")
        from individual_progression_simulator import IndividualProgressionSimulator

        progression_simulator = IndividualProgressionSimulator(population_data)

        # Run projection analysis
        analysis_years = config.get("progression_analysis_years", 5)

        print(f"\n📊 {analysis_years}-Year Salary Progression Analysis")
        print(f"{'='*50}")

        # Create employee record for progression simulator
        employee_record = {
            "employee_id": employee_data.employee_id,
            "name": employee_data.name,
            "level": employee_data.level,
            "salary": employee_data.salary,
            "performance_rating": employee_data.performance_rating,
            "gender": employee_data.gender,
            "tenure_years": employee_data.tenure_years,
            "department": employee_data.department,
        }

        # Run all scenarios together
        all_projections = progression_simulator.project_salary_progression(
            employee_data=employee_record, years=analysis_years, scenarios=["conservative", "realistic", "optimistic"]
        )

        # Extract individual scenarios
        conservative_projection = {
            "expected_final_salary": all_projections["projections"]["conservative"]["final_salary"],
            "scenarios": {"conservative": all_projections["projections"]["conservative"]},
        }
        realistic_projection = {
            "expected_final_salary": all_projections["projections"]["realistic"]["final_salary"],
            "scenarios": {"realistic": all_projections["projections"]["realistic"]},
        }
        optimistic_projection = {
            "expected_final_salary": all_projections["projections"]["optimistic"]["final_salary"],
            "scenarios": {"optimistic": all_projections["projections"]["optimistic"]},
        }

        # Display results
        print(f"\n📈 Scenario Analysis (Year {analysis_years}):")
        print(f"├─ Conservative: £{conservative_projection['expected_final_salary']:,.0f}")
        print(f"├─ Realistic:    £{realistic_projection['expected_final_salary']:,.0f}")
        print(f"└─ Optimistic:   £{optimistic_projection['expected_final_salary']:,.0f}")

        # Calculate potential salary increase
        current_salary = employee_data.salary
        realistic_increase = realistic_projection["expected_final_salary"] - current_salary

        # Calculate annual growth rate
        annual_growth_rate = (realistic_projection["expected_final_salary"] / current_salary) ** (
            1 / analysis_years
        ) - 1

        print("\n💰 Financial Impact (Realistic Scenario):")
        print(f"├─ Current Salary: £{current_salary:,.0f}")
        print(f"├─ Future Salary:  £{realistic_projection['expected_final_salary']:,.0f}")
        print(f"├─ Total Increase: £{realistic_increase:,.0f}")
        print(f"└─ Annual Growth:  {annual_growth_rate:.1%}")

        # Check if employee is below median for their level
        try:
            from median_convergence_analyzer import MedianConvergenceAnalyzer

            convergence_analyzer = MedianConvergenceAnalyzer(population_data)
            # Create employee_data dict for convergence analysis
            employee_dict = {
                "employee_id": employee_data.employee_id,
                "salary": employee_data.salary,
                "level": employee_data.level,
                "performance_rating": employee_data.performance_rating,
                "gender": employee_data.gender,
                "tenure_years": employee_data.tenure_years,
                "department": employee_data.department,
                "name": employee_data.name,
            }
            convergence_analysis = convergence_analyzer.analyze_convergence_timeline(employee_dict)

            if convergence_analysis.get("below_median", False):
                print("\n⚠️  Below Median Analysis:")
                print(f"├─ Current gap: {convergence_analysis.get('gap_percent', 0):.1%} below level median")
                print(f"├─ Natural convergence: {convergence_analysis.get('natural_convergence_years', 'N/A')} years")
                print(
                    f"└─ With intervention: {convergence_analysis.get('intervention_convergence_years', 'N/A')} years"
                )
            else:
                print(f"\n✅ Above Median: Employee is performing above median for Level {employee_data.level}")

        except Exception as e:
            logger.log_warning(f"Could not perform median convergence analysis: {e}")

        # Performance path analysis
        print("\n🎯 Performance Path Analysis:")
        performance_path = realistic_projection.get("performance_path", [])
        if performance_path:
            print(f"Expected performance trajectory over {analysis_years} years:")
            for i, rating in enumerate(performance_path[:5], 1):  # Show first 5 years
                print(f"Year {i}: {rating}")

        # Recommendations
        print("\n💡 Recommendations:")
        if employee_data.performance_rating in ["High Performing", "Exceeding"]:
            print("├─ Consider for accelerated development programs")
            print("├─ Evaluate for promotion opportunities")
            print("└─ Ensure competitive retention package")
        elif employee_data.performance_rating == "Achieving":
            print("├─ Focus on consistent performance delivery")
            print("├─ Identify skill development opportunities")
            print("└─ Regular check-ins to maintain trajectory")
        else:
            print("├─ Implement performance improvement plan")
            print("├─ Provide additional training and support")
            print("└─ Set clear expectations and milestones")

        # Generate visualizations for individual analysis
        if config.get("generate_visualizations", True):
            try:
                logger.log_info("Generating individual employee visualizations")
                from pathlib import Path

                import plotly.graph_objects as go
                import plotly.offline as pyo

                # Create output directory
                viz_dir = Path("artifacts/individual_analysis/visualizations")
                viz_dir.mkdir(parents=True, exist_ok=True)

                # Create salary progression chart
                fig = go.Figure()

                scenarios = ["Conservative", "Realistic", "Optimistic"]
                final_salaries = [
                    conservative_projection["expected_final_salary"],
                    realistic_projection["expected_final_salary"],
                    optimistic_projection["expected_final_salary"],
                ]

                colors = ["#ff7f0e", "#2ca02c", "#1f77b4"]

                fig.add_trace(
                    go.Bar(
                        x=scenarios,
                        y=final_salaries,
                        marker_color=colors,
                        text=[f"£{salary:,.0f}" for salary in final_salaries],
                        textposition="auto",
                    )
                )

                # Add current salary line
                fig.add_hline(
                    y=employee_data.salary,
                    line_dash="dash",
                    line_color="red",
                    annotation_text=f"Current Salary: £{employee_data.salary:,.0f}",
                )

                fig.update_layout(
                    title=f"5-Year Salary Projection - {employee_data.name}",
                    xaxis_title="Scenario",
                    yaxis_title="Projected Salary (£)",
                    showlegend=False,
                    height=500,
                )

                # Save chart
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                chart_file = viz_dir / f"salary_projection_{employee_data.employee_id}_{timestamp}.html"
                pyo.plot(fig, filename=str(chart_file), auto_open=False)

                print("\n📈 Visualizations generated:")
                print(f"├─ {chart_file}")
                logger.log_info(f"Generated salary projection chart: {chart_file}")

            except Exception as viz_error:
                logger.log_warning(f"Could not generate visualizations: {viz_error}")

        # Export individual analysis if requested
        if config.get("export_individual_analysis", True):
            export_individual_analysis_results(
                employee_data,
                {
                    "conservative": conservative_projection,
                    "realistic": realistic_projection,
                    "optimistic": optimistic_projection,
                    "convergence_analysis": convergence_analysis if "convergence_analysis" in locals() else None,
                },
            )

        print("\n✅ Individual analysis completed successfully")

    except Exception as e:
        logger.log_error(f"Individual employee analysis failed: {e}")
        print(f"\nError during analysis: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


def export_individual_analysis_results(employee_data, analysis_results: Dict[str, Any]) -> None:
    """
    Export individual employee analysis results to file.

    Args:
        employee_data: EmployeeData instance
        analysis_results: Dictionary containing analysis results
    """
    try:
        from datetime import datetime
        import json
        from pathlib import Path

        # Create output directory
        output_dir = Path("artifacts/individual_analysis")
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Calculate annual growth rate from analysis results
        current_salary = employee_data.salary
        final_salary = analysis_results["realistic"]["expected_final_salary"]
        timeline_years = analysis_results["realistic"].get("timeline_years", 5)  # Default to 5 years

        # Calculate compound annual growth rate (CAGR)
        if timeline_years > 0 and current_salary > 0:
            annual_growth_rate = ((final_salary / current_salary) ** (1 / timeline_years) - 1) * 100
        else:
            annual_growth_rate = 0

        # Create comprehensive results dictionary
        export_data = {
            "employee_info": {
                "name": employee_data.name,
                "employee_id": employee_data.employee_id,
                "level": employee_data.level,
                "current_salary": employee_data.salary,
                "performance_rating": employee_data.performance_rating,
                "gender": employee_data.gender,
                "tenure_years": employee_data.tenure_years,
                "department": employee_data.department,
            },
            "analysis_timestamp": timestamp,
            "projection_results": analysis_results,
            "summary": {
                "current_salary": employee_data.salary,
                "realistic_final_salary": analysis_results["realistic"]["expected_final_salary"],
                "total_potential_increase": analysis_results["realistic"]["expected_final_salary"]
                - employee_data.salary,
                "annual_growth_rate": annual_growth_rate,
            },
        }

        # Export to JSON
        json_file = output_dir / f"individual_analysis_{employee_data.employee_id}_{timestamp}.json"
        with open(json_file, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        print(f"\n📄 Analysis exported to: {json_file}")

    except Exception as e:
        get_smart_logger().log_warning(f"Could not export analysis results: {e}")


def run_gel_reporting(orchestrator, simulation_results, config):
    """
    Run GEL scenario reporting with cohesive HTML and Markdown outputs.

    Args:
        orchestrator: EmployeeSimulationOrchestrator instance
        simulation_results: Results from simulation
        config: Configuration dictionary

    Returns:
        Dictionary with GEL reporting results and file paths
    """
    logger = get_smart_logger()

    try:
        # Extract configuration
        org = config.get("gel_org", "GEL")
        roles_config_path = config.get("gel_roles_config_path")
        timestamp = datetime.now()

        # Initialize GEL output manager
        gel_output = GELOutputManager(base_results_dir="results")

        # Create run directory
        run_dirs = gel_output.create_gel_run_directory(org=org, timestamp=timestamp, create_latest_link=True)

        logger.log_info(f"Created GEL run directory: {run_dirs['run_root']}")

        # Load roles configuration if provided
        roles_config = None
        roles_config_hash = "default"
        if roles_config_path:
            try:
                roles_loader = RolesConfigLoader()
                roles_config = roles_loader.load_config(roles_config_path)
                roles_config_hash = roles_loader.calculate_config_hash(roles_config)
                logger.log_info(f"Loaded roles config: {len(roles_config.roles)} roles")
            except Exception as e:
                logger.log_warning(f"Failed to load roles config: {e}")

        # Apply GEL policy constraints
        population_data = simulation_results.get("population_data", [])
        if population_data and roles_config:
            try:
                policy_constraints = GELPolicyConstraints(
                    population_data,
                    config={
                        "max_direct_reports": roles_config.intervention_policy.max_direct_reports,
                        "inequality_budget_percent": roles_config.intervention_policy.inequality_budget_percent,
                        "high_performer_threshold": 4.0,
                    },
                )

                # Analyze managers and teams
                manager_teams = policy_constraints.identify_managers_and_teams()
                prioritized_interventions = policy_constraints.prioritize_interventions(manager_teams)
                optimized_allocations = policy_constraints.optimize_budget_allocation(prioritized_interventions)
                policy_summary = policy_constraints.generate_policy_summary(manager_teams, optimized_allocations)

                logger.log_info(f"Applied policy constraints: {len(manager_teams)} managers analyzed")
            except Exception as e:
                logger.log_warning(f"Policy constraints failed: {e}")
                policy_summary = {}
        else:
            policy_summary = {}

        # Prepare analysis payload
        analysis_payload = {
            "population_stratification": simulation_results.get("advanced_analysis", {}).get("median_convergence", {}),
            "inequality_analysis": simulation_results.get("advanced_analysis", {}).get("intervention_strategies", {}),
            "high_performers": policy_summary.get("intervention_impact", {}),
            "recommendations": {
                "immediate": [],
                "medium_term": policy_summary.get("recommendations", []),
                "success_metrics": [
                    {
                        "name": "Gender Pay Gap",
                        "description": "Overall percentage gap between genders",
                        "target_value": "< 5%",
                    },
                    {
                        "name": "Policy Compliance",
                        "description": "Percentage of managers with ≤6 direct reports",
                        "target_value": "100%",
                    },
                ],
            },
            "role_config": {"roles": roles_config.roles if roles_config else []},
        }

        # Create manifest
        manifest_data = gel_output.create_manifest_data(
            scenario=org,
            org=org,
            timestamp=timestamp,
            config_hash=roles_config_hash,
            population=len(population_data),
            median_salary=simulation_results.get("summary_metrics", {}).get("median_salary", 0),
            below_median_pct=simulation_results.get("advanced_analysis", {})
            .get("median_convergence", {})
            .get("below_median_percent", 0),
            gender_gap_pct=simulation_results.get("summary_metrics", {}).get("gender_pay_gap_percent", 0),
            intervention_budget_pct=roles_config.intervention_policy.inequality_budget_percent if roles_config else 0.5,
            recommended_uplifts_cost_pct=policy_summary.get("budget_analysis", {}).get("budget_utilization_percent", 0)
            / 100,
            additional_metadata={
                "random_seed": config.get("random_seed", 42),
                "currency": roles_config.currency if roles_config else "GBP",
                "config_version": roles_config.version if roles_config else 1,
                "max_direct_reports": roles_config.intervention_policy.max_direct_reports if roles_config else 6,
            },
        )

        # Generate reports
        md_builder = MarkdownReportBuilder(output_dir=run_dirs["run_root"])
        html_builder = HTMLReportBuilder(output_dir=run_dirs["run_root"])

        # Create temporary files first
        temp_md = md_builder.build_gel_report(analysis_payload, manifest_data, "report.md")
        temp_html = html_builder.build_gel_report(
            analysis_payload, manifest_data, assets_dir=run_dirs["assets"], output_file="index.html"
        )

        # Generate professional dashboard
        from professional_dashboard_builder import ProfessionalDashboardBuilder

        dashboard_builder = ProfessionalDashboardBuilder()

        # Load scenario config for dashboard context
        scenario_config = config if config else {}

        dashboard_path = dashboard_builder.build_comprehensive_dashboard(
            analysis_payload=analysis_payload,
            manifest=manifest_data,
            run_directory=run_dirs["run_root"],
            scenario_config=scenario_config,
            output_file="professional_dashboard.html",
        )

        # Organize all outputs
        final_paths = gel_output.organize_gel_outputs(
            run_directories=run_dirs,
            html_report=temp_html,
            markdown_report=temp_md,
            manifest_data=manifest_data,
            cleanup_temp=False,  # Keep files since they're already in final location
        )

        # Validate output
        validation = gel_output.validate_gel_output(run_dirs["run_root"])

        return {
            "success": True,
            "report_path": str(run_dirs["run_root"]),
            "html_report": str(final_paths.get("html_report", run_dirs["run_root"] / "index.html")),
            "markdown_report": str(final_paths.get("markdown_report", run_dirs["run_root"] / "report.md")),
            "professional_dashboard": str(dashboard_path),
            "manifest": str(final_paths.get("manifest", run_dirs["run_root"] / "manifest.json")),
            "assets_dir": str(run_dirs["assets"]),
            "validation": validation,
            "policy_summary": policy_summary,
            "timestamp": timestamp.isoformat() + "Z",
        }

    except Exception as e:
        logger.log_error(f"GEL reporting failed: {e}")
        return {"success": False, "error": str(e)}


def main():
    """
    Command-line interface for the simulation orchestrator.
    """
    parser = argparse.ArgumentParser(description="Employee Population Simulation Orchestrator")
    parser.add_argument(
        "--mode",
        choices=["full", "quick-validation", "story-validation", "advanced-analysis-only"],
        default="full",
        help="Simulation mode to run",
    )
    parser.add_argument("--config", help="Path to JSON configuration file")
    parser.add_argument("--scenario", help="Use predefined scenario from config.json")
    parser.add_argument("--population-size", type=int, help="Number of employees to generate (overrides config)")
    parser.add_argument("--max-cycles", type=int, default=15, help="Maximum number of review cycles to simulate")
    parser.add_argument("--random-seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument("--no-viz", action="store_true", help="Skip visualization generation")
    parser.add_argument(
        "--export-formats",
        nargs="+",
        choices=["csv", "excel", "json"],
        default=["csv", "excel", "json"],
        help="Export formats",
    )

    # Story tracking arguments
    parser.add_argument("--enable-stories", action="store_true", help="Enable employee story tracking")
    parser.add_argument(
        "--generate-stories",
        action="store_true",
        help="Generate individual employee stories (implies --enable-stories)",
    )
    parser.add_argument("--interactive-viz", action="store_true", help="Generate interactive visualizations")

    # Advanced analysis arguments
    parser.add_argument("--advanced-analysis", action="store_true", help="Enable advanced salary progression analysis")
    parser.add_argument("--individual-progression", action="store_true", help="Run individual progression analysis")
    parser.add_argument("--median-convergence", action="store_true", help="Run median convergence analysis")
    parser.add_argument("--intervention-strategies", action="store_true", help="Run intervention strategy analysis")
    parser.add_argument(
        "--analysis-years", type=int, default=5, help="Number of years for progression analysis (default: 5)"
    )

    # GEL scenario specific arguments
    parser.add_argument("--report", action="store_true", help="Generate cohesive GEL report (HTML and Markdown)")
    parser.add_argument("--roles-config", type=str, help="Path to YAML roles configuration file")
    parser.add_argument("--org", type=str, help="Organization identifier for GEL reporting")

    parser.add_argument(
        "--log-level", choices=["ERROR", "WARNING", "INFO", "DEBUG"], default="INFO", help="Logging level"
    )

    # Individual employee analysis arguments
    parser.add_argument(
        "--employee-data", type=str, help="Individual employee data in format 'level:X,salary:Y,performance:Z'"
    )

    args = parser.parse_args()

    # Load configuration
    if args.config:
        try:
            with open(args.config, "r") as f:
                config = json.load(f)
            get_smart_logger().log_info(f"Loaded configuration from {args.config}")
        except Exception as e:
            get_smart_logger().log_error(f"Failed to load configuration: {e}")
            sys.exit(1)
    elif args.scenario:
        # Load configuration with scenario
        try:
            from config_manager import ConfigurationManager

            config_manager = ConfigurationManager("config.json")
            config = config_manager.get_orchestrator_config(scenario=args.scenario)
            get_smart_logger().log_info(f"Loaded scenario '{args.scenario}' configuration")
        except Exception as e:
            get_smart_logger().log_error(f"Failed to load scenario configuration: {e}")
            sys.exit(1)
    else:
        # Try to load default config.json, fall back to command-line arguments
        try:
            from config_manager import ConfigurationManager

            config_manager = ConfigurationManager("config.json")
            config = config_manager.get_orchestrator_config()
            get_smart_logger().log_info("Loaded default configuration from config.json")
        except Exception as e:
            get_smart_logger().log_warning(f"Could not load config.json ({e}), using command-line arguments")
            config = {
                "population_size": args.population_size or 1000,
                "random_seed": args.random_seed,
                "max_cycles": args.max_cycles,
                "convergence_threshold": 0.001,
                "export_formats": args.export_formats,
                "generate_visualizations": not args.no_viz,
                "export_individual_files": True,
                "export_comprehensive_report": True,
                # Story tracking configuration from CLI
                "enable_story_tracking": args.enable_stories or args.generate_stories,
                "generate_interactive_dashboard": args.interactive_viz,
                "create_individual_story_charts": args.generate_stories,
                # Advanced analysis configuration from CLI
                "enable_advanced_analysis": args.advanced_analysis
                or args.individual_progression
                or args.median_convergence
                or args.intervention_strategies,
                "run_individual_progression_analysis": args.individual_progression or args.advanced_analysis,
                "run_median_convergence_analysis": args.median_convergence or args.advanced_analysis,
                "run_intervention_strategy_analysis": args.intervention_strategies or args.advanced_analysis,
                "progression_analysis_years": args.analysis_years,
                "log_level": args.log_level,
            }

    # Apply command-line overrides to config if provided
    if args.population_size:
        config["population_size"] = args.population_size
    if hasattr(args, "max_cycles") and args.max_cycles != 15:  # Only override if different from default
        config["max_cycles"] = args.max_cycles
    if hasattr(args, "random_seed") and args.random_seed != 42:  # Only override if different from default
        config["random_seed"] = args.random_seed
    if hasattr(args, "analysis_years") and args.analysis_years != 5:  # Only override if different from default
        config["progression_analysis_years"] = args.analysis_years

    # Handle GEL scenario specific configuration
    if args.report or args.roles_config:
        config["enable_gel_reporting"] = True
        config["gel_org"] = args.org or "GEL"
        config["gel_roles_config_path"] = args.roles_config

        # Enable required analysis for GEL reporting
        config["enable_advanced_analysis"] = True
        config["run_median_convergence_analysis"] = True
        config["run_intervention_strategy_analysis"] = True

        # Use clean GEL output format
        config["gel_output_format"] = True

        get_smart_logger().log_info(f"Enabled GEL reporting for organization: {config['gel_org']}")
        if args.roles_config:
            get_smart_logger().log_info(f"Using roles configuration: {args.roles_config}")

    # Handle individual employee data if provided
    if args.employee_data:
        try:
            from individual_employee_parser import parse_employee_data_string

            get_smart_logger().log_info(f"Parsing individual employee data: {args.employee_data}")

            # Parse and validate employee data
            employee_data = parse_employee_data_string(args.employee_data)
            get_smart_logger().log_info(
                f"Parsed employee: Level {employee_data.level}, £{employee_data.salary:,.0f}, {employee_data.performance_rating}"
            )

            # Run individual employee analysis
            return run_individual_employee_analysis(employee_data, config)

        except Exception as e:
            get_smart_logger().log_error(f"Failed to parse individual employee data: {e}")
            print(f"\nError: {e}")
            print("\nExpected format: 'level:X,salary:Y,performance:Z'")
            print("Example: 'level:5,salary:80692.5,performance:Exceeding'")
            print("\nValid performance ratings: Not met, Partially met, Achieving, High Performing, Exceeding")
            sys.exit(1)

    # Initialize orchestrator
    orchestrator = EmployeeSimulationOrchestrator(config=config)

    try:
        if args.mode == "quick-validation":
            # Run quick validation
            validation_results = orchestrator.run_quick_validation()
            print("\n=== QUICK VALIDATION RESULTS ===")
            print(json.dumps(validation_results, indent=2, default=str))

            if validation_results["overall"]["status"] == "FAIL":
                sys.exit(1)

        elif args.mode == "story-validation":
            # Run story tracking validation with small population
            print("\n=== STORY TRACKING VALIDATION ===")
            validation_config = config.copy()
            validation_config.update(
                {
                    "population_size": 100,
                    "max_cycles": 3,
                    "enable_story_tracking": True,
                    "export_story_data": True,
                    "generate_summary_report": True,
                    "tracked_employee_count": 10,  # Max employees per category
                    "story_categories": ["gender_gap", "above_range", "high_performer"],
                }
            )

            validation_orchestrator = EmployeeSimulationOrchestrator(config=validation_config)
            results = validation_orchestrator.run_with_story_tracking()

            # Validate story tracking results
            story_validation = {
                "total_tracked_employees": results["summary_metrics"].get("total_tracked_employees", 0),
                "categories_found": len(results.get("employee_stories", {})),
                "story_files_generated": "employee_stories" in results.get("files_generated", {}),
                "summary_report_generated": "summary_report" in results.get("files_generated", {}),
            }

            validation_passed = (
                story_validation["total_tracked_employees"] >= 5
                and story_validation["categories_found"] >= 1
                and story_validation["story_files_generated"]
                and story_validation["summary_report_generated"]
            )

            print(f"Total tracked employees: {story_validation['total_tracked_employees']}")
            print(f"Categories found: {story_validation['categories_found']}")
            print(f"Story files generated: {story_validation['story_files_generated']}")
            print(f"Summary report generated: {story_validation['summary_report_generated']}")
            print(f"\nValidation: {'✓ PASS' if validation_passed else '✗ FAIL'}")

            if not validation_passed:
                sys.exit(1)

        elif args.mode == "advanced-analysis-only":
            # Run advanced analysis only (without full simulation)
            print("\n=== ADVANCED ANALYSIS MODE ===")
            advanced_results = orchestrator.run_advanced_analysis()

            print(
                f"Advanced Analysis Status: {'✓ ENABLED' if advanced_results['advanced_analysis_enabled'] else '✗ DISABLED'}"
            )
            if advanced_results["advanced_analysis_enabled"]:
                print(f"Population Size: {advanced_results['population_size']:,}")
                print(f"Analysis Components: {len(advanced_results['analysis_results'])}")

                for component, data in advanced_results["analysis_results"].items():
                    component_name = component.replace("_", " ").title()
                    print(f"  ✅ {component_name}")

                if advanced_results.get("files_generated"):
                    print(f"\nFiles Generated: {len(advanced_results['files_generated'])}")
                    for file_type, file_path in advanced_results["files_generated"].items():
                        print(f"  📄 {file_type.replace('_', ' ').title()}: {file_path}")

                # Display dashboard information
                if advanced_results.get("dashboard_files"):
                    dashboard_info = advanced_results["dashboard_files"]
                    print("\n🎯 Management Dashboard: Generated")
                    print(f"  📊 Main Dashboard: {dashboard_info.get('main_dashboard', 'N/A')}")
                    print(f"  📈 Components: {dashboard_info.get('components_generated', 0)} interactive charts")

                    # Notify user about auto-opened dashboard
                    if orchestrator.config.get("auto_open_dashboard", True):
                        print("  🌐 Dashboard automatically opened in browser")
                    else:
                        print(f"  💡 Open dashboard manually: file://{dashboard_info.get('main_dashboard', '')}")

            return  # Exit after advanced analysis

        else:
            # Run complete simulation (with or without story tracking)
            if config.get("enable_story_tracking", False):
                results = orchestrator.run_with_story_tracking()
            else:
                results = orchestrator.run_complete_simulation()

            # Run advanced analysis if enabled (in addition to regular simulation)
            if config.get("enable_advanced_analysis", False):
                print("\n=== RUNNING ADVANCED ANALYSIS ===")
                try:
                    population_data = results.get("population_data", [])
                    advanced_results = orchestrator.run_advanced_analysis(population_data)

                    # Merge advanced analysis results into main results
                    if advanced_results.get("advanced_analysis_enabled", False):
                        results["advanced_analysis"] = advanced_results
                        if advanced_results.get("files_generated"):
                            if "files_generated" not in results:
                                results["files_generated"] = {}
                            results["files_generated"]["advanced_analysis"] = advanced_results["files_generated"]

                        print(f"Advanced Analysis: {len(advanced_results['analysis_results'])} components completed")
                    else:
                        print("Advanced Analysis: Disabled in configuration")

                except Exception as e:
                    print(f"Advanced Analysis Failed: {e}")
                    # Continue with regular results even if advanced analysis fails

            # Run GEL reporting if enabled
            if config.get("enable_gel_reporting", False):
                print("\n=== GENERATING GEL REPORTS ===")
                try:
                    gel_results = run_gel_reporting(orchestrator, results, config)

                    # Merge GEL results
                    if gel_results:
                        results["gel_reporting"] = gel_results
                        print(f"✅ GEL Reports generated: {gel_results.get('report_path', 'Unknown location')}")
                        print(f"📊 HTML Report: {gel_results.get('html_report', 'index.html')}")
                        print(f"📝 Markdown Report: {gel_results.get('markdown_report', 'report.md')}")
                        print(f"📋 Manifest: {gel_results.get('manifest', 'manifest.json')}")

                except Exception as e:
                    print(f"GEL Reporting Failed: {e}")
                    # Continue with regular results even if GEL reporting fails

            print("\n=== SIMULATION COMPLETED SUCCESSFULLY ===")
            print(f"Timestamp: {results['timestamp']}")
            print(f"Population Size: {results['summary_metrics']['population_size']}")
            print(f"Cycles Completed: {results['summary_metrics']['cycles_completed']}")
            print(f"Final Gini Coefficient: {results['summary_metrics']['final_gini_coefficient']}")
            print(f"Convergence Achieved: {results['summary_metrics']['convergence_achieved']}")

            print("\n=== FILES GENERATED ===")
            for category, files in results["files_generated"].items():
                if isinstance(files, dict):
                    print(f"{category.upper()}:")
                    for subcategory, subfiles in files.items():
                        if isinstance(subfiles, dict):
                            for format_type, filepath in subfiles.items():
                                print(f"  {subcategory} ({format_type}): {filepath}")
                        else:
                            print(f"  {subcategory}: {subfiles}")
                else:
                    print(f"{category.upper()}: {files}")

            print("\n=== VALIDATION STATUS ===")
            if "final_summary" in results and "validation_status" in results["final_summary"]:
                for component, status in results["final_summary"]["validation_status"].items():
                    status_str = "✓ PASS" if status else "✗ FAIL"
                    print(f"{component.title()}: {status_str}")
            else:
                validation_status = results.get("validation_results", {})
                for component, result in validation_status.items():
                    if isinstance(result, dict) and "median_constraint_met" in result:
                        status_str = "✓ PASS" if result["median_constraint_met"] else "✗ FAIL"
                        print(f"{component.title()}: {status_str}")
                    elif isinstance(result, dict) and "all_tests_passed" in result:
                        status_str = "✓ PASS" if result["all_tests_passed"] else "✗ FAIL"
                        print(f"{component.title()}: {status_str}")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

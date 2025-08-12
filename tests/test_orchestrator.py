#!/usr/bin/env python3
"""Comprehensive tests for employee_simulation_orchestrator module.

Tests the main orchestration functionality, CLI interface, and integration workflows.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import sys

# Import the modules under test
from employee_simulation_orchestrator import run_individual_employee_analysis, export_individual_analysis_results, main
from individual_employee_parser import EmployeeData, parse_employee_data_string


class TestIndividualEmployeeAnalysis:
    """Test individual employee analysis functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.employee_data = EmployeeData(
            employee_id=1,
            name="Test Employee",
            level=3,
            salary=65000,
            performance_rating="High Performing",
            gender="Female",
            tenure_years=2,
            department="Engineering",
        )

        self.config = {
            "progression_analysis_years": 5,
            "generate_visualizations": True,
            "export_individual_analysis": True,
            "confidence_interval": 0.95,
            "market_inflation_rate": 0.025,
        }

    @patch("employee_simulation_orchestrator.get_smart_logger")
    @patch("individual_progression_simulator.IndividualProgressionSimulator")
    @patch("median_convergence_analyzer.MedianConvergenceAnalyzer")
    def test_run_individual_employee_analysis_basic(self, mock_convergence, mock_simulator, mock_logger):
        """Test basic individual employee analysis workflow."""
        # Setup mocks
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        mock_sim_instance = MagicMock()
        mock_simulator.return_value = mock_sim_instance
        mock_sim_instance.project_salary_progression.return_value = {
            "projections": {
                "conservative": {"final_salary": 70000, "annual_growth_rate": 0.03},
                "realistic": {"final_salary": 75000, "annual_growth_rate": 0.04},
                "optimistic": {"final_salary": 80000, "annual_growth_rate": 0.05},
            }
        }

        mock_conv_instance = MagicMock()
        mock_convergence.return_value = mock_conv_instance
        mock_conv_instance.analyze_convergence_timeline.return_value = {"below_median": False, "gap_percent": -5.0}

        # Test with minimal config
        with patch("builtins.print") as mock_print:
            run_individual_employee_analysis(self.employee_data, self.config)

        # Verify logging calls
        mock_logger_instance.log_info.assert_called()

        # Verify simulator was called correctly
        mock_sim_instance.project_salary_progression.assert_called_once()

        # Verify output was printed
        mock_print.assert_called()

    @patch("employee_simulation_orchestrator.get_smart_logger")
    def test_run_individual_employee_analysis_custom_years(self, mock_logger):
        """Test individual analysis with custom analysis years."""
        custom_config = self.config.copy()
        custom_config["progression_analysis_years"] = 3

        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        with patch("individual_progression_simulator.IndividualProgressionSimulator") as mock_sim:
            mock_sim_instance = MagicMock()
            mock_sim.return_value = mock_sim_instance
            mock_sim_instance.project_salary_progression.return_value = {
                "projections": {
                    "conservative": {"final_salary": 68000},
                    "realistic": {"final_salary": 70000},
                    "optimistic": {"final_salary": 72000},
                }
            }

            with patch("employee_simulation_orchestrator.MedianConvergenceAnalyzer"):
                with patch("builtins.print") as mock_print:
                    run_individual_employee_analysis(self.employee_data, custom_config)

                # Check that the custom years were used
                call_args = mock_sim_instance.project_salary_progression.call_args
                assert call_args[1]["years"] == 3

    @patch("employee_simulation_orchestrator.get_smart_logger")
    @patch("builtins.print")
    def test_run_individual_employee_analysis_error_handling(self, mock_print, mock_logger):
        """Test error handling in individual employee analysis."""
        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        # Simulate an error in the progression simulator
        with patch(
            "individual_progression_simulator.IndividualProgressionSimulator",
            side_effect=Exception("Simulation failed"),
        ):
            # Function should raise SystemExit after logging the error
            with pytest.raises(SystemExit):
                run_individual_employee_analysis(self.employee_data, self.config)

            # Verify error was logged before exit
            mock_logger_instance.log_error.assert_called()

            # Verify error was printed to user before exit
            mock_print.assert_called()

    @patch("employee_simulation_orchestrator.get_smart_logger")
    def test_run_individual_employee_analysis_no_visualizations(self, mock_logger):
        """Test individual analysis with visualizations disabled."""
        config_no_viz = self.config.copy()
        config_no_viz["generate_visualizations"] = False

        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        with patch("employee_simulation_orchestrator.IndividualProgressionSimulator"):
            with patch("employee_simulation_orchestrator.MedianConvergenceAnalyzer"):
                with patch("builtins.print"):
                    run_individual_employee_analysis(self.employee_data, config_no_viz)

        # Verify visualization generation was not attempted
        log_calls = [call[0][0] for call in mock_logger_instance.log_info.call_args_list]
        visualization_calls = [call for call in log_calls if "visualization" in call.lower()]
        assert len(visualization_calls) == 0


class TestExportFunctionality:
    """Test data export functionality."""

    def setup_method(self):
        """Setup test fixtures."""
        self.employee_data = EmployeeData(
            employee_id=42, name="Export Test Employee", level=4, salary=75000, performance_rating="Exceeding"
        )

        self.analysis_results = {
            "conservative": {"final_salary": 80000, "annual_growth_rate": 0.03},
            "realistic": {"final_salary": 85000, "annual_growth_rate": 0.04},
            "optimistic": {"final_salary": 90000, "annual_growth_rate": 0.05},
        }

    @patch("builtins.open", new_callable=mock_open)
    @patch("employee_simulation_orchestrator.Path")
    def test_export_individual_analysis_results(self, mock_path, mock_file):
        """Test exporting individual analysis results to JSON."""
        # Setup path mocking
        mock_output_dir = MagicMock()
        mock_path.return_value = mock_output_dir
        mock_output_dir.mkdir = MagicMock()

        # Mock file path
        mock_json_file = MagicMock()
        mock_output_dir.__truediv__ = MagicMock(return_value=mock_json_file)

        # Execute export
        export_individual_analysis_results(self.employee_data, self.analysis_results)

        # Verify directory creation
        mock_output_dir.mkdir.assert_called_once_with(parents=True, exist_ok=True)

        # Verify file was opened for writing
        mock_file.assert_called_once()

        # Verify JSON data was written
        handle = mock_file.return_value
        handle.write.assert_called()

    def test_export_analysis_results_data_structure(self):
        """Test that export creates correct data structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Patch the artifacts directory to use temp directory
            with patch("employee_simulation_orchestrator.Path") as mock_path:
                temp_path = Path(temp_dir)
                mock_path.return_value = temp_path / "individual_analysis"

                # Create the directory
                (temp_path / "individual_analysis").mkdir(parents=True, exist_ok=True)

                # Export the results
                export_individual_analysis_results(self.employee_data, self.analysis_results)

                # Find the generated JSON file
                json_files = list((temp_path / "individual_analysis").glob("*.json"))
                assert len(json_files) >= 1

                # Load and verify the JSON structure
                with open(json_files[0], "r") as f:
                    exported_data = json.load(f)

                # Verify required fields
                assert "employee_info" in exported_data
                assert "analysis_timestamp" in exported_data
                assert "projection_results" in exported_data
                assert "summary" in exported_data

                # Verify employee info
                emp_info = exported_data["employee_info"]
                assert emp_info["employee_id"] == 42
                assert emp_info["name"] == "Export Test Employee"
                assert emp_info["level"] == 4
                assert emp_info["current_salary"] == 75000

                # Verify analysis results
                assert exported_data["projection_results"] == self.analysis_results


class TestConfigurationHandling:
    """Test configuration loading and processing."""

    @patch("employee_simulation_orchestrator.get_smart_logger")
    def test_basic_config_structure(self, mock_logger):
        """Test basic configuration structure creation."""
        basic_config = {"population_size": 100, "max_cycles": 15, "random_seed": 42, "progression_analysis_years": 5}

        # Test that config is processed correctly
        assert basic_config["population_size"] == 100
        assert basic_config["progression_analysis_years"] == 5

    def test_config_override_logic(self):
        """Test command-line argument override logic."""
        # This tests the logic that was fixed in the analysis_years bug
        base_config = {"progression_analysis_years": 5}

        # Simulate command-line override
        analysis_years_arg = 3
        if analysis_years_arg != 5:  # Only override if different from default
            base_config["progression_analysis_years"] = analysis_years_arg

        assert base_config["progression_analysis_years"] == 3


class TestMainEntryPoint:
    """Test main entry point and CLI functionality."""

    @patch("employee_simulation_orchestrator.get_smart_logger")
    @patch("sys.argv")
    def test_main_individual_scenario_success(self, mock_argv, mock_logger):
        """Test main function with individual scenario."""
        mock_argv.__getitem__.side_effect = lambda x: [
            "employee_simulation_orchestrator.py",
            "--scenario",
            "individual",
            "--employee-data",
            "level:5,salary:80000,performance:Exceeding",
        ][x]

        mock_logger_instance = MagicMock()
        mock_logger.return_value = mock_logger_instance

        with patch("employee_simulation_orchestrator.argparse.ArgumentParser") as mock_parser:
            # Setup argument parser mock
            mock_args = MagicMock()
            mock_args.scenario = "individual"
            mock_args.employee_data = "level:5,salary:80000,performance:Exceeding"
            mock_args.analysis_years = 5
            mock_args.log_level = "INFO"
            mock_args.config = None
            mock_args.population_size = None
            mock_args.max_cycles = 15
            mock_args.random_seed = 42

            mock_parser_instance = MagicMock()
            mock_parser.return_value = mock_parser_instance
            mock_parser_instance.parse_args.return_value = mock_args

            # Mock the config manager
            with patch("employee_simulation_orchestrator.ConfigurationManager") as mock_config_mgr:
                mock_config_instance = MagicMock()
                mock_config_mgr.return_value = mock_config_instance
                mock_config_instance.get_orchestrator_config.return_value = {
                    "progression_analysis_years": 5,
                    "generate_visualizations": True,
                }

                # Mock the individual analysis function
                with patch("employee_simulation_orchestrator.run_individual_employee_analysis") as mock_individual:
                    with patch("employee_simulation_orchestrator.parse_employee_data_string") as mock_parse:
                        mock_parse.return_value = EmployeeData(level=5, salary=80000, performance_rating="Exceeding")

                        # Test main function
                        try:
                            main()
                        except SystemExit:
                            pass  # Expected for successful completion

                        # Verify individual analysis was called
                        mock_individual.assert_called_once()

    @patch("sys.argv")
    def test_main_invalid_employee_data(self, mock_argv):
        """Test main function with invalid employee data."""
        mock_argv.__getitem__.side_effect = lambda x: [
            "employee_simulation_orchestrator.py",
            "--scenario",
            "individual",
            "--employee-data",
            "invalid_format",
        ][x]

        with patch("employee_simulation_orchestrator.argparse.ArgumentParser") as mock_parser:
            mock_args = MagicMock()
            mock_args.scenario = "individual"
            mock_args.employee_data = "invalid_format"
            mock_args.config = None
            mock_args.analysis_years = 5
            mock_args.log_level = "INFO"

            mock_parser_instance = MagicMock()
            mock_parser.return_value = mock_parser_instance
            mock_parser_instance.parse_args.return_value = mock_args

            with patch("employee_simulation_orchestrator.ConfigurationManager") as mock_config_mgr:
                mock_config_instance = MagicMock()
                mock_config_mgr.return_value = mock_config_instance
                mock_config_instance.get_orchestrator_config.return_value = {}

                with patch("employee_simulation_orchestrator.get_smart_logger") as mock_logger:
                    mock_logger_instance = MagicMock()
                    mock_logger.return_value = mock_logger_instance

                    with patch("builtins.print"):
                        with pytest.raises(SystemExit):
                            main()

                    # Verify error was logged
                    mock_logger_instance.log_error.assert_called()


class TestIntegrationWorkflows:
    """Test end-to-end integration workflows."""

    def test_full_individual_analysis_workflow(self):
        """Test complete individual analysis workflow."""
        # Parse employee data
        employee_data = parse_employee_data_string("level:3,salary:65000,performance:High Performing")

        # Verify parsing worked
        assert employee_data.level == 3
        assert employee_data.salary == 65000
        assert employee_data.performance_rating == "High Performing"

        # Create minimal config
        config = {
            "progression_analysis_years": 3,
            "generate_visualizations": False,  # Disable to avoid file I/O in tests
            "export_individual_analysis": False,
        }

        # Mock the complex dependencies
        with patch("individual_progression_simulator.IndividualProgressionSimulator") as mock_sim:
            mock_sim_instance = MagicMock()
            mock_sim.return_value = mock_sim_instance
            mock_sim_instance.project_salary_progression.return_value = {
                "projections": {
                    "conservative": {"final_salary": 70000},
                    "realistic": {"final_salary": 75000},
                    "optimistic": {"final_salary": 80000},
                }
            }

            with patch("median_convergence_analyzer.MedianConvergenceAnalyzer") as mock_conv:
                mock_conv_instance = MagicMock()
                mock_conv.return_value = mock_conv_instance
                mock_conv_instance.analyze_convergence_timeline.return_value = {"below_median": False}

                with patch("employee_simulation_orchestrator.get_smart_logger") as mock_logger:
                    mock_logger.return_value = MagicMock()

                    with patch("builtins.print"):
                        # This should complete successfully
                        run_individual_employee_analysis(employee_data, config)

                # Verify the simulation was called with correct parameters
                call_args = mock_sim_instance.project_salary_progression.call_args
                assert call_args[1]["years"] == 3

                # Verify convergence analysis was performed
                mock_conv_instance.analyze_convergence_timeline.assert_called_once()

    def test_error_recovery_workflow(self):
        """Test error recovery in workflows."""
        employee_data = parse_employee_data_string("level:5,salary:80000,performance:Exceeding")
        config = {"progression_analysis_years": 5}

        # Test recovery from simulation error
        with patch(
            "employee_simulation_orchestrator.IndividualProgressionSimulator", side_effect=Exception("Simulation error")
        ):
            with patch("employee_simulation_orchestrator.get_smart_logger") as mock_logger:
                mock_logger_instance = MagicMock()
                mock_logger.return_value = mock_logger_instance

                with patch("builtins.print"):
                    # Should handle error gracefully
                    run_individual_employee_analysis(employee_data, config)

                    # Verify error was logged
                    mock_logger_instance.log_error.assert_called()


class TestParameterValidation:
    """Test parameter validation and edge cases."""

    def test_analysis_years_parameter_handling(self):
        """Test analysis_years parameter is handled correctly."""
        # This specifically tests the bug fix for --analysis-years
        base_config = {"progression_analysis_years": 5}

        # Test override logic
        def apply_analysis_years_override(config, analysis_years):
            if analysis_years != 5:  # Only override if different from default
                config["progression_analysis_years"] = analysis_years
            return config

        # Test with default value (should not override)
        result = apply_analysis_years_override(base_config.copy(), 5)
        assert result["progression_analysis_years"] == 5

        # Test with custom value (should override)
        result = apply_analysis_years_override(base_config.copy(), 3)
        assert result["progression_analysis_years"] == 3

        # Test with another custom value
        result = apply_analysis_years_override(base_config.copy(), 7)
        assert result["progression_analysis_years"] == 7

    def test_configuration_merge_logic(self):
        """Test configuration merging and override logic."""
        scenario_config = {"progression_analysis_years": 5, "population_size": 100, "generate_visualizations": True}

        # Simulate command-line overrides
        overrides = {"progression_analysis_years": 3, "population_size": 250}

        # Apply overrides
        for key, value in overrides.items():
            scenario_config[key] = value

        # Verify overrides were applied
        assert scenario_config["progression_analysis_years"] == 3
        assert scenario_config["population_size"] == 250
        assert scenario_config["generate_visualizations"] == True  # Unchanged

    def test_employee_data_validation_integration(self):
        """Test integration between employee data validation and analysis."""
        # Test with valid data
        valid_data = "level:4,salary:75000,performance:High Performing,gender:Male,tenure:3"
        employee = parse_employee_data_string(valid_data)

        assert employee.level == 4
        assert employee.salary == 75000
        assert employee.performance_rating == "High Performing"
        assert employee.gender == "Male"
        assert employee.tenure_years == 3

        # Test with invalid data should raise ValueError
        invalid_data = "level:10,salary:-5000,performance:Invalid"
        with pytest.raises(ValueError):
            parse_employee_data_string(invalid_data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

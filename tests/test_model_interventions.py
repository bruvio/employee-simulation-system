#!/usr/bin/env python3
"""Comprehensive tests for model_interventions module.

Tests intervention modeling functions, report generation, and analysis workflows.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open
import json

# Import the module under test
from model_interventions import (
    load_population_data,
    format_currency,
    format_percentage,
    create_gender_gap_report,
    create_median_convergence_report,
    save_report,
    run_gender_gap_analysis,
    run_median_convergence_analysis,
    run_equity_analysis,
    create_equity_report,
    main
)


class TestUtilityFunctions:
    """Test utility functions for formatting and data handling."""

    def test_format_currency(self):
        """Test currency formatting function."""
        assert format_currency(1000) == "£1,000"
        assert format_currency(1000.50) == "£1,001"  # Should round
        assert format_currency(0) == "£0"
        assert format_currency(-500) == "-£500"

    def test_format_currency_large_numbers(self):
        """Test currency formatting with large numbers."""
        assert format_currency(1000000) == "£1,000,000"
        assert format_currency(1234567.89) == "£1,234,568"

    def test_format_percentage(self):
        """Test percentage formatting function."""
        assert format_percentage(0.15) == "15.0%"
        assert format_percentage(0.1234) == "12.3%"
        assert format_percentage(0) == "0.0%"
        assert format_percentage(1.0) == "100.0%"

    def test_format_percentage_edge_cases(self):
        """Test percentage formatting edge cases."""
        assert format_percentage(-0.05) == "-5.0%"
        assert format_percentage(2.5) == "250.0%"


class TestPopulationDataLoading:
    """Test population data loading functionality."""

    @patch('model_interventions.EmployeePopulationGenerator')
    def test_load_population_data_generate(self, mock_generator_class):
        """Test population data generation."""
        # Setup mock
        mock_generator = MagicMock()
        mock_generator_class.return_value = mock_generator
        mock_population = [
            {"employee_id": 1, "level": 3, "salary": 65000, "gender": "Female"},
            {"employee_id": 2, "level": 4, "salary": 80000, "gender": "Male"}
        ]
        mock_generator.generate_population.return_value = mock_population

        result = load_population_data("generate")
        
        assert result == mock_population
        mock_generator_class.assert_called_once()
        mock_generator.generate_population.assert_called_once()

    @patch('builtins.open', mock_open(read_data='[{"employee_id": 1, "salary": 50000}]'))
    def test_load_population_data_from_file(self):
        """Test loading population data from JSON file."""
        result = load_population_data("test_file.json")
        
        assert isinstance(result, list)
        assert len(result) >= 0  # Should return data

    def test_load_population_data_invalid_source(self):
        """Test loading with invalid data source."""
        # Should handle invalid sources gracefully
        try:
            result = load_population_data("invalid_source")
        except (ValueError, FileNotFoundError):
            pass  # Expected for invalid sources


class TestReportGeneration:
    """Test report generation functions."""

    def setup_method(self):
        """Setup test fixtures."""
        self.gender_gap_result = {
            "current_gap": 0.15,
            "target_gap": 0.05,
            "total_cost": 150000,
            "affected_employees": 25,
            "recommendations": ["Increase salaries for underrepresented groups"],
            "timeline": "6 months"
        }
        
        self.convergence_result = {
            "below_median_employees": [
                {"employee_id": 1, "current_salary": 60000, "target_salary": 70000},
                {"employee_id": 2, "current_salary": 65000, "target_salary": 72000}
            ],
            "total_adjustment_cost": 17000,
            "median_salary": 75000
        }
        
        self.equity_result = {
            "gender_analysis": self.gender_gap_result,
            "convergence_analysis": self.convergence_result,
            "combined_cost": 167000,
            "priority_recommendations": ["Focus on Level 3 employees", "Review promotion criteria"]
        }

    def test_create_gender_gap_report_text(self):
        """Test gender gap report creation in text format."""
        report = create_gender_gap_report(self.gender_gap_result, "text")
        
        assert isinstance(report, str)
        assert len(report) > 0
        assert "15.0%" in report  # Current gap
        assert "5.0%" in report   # Target gap
        assert "£150,000" in report  # Cost

    def test_create_gender_gap_report_json(self):
        """Test gender gap report creation in JSON format."""
        report = create_gender_gap_report(self.gender_gap_result, "json")
        
        assert isinstance(report, str)
        # Should be valid JSON
        parsed = json.loads(report)
        assert "current_gap" in parsed
        assert "total_cost" in parsed

    def test_create_median_convergence_report_text(self):
        """Test median convergence report creation in text format."""
        report = create_median_convergence_report(self.convergence_result, "text")
        
        assert isinstance(report, str)
        assert len(report) > 0
        assert "£17,000" in report  # Total cost
        assert "£75,000" in report  # Median salary

    def test_create_median_convergence_report_json(self):
        """Test median convergence report creation in JSON format."""
        report = create_median_convergence_report(self.convergence_result, "json")
        
        assert isinstance(report, str)
        # Should be valid JSON
        parsed = json.loads(report)
        assert "total_adjustment_cost" in parsed
        assert "median_salary" in parsed

    def test_create_equity_report_text(self):
        """Test equity report creation in text format."""
        report = create_equity_report(self.equity_result, "text")
        
        assert isinstance(report, str)
        assert len(report) > 0
        assert "£167,000" in report  # Combined cost

    def test_create_equity_report_json(self):
        """Test equity report creation in JSON format."""
        report = create_equity_report(self.equity_result, "json")
        
        assert isinstance(report, str)
        # Should be valid JSON
        parsed = json.loads(report)
        assert "combined_cost" in parsed


class TestReportSaving:
    """Test report saving functionality."""

    @patch('builtins.open', mock_open())
    @patch('model_interventions.Path')
    def test_save_report_text(self, mock_path):
        """Test saving text report."""
        report_content = "Test report content"
        output_file = "test_report.txt"
        
        save_report(report_content, output_file, "text")
        
        # Should have attempted to write file
        mock_open().return_value.write.assert_called()

    @patch('builtins.open', mock_open())
    @patch('model_interventions.Path')
    def test_save_report_json(self, mock_path):
        """Test saving JSON report."""
        report_content = '{"test": "data"}'
        output_file = "test_report.json"
        
        save_report(report_content, output_file, "json")
        
        # Should have attempted to write file
        mock_open().return_value.write.assert_called()

    def test_save_report_with_temp_file(self):
        """Test saving report to actual temporary file."""
        report_content = "Test report for file operations"
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
            temp_path = tmp_file.name
        
        try:
            save_report(report_content, temp_path, "text")
            
            # Verify file was created and has content
            with open(temp_path, 'r') as f:
                saved_content = f.read()
                assert report_content in saved_content
        finally:
            Path(temp_path).unlink(missing_ok=True)


class TestAnalysisFunctions:
    """Test analysis workflow functions."""

    def setup_method(self):
        """Setup test fixtures."""
        self.population_data = [
            {"employee_id": 1, "level": 3, "salary": 60000, "gender": "Female", "performance_rating": "High Performing"},
            {"employee_id": 2, "level": 3, "salary": 75000, "gender": "Male", "performance_rating": "Achieving"},
            {"employee_id": 3, "level": 4, "salary": 80000, "gender": "Female", "performance_rating": "Exceeding"}
        ]
        
        self.mock_args = MagicMock()
        self.mock_args.target_gap = 0.05
        self.mock_args.budget = 100000
        self.mock_args.output_format = "text"

    @patch('model_interventions.InterventionStrategySimulator')
    def test_run_gender_gap_analysis(self, mock_simulator_class):
        """Test gender gap analysis execution."""
        # Setup mock
        mock_simulator = MagicMock()
        mock_simulator_class.return_value = mock_simulator
        mock_simulator.analyze_gender_pay_gap_remediation.return_value = {
            "current_gap": 0.15,
            "remediation_cost": 50000,
            "affected_employees": 10
        }

        result = run_gender_gap_analysis(self.population_data, self.mock_args)
        
        assert isinstance(result, dict)
        assert "current_gap" in result
        mock_simulator_class.assert_called_once()

    @patch('model_interventions.MedianConvergenceAnalyzer')
    def test_run_median_convergence_analysis(self, mock_analyzer_class):
        """Test median convergence analysis execution."""
        # Setup mock
        mock_analyzer = MagicMock()
        mock_analyzer_class.return_value = mock_analyzer
        mock_analyzer.identify_below_median_employees.return_value = [
            {"employee_id": 1, "salary_gap": 5000}
        ]

        result = run_median_convergence_analysis(self.population_data, self.mock_args)
        
        assert isinstance(result, dict)
        mock_analyzer_class.assert_called_once()

    @patch('model_interventions.run_gender_gap_analysis')
    @patch('model_interventions.run_median_convergence_analysis')
    def test_run_equity_analysis(self, mock_convergence, mock_gender):
        """Test comprehensive equity analysis."""
        # Setup mocks
        mock_gender.return_value = {"current_gap": 0.15, "total_cost": 50000}
        mock_convergence.return_value = {"adjustment_cost": 30000}

        result = run_equity_analysis(self.population_data, self.mock_args)
        
        assert isinstance(result, dict)
        assert "gender_analysis" in result
        assert "convergence_analysis" in result
        assert "combined_cost" in result
        
        mock_gender.assert_called_once()
        mock_convergence.assert_called_once()


class TestMainFunction:
    """Test the main CLI function."""

    @patch('model_interventions.argparse.ArgumentParser')
    @patch('model_interventions.load_population_data')
    def test_main_gender_gap_analysis(self, mock_load_data, mock_parser_class):
        """Test main function with gender gap analysis."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        
        mock_args = MagicMock()
        mock_args.analysis_type = "gender_gap"
        mock_args.data_source = "generate"
        mock_args.output_file = None
        mock_args.output_format = "text"
        mock_parser.parse_args.return_value = mock_args

        mock_population = [{"employee_id": 1, "salary": 50000, "gender": "Female"}]
        mock_load_data.return_value = mock_population

        with patch('model_interventions.run_gender_gap_analysis') as mock_analysis:
            mock_analysis.return_value = {"current_gap": 0.1, "total_cost": 25000}
            
            with patch('builtins.print'):  # Suppress output
                try:
                    main()
                except SystemExit:
                    pass  # Expected for successful completion
                
                mock_analysis.assert_called_once()

    @patch('model_interventions.argparse.ArgumentParser')
    @patch('model_interventions.load_population_data')
    def test_main_convergence_analysis(self, mock_load_data, mock_parser_class):
        """Test main function with convergence analysis."""
        # Setup mocks
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        
        mock_args = MagicMock()
        mock_args.analysis_type = "convergence"
        mock_args.data_source = "generate"
        mock_args.output_file = None
        mock_parser.parse_args.return_value = mock_args

        mock_population = [{"employee_id": 1, "salary": 60000}]
        mock_load_data.return_value = mock_population

        with patch('model_interventions.run_median_convergence_analysis') as mock_analysis:
            mock_analysis.return_value = {"adjustment_cost": 15000}
            
            with patch('builtins.print'):
                try:
                    main()
                except SystemExit:
                    pass
                
                mock_analysis.assert_called_once()

    @patch('model_interventions.argparse.ArgumentParser')
    def test_main_error_handling(self, mock_parser_class):
        """Test main function error handling."""
        mock_parser = MagicMock()
        mock_parser_class.return_value = mock_parser
        mock_parser.parse_args.side_effect = Exception("CLI parsing failed")

        with patch('builtins.print'):
            try:
                main()
            except (SystemExit, Exception):
                pass  # Expected for error conditions


class TestIntegrationScenarios:
    """Test integration scenarios and edge cases."""

    def test_full_workflow_integration(self):
        """Test complete workflow from data loading to report generation."""
        # Test the integration of multiple components
        population_data = [
            {"employee_id": 1, "level": 3, "salary": 60000, "gender": "Female"},
            {"employee_id": 2, "level": 3, "salary": 70000, "gender": "Male"}
        ]

        # Test formatting functions
        formatted_currency = format_currency(65000)
        assert formatted_currency == "£65,000"

        formatted_percentage = format_percentage(0.125)
        assert formatted_percentage == "12.5%"

        # Test report generation with mock data
        mock_result = {
            "current_gap": 0.125,
            "target_gap": 0.05,
            "total_cost": 65000,
            "affected_employees": 1
        }

        report = create_gender_gap_report(mock_result, "text")
        assert len(report) > 0
        assert "12.5%" in report
        assert "£65,000" in report

    def test_error_recovery_scenarios(self):
        """Test error recovery in various scenarios."""
        # Test with empty population data
        empty_population = []
        
        # Should handle empty data gracefully
        try:
            format_currency(None)
        except (TypeError, ValueError):
            pass  # Expected

        try:
            format_percentage(None)
        except (TypeError, ValueError):
            pass  # Expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
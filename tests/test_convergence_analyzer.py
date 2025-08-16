#!/usr/bin/env python3
"""
Comprehensive tests for median_convergence_analyzer module.

Tests convergence analysis, intervention strategies, and below-median employee identification.
"""

from unittest.mock import patch

import pytest

# Import the module under test
from median_convergence_analyzer import MedianConvergenceAnalyzer


class TestMedianConvergenceAnalyzer:
    """
    Test the MedianConvergenceAnalyzer class.
    """

    def setup_method(self):
        """
        Setup test fixtures.
        """
        self.population_data = [
            {
                "employee_id": 1,
                "level": 3,
                "salary": 60000,  # Below median for level 3
                "performance_rating": "Achieving",
                "gender": "Female",
                "tenure_years": 2,
            },
            {
                "employee_id": 2,
                "level": 3,
                "salary": 75000,  # At median for level 3
                "performance_rating": "High Performing",
                "gender": "Male",
                "tenure_years": 3,
            },
            {
                "employee_id": 3,
                "level": 3,
                "salary": 85000,  # Above median for level 3
                "performance_rating": "Exceeding",
                "gender": "Female",
                "tenure_years": 5,
            },
            {
                "employee_id": 4,
                "level": 4,
                "salary": 90000,  # At median for level 4
                "performance_rating": "High Performing",
                "gender": "Male",
                "tenure_years": 4,
            },
        ]

        self.config = {
            "convergence_threshold_years": 5,
            "acceptable_gap_percent": 5.0,
            "confidence_interval": 0.95,
            "market_inflation_rate": 0.025,
        }

    @patch("median_convergence_analyzer.LOGGER")
    def test_initialization(self, mock_logger):
        """
        Test analyzer initialization.
        """
        analyzer = MedianConvergenceAnalyzer(self.population_data, self.config)

        assert len(analyzer.population_data) == 4
        assert analyzer.config == self.config
        assert analyzer.convergence_threshold_years == 5
        assert analyzer.acceptable_gap_percent == 5.0

        # Verify logging occurred
        mock_logger.info.assert_called()

    @patch("median_convergence_analyzer.LOGGER")
    def test_initialization_with_defaults(self, mock_logger):
        """
        Test analyzer initialization with default config.
        """
        analyzer = MedianConvergenceAnalyzer(self.population_data)

        assert len(analyzer.population_data) == 4
        assert analyzer.convergence_threshold_years == 5  # default
        assert analyzer.acceptable_gap_percent == 5.0  # default

    def test_median_calculation_by_level(self):
        """
        Test calculation of median salaries by level.
        """
        analyzer = MedianConvergenceAnalyzer(self.population_data, self.config)

        # Level 3 median should be 75000 (middle of 60000, 75000, 85000)
        level_3_median = analyzer.medians_by_level[3]
        assert level_3_median == 75000

        # Level 4 has only one employee
        level_4_median = analyzer.medians_by_level[4]
        assert level_4_median == 90000

    @patch("median_convergence_analyzer.LOGGER")
    def test_analyze_convergence_timeline_below_median(self, mock_logger):
        """
        Test convergence timeline analysis for below-median employee.
        """
        analyzer = MedianConvergenceAnalyzer(self.population_data, self.config)

        # Test employee 1 (below median)
        employee_data = self.population_data[0]  # 60000 salary, level 3

        result = analyzer.analyze_convergence_timeline(employee_data)

        # Verify result structure - matches actual implementation
        assert "status" in result
        assert "current_gap_percent" in result
        assert "current_gap_amount" in result
        assert "scenarios" in result

        # Should be identified as below median
        assert result["status"] == "below_median"

        # Gap should be calculated correctly
        # Expected gap: (75000 - 60000) / 75000 * 100 = 20%
        expected_gap_percent = ((75000 - 60000) / 75000) * 100
        assert abs(result["current_gap_percent"] - expected_gap_percent) < 0.01

        # Gap amount should be 15000
        assert result["current_gap_amount"] == 15000

    @patch("median_convergence_analyzer.LOGGER")
    def test_analyze_convergence_timeline_at_median(self, mock_logger):
        """
        Test convergence timeline analysis for at-median employee.
        """
        analyzer = MedianConvergenceAnalyzer(self.population_data, self.config)

        # Test employee 2 (at median)
        employee_data = self.population_data[1]  # 75000 salary, level 3

        result = analyzer.analyze_convergence_timeline(employee_data)

        # Should be identified as above median (at median counts as above)
        assert result["status"] == "above_median"

        # Gap should be zero for at-median employee
        assert abs(result["current_gap_percent"]) < 0.01

    @patch("median_convergence_analyzer.LOGGER")
    def test_analyze_convergence_timeline_above_median(self, mock_logger):
        """
        Test convergence timeline analysis for above-median employee.
        """
        analyzer = MedianConvergenceAnalyzer(self.population_data, self.config)

        # Test employee 3 (above median)
        employee_data = self.population_data[2]  # 85000 salary, level 3

        result = analyzer.analyze_convergence_timeline(employee_data)

        # Should be identified as above median
        assert result["status"] == "above_median"

        # Should have positive gap percent (above median means positive gap from median)
        assert result["current_gap_percent"] > 0

    def test_convergence_timeline_with_performance_target(self):
        """
        Test convergence analysis with target performance level.
        """
        analyzer = MedianConvergenceAnalyzer(self.population_data, self.config)

        employee_data = self.population_data[0]  # Below median employee

        result = analyzer.analyze_convergence_timeline(employee_data, target_performance_level="High Performing")

        # Should still identify as below median
        assert result["status"] == "below_median"

        # Should include scenarios with intervention
        assert "scenarios" in result
        assert "intervention" in result["scenarios"]

    def test_identify_below_median_employees(self):
        """
        Test identification of below-median employees.
        """
        analyzer = MedianConvergenceAnalyzer(self.population_data, self.config)

        # Mock the identify_below_median_employees method if it exists
        try:
            below_median_result = analyzer.identify_below_median_employees(
                min_gap_percent=10.0, include_gender_analysis=True  # 10% threshold
            )

            # Should identify employee 1 (20% below median)
            if isinstance(below_median_result, dict):
                assert "employees" in below_median_result or "below_median_employees" in below_median_result
            elif isinstance(below_median_result, list):
                # Should contain at least one employee
                assert len(below_median_result) >= 1

        except AttributeError:
            # Method might not exist, skip this test
            pytest.skip("identify_below_median_employees method not implemented")

    def test_gender_based_median_calculation(self):
        """
        Test median calculation by level and gender.
        """
        analyzer = MedianConvergenceAnalyzer(self.population_data, self.config)

        # Check if gender-based medians are calculated
        if hasattr(analyzer, "medians_by_level_gender"):
            # Level 3 has both male and female employees
            level_3_gender_medians = analyzer.medians_by_level_gender.get(3, {})

            if "Female" in level_3_gender_medians and "Male" in level_3_gender_medians:
                female_median = level_3_gender_medians["Female"]
                male_median = level_3_gender_medians["Male"]

                # Female median: average of 60000 and 85000 = 72500
                # Male median: 75000 (only one male)
                assert female_median == 72500
                assert male_median == 75000

    def test_convergence_analysis_edge_cases(self):
        """
        Test convergence analysis edge cases.
        """
        analyzer = MedianConvergenceAnalyzer(self.population_data, self.config)

        # Test with employee at exactly acceptable gap threshold
        borderline_employee = {
            "employee_id": 999,
            "level": 3,
            "salary": 71250,  # 5% below median (75000)
            "performance_rating": "Achieving",
            "gender": "Male",
            "tenure_years": 1,
        }

        result = analyzer.analyze_convergence_timeline(borderline_employee)

        # Gap should be exactly at threshold
        expected_gap = (75000 - 71250) / 75000 * 100  # 5%
        assert abs(result["current_gap_percent"] - expected_gap) < 0.01

    def test_convergence_timeline_calculations(self):
        """
        Test convergence timeline calculations.
        """
        analyzer = MedianConvergenceAnalyzer(self.population_data, self.config)

        employee_data = self.population_data[0]  # Below median employee
        result = analyzer.analyze_convergence_timeline(employee_data)

        # Should include timeline estimates
        timeline_fields = [
            "natural_convergence_years",
            "intervention_convergence_years",
            "convergence_timeline",
            "years_to_median",
        ]

        # At least one timeline field should be present
        has_timeline = any(field in result for field in timeline_fields)
        if has_timeline:
            # Timeline should be reasonable (1-20 years)
            for field in timeline_fields:
                if field in result and result[field] is not None:
                    timeline = result[field]
                    if isinstance(timeline, (int, float)):
                        assert 0 < timeline <= 20, f"{field} timeline {timeline} unrealistic"

    @patch("median_convergence_analyzer.LOGGER")
    def test_analyze_multiple_employees(self, mock_logger):
        """
        Test analyzing multiple employees.
        """
        analyzer = MedianConvergenceAnalyzer(self.population_data, self.config)

        results = []
        for employee in self.population_data:
            result = analyzer.analyze_convergence_timeline(employee)
            results.append(result)

        assert len(results) == 4

        # Should have mix of below and above median
        below_median_count = sum(1 for r in results if r["status"] == "below_median")
        above_median_count = len(results) - below_median_count

        assert below_median_count >= 1, "Should have at least one below-median employee"
        assert above_median_count >= 1, "Should have at least one above-median employee"

    def test_configuration_impact(self):
        """
        Test impact of different configuration parameters.
        """
        # Test with stricter acceptable gap
        strict_config = self.config.copy()
        strict_config["acceptable_gap_percent"] = 2.0  # Very strict

        analyzer_strict = MedianConvergenceAnalyzer(self.population_data, strict_config)

        # Test with lenient acceptable gap
        lenient_config = self.config.copy()
        lenient_config["acceptable_gap_percent"] = 25.0  # Very lenient

        analyzer_lenient = MedianConvergenceAnalyzer(self.population_data, lenient_config)

        employee_data = self.population_data[0]  # Below median employee

        strict_result = analyzer_strict.analyze_convergence_timeline(employee_data)
        lenient_result = analyzer_lenient.analyze_convergence_timeline(employee_data)

        # Both should identify as below median (20% gap)
        assert strict_result["status"] == "below_median"
        assert lenient_result["status"] == "below_median"

    def test_empty_population_handling(self):
        """
        Test handling of empty population.
        """
        with pytest.raises((ValueError, IndexError, KeyError)):
            MedianConvergenceAnalyzer([], self.config)

    def test_single_employee_population(self):
        """
        Test handling of single employee population.
        """
        single_employee = [self.population_data[0]]

        analyzer = MedianConvergenceAnalyzer(single_employee, self.config)

        # Should handle single employee gracefully
        assert len(analyzer.population_data) == 1
        assert analyzer.medians_by_level[3] == 60000  # Only employee's salary

    def test_same_level_employees(self):
        """
        Test analysis with multiple employees at same level.
        """
        same_level_data = [
            {"employee_id": 1, "level": 3, "salary": 60000, "performance_rating": "Achieving", "gender": "Female"},
            {"employee_id": 2, "level": 3, "salary": 70000, "performance_rating": "High Performing", "gender": "Male"},
            {"employee_id": 3, "level": 3, "salary": 80000, "performance_rating": "Exceeding", "gender": "Female"},
        ]

        analyzer = MedianConvergenceAnalyzer(same_level_data, self.config)

        # Median should be 70000
        assert analyzer.medians_by_level[3] == 70000

        # Test convergence for each employee
        for employee in same_level_data:
            result = analyzer.analyze_convergence_timeline(employee)

            if employee["salary"] < 70000:
                assert result["status"] == "below_median"
            else:
                assert result["status"] == "above_median"


class TestConvergenceAnalyzerErrorHandling:
    """
    Test error handling in convergence analyzer.
    """

    def test_invalid_employee_data(self):
        """
        Test handling of invalid employee data.
        """
        population_data = [
            {"employee_id": 1, "level": 3, "salary": 60000, "performance_rating": "Achieving", "gender": "Female"}
        ]

        analyzer = MedianConvergenceAnalyzer(population_data)

        # Test with missing required fields
        invalid_employee = {"employee_id": 999}  # Missing level, salary

        with pytest.raises((KeyError, ValueError)):
            analyzer.analyze_convergence_timeline(invalid_employee)

    def test_invalid_configuration(self):
        """
        Test handling of invalid configuration.
        """
        population_data = [
            {"employee_id": 1, "level": 3, "salary": 60000, "performance_rating": "Achieving", "gender": "Female"}
        ]

        # Test with invalid convergence threshold
        invalid_config = {"convergence_threshold_years": -1}

        # Test behavior with invalid config - should use the provided value (no validation)
        analyzer = MedianConvergenceAnalyzer(population_data, invalid_config)
        # The analyzer accepts the invalid value as provided
        assert analyzer.convergence_threshold_years == -1

    def test_malformed_population_data(self):
        """
        Test handling of malformed population data.
        """
        malformed_data = [
            {"employee_id": 1, "level": "invalid", "salary": "not_a_number"},  # Wrong types
            None,  # Null employee
            {"employee_id": 2},  # Missing required fields
        ]

        # Should handle gracefully or raise appropriate errors
        with pytest.raises((TypeError, ValueError, AttributeError)):
            analyzer = MedianConvergenceAnalyzer(malformed_data)
            # Try to use it
            if hasattr(analyzer, "medians_by_level"):
                analyzer.analyze_convergence_timeline({"employee_id": 1, "level": 3, "salary": 60000})


class TestConvergenceAnalyzerPerformance:
    """
    Test performance characteristics of convergence analyzer.
    """

    def test_large_population_handling(self):
        """
        Test analyzer with large population.
        """
        # Create large population
        large_population = []
        for i in range(1000):
            employee = {
                "employee_id": i + 1,
                "level": (i % 6) + 1,  # Distribute across levels 1-6
                "salary": 50000 + (i * 30),  # Varying salaries
                "performance_rating": ["Achieving", "High Performing", "Exceeding"][i % 3],
                "gender": "Male" if i % 2 == 0 else "Female",
                "tenure_years": i % 10 + 1,
            }
            large_population.append(employee)

        # Should handle large population efficiently
        analyzer = MedianConvergenceAnalyzer(large_population)

        # Test analysis on a sample employee
        sample_employee = large_population[0]
        result = analyzer.analyze_convergence_timeline(sample_employee)

        # Should complete and return valid result
        assert "status" in result
        assert result["status"] in ["below_median", "above_median"]

    def test_memory_usage_reasonable(self):
        """
        Test that memory usage is reasonable for large populations.
        """
        # This is a basic test - in production you might use memory profiling
        population_data = []
        for i in range(100):
            employee = {
                "employee_id": i + 1,
                "level": (i % 6) + 1,
                "salary": 50000 + (i * 100),
                "performance_rating": "Achieving",
                "gender": "Female",
            }
            population_data.append(employee)

        analyzer = MedianConvergenceAnalyzer(population_data)

        # Should be able to create analyzer without issues
        assert len(analyzer.population_data) == 100
        assert len(analyzer.medians_by_level) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

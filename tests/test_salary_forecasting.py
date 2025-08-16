#!/usr/bin/env python3

import os
import sys

import numpy as np
import pytest

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from salary_forecasting_engine import SalaryForecastingEngine


class TestSalaryForecastingEngine:
    """
    Test suite for SalaryForecastingEngine mathematical calculations.
    """

    @pytest.fixture
    def engine(self):
        """
        Create a SalaryForecastingEngine instance for testing.
        """
        return SalaryForecastingEngine(confidence_level=0.95, market_inflation_rate=0.025)

    def test_cagr_calculation_basic(self, engine):
        """
        Test basic CAGR calculation.

        Args:
          engine:

        Returns:
        """
        # Known case: £80,000 to £100,000 over 5 years
        cagr = engine.calculate_cagr(80000, 100000, 5)
        expected = (100000 / 80000) ** (1 / 5) - 1  # ~0.04564 (4.56%)
        assert abs(cagr - expected) < 0.00001

    def test_cagr_calculation_edge_cases(self, engine):
        """
        Test CAGR calculation edge cases.

        Args:
          engine:

        Returns:
        """
        # Same start and end values
        cagr = engine.calculate_cagr(80000, 80000, 5)
        assert abs(cagr - 0.0) < 0.00001

        # One year duration
        cagr = engine.calculate_cagr(80000, 84000, 1)
        expected = 0.05  # 5% growth
        assert abs(cagr - expected) < 0.00001

    def test_cagr_invalid_inputs(self, engine):
        """
        Test CAGR calculation with invalid inputs.

        Args:
          engine:

        Returns:
        """
        with pytest.raises(ValueError):
            engine.calculate_cagr(-80000, 100000, 5)  # Negative start

        with pytest.raises(ValueError):
            engine.calculate_cagr(80000, -100000, 5)  # Negative end

        with pytest.raises(ValueError):
            engine.calculate_cagr(80000, 100000, -5)  # Negative years

        with pytest.raises(ValueError):
            engine.calculate_cagr(0, 100000, 5)  # Zero start

    def test_compound_growth_projection(self, engine):
        """
        Test compound growth projection.

        Args:
          engine:

        Returns:
        """
        # £80,000 at 5% for 3 years = £92,610
        future_value = engine.project_compound_growth(80000, 0.05, 3)
        expected = 80000 * (1.05**3)  # 92610
        assert abs(future_value - expected) < 0.01

    def test_compound_growth_zero_years(self, engine):
        """
        Test compound growth with zero years.

        Args:
          engine:

        Returns:
        """
        future_value = engine.project_compound_growth(80000, 0.05, 0)
        assert future_value == 80000  # No growth

    def test_compound_growth_invalid_inputs(self, engine):
        """
        Test compound growth with invalid inputs.

        Args:
          engine:

        Returns:
        """
        with pytest.raises(ValueError):
            engine.project_compound_growth(-80000, 0.05, 3)  # Negative initial

        with pytest.raises(ValueError):
            engine.project_compound_growth(80000, 0.05, -3)  # Negative years

    def test_uplift_increase_calculation(self, engine):
        """
        Test uplift increase calculation using UPLIFT_MATRIX.

        Args:
          engine:

        Returns:
        """
        # Level 5 (advanced) High Performing: 1.25% + 2.25% + 0.75% = 4.25%
        new_salary = engine.calculate_uplift_increase(80000, 5, "High Performing")
        expected = 80000 * 1.0425  # 83400
        assert abs(new_salary - expected) < 0.01

        # Level 3 (expert) Exceeding: 1.25% + 3.0% + 1.0% = 5.25%
        new_salary = engine.calculate_uplift_increase(75000, 3, "Exceeding")
        expected = 75000 * 1.0525  # 78937.50
        assert abs(new_salary - expected) < 0.01

    def test_uplift_invalid_inputs(self, engine):
        """
        Test uplift calculation with invalid inputs.

        Args:
          engine:

        Returns:
        """
        with pytest.raises(ValueError):
            engine.calculate_uplift_increase(80000, 5, "Invalid Rating")

        with pytest.raises(ValueError):
            engine.calculate_uplift_increase(80000, 7, "High Performing")  # Invalid level

    def test_confidence_interval_calculation(self, engine):
        """
        Test confidence interval calculation.

        Args:
          engine:

        Returns:
        """
        # Test with known values
        values = [80000, 82000, 84000, 86000, 88000]
        lower, upper = engine.calculate_confidence_interval(values, confidence_level=0.95)

        # Should be symmetric around mean (84000)
        mean = np.mean(values)
        assert lower < mean < upper
        assert upper - mean == mean - lower  # Symmetric

    def test_confidence_interval_edge_cases(self, engine):
        """
        Test confidence interval edge cases.

        Args:
          engine:

        Returns:
        """
        # Single value
        values = [80000]
        lower, upper = engine.calculate_confidence_interval(values)
        assert lower == upper == 80000  # No variance

        # Empty list should raise error
        with pytest.raises(ValueError):
            engine.calculate_confidence_interval([])

    def test_performance_scenarios_generation(self, engine):
        """
        Test performance scenario generation.

        Args:
          engine:

        Returns:
        """
        scenarios = engine.generate_performance_scenarios("Achieving")

        # Should have three scenarios
        assert len(scenarios) == 3
        assert "conservative" in scenarios
        assert "realistic" in scenarios
        assert "optimistic" in scenarios

        # Each scenario should have 5 years
        for scenario_name, path in scenarios.items():
            assert len(path) == 5
            assert all(isinstance(rating, str) for rating in path)

        # Conservative should generally be lower than optimistic
        conservative_final = scenarios["conservative"][-1]
        optimistic_final = scenarios["optimistic"][-1]

        # Define rating order for comparison
        rating_order = ["Not met", "Partially met", "Achieving", "High Performing", "Exceeding"]
        conservative_index = rating_order.index(conservative_final)
        optimistic_index = rating_order.index(optimistic_final)

        assert optimistic_index >= conservative_index

    def test_time_to_target_calculation(self, engine):
        """
        Test time to target salary calculation.

        Args:
          engine:

        Returns:
        """
        # £80,000 to £100,000 at 5% growth
        years = engine.calculate_time_to_target(80000, 100000, 0.05)
        expected = np.log(100000 / 80000) / np.log(1.05)  # ~4.56 years
        assert abs(years - expected) < 0.01

    def test_time_to_target_invalid_inputs(self, engine):
        """
        Test time to target with invalid inputs.

        Args:
          engine:

        Returns:
        """
        with pytest.raises(ValueError):
            engine.calculate_time_to_target(0, 100000, 0.05)  # Zero current

        with pytest.raises(ValueError):
            engine.calculate_time_to_target(100000, 80000, 0.05)  # Target < current

        with pytest.raises(ValueError):
            engine.calculate_time_to_target(80000, 100000, 0)  # Zero growth rate

    def test_market_adjustments(self, engine):
        """
        Test market adjustment application.

        Args:
          engine:

        Returns:
        """
        # Base salary path
        salary_path = [80000, 82000, 84000, 86000, 88000, 90000]

        # Apply market adjustments at years 3 and 6
        adjusted_path = engine.apply_market_adjustments(salary_path, [2, 5])  # 0-indexed

        # Adjusted path should be higher from adjustment points onward
        assert adjusted_path[0] == salary_path[0]  # No change at start
        assert adjusted_path[1] == salary_path[1]  # No change before first adjustment
        assert adjusted_path[2] > salary_path[2]  # First adjustment applied
        assert adjusted_path[5] > adjusted_path[4] * 1.02  # Second adjustment applied

        # Empty path should return empty
        assert engine.apply_market_adjustments([]) == []

    def test_population_median_progression(self, engine):
        """
        Test population median progression calculation.

        Args:
          engine:

        Returns:
        """
        # Create test population data
        population_data = [
            {"employee_id": 1, "level": 3, "salary": 75000, "gender": "Male"},
            {"employee_id": 2, "level": 3, "salary": 80000, "gender": "Female"},
            {"employee_id": 3, "level": 3, "salary": 85000, "gender": "Male"},
            {"employee_id": 4, "level": 5, "salary": 90000, "gender": "Female"},
            {"employee_id": 5, "level": 5, "salary": 95000, "gender": "Male"},
        ]

        median_progression = engine.calculate_population_median_progression(population_data, years=3)

        # Should have entries for levels 3 and 5
        assert 3 in median_progression
        assert 5 in median_progression

        # Each level should have 4 values (current + 3 years)
        assert len(median_progression[3]) == 4
        assert len(median_progression[5]) == 4

        # Values should increase over time
        for level_path in median_progression.values():
            for i in range(1, len(level_path)):
                assert level_path[i] > level_path[i - 1]

    def test_validation_method(self, engine):
        """
        Test the built-in validation method.

        Args:
          engine:

        Returns:
        """
        result = engine.validate_calculations()
        assert result is True  # All validations should pass

    def test_performance_variance_calculation(self, engine):
        """
        Test performance variance calculation.

        Args:
          engine:

        Returns:
        """
        variance = engine._calculate_performance_variance()

        # Should have variance for all performance ratings
        expected_ratings = ["Not met", "Partially met", "Achieving", "High Performing", "Exceeding"]
        for rating in expected_ratings:
            assert rating in variance
            assert variance[rating] > 0  # All variances should be positive

        # Higher performance ratings should generally have higher variance
        assert variance["Exceeding"] > variance["Not met"]
        assert variance["High Performing"] > variance["Partially met"]


def test_engine_initialization():
    """
    Test engine initialization with different parameters.
    """
    # Default initialization
    engine1 = SalaryForecastingEngine()
    assert engine1.confidence_level == 0.95
    assert engine1.market_inflation_rate == 0.025

    # Custom initialization
    engine2 = SalaryForecastingEngine(confidence_level=0.90, market_inflation_rate=0.03)
    assert engine2.confidence_level == 0.90
    assert engine2.market_inflation_rate == 0.03


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])

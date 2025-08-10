#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

import numpy as np
import pandas as pd
import argparse
import json
from typing import List, Dict, Tuple, Optional, Union
from scipy import stats
from logger import LOGGER
from employee_population_simulator import UPLIFT_MATRIX, LEVEL_MAPPING


class SalaryForecastingEngine:
    """
    Core mathematical utilities for salary progression modeling and forecasting.

    Provides CAGR calculations, compound growth formulas, confidence intervals,
    and statistical modeling for individual employee salary projections.
    """

    def __init__(self, confidence_level=0.95, market_inflation_rate=0.025):
        self.confidence_level = confidence_level
        self.market_inflation_rate = market_inflation_rate
        self.performance_variance = self._calculate_performance_variance()

        LOGGER.info(f"Initialized SalaryForecastingEngine with {confidence_level:.1%} confidence intervals")
        LOGGER.info(f"Market inflation rate: {market_inflation_rate:.2%}")

    def calculate_cagr(self, starting_value: float, ending_value: float, years: int) -> float:
        """
        Calculate Compound Annual Growth Rate (CAGR)

        Formula: CAGR = (ending_value / starting_value)^(1/years) - 1

        Args:
            starting_value: Initial salary
            ending_value: Final salary after specified years
            years: Number of years between starting and ending values

        Returns:
            CAGR as decimal (e.g., 0.05 for 5%)
        """
        if starting_value <= 0 or ending_value <= 0 or years <= 0:
            raise ValueError("All values must be positive")

        cagr = (ending_value / starting_value) ** (1 / years) - 1
        return cagr

    def project_compound_growth(self, initial_value: float, growth_rate: float, years: int) -> float:
        """
        Project future value using compound growth

        Formula: future_value = initial_value × (1 + growth_rate)^years

        Args:
            initial_value: Starting salary
            growth_rate: Annual growth rate as decimal
            years: Number of years to project

        Returns:
            Projected future salary
        """
        if initial_value <= 0 or years < 0:
            raise ValueError("Initial value must be positive and years non-negative")

        future_value = initial_value * ((1 + growth_rate) ** years)
        return future_value

    def calculate_uplift_increase(self, current_salary: float, level: int, performance_rating: str) -> float:
        """
        Calculate salary increase based on UPLIFT_MATRIX

        Args:
            current_salary: Current employee salary
            level: Employee level (1-6)
            performance_rating: Performance rating string

        Returns:
            New salary after uplift application
        """
        if performance_rating not in UPLIFT_MATRIX:
            raise ValueError(f"Invalid performance rating: {performance_rating}")

        if level not in LEVEL_MAPPING:
            raise ValueError(f"Invalid level: {level}")

        level_category = LEVEL_MAPPING[level]
        uplift_data = UPLIFT_MATRIX[performance_rating]

        total_increase_rate = uplift_data["baseline"] + uplift_data["performance"] + uplift_data[level_category]

        new_salary = current_salary * (1 + total_increase_rate)
        return new_salary

    def calculate_confidence_interval(
        self, projected_values: List[float], confidence_level: Optional[float] = None
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval for projected salary values

        Args:
            projected_values: List of projected salary values
            confidence_level: Confidence level (defaults to instance setting)

        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if not projected_values:
            raise ValueError("projected_values cannot be empty")

        confidence = confidence_level or self.confidence_level
        values_array = np.array(projected_values)

        # Handle single value case
        if len(values_array) == 1:
            single_value = values_array[0]
            return (single_value, single_value)

        mean = np.mean(values_array)
        std_error = stats.sem(values_array)  # Standard error of the mean

        # Calculate confidence interval using t-distribution
        degrees_freedom = len(values_array) - 1
        confidence_interval = stats.t.interval(confidence, degrees_freedom, loc=mean, scale=std_error)

        return confidence_interval

    def generate_performance_scenarios(self, current_rating: str) -> Dict[str, List[str]]:
        """
        Generate realistic performance rating paths for different scenarios

        Args:
            current_rating: Current performance rating

        Returns:
            Dict with conservative, realistic, optimistic scenario paths
        """
        rating_progression = {
            "Not met": {
                "conservative": ["Not met", "Not met", "Partially met", "Partially met", "Achieving"],
                "realistic": ["Not met", "Partially met", "Achieving", "Achieving", "High Performing"],
                "optimistic": ["Partially met", "Achieving", "High Performing", "High Performing", "Exceeding"],
            },
            "Partially met": {
                "conservative": ["Partially met", "Partially met", "Achieving", "Achieving", "Achieving"],
                "realistic": ["Partially met", "Achieving", "Achieving", "High Performing", "High Performing"],
                "optimistic": ["Achieving", "High Performing", "High Performing", "Exceeding", "Exceeding"],
            },
            "Achieving": {
                "conservative": ["Achieving", "Achieving", "Achieving", "High Performing", "High Performing"],
                "realistic": ["Achieving", "Achieving", "High Performing", "High Performing", "Exceeding"],
                "optimistic": ["Achieving", "High Performing", "High Performing", "Exceeding", "Exceeding"],
            },
            "High Performing": {
                "conservative": [
                    "High Performing",
                    "High Performing",
                    "High Performing",
                    "High Performing",
                    "Exceeding",
                ],
                "realistic": ["High Performing", "High Performing", "Exceeding", "Exceeding", "Exceeding"],
                "optimistic": ["High Performing", "Exceeding", "Exceeding", "Exceeding", "Exceeding"],
            },
            "Exceeding": {
                "conservative": ["Exceeding", "Exceeding", "High Performing", "High Performing", "Exceeding"],
                "realistic": ["Exceeding", "Exceeding", "Exceeding", "Exceeding", "Exceeding"],
                "optimistic": ["Exceeding", "Exceeding", "Exceeding", "Exceeding", "Exceeding"],
            },
        }

        if current_rating not in rating_progression:
            # Default to 'Achieving' scenarios
            current_rating = "Achieving"

        return rating_progression[current_rating]

    def calculate_time_to_target(self, current_salary: float, target_salary: float, annual_growth_rate: float) -> float:
        """
        Calculate years needed to reach target salary

        Formula: years = log(target / current) / log(1 + growth_rate)

        Args:
            current_salary: Current salary
            target_salary: Target salary to reach
            annual_growth_rate: Expected annual growth rate

        Returns:
            Number of years to reach target (can be fractional)
        """
        if current_salary <= 0 or target_salary <= current_salary or annual_growth_rate <= 0:
            raise ValueError("Invalid input values for time to target calculation")

        years = np.log(target_salary / current_salary) / np.log(1 + annual_growth_rate)
        return years

    def apply_market_adjustments(
        self, salary_path: List[float], market_adjustment_years: List[int] = None
    ) -> List[float]:
        """
        Apply market adjustment cycles to salary progression

        Args:
            salary_path: List of projected salaries by year
            market_adjustment_years: Years when market adjustments occur

        Returns:
            Adjusted salary path with market corrections
        """
        if not salary_path:
            return salary_path

        # Default market adjustments every 3 years
        adjustment_years = market_adjustment_years or [3, 6, 9]
        adjusted_path = salary_path.copy()

        for year in adjustment_years:
            if year < len(adjusted_path):
                # Apply market adjustment (additional 2-4% boost)
                market_boost = np.random.uniform(0.02, 0.04)
                adjusted_path[year] *= 1 + market_boost

                # Apply boost to subsequent years as well
                for subsequent_year in range(year + 1, len(adjusted_path)):
                    adjusted_path[subsequent_year] *= 1 + market_boost

        return adjusted_path

    def calculate_population_median_progression(
        self, population_data: List[Dict], years: int = 5
    ) -> Dict[int, List[float]]:
        """
        Calculate median salary progression by level across population

        Args:
            population_data: List of employee dictionaries
            years: Number of years to project

        Returns:
            Dict mapping level to list of median salaries by year
        """
        median_progression = {}

        # Group by level
        df = pd.DataFrame(population_data)

        for level in sorted(df["level"].unique()):
            level_employees = df[df["level"] == level]
            current_median = level_employees["salary"].median()

            # Project median growth (assumes market-rate increases)
            median_path = [current_median]
            for year in range(1, years + 1):
                # Median grows at slightly below individual growth rates
                median_growth_rate = self.market_inflation_rate + 0.01  # 1% above inflation
                projected_median = median_path[0] * ((1 + median_growth_rate) ** year)
                median_path.append(projected_median)

            median_progression[level] = median_path

        return median_progression

    def _calculate_performance_variance(self) -> Dict[str, float]:
        """
        Calculate historical variance in performance-based salary increases

        Returns:
            Dict mapping performance ratings to variance estimates
        """
        # Based on industry research - performance rating volatility
        return {
            "Not met": 0.005,  # Very low variance
            "Partially met": 0.008,
            "Achieving": 0.010,  # Base variance
            "High Performing": 0.015,
            "Exceeding": 0.020,  # Highest variance for top performers
        }

    def validate_calculations(self) -> bool:
        """
        Validate mathematical calculations with known test cases

        Returns:
            True if all validations pass
        """
        try:
            # Test CAGR calculation
            cagr = self.calculate_cagr(80000, 100000, 5)
            expected_cagr = 0.04564  # ~4.56%
            assert abs(cagr - expected_cagr) < 0.001, f"CAGR test failed: {cagr} vs {expected_cagr}"

            # Test compound growth
            future_salary = self.project_compound_growth(80000, 0.05, 3)
            expected_future = 92610  # 80000 * 1.05^3
            assert (
                abs(future_salary - expected_future) < 1
            ), f"Compound growth test failed: {future_salary} vs {expected_future}"

            # Test uplift calculation
            new_salary = self.calculate_uplift_increase(80000, 5, "High Performing")
            # Level 5 = "advanced", High Performing = 1.25% + 2.25% + 0.75% = 4.25%
            expected_salary = 80000 * 1.0425  # = 83400
            assert abs(new_salary - expected_salary) < 1, f"Uplift test failed: {new_salary} vs {expected_salary}"

            # Test time to target
            years = self.calculate_time_to_target(80000, 100000, 0.05)
            expected_years = 4.56  # log(100000/80000)/log(1.05)
            assert abs(years - expected_years) < 0.1, f"Time to target test failed: {years} vs {expected_years}"

            LOGGER.info("✅ All mathematical validations passed")
            return True

        except Exception as e:
            LOGGER.error(f"❌ Validation failed: {e}")
            return False


def main():
    """Main function for testing and validation"""
    parser = argparse.ArgumentParser(description="Salary Forecasting Engine")
    parser.add_argument("--test-calculations", action="store_true", help="Run validation tests")
    parser.add_argument(
        "--calculate-cagr",
        nargs=3,
        type=float,
        metavar=("start", "end", "years"),
        help="Calculate CAGR for given start, end, years",
    )
    parser.add_argument(
        "--project-growth",
        nargs=3,
        type=float,
        metavar=("initial", "rate", "years"),
        help="Project compound growth for initial, rate, years",
    )

    args = parser.parse_args()

    engine = SalaryForecastingEngine()

    if args.test_calculations:
        success = engine.validate_calculations()
        exit(0 if success else 1)

    if args.calculate_cagr:
        start, end, years = args.calculate_cagr
        cagr = engine.calculate_cagr(start, end, int(years))
        print(f"CAGR: {cagr:.4f} ({cagr:.2%})")

    if args.project_growth:
        initial, rate, years = args.project_growth
        future_value = engine.project_compound_growth(initial, rate, int(years))
        print(f"Future value: £{future_value:,.2f}")

    if not any([args.test_calculations, args.calculate_cagr, args.project_growth]):
        # Interactive demo
        print("🧮 Salary Forecasting Engine Demo")
        print("=" * 40)

        # Demo CAGR calculation
        cagr = engine.calculate_cagr(80000, 100000, 5)
        print(f"CAGR Example: £80,000 → £100,000 over 5 years = {cagr:.2%}")

        # Demo compound growth
        future_salary = engine.project_compound_growth(80000, 0.05, 3)
        print(f"Compound Growth: £80,000 at 5% for 3 years = £{future_salary:,.2f}")

        # Demo uplift calculation
        new_salary = engine.calculate_uplift_increase(80000, 5, "High Performing")
        print(f"Uplift Calculation: £80,000 Level 5 High Performing = £{new_salary:,.2f}")

        # Demo performance scenarios
        scenarios = engine.generate_performance_scenarios("Achieving")
        print(f"Performance Scenarios from 'Achieving':")
        for scenario, path in scenarios.items():
            print(f"  {scenario}: {' → '.join(path)}")


if __name__ == "__main__":
    main()

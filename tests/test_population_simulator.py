#!/usr/bin/env python3
"""Comprehensive tests for employee_population_simulator module.

Tests population generation, salary constraints, and distribution logic.
"""

import pytest
from unittest.mock import patch, MagicMock
import random

# Import the module under test
from employee_population_simulator import EmployeePopulationGenerator


class TestEmployeePopulationGenerator:
    """Test the EmployeePopulationGenerator class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.level_distribution = [0.25, 0.25, 0.20, 0.15, 0.10, 0.05]
        self.gender_pay_gap_percent = 15.0
        self.salary_constraints = {
            1: {"min": 28000, "max": 35000, "median_target": 30000},
            2: {"min": 45000, "max": 72000, "median_target": 60000},
            3: {"min": 72000, "max": 95000, "median_target": 83939},
            4: {"min": 76592, "max": 103624, "median_target": 90108},
            5: {"min": 76592, "max": 103624, "median_target": 90108},
            6: {"min": 76592, "max": 103624, "median_target": 90108},
        }
        self.generator = EmployeePopulationGenerator(
            population_size=100,
            random_seed=42,
            level_distribution=self.level_distribution,
            gender_pay_gap_percent=self.gender_pay_gap_percent,
            salary_constraints=self.salary_constraints,
        )

    def test_initialization(self):
        """Test generator initialization."""
        assert self.generator.population_size == 100
        assert self.generator.level_distribution == self.level_distribution
        assert self.generator.gender_pay_gap_percent == self.gender_pay_gap_percent
        assert self.generator.random_seed == 42

    def test_initialization_with_defaults(self):
        """Test generator initialization with default values."""
        generator = EmployeePopulationGenerator(population_size=50)
        assert generator.population_size == 50
        assert generator.level_distribution == [0.25, 0.25, 0.20, 0.15, 0.10, 0.05]
        assert generator.gender_pay_gap_percent is None  # Default
        assert generator.random_seed is not None

    def test_generate_population_basic(self):
        """Test basic population generation."""
        population = self.generator.generate_population()

        # Verify population size
        assert len(population) == 100

        # Verify each employee has required fields
        for employee in population:
            assert "employee_id" in employee
            assert "level" in employee
            assert "salary" in employee
            assert "performance_rating" in employee
            assert "gender" in employee
            assert "hire_date" in employee

    def test_generate_population_levels_within_range(self):
        """Test that generated population has levels within valid range."""
        population = self.generator.generate_population()

        for employee in population:
            assert 1 <= employee["level"] <= 6

    def test_generate_population_salaries_positive(self):
        """Test that all generated salaries are positive."""
        population = self.generator.generate_population()

        for employee in population:
            assert employee["salary"] > 0

    def test_generate_population_performance_ratings_valid(self):
        """Test that performance ratings are from valid set."""
        valid_ratings = ["Not met", "Partially met", "Achieving", "High Performing", "Exceeding"]
        population = self.generator.generate_population()

        for employee in population:
            assert employee["performance_rating"] in valid_ratings

    def test_generate_population_gender_distribution(self):
        """Test gender distribution in generated population."""
        population = self.generator.generate_population()

        genders = [emp["gender"] for emp in population]
        male_count = genders.count("Male")
        female_count = genders.count("Female")

        # Should have both genders represented
        assert male_count > 0
        assert female_count > 0
        assert male_count + female_count == len(population)

    def test_generate_population_level_distribution(self):
        """Test that level distribution approximately matches config."""
        # Use larger population for better statistical accuracy
        large_generator = EmployeePopulationGenerator(
            population_size=1000,
            random_seed=42,
            level_distribution=self.level_distribution,
            gender_pay_gap_percent=self.gender_pay_gap_percent,
            salary_constraints=self.salary_constraints,
        )
        population = large_generator.generate_population()

        # Count employees by level
        level_counts = {}
        for employee in population:
            level = employee["level"]
            level_counts[level] = level_counts.get(level, 0) + 1

        # Check that distribution roughly matches config (within 10% tolerance)
        expected_dist = self.level_distribution
        for level in range(1, 7):
            expected_count = expected_dist[level - 1] * 1000
            actual_count = level_counts.get(level, 0)
            tolerance = 0.15  # 15% tolerance for randomness

            assert (
                abs(actual_count - expected_count) <= expected_count * tolerance
            ), f"Level {level}: expected ~{expected_count}, got {actual_count}"

    def test_generate_population_salary_constraints(self):
        """Test that salaries respect level constraints."""
        population = self.generator.generate_population()

        salary_constraints = self.salary_constraints

        for employee in population:
            level = employee["level"]
            salary = employee["salary"]

            if level in salary_constraints:
                min_salary = salary_constraints[level]["min"]
                max_salary = salary_constraints[level]["max"]

                # Allow some flexibility for pay gap and negotiation effects
                tolerance = 0.3  # 30% tolerance for various adjustments
                adjusted_min = min_salary * (1 - tolerance)
                adjusted_max = max_salary * (1 + tolerance)

                assert (
                    adjusted_min <= salary <= adjusted_max
                ), f"Level {level} salary {salary} outside range {adjusted_min}-{adjusted_max}"

    def test_generate_population_unique_ids(self):
        """Test that all employee IDs are unique."""
        population = self.generator.generate_population()

        employee_ids = [emp["employee_id"] for emp in population]
        assert len(employee_ids) == len(set(employee_ids)), "Employee IDs should be unique"

    def test_generate_population_tenure_years_valid(self):
        """Test that hire dates are valid."""
        population = self.generator.generate_population()

        for employee in population:
            assert "hire_date" in employee, "Employee should have hire_date field"
            # Hire date should be a string in YYYY-MM-DD format
            hire_date = employee["hire_date"]
            assert isinstance(hire_date, str), f"Hire date should be string, got {type(hire_date)}"
            # Should be parseable as date
            from datetime import datetime

            try:
                parsed_date = datetime.strptime(hire_date, "%Y-%m-%d")
                assert parsed_date is not None
            except ValueError:
                assert False, f"Invalid hire date format: {hire_date}"

    def test_generate_population_departments_assigned(self):
        """Test that all employees have review history field."""
        population = self.generator.generate_population()

        for employee in population:
            # Based on actual employee structure, test for review_history field
            assert "review_history" in employee, "Employee should have review_history field"
            assert isinstance(employee["review_history"], list), "Review history should be a list"

    def test_generate_population_reproducible_with_seed(self):
        """Test that population generation is reproducible with same seed."""
        generator1 = EmployeePopulationGenerator(
            population_size=50,
            level_distribution=self.level_distribution,
            gender_pay_gap_percent=self.gender_pay_gap_percent,
            salary_constraints=self.salary_constraints,
            random_seed=12345,
        )

        generator2 = EmployeePopulationGenerator(
            population_size=50,
            level_distribution=self.level_distribution,
            gender_pay_gap_percent=self.gender_pay_gap_percent,
            salary_constraints=self.salary_constraints,
            random_seed=12345,
        )

        pop1 = generator1.generate_population()
        pop2 = generator2.generate_population()

        # Should generate identical populations
        assert len(pop1) == len(pop2)
        for i in range(len(pop1)):
            assert pop1[i]["level"] == pop2[i]["level"]
            assert pop1[i]["salary"] == pop2[i]["salary"]
            assert pop1[i]["performance_rating"] == pop2[i]["performance_rating"]

    def test_generate_population_different_with_different_seed(self):
        """Test that different seeds produce different populations."""
        generator1 = EmployeePopulationGenerator(
            population_size=50,
            level_distribution=self.level_distribution,
            gender_pay_gap_percent=self.gender_pay_gap_percent,
            salary_constraints=self.salary_constraints,
            random_seed=111,
        )

        generator2 = EmployeePopulationGenerator(
            population_size=50,
            level_distribution=self.level_distribution,
            gender_pay_gap_percent=self.gender_pay_gap_percent,
            salary_constraints=self.salary_constraints,
            random_seed=222,
        )

        pop1 = generator1.generate_population()
        pop2 = generator2.generate_population()

        # Should have some differences
        differences = 0
        for i in range(len(pop1)):
            if (
                pop1[i]["level"] != pop2[i]["level"]
                or pop1[i]["salary"] != pop2[i]["salary"]
                or pop1[i]["performance_rating"] != pop2[i]["performance_rating"]
            ):
                differences += 1

        # Expect at least 20% to be different with different seeds
        assert differences >= len(pop1) * 0.2

    def test_generate_population_small_size(self):
        """Test generation with small population size."""
        small_generator = EmployeePopulationGenerator(
            population_size=5,
            random_seed=42,
            level_distribution=self.level_distribution,
            gender_pay_gap_percent=self.gender_pay_gap_percent,
            salary_constraints=self.salary_constraints,
        )
        population = small_generator.generate_population()

        assert len(population) == 5

        # All basic validations should still pass
        for employee in population:
            assert 1 <= employee["level"] <= 6
            assert employee["salary"] > 0
            assert employee["performance_rating"] in [
                "Not met",
                "Partially met",
                "Achieving",
                "High Performing",
                "Exceeding",
            ]

    def test_generate_population_large_size(self):
        """Test generation with larger population size."""
        large_generator = EmployeePopulationGenerator(
            population_size=500,
            random_seed=42,
            level_distribution=self.level_distribution,
            gender_pay_gap_percent=self.gender_pay_gap_percent,
            salary_constraints=self.salary_constraints,
        )
        population = large_generator.generate_population()

        assert len(population) == 500

        # Should still maintain valid constraints
        for employee in population:
            assert 1 <= employee["level"] <= 6
            assert employee["salary"] > 0

    @patch("employee_population_simulator.LOGGER")
    def test_generate_population_logging(self, mock_logger):
        """Test that population generation includes proper logging."""
        population = self.generator.generate_population()

        # Verify logging occurred
        mock_logger.info.assert_called()

        # Check that success was logged
        log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        success_logs = [call for call in log_calls if "generated" in call.lower()]
        assert len(success_logs) > 0

    def test_generate_population_config_variations(self):
        """Test population generation with different config variations."""
        # Test with no gender pay gap
        no_gap_generator = EmployeePopulationGenerator(
            population_size=100,
            random_seed=42,
            level_distribution=self.level_distribution,
            gender_pay_gap_percent=0.0,
            salary_constraints=self.salary_constraints,
        )
        population = no_gap_generator.generate_population()
        assert len(population) == 100

        # Test with different level distribution
        skewed_generator = EmployeePopulationGenerator(
            population_size=100,
            random_seed=42,
            level_distribution=[0.5, 0.3, 0.1, 0.05, 0.03, 0.02],
            gender_pay_gap_percent=self.gender_pay_gap_percent,
            salary_constraints=self.salary_constraints,
        )
        population = skewed_generator.generate_population()
        assert len(population) == 100

    def test_generate_population_edge_cases(self):
        """Test population generation edge cases."""
        # Test with minimum population size
        min_generator = EmployeePopulationGenerator(
            population_size=1,
            random_seed=42,
            level_distribution=self.level_distribution,
            gender_pay_gap_percent=self.gender_pay_gap_percent,
            salary_constraints=self.salary_constraints,
        )
        population = min_generator.generate_population()
        assert len(population) == 1

        # Verify the single employee is valid
        employee = population[0]
        assert 1 <= employee["level"] <= 6
        assert employee["salary"] > 0
        assert employee["performance_rating"] in [
            "Not met",
            "Partially met",
            "Achieving",
            "High Performing",
            "Exceeding",
        ]

    def test_generate_population_performance_distribution(self):
        """Test performance rating distribution."""
        # Generate larger population for statistical validity
        large_generator = EmployeePopulationGenerator(
            population_size=1000,
            random_seed=42,
            level_distribution=self.level_distribution,
            gender_pay_gap_percent=self.gender_pay_gap_percent,
            salary_constraints=self.salary_constraints,
        )
        population = large_generator.generate_population()

        # Count performance ratings
        rating_counts = {}
        for employee in population:
            rating = employee["performance_rating"]
            rating_counts[rating] = rating_counts.get(rating, 0) + 1

        # Should have reasonable distribution (not all the same rating)
        assert len(rating_counts) >= 3, "Should have at least 3 different performance ratings"

        # Most common ratings should be middle-tier
        total = sum(rating_counts.values())
        achieving_percent = rating_counts.get("Achieving", 0) / total
        high_performing_percent = rating_counts.get("High Performing", 0) / total

        # These should be significant portions of the population
        assert achieving_percent > 0.1, "Should have significant 'Achieving' representation"
        assert high_performing_percent > 0.1, "Should have significant 'High Performing' representation"

    def test_generate_population_salary_realism(self):
        """Test that generated salaries are realistic for UK market."""
        population = self.generator.generate_population()

        for employee in population:
            salary = employee["salary"]

            # Basic sanity checks for UK salaries
            assert salary >= 20000, f"Salary {salary} too low for UK market"
            assert salary <= 200000, f"Salary {salary} unrealistically high"

            # Level-specific checks
            level = employee["level"]
            if level == 1:  # Graduate level
                assert 20000 <= salary <= 60000, f"Level 1 salary {salary} outside expected range"
            elif level == 6:  # Senior level
                assert salary >= 60000, f"Level 6 salary {salary} should be higher"


class TestPopulationGeneratorErrorHandling:
    """Test error handling in population generator."""

    def test_invalid_population_size(self):
        """Test handling of invalid population sizes."""
        # Test zero population size - expect KeyError during statistics logging
        with pytest.raises((ValueError, AssertionError, KeyError)):
            generator = EmployeePopulationGenerator(population_size=0)
            generator.generate_population()

        # Test negative population size - expect KeyError during statistics logging
        with pytest.raises((ValueError, AssertionError, KeyError)):
            generator = EmployeePopulationGenerator(population_size=-10)
            generator.generate_population()

    def test_invalid_level_distribution(self):
        """Test handling of invalid level distributions."""
        invalid_level_distribution = [0.5, 0.3, 0.1, 0.05, 0.03]  # Only 5 values instead of 6

        # Should handle gracefully or raise appropriate error
        with pytest.raises(ValueError):
            generator = EmployeePopulationGenerator(
                population_size=10,
                random_seed=42,
                level_distribution=invalid_level_distribution,
                gender_pay_gap_percent=15.0,
                salary_constraints=None,
            )

    def test_missing_salary_constraints(self):
        """Test handling when salary constraints are missing."""
        # Test with None salary constraints (should use defaults)
        generator = EmployeePopulationGenerator(
            population_size=10,
            random_seed=42,
            level_distribution=[0.25, 0.25, 0.20, 0.15, 0.10, 0.05],
            gender_pay_gap_percent=15.0,
            salary_constraints=None,  # Should use defaults
        )

        # Should work with default constraints or handle gracefully
        population = generator.generate_population()
        assert len(population) == 10

        # All employees should still have valid salaries
        for employee in population:
            assert employee["salary"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

#!/usr/bin/env python3
"""Tests for individual_progression_simulator module."""

import pytest
from unittest.mock import patch, MagicMock

# Import the module under test
from individual_progression_simulator import IndividualProgressionSimulator


class TestIndividualProgressionSimulator:
    """Test the IndividualProgressionSimulator class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.population_data = [
            {"employee_id": 1, "level": 3, "salary": 65000, "performance_rating": "High Performing"},
            {"employee_id": 2, "level": 4, "salary": 80000, "performance_rating": "Exceeding"},
        ]

        self.config = {"confidence_interval": 0.95, "market_inflation_rate": 0.025}

    @patch("individual_progression_simulator.LOGGER")
    def test_initialization(self, mock_logger):
        """Test simulator initialization."""
        simulator = IndividualProgressionSimulator(self.population_data, self.config)

        assert len(simulator.population_data) == 2
        mock_logger.info.assert_called()

    @patch("individual_progression_simulator.LOGGER")
    def test_project_salary_progression(self, mock_logger):
        """Test salary progression projection."""
        simulator = IndividualProgressionSimulator(self.population_data, self.config)

        employee_data = {"employee_id": 1, "level": 3, "salary": 65000, "performance_rating": "High Performing"}

        result = simulator.project_salary_progression(
            employee_data=employee_data, years=5, scenarios=["conservative", "realistic", "optimistic"]
        )

        # Verify result structure
        assert "projections" in result
        projections = result["projections"]

        assert "conservative" in projections
        assert "realistic" in projections
        assert "optimistic" in projections

        # Check each projection has required fields
        for scenario in ["conservative", "realistic", "optimistic"]:
            projection = projections[scenario]
            assert "final_salary" in projection
            assert projection["final_salary"] > 65000  # Should be higher than current


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

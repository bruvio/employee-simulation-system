#!/usr/bin/env python3
"""Tests for intervention_strategy_simulator module."""

import pytest
from unittest.mock import patch, MagicMock

# Import the module under test
from intervention_strategy_simulator import InterventionStrategySimulator


class TestInterventionStrategySimulator:
    """Test the InterventionStrategySimulator class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.population_data = [
            {"employee_id": 1, "level": 3, "salary": 60000, "performance_rating": "Achieving", "gender": "Female"},
            {"employee_id": 2, "level": 3, "salary": 75000, "performance_rating": "High Performing", "gender": "Male"},
        ]

        self.config = {"intervention_budget_constraint": 100000, "target_gender_gap_percent": 5.0}

    @patch("intervention_strategy_simulator.LOGGER")
    def test_initialization(self, mock_logger):
        """Test simulator initialization."""
        simulator = InterventionStrategySimulator(population_data=self.population_data, config=self.config)

        assert len(simulator.population_data) == 2
        assert simulator.config == self.config
        mock_logger.info.assert_called()

    @patch("intervention_strategy_simulator.LOGGER")
    def test_empty_population(self, mock_logger):
        """Test with empty population."""
        # Empty population should raise an error during initialization
        with pytest.raises((ValueError, KeyError, IndexError)):
            simulator = InterventionStrategySimulator(population_data=[], config=self.config)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

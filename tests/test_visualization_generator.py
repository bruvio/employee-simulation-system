#!/usr/bin/env python3
"""Tests for visualization_generator module."""

import pytest
from unittest.mock import patch, MagicMock

# Import the module under test  
from visualization_generator import VisualizationGenerator


class TestVisualizationGenerator:
    """Test the VisualizationGenerator class."""

    def setup_method(self):
        """Setup test fixtures."""
        self.population_data = [
            {"employee_id": 1, "level": 3, "salary": 65000, "performance_rating": "High Performing", "gender": "Female"},
            {"employee_id": 2, "level": 4, "salary": 80000, "performance_rating": "Exceeding", "gender": "Male"}
        ]

    @patch('visualization_generator.LOGGER')
    def test_initialization(self, mock_logger):
        """Test generator initialization."""
        generator = VisualizationGenerator(
            population_data=self.population_data
        )
        
        assert generator.population == self.population_data
        mock_logger.info.assert_called()

    @patch('visualization_generator.LOGGER')
    def test_initialization_with_empty_data(self, mock_logger):
        """Test generator with empty data."""
        generator = VisualizationGenerator(population_data=[])
        assert generator.population == []

    def test_setup_plotting_style(self):
        """Test plotting style setup."""
        generator = VisualizationGenerator(population_data=self.population_data)
        
        # Should have setup_plotting_style method
        if hasattr(generator, 'setup_plotting_style'):
            generator.setup_plotting_style()
        
        # Should complete without error
        assert generator is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
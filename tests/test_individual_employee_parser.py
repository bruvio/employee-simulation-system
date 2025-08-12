#!/usr/bin/env python3
"""Unit tests for individual_employee_parser module.

Tests the IndividualEmployeeParser class and related functions for parsing
and validating individual employee data from various formats.

Author: Employee Simulation System
Date: 2025-08-11
"""

import pytest
from pydantic import ValidationError

# Import the module under test
from individual_employee_parser import (
    IndividualEmployeeParser,
    EmployeeData,
    parse_employee_data_string,
    validate_employee_data,
    create_individual_employee
)


class TestEmployeeData:
    """Test the EmployeeData pydantic model validation."""
    
    def test_valid_employee_data(self):
        """Test creating EmployeeData with valid data."""
        employee = EmployeeData(
            level=5,
            salary=80000,
            performance_rating="Exceeding"
        )
        
        assert employee.level == 5
        assert employee.salary == 80000
        assert employee.performance_rating == "Exceeding"
        assert employee.gender == "Female"  # Default value
        assert employee.tenure_years == 1   # Default value
    
    def test_invalid_performance_rating(self):
        """Test validation fails for invalid performance rating."""
        with pytest.raises(ValidationError) as exc_info:
            EmployeeData(
                level=3,
                salary=75000,
                performance_rating="Outstanding"  # Invalid rating
            )
        
        assert "Performance rating must be one of" in str(exc_info.value)
    
    def test_invalid_level_range(self):
        """Test validation fails for level outside 1-6 range."""
        # Test level too low
        with pytest.raises(ValidationError):
            EmployeeData(
                level=0,
                salary=50000,
                performance_rating="Achieving"
            )
        
        # Test level too high
        with pytest.raises(ValidationError):
            EmployeeData(
                level=7,
                salary=100000,
                performance_rating="High Performing"
            )
    
    def test_invalid_salary_negative(self):
        """Test validation fails for negative salary."""
        with pytest.raises(ValidationError):
            EmployeeData(
                level=3,
                salary=-50000,
                performance_rating="Achieving"
            )
    
    def test_salary_level_validation(self):
        """Test salary range validation based on level."""
        # Valid salary for level
        employee = EmployeeData(
            level=3,
            salary=85000,  # Within range for level 3 (72000-95000)
            performance_rating="Achieving"
        )
        assert employee.salary == 85000
        
        # Salary way outside range should fail
        with pytest.raises(ValidationError) as exc_info:
            EmployeeData(
                level=1,
                salary=200000,  # Way too high for level 1 (28000-35000)
                performance_rating="Achieving"
            )
        
        assert "outside expected range" in str(exc_info.value)
    
    def test_invalid_gender(self):
        """Test validation fails for invalid gender."""
        with pytest.raises(ValidationError):
            EmployeeData(
                level=3,
                salary=75000,
                performance_rating="Achieving",
                gender="Other"  # Not in allowed list
            )


class TestIndividualEmployeeParser:
    """Test the IndividualEmployeeParser class."""
    
    def test_parse_from_string_basic(self):
        """Test parsing basic employee data from string."""
        parser = IndividualEmployeeParser()
        result = parser.parse_from_string("level:5,salary:80692.5,performance:Exceeding")
        
        expected = {
            'level': 5,
            'salary': 80692.5,
            'performance_rating': 'Exceeding'
        }
        
        assert result == expected
    
    def test_parse_from_string_extended(self):
        """Test parsing extended employee data from string."""
        parser = IndividualEmployeeParser()
        data_string = "level:3,salary:75000,performance:High Performing,gender:Male,tenure:3,name:John Doe"
        result = parser.parse_from_string(data_string)
        
        expected = {
            'level': 3,
            'salary': 75000.0,
            'performance_rating': 'High Performing',
            'gender': 'Male',
            'tenure_years': 3,
            'name': 'John Doe'
        }
        
        assert result == expected
    
    def test_parse_from_string_performance_alias(self):
        """Test parsing with 'performance' instead of 'performance_rating'."""
        parser = IndividualEmployeeParser()
        result = parser.parse_from_string("level:2,salary:60000,performance:Achieving")
        
        assert result['performance_rating'] == 'Achieving'
    
    def test_parse_from_string_empty_string(self):
        """Test parsing fails with empty string."""
        parser = IndividualEmployeeParser()
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_from_string("")
        
        assert "cannot be empty" in str(exc_info.value)
    
    def test_parse_from_string_invalid_format(self):
        """Test parsing fails with invalid format."""
        parser = IndividualEmployeeParser()
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_from_string("level=5,salary=80000")  # Using = instead of :
        
        assert "Expected 'key:value'" in str(exc_info.value)
    
    def test_parse_from_string_missing_required_fields(self):
        """Test parsing fails when required fields are missing."""
        parser = IndividualEmployeeParser()
        
        with pytest.raises(ValueError) as exc_info:
            parser.parse_from_string("level:5,salary:80000")  # Missing performance
        
        assert "Missing required fields" in str(exc_info.value)
    
    def test_parse_from_string_invalid_numeric_values(self):
        """Test parsing fails with invalid numeric values."""
        parser = IndividualEmployeeParser()
        
        with pytest.raises(ValueError):
            parser.parse_from_string("level:five,salary:80000,performance:Achieving")  # Non-numeric level
        
        with pytest.raises(ValueError):
            parser.parse_from_string("level:5,salary:eighty_thousand,performance:Achieving")  # Non-numeric salary
    
    def test_parse_from_dict_basic(self):
        """Test parsing from dictionary format."""
        parser = IndividualEmployeeParser()
        input_dict = {
            'level': 4,
            'salary': 90000,
            'performance_rating': 'High Performing'
        }
        
        result = parser.parse_from_dict(input_dict)
        assert result == input_dict
    
    def test_parse_from_dict_normalize_keys(self):
        """Test dictionary parsing normalizes key names."""
        parser = IndividualEmployeeParser()
        input_dict = {
            'level': 3,
            'salary': 75000,
            'performance': 'Achieving',  # Should normalize to performance_rating
            'tenure': 2                  # Should normalize to tenure_years
        }
        
        result = parser.parse_from_dict(input_dict)
        
        assert result['performance_rating'] == 'Achieving'
        assert result['tenure_years'] == 2
        assert 'performance' not in result
        assert 'tenure' not in result
    
    def test_parse_from_dict_invalid_input(self):
        """Test parsing from dictionary fails with invalid input."""
        parser = IndividualEmployeeParser()
        
        with pytest.raises(ValueError):
            parser.parse_from_dict("not_a_dict")
    
    def test_validate_and_create_success(self):
        """Test successful validation and creation."""
        parser = IndividualEmployeeParser()
        data = {
            'level': 5,
            'salary': 80000,
            'performance_rating': 'Exceeding'
        }
        
        employee = parser.validate_and_create(data)
        
        assert isinstance(employee, EmployeeData)
        assert employee.level == 5
        assert employee.salary == 80000
        assert employee.performance_rating == 'Exceeding'
    
    def test_validate_and_create_failure(self):
        """Test validation failure creates user-friendly error."""
        parser = IndividualEmployeeParser()
        data = {
            'level': 10,  # Invalid level
            'salary': -5000,  # Invalid salary
            'performance_rating': 'Invalid Rating'  # Invalid rating
        }
        
        with pytest.raises(ValueError) as exc_info:
            parser.validate_and_create(data)
        
        error_msg = str(exc_info.value)
        assert "validation failed" in error_msg


class TestConvenienceFunctions:
    """Test the convenience functions."""
    
    def test_parse_employee_data_string_success(self):
        """Test successful parsing with convenience function."""
        employee = parse_employee_data_string("level:5,salary:80692.5,performance:Exceeding")
        
        assert isinstance(employee, EmployeeData)
        assert employee.level == 5
        assert employee.salary == 80692.5
        assert employee.performance_rating == "Exceeding"
    
    def test_parse_employee_data_string_failure(self):
        """Test parsing failure with convenience function."""
        with pytest.raises(ValueError):
            parse_employee_data_string("level:invalid,salary:80000,performance:Achieving")
    
    def test_validate_employee_data_success(self):
        """Test successful validation with convenience function."""
        data = {
            'level': 3,
            'salary': 75000,
            'performance': 'High Performing'  # Test alias handling
        }
        
        employee = validate_employee_data(data)
        
        assert isinstance(employee, EmployeeData)
        assert employee.performance_rating == 'High Performing'
    
    def test_create_individual_employee(self):
        """Test creating employee record compatible with simulation system."""
        employee_data = EmployeeData(
            employee_id=42,
            name="Test Employee",
            level=4,
            salary=85000,
            performance_rating="High Performing",
            gender="Male",
            tenure_years=3,
            department="Marketing"
        )
        
        employee_record = create_individual_employee(employee_data)
        
        # Check required fields
        assert employee_record['employee_id'] == 42
        assert employee_record['name'] == "Test Employee"
        assert employee_record['level'] == 4
        assert employee_record['salary'] == 85000
        assert employee_record['performance_rating'] == "High Performing"
        assert employee_record['gender'] == "Male"
        assert employee_record['tenure_years'] == 3
        assert employee_record['department'] == "Marketing"
        
        # Check additional simulation system fields
        assert 'hire_date' in employee_record
        assert 'promotion_eligible' in employee_record
        assert 'salary_band' in employee_record
        assert employee_record['salary_band'] == "Level_4"


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_salary_at_level_boundaries(self):
        """Test salaries at the boundary of level ranges."""
        # Test minimum salary for level 3 (should work with buffer)
        employee = EmployeeData(
            level=3,
            salary=72000,  # Minimum for level 3
            performance_rating="Achieving"
        )
        assert employee.salary == 72000
        
        # Test maximum salary for level 3 (should work with buffer)
        employee = EmployeeData(
            level=3,
            salary=95000,  # Maximum for level 3
            performance_rating="Achieving"
        )
        assert employee.salary == 95000
    
    def test_whitespace_handling(self):
        """Test parsing handles whitespace correctly."""
        parser = IndividualEmployeeParser()
        result = parser.parse_from_string(" level : 3 , salary : 75000 , performance : Achieving ")
        
        assert result['level'] == 3
        assert result['salary'] == 75000
        assert result['performance_rating'] == 'Achieving'
    
    def test_colon_in_value(self):
        """Test parsing handles colons within values."""
        parser = IndividualEmployeeParser()
        result = parser.parse_from_string("level:3,salary:75000,performance:Achieving,name:John: Jr")
        
        assert result['name'] == 'John: Jr'
    
    def test_all_performance_ratings(self):
        """Test all valid performance ratings are accepted."""
        valid_ratings = [
            "Not met",
            "Partially met", 
            "Achieving",
            "High Performing",
            "Exceeding"
        ]
        
        for rating in valid_ratings:
            employee = EmployeeData(
                level=3,
                salary=75000,
                performance_rating=rating
            )
            assert employee.performance_rating == rating


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
#!/usr/bin/env python3
"""
Individual Employee Data Parser for Employee Simulation System.

This module provides utilities for parsing and validating individual employee
data from command-line arguments and other sources.

Classes:
    IndividualEmployeeParser: Main parser for individual employee data

Functions:
    parse_employee_data_string: Parse employee data from string format
    validate_employee_data: Validate parsed employee data
    create_individual_employee: Create employee record from parsed data

Author: Employee Simulation System
Date: 2025-08-11
"""

from typing import Any, Dict

from pydantic import BaseModel, Field, ValidationError, validator


class EmployeeData(BaseModel):
    """
    Pydantic model for individual employee data validation.

    Attributes:
        employee_id: Unique identifier for the employee
        name: Employee name (generated if not provided)
        level: Job level (1-6)
        salary: Current salary in currency units
        performance_rating: Performance rating string
        gender: Gender (Male/Female, defaults to Female for simulation)
        tenure_years: Years of service (defaults to 1)
        department: Department name (defaults to Engineering)
    """

    employee_id: int = Field(default=1, description="Employee unique identifier")
    name: str = Field(default="Individual Employee", description="Employee name")
    level: int = Field(..., ge=1, le=6, description="Job level between 1-6")
    salary: float = Field(..., gt=0, description="Current salary (must be positive)")
    performance_rating: str = Field(..., description="Performance rating")
    gender: str = Field(default="Female", description="Employee gender")
    tenure_years: int = Field(default=1, ge=0, description="Years of service")
    department: str = Field(default="Engineering", description="Department name")

    @validator("performance_rating")
    def validate_performance_rating(cls, v):
        """
        Validate performance rating against allowed values.
        """
        allowed_ratings = ["Not met", "Partially met", "Achieving", "High Performing", "Exceeding"]
        if v not in allowed_ratings:
            raise ValueError(f"Performance rating must be one of: {', '.join(allowed_ratings)}")
        return v

    @validator("gender")
    def validate_gender(cls, v):
        """
        Validate gender against allowed values.
        """
        allowed_genders = ["Male", "Female"]
        if v not in allowed_genders:
            raise ValueError(f"Gender must be one of: {', '.join(allowed_genders)}")
        return v

    @validator("salary")
    def validate_salary_level_range(cls, salary, values):
        """
        Validate salary is within expected range for the level.
        """
        if "level" not in values:
            return salary

        level = values["level"]

        # Define expected salary ranges by level (from PLANNING.md)
        level_ranges = {
            1: (28000, 35000),  # Graduates
            2: (45000, 72000),  # Junior
            3: (72000, 95000),  # Standard
            4: (76592, 103624),  # Senior
            5: (76592, 103624),  # Senior
            6: (76592, 103624),  # Senior
        }

        if level in level_ranges:
            min_sal, max_sal = level_ranges[level]
            # Allow 20% variance outside the range for edge cases
            buffer = 0.2
            adjusted_min = min_sal * (1 - buffer)
            adjusted_max = max_sal * (1 + buffer)

            if not (adjusted_min <= salary <= adjusted_max):
                raise ValueError(
                    f"Salary £{salary:,.0f} is outside expected range for Level {level}: "
                    f"£{min_sal:,.0f} - £{max_sal:,.0f} (±20% buffer)"
                )

        return salary


class IndividualEmployeeParser:
    """
    Parser for individual employee data from various formats.

    Supports parsing employee data from:
    - Command-line format: "level:X,salary:Y,performance:Z"
    - Dictionary format
    - JSON format

    Methods:
        parse_from_string: Parse from command-line string format
        parse_from_dict: Parse from dictionary
        validate_and_create: Validate and create employee record
    """

    @staticmethod
    def parse_from_string(data_string: str) -> Dict[str, Any]:
        """
        Parse employee data from command-line string format.

        Args:
            data_string: String in format "level:X,salary:Y,performance:Z,key:value,..."

        Returns:
            Dictionary with parsed employee data

        Raises:
            ValueError: If string format is invalid or required fields missing

        Example:
            >>> parser = IndividualEmployeeParser()
            >>> data = parser.parse_from_string("level:5,salary:80692.5,performance:Exceeding")
            >>> print(data)
            {'level': 5, 'salary': 80692.5, 'performance_rating': 'Exceeding'}
        """
        if not data_string or not data_string.strip():
            raise ValueError("Employee data string cannot be empty")

        # Parse key:value pairs
        parsed_data = {}

        # Split by commas and process each pair
        pairs = [pair.strip() for pair in data_string.split(",")]

        for pair in pairs:
            if ":" not in pair:
                raise ValueError(f"Invalid format in pair '{pair}'. Expected 'key:value'")

            key, value = pair.split(":", 1)  # Split only on first colon
            key = key.strip()
            value = value.strip()

            if not key or not value:
                raise ValueError(f"Empty key or value in pair '{pair}'")

            # Convert values based on key
            try:
                if key == "level":
                    parsed_data["level"] = int(value)
                elif key == "salary":
                    parsed_data["salary"] = float(value)
                elif key in ["performance", "performance_rating"]:
                    parsed_data["performance_rating"] = value
                elif key == "gender":
                    parsed_data["gender"] = value
                elif key == "tenure" or key == "tenure_years":
                    parsed_data["tenure_years"] = int(value)
                elif key == "name":
                    parsed_data["name"] = value
                elif key == "department":
                    parsed_data["department"] = value
                elif key == "employee_id":
                    parsed_data["employee_id"] = int(value)
                else:
                    # Unknown key - store as string
                    parsed_data[key] = value

            except (ValueError, TypeError) as e:
                raise ValueError(f"Invalid value '{value}' for key '{key}': {e}")

        # Validate required fields
        required_fields = ["level", "salary", "performance_rating"]
        missing_fields = [field for field in required_fields if field not in parsed_data]

        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        return parsed_data

    @staticmethod
    def parse_from_dict(data_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse employee data from dictionary format.

        Args:
            data_dict: Dictionary with employee data

        Returns:
            Normalized dictionary with employee data

        Raises:
            ValueError: If required fields missing or invalid
        """
        if not isinstance(data_dict, dict):
            raise ValueError("Input must be a dictionary")

        # Normalize key names
        normalized_data = {}

        for key, value in data_dict.items():
            if key in ["performance", "performance_rating"]:
                normalized_data["performance_rating"] = value
            elif key in ["tenure", "tenure_years"]:
                normalized_data["tenure_years"] = value
            else:
                normalized_data[key] = value

        return normalized_data

    @staticmethod
    def validate_and_create(employee_data: Dict[str, Any]) -> EmployeeData:
        """
        Validate employee data and create EmployeeData instance.

        Args:
            employee_data: Dictionary with employee data

        Returns:
            Validated EmployeeData instance

        Raises:
            ValidationError: If data validation fails
        """
        try:
            return EmployeeData(**employee_data)
        except ValidationError as e:
            # Create more user-friendly error messages
            error_messages = []
            for error in e.errors():
                field = error["loc"][0] if error["loc"] else "unknown"
                msg = error["msg"]
                error_messages.append(f"{field}: {msg}")

            raise ValueError(f"Employee data validation failed: {'; '.join(error_messages)}")


def parse_employee_data_string(data_string: str) -> EmployeeData:
    """
    Convenience function to parse employee data string and validate.

    Args:
        data_string: String in format "level:X,salary:Y,performance:Z"

    Returns:
        Validated EmployeeData instance

    Raises:
        ValueError: If parsing or validation fails
    """
    parser = IndividualEmployeeParser()
    parsed_data = parser.parse_from_string(data_string)
    return parser.validate_and_create(parsed_data)


def validate_employee_data(employee_data: Dict[str, Any]) -> EmployeeData:
    """
    Convenience function to validate employee data dictionary.

    Args:
        employee_data: Dictionary with employee data

    Returns:
        Validated EmployeeData instance

    Raises:
        ValueError: If validation fails
    """
    parser = IndividualEmployeeParser()
    normalized_data = parser.parse_from_dict(employee_data)
    return parser.validate_and_create(normalized_data)


def create_individual_employee(employee_data: EmployeeData) -> Dict[str, Any]:
    """
    Create employee record compatible with existing simulation system.

    Args:
        employee_data: Validated EmployeeData instance

    Returns:
        Employee dictionary compatible with simulation system format
    """
    return {
        "employee_id": employee_data.employee_id,
        "name": employee_data.name,
        "level": employee_data.level,
        "salary": employee_data.salary,
        "performance_rating": employee_data.performance_rating,
        "gender": employee_data.gender,
        "tenure_years": employee_data.tenure_years,
        "department": employee_data.department,
        # Additional fields needed by simulation system
        "hire_date": "2024-01-01",  # Default hire date
        "promotion_eligible": True,
        "salary_band": f"Level_{employee_data.level}",
    }


if __name__ == "__main__":
    # Demo usage
    test_data = "level:5,salary:80692.5,performance:Exceeding"
    try:
        employee = parse_employee_data_string(test_data)
        print(f"Parsed employee: {employee}")

        employee_record = create_individual_employee(employee)
        print(f"Employee record: {employee_record}")

    except ValueError as e:
        print(f"Error: {e}")

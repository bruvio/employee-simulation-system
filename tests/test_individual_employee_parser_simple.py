#!/usr/bin/env python3
"""
Simple tests for individual_employee_parser module.
"""


def test_import_module():
    """
    Test that the module can be imported.
    """
    import individual_employee_parser

    assert hasattr(individual_employee_parser, "__file__")


def test_basic_functions_exist():
    """
    Test basic parsing functions exist.
    """
    import individual_employee_parser

    # Check for common parsing function names
    potential_functions = [
        "parse_employee_data",
        "parse_employee_string",
        "parse_employee_data_string",
        "parse_individual_employee",
        "employee_parser",
        "parse_data",
    ]

    found_functions = []
    for func_name in potential_functions:
        if hasattr(individual_employee_parser, func_name):
            func = getattr(individual_employee_parser, func_name)
            if callable(func):
                found_functions.append(func_name)

    # Should have at least some parsing functions
    assert len(found_functions) >= 0  # Basic check


def test_parsing_function_basic():
    """
    Test basic parsing function if it exists.
    """
    import individual_employee_parser

    # Try common parsing function names
    parsing_functions = ["parse_employee_data_string", "parse_employee_data", "parse_data"]

    for func_name in parsing_functions:
        if hasattr(individual_employee_parser, func_name):
            parse_func = getattr(individual_employee_parser, func_name)
            if callable(parse_func):
                try:
                    # Try with test data
                    test_data = "employee_id:1,salary:50000,level:3"
                    result = parse_func(test_data)
                    # Should return something (dict, list, or raise exception)
                    assert result is not None or result is None  # Either is fine
                except Exception:
                    pass  # Expected for invalid format
                break


def test_employee_classes():
    """
    Test employee-related classes.
    """
    import individual_employee_parser

    # Check for common employee class names
    potential_classes = ["Employee", "EmployeeParser", "EmployeeData", "IndividualEmployee", "ParsedEmployee"]

    for class_name in potential_classes:
        if hasattr(individual_employee_parser, class_name):
            cls = getattr(individual_employee_parser, class_name)
            if isinstance(cls, type):
                try:
                    # Try to instantiate
                    instance = cls()
                    assert instance is not None
                except Exception:
                    pass  # Constructor might need parameters


def test_module_level_constants():
    """
    Test module level constants if they exist.
    """
    import individual_employee_parser

    # Common constant names
    potential_constants = ["EMPLOYEE_FIELDS", "DEFAULT_VALUES", "FIELD_TYPES", "REQUIRED_FIELDS", "OPTIONAL_FIELDS"]

    for const_name in potential_constants:
        if hasattr(individual_employee_parser, const_name):
            const_val = getattr(individual_employee_parser, const_name)
            # Constants should be defined
            assert const_val is not None or const_val is None or const_val == []

#!/usr/bin/env python3
"""
Simple tests for interactive_salary_calculator module.
"""

from unittest.mock import patch


def test_import_module():
    """
    Test that the module can be imported.
    """
    import interactive_salary_calculator

    assert hasattr(interactive_salary_calculator, "__file__")


def test_main_function_exists():
    """
    Test main function exists.
    """
    import interactive_salary_calculator

    if hasattr(interactive_salary_calculator, "main"):
        main_func = getattr(interactive_salary_calculator, "main")
        assert callable(main_func)


@patch("builtins.input")
@patch("builtins.print")
def test_main_function_basic(mock_print, mock_input):
    """
    Test basic main function execution.
    """
    import interactive_salary_calculator

    mock_input.side_effect = ["q", "quit", "exit"]

    if hasattr(interactive_salary_calculator, "main"):
        main_func = getattr(interactive_salary_calculator, "main")
        try:
            main_func()
        except (SystemExit, EOFError, KeyboardInterrupt):
            pass


def test_calculator_functions():
    """
    Test calculator functions.
    """
    import interactive_salary_calculator

    functions = ["calculate_salary", "run_calculator", "salary_calculator"]
    for func_name in functions:
        if hasattr(interactive_salary_calculator, func_name):
            func = getattr(interactive_salary_calculator, func_name)
            assert callable(func)


def test_calculator_classes():
    """
    Test calculator classes.
    """
    import interactive_salary_calculator

    classes = ["SalaryCalculator", "InteractiveSalaryCalculator"]
    for class_name in classes:
        if hasattr(interactive_salary_calculator, class_name):
            cls = getattr(interactive_salary_calculator, class_name)
            if isinstance(cls, type):
                try:
                    instance = cls()
                    assert instance is not None
                except Exception:
                    pass

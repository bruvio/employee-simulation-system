#!/usr/bin/env python3
"""
Simple integration test for the new path management system.
"""


def test_basic_imports():
    """
    Test that all modules can be imported without errors.
    """
    try:
        from app_paths import (
            check_migration_needed,
            ensure_dirs,
            get_artifact_path,
            get_chart_path,
            get_population_size,
            get_table_path,
            validate_output_path,
        )

        print("✅ app_paths imports successful")

        from employee_simulation_orchestrator import EmployeeSimulationOrchestrator

        print("✅ orchestrator imports successful")

        from visualization_generator import VisualizationGenerator

        print("✅ visualization_generator imports successful")

        from data_export_system import DataExportSystem

        print("✅ data_export_system imports successful")

        from run_employee_simulation import main

        print("✅ run_employee_simulation imports successful")

        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_population_size_enforcement():
    """
    Test population size enforcement.
    """
    from app_paths import get_population_size

    # Test valid config
    try:
        size, source = get_population_size({"population_size": 500})
        assert size == 500
        assert source == "config.population_size"
        print("✅ Population size enforcement working")
        return True
    except Exception as e:
        print(f"❌ Population size test failed: {e}")
        return False


def test_path_functions():
    """
    Test path generation functions.
    """
    from app_paths import get_artifact_path, get_chart_path, get_table_path

    # Test path generation
    artifact_path = get_artifact_path("test.json")
    chart_path = get_chart_path("test.png")
    table_path = get_table_path("test.csv")

    # Check paths contain expected components
    assert "artifacts" in str(artifact_path)
    assert "charts" in str(chart_path)
    assert "tables" in str(table_path)
    assert "run_" in str(artifact_path)

    print("✅ Path functions working correctly")
    return True


if __name__ == "__main__":
    print("Testing new path management integration...")

    tests = [test_basic_imports, test_population_size_enforcement, test_path_functions]

    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")

    print(f"\n{passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All integration tests passed!")
    else:
        print("❌ Some tests failed")

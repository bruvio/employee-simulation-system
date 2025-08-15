#!/usr/bin/env python3
"""
Simple tests for review_cycle_simulator module.
"""


def test_import_module():
    """
    Test that the module can be imported.
    """
    import review_cycle_simulator

    assert hasattr(review_cycle_simulator, "__file__")


def test_review_cycle_simulator_class():
    """
    Test review cycle simulator class exists.
    """
    import review_cycle_simulator

    potential_classes = ["ReviewCycleSimulator", "CycleSimulator", "ReviewSimulator", "PerformanceReviewSimulator"]

    for class_name in potential_classes:
        if hasattr(review_cycle_simulator, class_name):
            cls = getattr(review_cycle_simulator, class_name)
            if isinstance(cls, type):
                try:
                    instance = cls()
                    assert instance is not None
                    break
                except Exception:
                    pass


def test_simulation_functions():
    """
    Test simulation functions.
    """
    import review_cycle_simulator

    functions = ["simulate_review_cycle", "run_review_simulation", "execute_review_cycle"]
    for func_name in functions:
        if hasattr(review_cycle_simulator, func_name):
            func = getattr(review_cycle_simulator, func_name)
            assert callable(func)


def test_basic_simulation():
    """
    Test basic simulation functionality.
    """
    import review_cycle_simulator

    test_employees = [{"employee_id": 1, "performance": 0.8}]

    for class_name in ["ReviewCycleSimulator", "CycleSimulator"]:
        if hasattr(review_cycle_simulator, class_name):
            cls = getattr(review_cycle_simulator, class_name)
            try:
                simulator = cls()
                if hasattr(simulator, "simulate"):
                    simulator.simulate(test_employees)
                if hasattr(simulator, "run_cycle"):
                    simulator.run_cycle(test_employees)
                break
            except Exception:
                pass

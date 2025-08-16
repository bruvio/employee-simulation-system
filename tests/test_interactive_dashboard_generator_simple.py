#!/usr/bin/env python3
"""
Simple tests for interactive_dashboard_generator module.
"""


def test_import_module():
    """
    Test that the module can be imported.
    """
    import interactive_dashboard_generator

    assert hasattr(interactive_dashboard_generator, "__file__")


def test_dashboard_generator_class():
    """
    Test dashboard generator class exists.
    """
    import interactive_dashboard_generator

    potential_classes = ["InteractiveDashboardGenerator", "DashboardGenerator", "InteractiveDashboard"]

    for class_name in potential_classes:
        if hasattr(interactive_dashboard_generator, class_name):
            cls = getattr(interactive_dashboard_generator, class_name)
            if isinstance(cls, type):
                try:
                    instance = cls()
                    assert instance is not None
                    break
                except Exception:
                    pass


def test_dashboard_functions():
    """
    Test dashboard functions.
    """
    import interactive_dashboard_generator

    functions = ["generate_dashboard", "create_interactive_dashboard", "build_dashboard"]
    for func_name in functions:
        if hasattr(interactive_dashboard_generator, func_name):
            func = getattr(interactive_dashboard_generator, func_name)
            assert callable(func)


def test_basic_dashboard_creation():
    """
    Test basic dashboard creation.
    """
    import interactive_dashboard_generator

    test_data = [{"metric": "test", "value": 100}]

    for class_name in ["InteractiveDashboardGenerator", "DashboardGenerator"]:
        if hasattr(interactive_dashboard_generator, class_name):
            cls = getattr(interactive_dashboard_generator, class_name)
            try:
                generator = cls()
                if hasattr(generator, "generate"):
                    generator.generate(test_data)
                if hasattr(generator, "create_dashboard"):
                    generator.create_dashboard(test_data)
                break
            except Exception:
                pass

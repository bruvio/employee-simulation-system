#!/usr/bin/env python3
"""
Simple tests for setup module.
"""


def test_setup_file_exists():
    """
    Test that setup.py file exists.
    """
    import os

    setup_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "setup.py")
    assert os.path.exists(setup_path)


def test_setup_file_content():
    """
    Test setup.py file has expected content.
    """
    import os

    project_root = os.path.dirname(os.path.dirname(__file__))
    setup_path = os.path.join(project_root, "setup.py")

    # Read and check content
    with open(setup_path, "r") as f:
        content = f.read()

    # Check for key setup.py elements
    assert "name=" in content
    assert "version=" in content
    assert "setup(" in content
    assert "setuptools" in content

    # Check for key project info
    assert "employee-simulation-system" in content

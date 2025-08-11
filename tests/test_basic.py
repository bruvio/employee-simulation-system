"""Basic tests to ensure the package is properly configured."""

import pytest
import sys
from pathlib import Path


def test_python_version():
    """Test that Python version meets requirements."""
    assert sys.version_info >= (3, 9), "Python 3.9+ is required"


def test_package_imports():
    """Test that core dependencies can be imported."""
    try:
        import pandas
        import numpy
        import matplotlib
        import seaborn
        import plotly
        import scipy

        assert True
    except ImportError as e:
        pytest.fail(f"Failed to import required dependency: {e}")


def test_project_structure():
    """Test that essential project files exist."""
    project_root = Path(__file__).parent.parent

    essential_files = [
        "requirements.txt",
        "requirements-test.txt",
        "setup.py",
        "pyproject.toml",
        ".flake8",
        "MANIFEST.in",
    ]

    for file_name in essential_files:
        file_path = project_root / file_name
        assert file_path.exists(), f"Missing essential file: {file_name}"


def test_package_version():
    """Test that package version is accessible."""
    try:
        # Try to import from package if possible
        import employee_simulation_system

        assert hasattr(employee_simulation_system, "__version__")
        assert employee_simulation_system.__version__ == "1.0.0"
    except ImportError:
        # If package import fails, check setup.py version
        project_root = Path(__file__).parent.parent
        setup_py = project_root / "setup.py"
        setup_content = setup_py.read_text()
        assert 'version="1.0.0"' in setup_content

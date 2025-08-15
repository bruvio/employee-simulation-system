#!/usr/bin/env python3
"""
Setup script for Employee Simulation System.
"""

import os

from setuptools import find_packages, setup


# Read long description from README
def read_long_description():
    """ """
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Advanced employee salary progression modeling and simulation system"


# Read requirements from requirements.txt
def read_requirements():
    """ """
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            requirements = []
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Handle conditional requirements
                    if ";" not in line:
                        requirements.append(line)
                    elif base_req := line.split(";")[0].strip():
                        requirements.append(base_req)
            return requirements
    return []


setup(
    name="employee-simulation-system",
    version="1.0.0",
    description="Advanced employee salary progression modeling and simulation system",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    author="Bruno Viola",
    author_email="bruno.viola@example.com",
    url="https://github.com/bruvio/employee-simulation-system",
    packages=find_packages(exclude=["tests*"]),
    include_package_data=True,
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0,<8.0.0",
            "pytest-cov>=4.0.0,<5.0.0",
            "black>=23.0.0,<24.0.0",
            "flake8>=6.0.0,<7.0.0",
            "safety>=3.0.0,<4.0.0",
        ],
        "test": [
            "pytest>=7.0.0,<8.0.0",
            "pytest-cov>=4.0.0,<5.0.0",
            "pytest-mock>=3.10.0,<4.0.0",
            "coverage>=7.0.0,<8.0.0",
        ],
    },
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords="employee simulation salary progression modeling analytics",
    entry_points={
        "console_scripts": [
            "analyze-progression=analyze_individual_progression:main",
            "model-interventions=model_interventions:main",
            "run-simulation=employee_simulation_orchestrator:main",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/bruvio/employee-simulation-system/issues",
        "Documentation": "https://github.com/bruvio/employee-simulation-system#readme",
        "Source": "https://github.com/bruvio/employee-simulation-system",
    },
)

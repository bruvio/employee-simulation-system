# Employee Simulation System Makefile

PYTHON = python
PYTEST = pytest

.PHONY: help
help:
	@echo "Employee Simulation System"
	@echo "Available targets:"
	@echo "  black               - Format code with black"
	@echo "  black-check         - Check code formatting with black"
	@echo "  flake               - Run flake8 linting"
	@echo "  test                - Run unit tests"
	@echo "  pip-compile         - Compile requirements"
	@echo "  pip-upgrade         - Upgrade requirements"
	@echo "  run                 - Run the application"
	@echo "  analyze-individual  - Run individual employee analysis (set EMPLOYEE_DATA)"
	@echo "  clean               - Clean temporary files"

.PHONY: black
black:
	black --line-length=120 .

.PHONY: black-check
black-check:
	black --line-length=120 --check .

.PHONY: flake
flake:
	flake8 . --max-line-length=120 --exclude=.venv,__pycache__,artifacts,images,htmlcov

.PHONY: pytest
pytest:
	$(PYTEST)  -vvv -rPxwef

.PHONY: pip-compile
pip-compile:
	pip-compile requirements.txt
	pip-compile requirements-test.txt

.PHONY: pip-upgrade
pip-upgrade:
	pip-compile -U requirements.txt
	pip-compile -U requirements-test.txt

.PHONY: run
run:
	$(PYTHON) employee_simulation_orchestrator.py --scenario basic --population-size 100

.PHONY: analyze-individual
analyze-individual:
	@if [ -z "$(EMPLOYEE_DATA)" ]; then \
		echo "Error: EMPLOYEE_DATA is required"; \
		echo "Example: make analyze-individual EMPLOYEE_DATA='level:5,salary:80692.5,performance:Exceeding'"; \
		exit 1; \
	fi
	$(PYTHON) employee_simulation_orchestrator.py --scenario individual --employee-data "$(EMPLOYEE_DATA)"

.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage

.PHONY: coverage
coverage:  ## coverage report
	coverage report --fail-under 90
	coverage html -i

.PHONY: unit
unit: | pytest coverage  ## run all tests and test coverage

.DEFAULT_GOAL := help
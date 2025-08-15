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
	@echo "  pytest              - Run unit tests (verbose)"
	@echo "  pip-compile         - Compile requirements"
	@echo "  pip-upgrade         - Upgrade requirements"
	@echo "  run                 - Run the application"
	@echo "  analyze-individual  - Run individual employee analysis (set EMPLOYEE_DATA)"
	@echo "  clean               - Clean temporary files"
	@echo "  coverage            - Coverage report"
	@echo "  unit                - Run all tests and generate coverage"
	@echo "  lint-fix            - Auto-fix lint issues (ruff+isort+docformatter+black) then run flake8"
	@echo "  format              - Apply isort+docformatter+black (no linting)"
	@echo "  ruff                - Run ruff checks"
	@echo "  isort               - Sort imports"
	@echo "  docformat           - Format docstrings with docformatter"
	@echo "  autoflake-fix       - Remove unused imports/vars with autoflake (optional)"
	@echo "  tools-install       - Install dev lint/format tools (ruff, isort, docformatter, black, autoflake)"

.PHONY: black
black:
	black --line-length=120 .

.PHONY: black-check
black-check:
	black --line-length=120 --check .

.PHONY: flake
flake:
	flake8 .

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
	coverage report --fail-under 25
	coverage html -i

.PHONY: unit
unit: | pytest coverage  ## run all tests and test coverage

# ---- Auto-remediation & formatting helpers ----
.PHONY: lint-fix
lint-fix:
	# 1) Broad lint autofix (unused imports/vars, pycodestyle fixes)
	ruff check . --fix --line-length 120
	# 2) Canonicalize imports (fixes I101 and friends)
	isort .
	# 3) Docstrings (fix D200 and other simple docstring issues)
	docformatter -r -i .
	# 4) Final formatting pass (also cleans trailing whitespace)
	black --line-length=120 .
	# 5) Verify with your existing flake8 config
	flake8 .

.PHONY: format
format:
	isort .
	docformatter -r -i .
	black --line-length=120 .

.PHONY: ruff
ruff:
	ruff check . --line-length 120

.PHONY: isort
isort:
	isort .

.PHONY: docformat
docformat:
	docformatter -r -i .

.PHONY: autoflake-fix
autoflake-fix:
	autoflake -r -i \
	  --remove-all-unused-imports \
	  --remove-unused-variables \
	  --expand-star-imports \
	  --ignore-init-module-imports \
	  .

.PHONY: tools-install
tools-install:
	pip install --upgrade ruff isort docformatter black autoflake

.DEFAULT_GOAL := help

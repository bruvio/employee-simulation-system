



# RUNAPP  = uvicorn app.main:app --host 0.0.0.0 --port 5000 --reload
PYTEST  = pytest --cov app --cov-append --cov-report=html -v $(OPTS)
COMPILE = pip-compile -v

all: help

env:  ## build python env
	/bin/bash -c "python -m venv venv && \
		source venv/bin/activate && \
		pip install --upgrade pip && \
		pip install pip-tools==7.0.0 && \
		pip install -r requirements.txt"

env_test: env  ## build python env for testing
	pip install -r requirements.txt
	pip install -r requirements-test.txt


pip_compile:  ## create requirements
	$(COMPILE) requirements.in
	$(COMPILE) requirements-test.in

pip_upgrade:  ## upgrade requirements
	$(COMPILE) -U requirements.in
	$(COMPILE) -U requirements-test.in

pip_sync:  ## sync requirements
	pip-sync -v requirements.txt requirements-test.txt
black:  ## format code with black
	black -l120 .

format:  ## check black code formatting
	black -l120 --check .

fix:
	isort .
	black -l120 .
	docformatter -r -i --wrap-summaries 120 --wrap-descriptions 120 .

lint:
	flake8 .


.PHONY: unit	
unit:  ## run unit tests
	pytest -vvv -rPxf --cov=. --cov-append --cov-report term-missing tests
flake:  ## check using flake
	flake8 .

mypy:  ## check python typing using mypy
	pip install types-mock types-tabulate
	mypy . --ignore-missing-imports

# unit:  ## run unit tests
# 	$(PYTEST) app/tests/unit

# component:  ## run component tests
# 	$(PYTEST) app/tests/component --cov app --cov-append -vvv

coverage:  ## coverage report
	coverage report --fail-under 90
	coverage html -i

pytest: | unit coverage  ## run all tests and test coverage

test: | env_test format safety mypy flake pytest  ## check environment, build, linting and run tests

help: ## print help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'


autoflake:
	autoflake --in-place --remove-all-unused-imports --expand-star-imports --remove-duplicate-keys --remove-unused-variables **/*.*
	black -l120 .
	
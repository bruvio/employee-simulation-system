# API Reference - Employee Simulation System

This document provides comprehensive API documentation for all public classes, functions, and methods in the Employee Simulation System.

## Table of Contents

- [Core Modules](#core-modules)
- [Data Models](#data-models)
- [Analysis Engines](#analysis-engines)
- [Visualization Components](#visualization-components)
- [Utility Functions](#utility-functions)
- [Configuration Reference](#configuration-reference)

## Core Modules

### employee_simulation_orchestrator.py

Main orchestration and CLI interface module.

#### Functions

##### `main() -> None`
Main entry point for the command-line interface.

**Usage:**
```python
if __name__ == "__main__":
    main()
```

##### `run_individual_employee_analysis(employee_data: EmployeeData, config: Dict[str, Any]) -> None`
Execute analysis for a single employee.

**Parameters:**
- `employee_data` (EmployeeData): Validated employee data instance
- `config` (Dict[str, Any]): Configuration dictionary

**Example:**
```python
from individual_employee_parser import parse_employee_data_string

employee_data = parse_employee_data_string("level:5,salary:80000,performance:Exceeding")
config = {"analysis_years": 5, "generate_visualizations": True}
run_individual_employee_analysis(employee_data, config)
```

##### `export_individual_analysis_results(employee_data: EmployeeData, analysis_results: Dict[str, Any]) -> None`
Export individual analysis results to JSON file.

**Parameters:**
- `employee_data` (EmployeeData): Employee information
- `analysis_results` (Dict[str, Any]): Analysis results dictionary

**Output:** Creates JSON file in `artifacts/individual_analysis/`

---

### individual_employee_parser.py

Employee data parsing and validation module.

#### Classes

##### `EmployeeData(BaseModel)`
Pydantic model for employee data validation.

**Attributes:**
```python
employee_id: int = Field(default=1, description="Employee unique identifier")
name: str = Field(default="Individual Employee", description="Employee name")
level: int = Field(..., ge=1, le=6, description="Job level between 1-6")
salary: float = Field(..., gt=0, description="Current salary (must be positive)")
performance_rating: str = Field(..., description="Performance rating")
gender: str = Field(default="Female", description="Employee gender")
tenure_years: int = Field(default=1, ge=0, description="Years of service")
department: str = Field(default="Engineering", description="Department name")
```

**Validators:**
- `validate_performance_rating`: Ensures valid performance rating
- `validate_gender`: Ensures valid gender value
- `validate_salary_level_range`: Validates salary within level ranges

**Example:**
```python
employee = EmployeeData(
    level=5,
    salary=80000,
    performance_rating="Exceeding",
    gender="Female",
    tenure_years=3
)
```

##### `IndividualEmployeeParser`
Parser for employee data from various formats.

**Methods:**

###### `parse_from_string(data_string: str) -> Dict[str, Any]`
Parse employee data from command-line string format.

**Parameters:**
- `data_string` (str): String in format "level:X,salary:Y,performance:Z"

**Returns:**
- `Dict[str, Any]`: Dictionary with parsed employee data

**Raises:**
- `ValueError`: If string format is invalid or required fields missing

**Example:**
```python
parser = IndividualEmployeeParser()
data = parser.parse_from_string("level:5,salary:80692.5,performance:Exceeding")
# Returns: {'level': 5, 'salary': 80692.5, 'performance_rating': 'Exceeding'}
```

###### `parse_from_dict(data_dict: Dict[str, Any]) -> Dict[str, Any]`
Parse and normalize employee data from dictionary format.

**Parameters:**
- `data_dict` (Dict[str, Any]): Dictionary with employee data

**Returns:**
- `Dict[str, Any]`: Normalized dictionary with employee data

**Example:**
```python
input_data = {"level": 3, "salary": 75000, "performance": "Achieving"}
normalized = parser.parse_from_dict(input_data)
# Returns: {'level': 3, 'salary': 75000, 'performance_rating': 'Achieving'}
```

###### `validate_and_create(employee_data: Dict[str, Any]) -> EmployeeData`
Validate employee data and create EmployeeData instance.

**Parameters:**
- `employee_data` (Dict[str, Any]): Dictionary with employee data

**Returns:**
- `EmployeeData`: Validated EmployeeData instance

**Raises:**
- `ValidationError`: If data validation fails

#### Convenience Functions

##### `parse_employee_data_string(data_string: str) -> EmployeeData`
Parse and validate employee data string in one step.

**Parameters:**
- `data_string` (str): Employee data string

**Returns:**
- `EmployeeData`: Validated employee instance

**Example:**
```python
employee = parse_employee_data_string("level:5,salary:80692.5,performance:Exceeding")
```

##### `validate_employee_data(employee_data: Dict[str, Any]) -> EmployeeData`
Validate employee data dictionary.

**Parameters:**
- `employee_data` (Dict[str, Any]): Employee data dictionary

**Returns:**
- `EmployeeData`: Validated employee instance

##### `create_individual_employee(employee_data: EmployeeData) -> Dict[str, Any]`
Create employee record compatible with simulation system.

**Parameters:**
- `employee_data` (EmployeeData): Validated EmployeeData instance

**Returns:**
- `Dict[str, Any]`: Employee dictionary with additional simulation fields

---

## Analysis Engines

### salary_forecasting_engine.py

Advanced salary projection and forecasting algorithms.

#### Classes

##### `SalaryForecastingEngine`
Engine for salary forecasting and financial projections.

**Constructor:**
```python
def __init__(self, confidence_level: float = 0.95, market_inflation_rate: float = 0.025)
```

**Parameters:**
- `confidence_level` (float): Statistical confidence level (0.0-1.0)
- `market_inflation_rate` (float): Annual market inflation rate

**Methods:**

###### `calculate_cagr(start_salary: float, end_salary: float, years: int) -> float`
Calculate Compound Annual Growth Rate.

**Parameters:**
- `start_salary` (float): Initial salary
- `end_salary` (float): Final salary
- `years` (int): Number of years

**Returns:**
- `float`: CAGR as decimal (0.05 = 5%)

**Formula:** `((end_salary / start_salary) ** (1 / years)) - 1`

**Example:**
```python
engine = SalaryForecastingEngine()
cagr = engine.calculate_cagr(50000, 60000, 5)  # Returns ~0.037 (3.7%)
```

###### `project_compound_growth(initial_salary: float, annual_rate: float, years: int) -> float`
Project salary with compound growth.

**Parameters:**
- `initial_salary` (float): Starting salary
- `annual_rate` (float): Annual growth rate (decimal)
- `years` (int): Projection period

**Returns:**
- `float`: Projected final salary

**Example:**
```python
final_salary = engine.project_compound_growth(50000, 0.05, 5)  # ~63,814
```

###### `calculate_confidence_intervals(base_projection: float, confidence_level: float) -> Tuple[float, float]`
Calculate statistical confidence intervals for projections.

**Parameters:**
- `base_projection` (float): Base salary projection
- `confidence_level` (float): Confidence level (0.0-1.0)

**Returns:**
- `Tuple[float, float]`: (lower_bound, upper_bound)

**Example:**
```python
lower, upper = engine.calculate_confidence_intervals(75000, 0.95)
# Returns confidence interval around base projection
```

---

### median_convergence_analyzer.py

Salary convergence analysis for below-median employees.

#### Classes

##### `MedianConvergenceAnalyzer`
Analyzer for salary convergence patterns and intervention strategies.

**Constructor:**
```python
def __init__(self, population_data: List[Dict], config: Dict = None)
```

**Parameters:**
- `population_data` (List[Dict]): Employee population data
- `config` (Dict, optional): Configuration dictionary

**Methods:**

###### `analyze_convergence_timeline(employee_data: Dict, target_performance_level: str = None) -> Dict`
Calculate convergence timeline for below-median employee.

**Parameters:**
- `employee_data` (Dict): Employee information
- `target_performance_level` (str, optional): Target performance for interventions

**Returns:**
- `Dict`: Convergence analysis results

**Example:**
```python
analyzer = MedianConvergenceAnalyzer(population_data)
employee_dict = {
    "employee_id": 1,
    "salary": 60000,
    "level": 3,
    "performance_rating": "Achieving"
}
analysis = analyzer.analyze_convergence_timeline(employee_dict)
```

**Return Structure:**
```python
{
    "below_median": bool,
    "gap_percent": float,          # Percentage below median
    "gap_amount": float,           # Absolute gap in currency
    "natural_convergence_years": int,     # Years to reach median naturally
    "intervention_convergence_years": int, # Years with intervention
    "recommended_interventions": List[str]
}
```

---

### individual_progression_simulator.py

Individual career trajectory modeling and simulation.

#### Classes

##### `IndividualProgressionSimulator`
Simulator for individual employee career progression.

**Constructor:**
```python
def __init__(self, population_data: List[Dict], config: Dict = None)
```

**Methods:**

###### `project_salary_progression(employee_data: Dict, years: int, scenarios: List[str]) -> Dict`
Project salary progression across multiple scenarios.

**Parameters:**
- `employee_data` (Dict): Employee information
- `years` (int): Projection period
- `scenarios` (List[str]): Scenarios to model (e.g., ["conservative", "realistic", "optimistic"])

**Returns:**
- `Dict`: Projection results for all scenarios

**Example:**
```python
simulator = IndividualProgressionSimulator(population_data)
projections = simulator.project_salary_progression(
    employee_data=employee_record,
    years=5,
    scenarios=["conservative", "realistic", "optimistic"]
)
```

---

## Visualization Components

### management_dashboard_generator.py

Executive dashboard generation with management-focused visualizations.

#### Classes

##### `ManagementDashboardGenerator`
Generator for executive-friendly management dashboards.

**Constructor:**
```python
def __init__(self, analysis_results: Dict[str, Any], population_data: List[Dict], 
             config: Dict[str, Any], smart_logger=None)
```

**Parameters:**
- `analysis_results` (Dict[str, Any]): Results from analysis pipeline
- `population_data` (List[Dict]): Employee population data
- `config` (Dict[str, Any]): Configuration settings
- `smart_logger` (optional): Smart logging manager instance

**Methods:**

###### `generate_executive_dashboard() -> Dict[str, str]`
Generate comprehensive executive dashboard.

**Returns:**
- `Dict[str, str]`: Dictionary containing paths to generated files

**Example:**
```python
generator = ManagementDashboardGenerator(
    analysis_results=results,
    population_data=population,
    config=config
)
dashboard_files = generator.generate_executive_dashboard()
```

---

## Utility Functions

### smart_logging_manager.py

Intelligent logging system with context-aware messaging.

#### Functions

##### `get_smart_logger() -> SmartLoggingManager`
Get singleton instance of smart logging manager.

**Returns:**
- `SmartLoggingManager`: Logger instance

**Example:**
```python
logger = get_smart_logger()
logger.log_info("Processing employee data")
logger.log_warning("Data validation warning")
logger.log_error("Processing failed")
```

#### Classes

##### `SmartLoggingManager`
Advanced logging manager with phase tracking and intelligent formatting.

**Methods:**

###### `log_info(message: str) -> None`
Log informational message.

###### `log_warning(message: str) -> None`
Log warning message.

###### `log_error(message: str) -> None`
Log error message.

###### `log_success(message: str) -> None`
Log success message with special formatting.

###### `start_phase(phase_name: str, total_steps: int) -> None`
Start tracking a multi-step phase.

**Example:**
```python
logger = SmartLoggingManager()
logger.start_phase("Data Processing", 5)
logger.log_info("Step 1: Loading data")
logger.log_info("Step 2: Validating data")
# ... continue with steps
```

---

## Configuration Reference

### Default Configuration Structure

```python
DEFAULT_CONFIG = {
    # Population settings
    "population_size": 100,
    "random_seed": 42,
    "level_distribution": [0.25, 0.25, 0.20, 0.15, 0.10, 0.05],
    
    # Analysis settings
    "analysis_years": 5,
    "max_cycles": 15,
    "confidence_interval": 0.95,
    "market_inflation_rate": 0.025,
    
    # Individual analysis settings
    "progression_analysis_years": 5,
    "export_individual_analysis": True,
    
    # Visualization settings
    "generate_visualizations": True,
    "auto_open_dashboard": True,
    "dashboard_theme": "executive",  # "executive", "analytical", "compliance"
    
    # Export settings
    "export_formats": ["json", "csv"],
    "export_individual_files": True,
    "export_comprehensive_report": True,
    
    # Advanced settings
    "run_median_convergence_analysis": True,
    "acceptable_gap_percent": 5.0,
    "convergence_threshold_years": 5,
    
    # Performance settings
    "enable_performance_optimization": True,
    "chunk_size": 1000,
    "parallel_processing": False,
    
    # Logging settings
    "log_level": "info",  # "debug", "info", "warning", "error"
    "log_to_file": False,
    "log_file_path": "logs/simulation.log"
}
```

### Scenario-Specific Configurations

#### Individual Scenario
```python
INDIVIDUAL_CONFIG = {
    "scenario_type": "individual",
    "generate_visualizations": True,
    "export_individual_analysis": True,
    "dashboard_theme": "analytical",
    "run_median_convergence_analysis": True
}
```

#### Basic Scenario
```python
BASIC_CONFIG = {
    "scenario_type": "basic",
    "population_size": 100,
    "max_cycles": 15,
    "generate_visualizations": True,
    "dashboard_theme": "executive",
    "export_formats": ["json", "csv", "html"]
}
```

#### Large Scale Scenario
```python
LARGE_SCALE_CONFIG = {
    "scenario_type": "large_scale", 
    "population_size": 2000,
    "max_cycles": 25,
    "enable_performance_optimization": True,
    "parallel_processing": True,
    "chunk_size": 500
}
```

#### Equity Focused Scenario
```python
EQUITY_FOCUSED_CONFIG = {
    "scenario_type": "equity_focused",
    "population_size": 750,
    "run_median_convergence_analysis": True,
    "generate_intervention_analysis": True,
    "dashboard_theme": "compliance",
    "acceptable_gap_percent": 3.0
}
```

### Environment Variables

The system supports configuration via environment variables:

```bash
# Population settings
export EMPLOYEE_SIM_POPULATION_SIZE=500
export EMPLOYEE_SIM_RANDOM_SEED=12345

# Analysis settings  
export EMPLOYEE_SIM_ANALYSIS_YEARS=7
export EMPLOYEE_SIM_CONFIDENCE_LEVEL=0.99

# Output settings
export EMPLOYEE_SIM_OUTPUT_DIR="/custom/output/path"
export EMPLOYEE_SIM_AUTO_OPEN=false

# Performance settings
export EMPLOYEE_SIM_PARALLEL=true
export EMPLOYEE_SIM_CHUNK_SIZE=1000
```

## Error Handling

### Common Exceptions

#### `ValidationError`
Raised when employee data validation fails.

**Common Causes:**
- Invalid level (not 1-6)
- Invalid performance rating
- Salary outside acceptable range for level

**Handling:**
```python
try:
    employee = EmployeeData(**data)
except ValidationError as e:
    print(f"Validation failed: {e}")
    # Handle validation errors appropriately
```

#### `ValueError`
Raised when input parameters are invalid.

**Common Causes:**
- Empty or malformed employee data string
- Invalid configuration values
- Missing required fields

#### `RuntimeError`
Raised when processing fails unexpectedly.

**Common Causes:**
- Memory allocation failures
- File system errors
- Visualization generation failures

### Best Practices

**Error Handling Pattern:**
```python
def robust_function(data: Any) -> Any:
    try:
        # Validate inputs
        if not data:
            raise ValueError("Input data cannot be empty")
            
        # Main processing logic
        result = process_data(data)
        
        # Validate outputs
        if not validate_result(result):
            raise RuntimeError("Processing produced invalid results")
            
        return result
        
    except ValidationError as e:
        logger.error(f"Validation failed in {__name__}: {e}")
        raise ValueError(f"Invalid input: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in {__name__}: {e}")
        raise RuntimeError(f"Processing failed: {e}")
```

---

## Examples and Use Cases

### Complete Individual Analysis Example

```python
from individual_employee_parser import parse_employee_data_string
from employee_simulation_orchestrator import run_individual_employee_analysis

# Parse employee data
employee_data = parse_employee_data_string(
    "level:5,salary:80692.5,performance:Exceeding,gender:Female,tenure:3,name:Sarah Johnson"
)

# Configure analysis
config = {
    "analysis_years": 7,
    "generate_visualizations": True,
    "export_individual_analysis": True,
    "confidence_interval": 0.99
}

# Run analysis
run_individual_employee_analysis(employee_data, config)

# Results automatically exported to artifacts/individual_analysis/
```

### Population Analysis with Custom Configuration

```python
from employee_simulation_orchestrator import run_simulation_with_config

# Custom configuration
config = {
    "population_size": 1500,
    "max_cycles": 20,
    "analysis_years": 8,
    "level_distribution": [0.10, 0.20, 0.40, 0.20, 0.08, 0.02],
    "generate_visualizations": True,
    "dashboard_theme": "compliance",
    "export_formats": ["json", "csv", "html"]
}

# Run simulation
results = run_simulation_with_config(config)
print(f"Generated {len(results.get('files_generated', {}))} output files")
```

### Custom Analysis Pipeline

```python
from salary_forecasting_engine import SalaryForecastingEngine
from median_convergence_analyzer import MedianConvergenceAnalyzer

# Initialize components
forecasting_engine = SalaryForecastingEngine(confidence_level=0.95)
convergence_analyzer = MedianConvergenceAnalyzer(population_data)

# Custom analysis workflow
employee_data = {"level": 3, "salary": 65000, "performance_rating": "Achieving"}

# Project salary scenarios
scenarios = forecasting_engine.generate_performance_scenarios(employee_data, years=5)

# Analyze convergence
convergence = convergence_analyzer.analyze_convergence_timeline(employee_data)

# Combine results
analysis_results = {
    "projections": scenarios,
    "convergence_analysis": convergence,
    "recommendations": generate_recommendations(scenarios, convergence)
}
```

---

## Version History

### Version 1.1.0 (Current)
- Added individual employee analysis functionality
- Enhanced visualization system with Plotly integration
- Improved error handling and validation
- Added comprehensive test suite
- Makefile automation for development workflow

### Version 1.0.1
- Bug fixes in population generation
- Performance optimizations for large datasets
- Updated documentation

### Version 1.0.0
- Initial release
- Basic population simulation
- Salary forecasting engine
- Visualization system
- Executive dashboard generation

---

*This API reference covers all public interfaces in the Employee Simulation System. For implementation details and internal APIs, see the [Developer Guide](DEVELOPER.md).*
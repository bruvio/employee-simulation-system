# Employee Simulation System - User Guide

This comprehensive guide explains how to use the Employee Simulation System for various HR analytics tasks, from individual employee analysis to large-scale population simulations.

## Table of Contents

- [Getting Started](#getting-started)
- [Individual Employee Analysis](#individual-employee-analysis)
- [Population Simulations](#population-simulations)
- [Configuration Options](#configuration-options)
- [Output Analysis](#output-analysis)
- [Advanced Features](#advanced-features)
- [Troubleshooting](#troubleshooting)

## Getting Started

### Installation and Setup

```bash
# Clone and setup
git clone https://github.com/bruvio/employee-simulation-system.git
cd employee-simulation-system

# Install dependencies
pip install -r requirements.txt

# Verify installation
python employee_simulation_orchestrator.py --help
```

### Basic Command Structure

```bash
python employee_simulation_orchestrator.py [OPTIONS]
```

**Core Options:**
- `--scenario`: Type of analysis (individual, basic, large_scale, equity_focused)
- `--employee-data`: Employee data for individual analysis
- `--population-size`: Number of employees to simulate
- `--analysis-years`: Projection period (default: 5 years)
- `--log-level`: Logging detail (info, debug, warning)

## Individual Employee Analysis

### Basic Individual Analysis

Analyze a single employee's career progression and salary trajectory:

```bash
python employee_simulation_orchestrator.py \
  --scenario individual \
  --employee-data "level:5,salary:80692.5,performance:Exceeding"
```

**What this does:**
- Analyzes career progression for a Level 5 employee
- Projects 5-year salary growth scenarios
- Compares against median salaries for their level
- Generates visualization charts
- Provides performance-based recommendations

### Extended Employee Data

Include additional employee attributes for more detailed analysis:

```bash
python employee_simulation_orchestrator.py \
  --scenario individual \
  --employee-data "level:3,salary:65000,performance:High Performing,gender:Female,tenure:3,name:Sarah Johnson,department:Marketing"
```

**Additional Data Fields:**
- `level`: Job level (1-6, required)
- `salary`: Current salary (required)
- `performance`: Performance rating (required)
- `gender`: Male/Female (optional, defaults to Female)
- `tenure`: Years of service (optional, defaults to 1)
- `name`: Employee name (optional, defaults to "Individual Employee")
- `department`: Department name (optional, defaults to "Engineering")

**Valid Performance Ratings:**
- "Not met"
- "Partially met"  
- "Achieving"
- "High Performing"
- "Exceeding"

### Custom Analysis Period

Adjust the projection timeframe:

```bash
python employee_simulation_orchestrator.py \
  --scenario individual \
  --employee-data "level:2,salary:55000,performance:Achieving" \
  --analysis-years 7
```
```bash
python employee_simulation_orchestrator.py \
  --scenario individual \
  --employee-data "level:5,salary:80692.5,performance:Exceeding" \
  --analysis-years 2
```


### Using Makefile Commands

```bash
# Quick individual analysis
make analyze-individual EMPLOYEE_DATA="level:4,salary:75000,performance:High Performing"

# With custom parameters
make analyze-individual EMPLOYEE_DATA="level:3,salary:62000,performance:Achieving,gender:Male,tenure:5"
```

### Individual Analysis Output

**Console Output:**
```
🧑‍💼 Individual Employee Analysis
==================================================
Employee: Sarah Johnson
Level: 3
Current Salary: £65,000.00
Performance Rating: High Performing
Gender: Female
Tenure: 3 years
Department: Marketing

📊 5-Year Salary Progression Analysis
==================================================

📈 Scenario Analysis (Year 5):
├─ Conservative: £78,450
├─ Realistic:    £82,340
└─ Optimistic:   £85,120

💰 Financial Impact (Realistic Scenario):
├─ Current Salary: £65,000
├─ Future Salary:  £82,340
├─ Total Increase: £17,340
└─ Annual Growth:  4.8%

✅ Above Median: Employee is performing above median for Level 3

💡 Recommendations:
├─ Consider for accelerated development programs
├─ Evaluate for promotion opportunities
└─ Ensure competitive retention package

📈 Visualizations generated:
├─ artifacts/individual_analysis/visualizations/salary_projection_1_*.html

📄 Analysis exported to: artifacts/individual_analysis/individual_analysis_1_*.json
```

**Generated Files:**
- **JSON Report**: Complete technical analysis with all calculations
- **HTML Chart**: Interactive salary projection visualization
- **Convergence Analysis**: Comparison with median salaries

## Population Simulations

### Basic Population Analysis

Generate and analyze a standard employee population:

```bash
# Default 100 employees
python employee_simulation_orchestrator.py --scenario basic

# Custom population size
python employee_simulation_orchestrator.py --scenario basic --population-size 500
```

**What this generates:**
- Realistic employee population with diverse levels, salaries, performance ratings
- Salary distribution analysis across levels
- Gender pay gap analysis
- Performance correlation insights
- Executive summary dashboard

### Large-Scale Enterprise Simulation

For comprehensive organizational analysis:

```bash
python employee_simulation_orchestrator.py \
  --scenario large_scale \
  --population-size 2000 \
  --max-cycles 25 \
  --analysis-years 7 \
  --random-seed 42
```

**Parameters:**
- `--population-size`: Number of employees (1000+ for large_scale)
- `--max-cycles`: Simulation cycles for career progression
- `--analysis-years`: Projection timeframe
- `--random-seed`: Reproducible results

### Pay Equity Focused Analysis

Specialized analysis for salary equity and pay gap investigation:

```bash
python employee_simulation_orchestrator.py \
  --scenario equity_focused \
  --population-size 750 \
  --log-level debug
```

**Focus Areas:**
- Gender pay gap analysis with statistical significance
- Level-based equity assessment
- Below-median employee identification
- Intervention cost modeling
- Compliance risk assessment

### Advanced Population Parameters

```bash
python employee_simulation_orchestrator.py \
  --scenario basic \
  --population-size 1000 \
  --max-cycles 20 \
  --random-seed 12345 \
  --analysis-years 10
```

## Configuration Options

### Command Line Configuration

**Core Parameters:**
```bash
--scenario SCENARIO          # Analysis type: individual, basic, large_scale, equity_focused
--employee-data DATA         # Employee data string for individual analysis
--population-size SIZE       # Number of employees to simulate (default: 100)
--max-cycles CYCLES          # Review cycles to simulate (default: 15)
--analysis-years YEARS       # Projection period in years (default: 5)
--random-seed SEED           # Random seed for reproducible results (default: 42)
--log-level LEVEL           # Logging level: debug, info, warning, error (default: info)
```

**Example with all parameters:**
```bash
python employee_simulation_orchestrator.py \
  --scenario equity_focused \
  --population-size 1500 \
  --max-cycles 30 \
  --analysis-years 8 \
  --random-seed 2024 \
  --log-level debug
```

### Scenario Configurations

Each scenario has different default configurations:

**Individual Scenario:**
- Focus: Single employee analysis
- Visualizations: Salary projection charts
- Outputs: JSON reports, HTML charts
- Time: Fast execution (< 30 seconds)

**Basic Scenario:**
- Population: 100-500 employees
- Analysis: Standard pay gap and distribution analysis
- Visualizations: Population dashboards
- Time: 1-3 minutes

**Large Scale Scenario:**
- Population: 1000+ employees  
- Analysis: Comprehensive statistical modeling
- Visualizations: Advanced charts and executive dashboards
- Time: 5-15 minutes
- Memory: Higher memory requirements

**Equity Focused Scenario:**
- Population: 500-1000 employees
- Analysis: Pay gap, intervention modeling
- Visualizations: Executive dashboards with recommendations
- Time: 3-8 minutes

## Output Analysis

### Understanding Individual Analysis Results

**Salary Scenarios Explained:**
- **Conservative**: Lower-bound projection based on minimal performance improvements
- **Realistic**: Expected trajectory based on current performance and typical progression
- **Optimistic**: Upper-bound projection assuming sustained high performance

**Median Convergence Analysis:**
- Shows if employee is above/below median for their level
- Calculates time to reach median salary
- Provides intervention recommendations for below-median employees

**Financial Impact Metrics:**
- **Total Increase**: Absolute salary growth over analysis period
- **Annual Growth Rate**: Compound annual growth rate (CAGR)
- **Performance Multiplier**: How performance rating affects growth

### Understanding Population Analysis Results

**Executive Dashboard Metrics:**
- **Gender Pay Gap**: Median salary difference between genders
- **Below Median Employees**: Count and percentage of employees below level median
- **Risk Assessment**: Overall compliance and equity risk score
- **Intervention Cost**: Estimated cost to close identified pay gaps

**Statistical Significance:**
- Pay gap analysis includes confidence intervals
- Population size affects statistical reliability
- Larger populations provide more robust insights

### Output File Structure

```
artifacts/
├── individual_analysis/           # Individual employee reports
│   ├── individual_analysis_1_20250812_125843.json
│   └── visualizations/
│       └── salary_projection_1_20250812_125842.html
├── advanced_analysis/             # Population-level analysis
│   ├── management_dashboard_20250812_130045.html
│   ├── technical_analysis_20250812_130045.json
│   └── charts/
│       ├── salary_distribution_20250812_130045.html
│       └── pay_gap_analysis_20250812_130045.html
└── exports/                       # Data exports
    ├── population_data_20250812_130045.csv
    └── analysis_results_20250812_130045.json
```

## Advanced Features

### Makefile Automation

The system includes a comprehensive Makefile for common operations:

```bash
# Development workflow
make black          # Format code
make flake          # Lint code
make test           # Run unit tests
make pip-compile    # Update dependencies
make pip-upgrade    # Upgrade dependencies

# Application execution
make run            # Run basic simulation
make analyze-individual EMPLOYEE_DATA="level:5,salary:80000,performance:Exceeding"
```

### Batch Employee Analysis

Process multiple employees using shell scripts:

```bash
#!/bin/bash
# analyze_team.sh
employees=(
    "level:3,salary:65000,performance:Achieving,name:Alice Smith"
    "level:4,salary:75000,performance:High Performing,name:Bob Johnson"  
    "level:5,salary:85000,performance:Exceeding,name:Carol Williams"
)

for emp in "${employees[@]}"; do
    echo "Analyzing: $emp"
    python employee_simulation_orchestrator.py --scenario individual --employee-data "$emp"
done
```

### Custom Configuration Files

Create reusable configuration files:

```python
# custom_config.py
ANALYSIS_CONFIG = {
    "population_size": 1000,
    "max_cycles": 20,
    "analysis_years": 7,
    "generate_visualizations": True,
    "confidence_interval": 0.95,
    "market_inflation_rate": 0.025,
    "export_formats": ["json", "csv", "html"]
}
```

### Integration with External Systems

Export data for use in other systems:

```bash
# Generate CSV for external analysis
python employee_simulation_orchestrator.py \
  --scenario basic \
  --population-size 500

# Files generated in artifacts/exports/
# - population_data_*.csv
# - analysis_results_*.json
```

## Troubleshooting

### Common Issues and Solutions

**1. Import Errors**
```bash
# Error: ModuleNotFoundError: No module named 'pandas'
# Solution:
pip install -r requirements.txt
```

**2. Memory Issues with Large Populations**
```bash
# Error: Memory allocation failed
# Solution: Reduce population size or use optimization
python employee_simulation_orchestrator.py --scenario basic --population-size 1000
# Instead of 5000+
```

**3. Invalid Employee Data Format**
```bash
# Error: Invalid format in pair 'level=5'
# Solution: Use colons, not equals
--employee-data "level:5,salary:80000,performance:Exceeding"
```

**4. Visualization Generation Errors**
```bash
# Error: Could not generate visualizations
# Solution: Install plotting libraries
pip install plotly matplotlib seaborn
```

**5. Performance Issues**
```bash
# Slow execution with large populations
# Solution: Use appropriate scenario type
--scenario large_scale  # For 1000+ employees
--scenario basic        # For <1000 employees
```

### Debug Mode

Enable detailed logging for troubleshooting:

```bash
python employee_simulation_orchestrator.py \
  --scenario individual \
  --employee-data "level:5,salary:80000,performance:Exceeding" \
  --log-level debug
```

### Validation Checks

Run system validation:

```bash
# Run all tests
make test

# Check code quality
make flake
make black-check

# Validate specific functionality
python -c "
from individual_employee_parser import parse_employee_data_string
try:
    result = parse_employee_data_string('level:5,salary:80000,performance:Exceeding')
    print('✅ Parser working correctly')
    print(result)
except Exception as e:
    print('❌ Parser error:', e)
"
```

### Getting Help

**Command Line Help:**
```bash
python employee_simulation_orchestrator.py --help
```

**System Information:**
```bash
# Check Python version
python --version

# Check installed packages
pip list | grep -E "(pandas|numpy|plotly|matplotlib)"

# Check available scenarios
python employee_simulation_orchestrator.py --help | grep -A 10 "scenario"
```

### Performance Guidelines

**Population Size Recommendations:**
- **Individual Analysis**: Any size (single employee)
- **Development/Testing**: 100-500 employees
- **Department Analysis**: 500-1,000 employees  
- **Enterprise Analysis**: 1,000-5,000 employees
- **Large Scale Research**: 5,000+ employees (requires significant memory)

**System Requirements by Scale:**
- Small (≤500): 1GB RAM, 1 CPU core
- Medium (500-2000): 2GB RAM, 2 CPU cores
- Large (2000-5000): 4GB RAM, 4 CPU cores  
- Enterprise (5000+): 8GB+ RAM, 8+ CPU cores

---

## Need More Help?

- 📋 Check the [README.md](../README.md) for system overview
- 🔧 Review [DEVELOPER.md](DEVELOPER.md) for technical details
- 🐛 Report issues on [GitHub Issues](https://github.com/bruvio/employee-simulation-system/issues)
- 📧 Contact: [bruvio](https://github.com/bruvio)

*This user guide covers the most common use cases. For advanced customization and development, see the developer documentation.*
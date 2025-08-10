# Employee Simulation System

A comprehensive Python-based employee simulation and story tracking system for analyzing organizational dynamics, salary distributions, and career progression patterns.

## Features

### 🏢 Core Simulation Engine
- **Realistic Population Generation**: Generate employee populations with configurable level distributions
- **Salary Constraint Engine**: Realistic salary constraints by level:
  - Level 1 (Graduates): £28,000 - £35,000
  - Level 2 (Junior): £45,000 - £72,000  
  - Level 3 (Standard Hire): £72,000 - £95,000+
  - Level 4-6 (Senior): £76,592 - £103,624

### 💰 Advanced Salary Dynamics
- **Negotiation Simulation**: Statistical modeling of salary negotiations
  - 30% of Level 3 employees negotiate hard (can reach ~£90k)
  - Graduated negotiation rates across all levels
- **Gender Pay Gap Modeling**: Configurable gender pay gap simulation (2024 UK average: 15.8%)
- **Level Distribution Skewing**: Custom level distributions (e.g., 50% Level 3 employees)

### 📚 Employee Story Tracking
- **Automatic Pattern Detection**: Identifies interesting employee patterns:
  - Gender gap affected employees
  - Above-range salary performers
  - High-performing outliers
- **Multi-cycle Career Progression**: Track employees through multiple review cycles
- **Interactive Story Analysis**: Detailed narratives and progression tracking

### 📊 Visualization & Analysis
- **Population Dashboards**: Comprehensive salary and performance visualizations
- **Interactive Jupyter Notebooks**: Widget-based exploration with real-time filtering
- **Export Capabilities**: Multiple format support (CSV, JSON, Excel, Markdown)

### 🎯 Smart Search & Filtering
- **Employee Matching**: Find employees matching specific criteria (salary, level, performance)
- **Tolerance-based Search**: Flexible salary ranges and performance filters
- **Story Integration**: See which employees are tracked for interesting patterns

## Quick Start

### Basic Usage

```python
from run_employee_simulation import EmployeeStoryExplorer

# Generate population with realistic constraints
explorer = EmployeeStoryExplorer()
success = explorer.run_simulation(
    population_size=1000,
    random_seed=42,
    target_salary=80000,
    target_level=3
)
```

### Custom Level Distribution

```python
# 50% Level 3 employees (standard hire level)
explorer.run_simulation(
    population_size=200,
    level_distribution=[0.05, 0.05, 0.50, 0.20, 0.15, 0.05],
    target_level=3
)
```

### Gender Pay Gap Simulation

```python
# Apply 2024 UK average gender pay gap
explorer.run_simulation(
    population_size=500,
    gender_pay_gap_percent=15.8,
    target_level=5
)
```

### Interactive Exploration

Open `employee_explorer.ipynb` for interactive widget-based exploration with:
- Real-time population generation
- Custom salary constraints
- Level distribution controls
- Gender pay gap simulation
- Advanced filtering and visualization

## Architecture

### Core Modules

1. **`employee_population_simulator.py`** - Population generation with realistic constraints
2. **`employee_simulation_orchestrator.py`** - Main coordination engine
3. **`employee_story_tracker.py`** - Pattern detection and story tracking
4. **`performance_review_system.py`** - Performance rating and progression logic
5. **`review_cycle_simulator.py`** - Multi-cycle career simulation
6. **`visualization_generator.py`** - Chart and graph generation
7. **`interactive_dashboard_generator.py`** - Interactive dashboard creation

### Key Features

- **Smart Logging**: Configurable logging with progress indicators
- **File Optimization**: Structured output organization
- **Performance Optimization**: Efficient handling of large populations (10K+ employees)
- **Story Export**: Multiple export formats with narrative generation

## Configuration Options

The system supports extensive configuration:

```python
config = {
    'population_size': 1000,
    'random_seed': 42,
    'level_distribution': [0.25, 0.25, 0.20, 0.15, 0.10, 0.05],
    'gender_pay_gap_percent': 15.8,
    'salary_constraints': {
        1: {'min': 28000, 'max': 35000, 'median_target': 30000},
        2: {'min': 45000, 'max': 72000, 'median_target': 60000},
        3: {'min': 72000, 'max': 95000, 'median_target': 83939}
    }
}
```

## Use Cases

### HR Analytics
- Analyze salary distributions and identify pay equity issues
- Model the impact of different hiring strategies
- Understand career progression patterns

### Organizational Planning
- Simulate the effects of level distribution changes
- Plan for salary budget impacts
- Model negotiation dynamics

### Research & Development
- Test hypotheses about organizational behavior
- Generate realistic datasets for HR tool development
- Analyze correlation between performance and compensation

## Output Examples

The system generates:
- **Population Analysis Reports**: Detailed markdown reports with insights
- **Visualization Charts**: Distribution plots, performance correlations
- **Employee Matches**: Specific employees meeting criteria
- **Story Narratives**: Interesting career progression patterns

## Requirements

- Python 3.9+
- pandas, numpy, matplotlib, seaborn, plotly
- jupyter, ipywidgets (for interactive notebooks)

## Getting Started

1. Install dependencies: `pip install -r requirements.txt`
2. Run basic simulation: `python run_employee_simulation.py`
3. Explore interactively: `jupyter notebook employee_explorer.ipynb`

---

*Generated with enhanced employee simulation system featuring realistic salary constraints, negotiation dynamics, and comprehensive story tracking.*
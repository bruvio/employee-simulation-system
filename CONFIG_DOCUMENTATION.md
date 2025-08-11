# Configuration System Documentation

## Overview

The Employee Simulation System uses a **structured JSON configuration file** (`config.json`) that allows you to:

1. **Set default simulation parameters** without changing code
2. **Use predefined scenarios** for common use cases  
3. **Create custom configurations** for specific business needs
4. **Override settings** via command-line arguments

## Configuration File Structure

### 1. **Base Configuration Sections**

```json
{
  "population": {        // Employee population settings
    "population_size": 200,
    "random_seed": 42,
    "gender_pay_gap_percent": null,
    "level_distribution": null,
    "salary_constraints": null
  },
  
  "simulation": {        // Simulation behavior  
    "max_cycles": 15,
    "convergence_threshold": 0.001
  },
  
  "advanced_analysis": { // Advanced analysis features
    "enable_advanced_analysis": true,
    "run_median_convergence_analysis": true,
    "progression_analysis_years": 5
  }
}
```

### 2. **User Story Scenarios** 

Quick configurations for common use cases:

```json
"user_stories": {
  "scenarios": {
    "quick_test": {
      "population_size": 200,
      "max_cycles": 5,
      "enable_story_tracking": true
    },
    
    "gender_gap_analysis": {
      "population_size": 200,
      "gender_pay_gap_percent": 15.8,
      "enable_advanced_analysis": true,
      "run_intervention_strategy_analysis": true
    }
  }
}
```

### 3. **Customization Examples**

Complete configurations for different company types:

```json
"customization_examples": {
  "startup_simulation": {
    "population_size": 200,
    "level_distribution": [0.40, 0.30, 0.20, 0.10, 0.00, 0.00],
    "salary_constraints": {
      "1": {"min": 25000, "max": 32000, "median_target": 28000},
      "2": {"min": 40000, "max": 65000, "median_target": 52000}
    }
  },
  
  "tech_company_simulation": {
    "population_size": 2000,
    "gender_pay_gap_percent": 12.3,
    "salary_constraints": {
      "1": {"min": 32000, "max": 42000},
      "3": {"min": 75000, "max": 110000},
      "6": {"min": 140000, "max": 200000}
    }
  }
}
```

## Difference Between Scenarios vs Customization Examples

| **User Story Scenarios** | **Customization Examples** |
|---------------------------|----------------------------|
| Quick, focused configurations | Complete company-specific setups |
| Test specific features | Model real business scenarios |
| Override a few key settings | Define full salary structures |
| Good for development/testing | Good for production analysis |

**Example:**
- `quick_test` scenario: Just changes population size and enables story tracking
- `tech_company_simulation`: Defines complete salary ranges, level distributions, and pay gap modeling for a tech company

## How to Use the Configuration System

### Method 1: Command Line (Easiest)

```bash
# Use default configuration (your current 200 employees + advanced analysis)
python employee_simulation_orchestrator.py --mode advanced-analysis-only

# Use a specific scenario
python employee_simulation_orchestrator.py --scenario quick_test

# Use scenario with overrides
python employee_simulation_orchestrator.py --scenario gender_gap_analysis --population-size 500

# Use company-specific example
python employee_simulation_orchestrator.py --scenario tech_company_simulation
```

### Method 2: Configuration Manager CLI

```bash
# List all available scenarios
python config_manager.py list

# Show details of a scenario  
python config_manager.py show comprehensive_analysis

# Create a custom config file
python config_manager.py create my_custom.json --scenario quick_test --population-size 300

# Test a scenario configuration
python config_manager.py test gender_gap_analysis
```

### Method 3: Programmatic Usage

```python
from config_manager import ConfigurationManager

# Load configuration
config_manager = ConfigurationManager("config.json")

# Get default config
config = config_manager.get_orchestrator_config()

# Get scenario config  
config = config_manager.get_orchestrator_config(scenario="quick_test")

# Get config with overrides
config = config_manager.get_orchestrator_config(
    scenario="gender_gap_analysis",
    overrides={"population_size": 1000, "log_level": "DEBUG"}
)

# Use with orchestrator
from employee_simulation_orchestrator import EmployeeSimulationOrchestrator
orchestrator = EmployeeSimulationOrchestrator(config=config)
```

## Creating Your Own Scenarios

### Option 1: Edit config.json directly

Add to the `user_stories.scenarios` section:

```json
"my_custom_scenario": {
  "population_size": 300,
  "enable_story_tracking": true,
  "enable_advanced_analysis": true,
  "gender_pay_gap_percent": 10.0
}
```

### Option 2: Use the configuration manager

```python
from config_manager import ConfigurationManager

config_manager = ConfigurationManager("config.json")
config_manager.save_scenario("my_scenario", {
    "population_size": 300,
    "enable_advanced_analysis": True
})
```

## Available Configuration Options

### Population Settings
- `population_size`: Number of employees (default: 200)
- `random_seed`: For reproducible results (default: 42)
- `gender_pay_gap_percent`: Gender pay gap % (e.g., 15.8)
- `level_distribution`: Employee level distribution array
- `salary_constraints`: Custom salary ranges by level

### Analysis Settings  
- `enable_advanced_analysis`: Enable advanced analysis features
- `run_individual_progression_analysis`: Individual salary forecasting
- `run_median_convergence_analysis`: Below-median employee analysis
- `run_intervention_strategy_analysis`: Pay gap remediation modeling
- `progression_analysis_years`: Years to project (default: 5)

### Story Tracking
- `enable_story_tracking`: Track interesting employee patterns
- `story_categories`: Which patterns to track (gender_gap, high_performer, etc.)
- `tracked_employee_count`: Max employees per category

### Export & Visualization
- `export_formats`: Output formats (csv, excel, json, markdown)
- `generate_visualizations`: Create charts and graphs
- `generate_interactive_dashboard`: Create HTML dashboards

## Quick Start Examples

### 1. Your Current Use Case
```bash
# This now works with 200 employees and advanced analysis enabled by default:
python employee_simulation_orchestrator.py --mode advanced-analysis-only --population-size 200 --advanced-analysis
```

### 2. Test Story Generation
```bash
python employee_simulation_orchestrator.py --scenario quick_test
```

### 3. Gender Pay Gap Analysis  
```bash
python employee_simulation_orchestrator.py --scenario gender_gap_analysis
```

### 4. Full Analysis Suite
```bash
python employee_simulation_orchestrator.py --scenario comprehensive_analysis
```

## Benefits of This System

1. **No Code Changes**: Modify behavior without touching Python files
2. **Reusable Scenarios**: Save configurations for repeated use
3. **Command-Line Flexibility**: Override any setting from command line
4. **Documentation**: Self-documenting configuration structure
5. **Version Control**: Track configuration changes with Git
6. **Sharing**: Share scenarios with team members easily

## File Hierarchy

```
employee-simulation-system/
├── config.json              # Main configuration file
├── config_manager.py        # Configuration management tool
├── config_examples.py       # Usage examples and documentation
├── CONFIG_DOCUMENTATION.md  # This documentation
└── employee_simulation_orchestrator.py  # Now config-aware
```

The configuration system eliminates hardcoded defaults and gives you flexible control over simulation parameters through structured JSON files and command-line tools.
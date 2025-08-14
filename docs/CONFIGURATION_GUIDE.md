# Employee Simulation System - Configuration Guide

## Overview

This guide explains how to configure the Employee Simulation System for different use cases, from quick testing to comprehensive organizational analysis. The system uses a JSON configuration file with scenarios to make common configurations easy to use.

## Understanding the Configuration Structure

The configuration is organized into logical sections:

```json
{
  "meta": { /* Version and metadata */ },
  "defaults": { /* Base settings for all scenarios */ },
  "scenarios": { /* Pre-configured combinations for specific use cases */ }
}
```

## Core Configuration Categories

### 1. Population Settings 👥

These settings control the simulated employee population:

| Setting | Purpose | Example Values |
|---------|---------|----------------|
| `population_size` | Number of employees to simulate | `200` (small), `1000` (medium), `5000` (large) |
| `random_seed` | Ensures reproducible results | `42` (any integer) |
| `gender_pay_gap_percent` | Starting gender pay gap | `12.5` (realistic), `0` (equal), `25` (high gap) |
| `currency` | Salary currency for reporting | `"GBP"`, `"USD"`, `"EUR"` |
| `level_distribution` | Employee distribution across levels | `[0.05, 0.15, 0.30, 0.25, 0.20, 0.05]` or `null` for automatic |

#### Salary Constraints by Level
Define realistic salary ranges for each organizational level:

```json
"salary_constraints": {
  "1": {"min": 28000, "max": 35000, "median_target": 30000},
  "2": {"min": 45000, "max": 72000, "median_target": 60000},
  "3": {"min": 72000, "max": 95000, "median_target": 83939}
}
```

**Use Cases:**
- **Startup**: Lower salary bands, compressed levels
- **Enterprise**: Wider ranges, more levels
- **Public Sector**: Structured bands with clear progression

### 2. Analysis Settings 📊

Control what types of analysis the system performs:

| Setting | Purpose | When to Use |
|---------|---------|-------------|
| `enable_advanced_analysis` | Enables deep analytical features | Always for meaningful results |
| `run_median_convergence_analysis` | Analyzes below-median employees | HR equity initiatives |
| `run_intervention_strategy_analysis` | Models management interventions | Budget planning, gap remediation |
| `run_individual_progression_analysis` | Individual career path modeling | Career development, coaching |

#### Analysis Parameters
```json
"progression_analysis_years": 5,           // How far to project
"convergence_threshold_years": 5,          // Timeline for convergence goals
"acceptable_gap_percent": 5.0,            // Target gap percentage
"intervention_budget_constraint": 0.005,  // Budget as % of payroll (0.5%)
"target_gender_gap_percent": 0.0          // Ultimate gap target
```

### 3. Story Tracking Settings 📖

Track specific employee scenarios for detailed analysis:

| Setting | Purpose | Best Practice |
|---------|---------|---------------|
| `enable_story_tracking` | Track interesting employee cases | Enable for detailed insights |
| `tracked_employee_count` | How many employees per category | `10-20` for meaningful sample |
| `story_categories` | Which scenarios to track | `["gender_gap", "high_performer", "below_median"]` |

**Story Categories Explained:**
- `"gender_gap"`: Employees affected by gender pay disparities
- `"high_performer"`: Top performers for recognition/retention
- `"below_median"`: Employees earning below their level median
- `"above_range"`: Employees above typical salary ranges

### 4. Output Settings 📋

Control what reports and files are generated:

| Setting | Purpose | Recommendation |
|---------|---------|----------------|
| `export_formats` | File formats for data export | `["csv", "json"]` for analysis, `["excel"]` for sharing |
| `generate_visualizations` | Create charts and graphs | `true` for presentations |
| `enable_report_generation` | Generate cohesive reports | `true` for GEL scenarios |
| `output_format` | Special output formatting | `"gel_cohesive"` for clean GEL reports |

### 5. GEL-Specific Settings 🏢

Settings specific to the GEL scenario and policy-constrained analysis:

| Setting | Purpose | GEL Standard |
|---------|---------|--------------|
| `max_direct_reports` | Manager span of control limit | `6` (policy requirement) |
| `roles_config_required` | Enforce role minimum salaries | `true` (use YAML config) |
| `intervention_budget_constraint` | Budget cap per manager | `0.005` (0.5% of team payroll) |

## Configuration Combinations by Use Case

### 🚀 Quick Testing
**Purpose**: Fast validation, development testing
```json
{
  "population_size": 200,
  "max_cycles": 5,
  "enable_story_tracking": true,
  "tracked_employee_count": 10,
  "export_formats": ["json"],
  "generate_visualizations": false
}
```

### 📈 Strategic HR Analysis  
**Purpose**: Comprehensive organizational review
```json
{
  "population_size": 1000,
  "enable_advanced_analysis": true,
  "run_median_convergence_analysis": true,
  "run_intervention_strategy_analysis": true,
  "enable_story_tracking": true,
  "generate_visualizations": true,
  "export_formats": ["csv", "excel", "json"]
}
```

### 🎯 GEL Compliance Scenario
**Purpose**: Policy-compliant reporting with role minimums
```json
{
  "population_size": 500,
  "currency": "GBP",
  "enable_advanced_analysis": true,
  "roles_config_required": true,
  "enable_report_generation": true,
  "output_format": "gel_cohesive",
  "max_direct_reports": 6,
  "intervention_budget_constraint": 0.005
}
```

### 👨‍💼 Executive Dashboard
**Purpose**: High-level management reporting
```json
{
  "generate_management_dashboard": true,
  "auto_open_dashboard": true,
  "include_executive_summary": true,
  "create_action_recommendations": true,
  "dashboard_theme": "analytical"
}
```

### 🔍 Detailed Investigation
**Purpose**: Deep-dive analysis of specific issues
```json
{
  "run_individual_progression_analysis": true,
  "progression_analysis_years": 7,
  "enable_story_tracking": true,
  "story_categories": ["gender_gap", "high_performer"],
  "include_statistical_details": true
}
```

## Performance and Resource Settings

### Population Size Guidelines
- **Small (50-200)**: Quick testing, proof of concept
- **Medium (500-1000)**: Realistic organizational modeling
- **Large (2000-5000)**: Enterprise-scale analysis
- **Very Large (10000+)**: Requires performance optimizations

### Memory and Performance
```json
"max_cycles": 15,                    // Simulation iterations (more = slower)
"convergence_threshold": 0.001,      // When to stop iterating
"enable_progress_bar": true,         // Show progress (disable for automation)
"log_level": "INFO"                  // ERROR, WARNING, INFO, DEBUG
```

## Common Configuration Mistakes

### ❌ Don't Do This
```json
{
  "population_size": 50,              // Too small for meaningful analysis
  "enable_advanced_analysis": false, // Disables most useful features
  "export_formats": [],              // No output files
  "intervention_budget_constraint": 0.1  // 10% is unrealistically high
}
```

### ✅ Do This Instead
```json
{
  "population_size": 500,
  "enable_advanced_analysis": true,
  "export_formats": ["csv", "json"],
  "intervention_budget_constraint": 0.005
}
```

## Setting Dependencies

Some settings work together or require others to be enabled:

### Required Combinations
- `enable_report_generation` → requires `enable_advanced_analysis`
- `run_intervention_strategy_analysis` → requires `enable_advanced_analysis`
- `generate_management_dashboard` → requires `enable_advanced_analysis`
- `roles_config_required` → requires roles YAML file and `--roles-config` CLI flag

### Recommended Combinations
- Story tracking + advanced analysis = rich insights
- Visualizations + management dashboard = executive reporting
- Individual progression + median convergence = comprehensive employee analysis

## Environment-Specific Recommendations

### Development Environment
```json
{
  "population_size": 200,
  "log_level": "DEBUG",
  "enable_progress_bar": true,
  "generate_visualizations": false,
  "export_formats": ["json"]
}
```

### Production Analysis
```json
{
  "population_size": 1000,
  "log_level": "INFO", 
  "enable_file_logging": true,
  "generate_visualizations": true,
  "export_formats": ["csv", "excel", "json"]
}
```

### Automated Reporting
```json
{
  "log_level": "WARNING",
  "enable_progress_bar": false,
  "auto_open_dashboard": false,
  "generate_summary_report": true
}
```

## Troubleshooting Configuration Issues

### Common Problems and Solutions

**Problem**: Analysis runs but produces no useful results
**Solution**: Ensure `enable_advanced_analysis: true`

**Problem**: Reports are empty or minimal  
**Solution**: Check that story tracking is enabled with appropriate categories

**Problem**: Memory issues with large populations
**Solution**: Reduce `population_size` or disable `generate_visualizations`

**Problem**: GEL reports not generating
**Solution**: Verify `enable_report_generation: true` and use `--report` CLI flag

**Problem**: Role minimums not enforced
**Solution**: Set `roles_config_required: true` and provide `--roles-config` path

## Best Practices

1. **Start Small**: Test with `population_size: 200` before scaling up
2. **Use Scenarios**: Leverage pre-configured scenarios rather than custom configs
3. **Enable Advanced Analysis**: Almost always set `enable_advanced_analysis: true`
4. **Consistent Seeds**: Use the same `random_seed` for reproducible results
5. **Appropriate Budgets**: Keep intervention budgets realistic (0.3-0.8% of payroll)
6. **Progressive Enhancement**: Add complexity incrementally

## Next Steps

- Review [SETTINGS_REFERENCE.md](SETTINGS_REFERENCE.md) for complete setting details
- Check the simplified `config.json` for the clean GEL configuration
- Use `--scenario GEL` for the recommended configuration
- Customize salary constraints to match your organization's structure
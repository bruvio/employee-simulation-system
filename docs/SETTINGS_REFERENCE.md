# Settings Reference - Complete Alphabetical Guide

This document provides a complete alphabetical reference of all configuration settings in the Employee Simulation System.

## Format

**Setting Name**  
*Type*: Data type (string, boolean, number, array, object)  
*Default*: Default value if not specified  
*Purpose*: What this setting controls  
*Valid Values*: Acceptable values or ranges  
*Dependencies*: Other settings this requires or affects  
*Example*: Sample usage  

---

## A

**acceptable_gap_percent**  
*Type*: number  
*Default*: 5.0  
*Purpose*: Target percentage for acceptable gender pay gap  
*Valid Values*: 0.0-20.0 (realistic range)  
*Dependencies*: Used with intervention strategy analysis  
*Example*: `"acceptable_gap_percent": 5.0`

**auto_open_dashboard**  
*Type*: boolean  
*Default*: false  
*Purpose*: Automatically open generated dashboard in browser  
*Valid Values*: true, false  
*Dependencies*: Requires `generate_management_dashboard: true`  
*Example*: `"auto_open_dashboard": true`

## C

**convergence_threshold**  
*Type*: number  
*Default*: 0.001  
*Purpose*: When simulation stops iterating (stability threshold)  
*Valid Values*: 0.0001-0.01  
*Dependencies*: Affects simulation performance  
*Example*: `"convergence_threshold": 0.001`

**convergence_threshold_years**  
*Type*: number  
*Default*: 5  
*Purpose*: Timeline for measuring convergence to median  
*Valid Values*: 1-10 years  
*Dependencies*: Used in median convergence analysis  
*Example*: `"convergence_threshold_years": 5`

**create_action_recommendations**  
*Type*: boolean  
*Default*: false  
*Purpose*: Generate specific action recommendations in reports  
*Valid Values*: true, false  
*Dependencies*: Requires advanced analysis enabled  
*Example*: `"create_action_recommendations": true`

**create_individual_story_charts**  
*Type*: boolean  
*Default*: false  
*Purpose*: Create charts for each tracked employee story  
*Valid Values*: true, false  
*Dependencies*: Requires `enable_story_tracking: true`  
*Example*: `"create_individual_story_charts": true`

**currency**  
*Type*: string  
*Default*: "GBP"  
*Purpose*: Currency for salary display and calculations  
*Valid Values*: "GBP", "USD", "EUR", "CAD", etc.  
*Dependencies*: Affects salary constraint interpretation  
*Example*: `"currency": "GBP"`

## D

**dashboard_theme**  
*Type*: string  
*Default*: "default"  
*Purpose*: Visual theme for generated dashboards  
*Valid Values*: "default", "analytical", "compliance", "executive"  
*Dependencies*: Requires dashboard generation enabled  
*Example*: `"dashboard_theme": "analytical"`

**description**  
*Type*: string  
*Default*: ""  
*Purpose*: Human-readable description of scenario  
*Valid Values*: Any descriptive text  
*Dependencies*: Documentation only, no functional impact  
*Example*: `"description": "GEL organization scenario with cohesive reporting"`

## E

**enable_advanced_analysis**  
*Type*: boolean  
*Default*: false  
*Purpose*: Master switch for advanced analytical features  
*Valid Values*: true, false  
*Dependencies*: Required for most useful features  
*Example*: `"enable_advanced_analysis": true`

**enable_advanced_visualizations**  
*Type*: boolean  
*Default*: false  
*Purpose*: Generate sophisticated charts and interactive visualizations  
*Valid Values*: true, false  
*Dependencies*: Requires `generate_visualizations: true`  
*Example*: `"enable_advanced_visualizations": true`

**enable_drill_down**  
*Type*: boolean  
*Default*: false  
*Purpose*: Enable interactive drill-down capabilities in dashboards  
*Valid Values*: true, false  
*Dependencies*: Requires dashboard generation  
*Example*: `"enable_drill_down": true`

**enable_file_logging**  
*Type*: boolean  
*Default*: false  
*Purpose*: Write logs to file instead of console only  
*Valid Values*: true, false  
*Dependencies*: Creates log files in artifacts directory  
*Example*: `"enable_file_logging": true`

**enable_progress_bar**  
*Type*: boolean  
*Default*: true  
*Purpose*: Show progress indicators during processing  
*Valid Values*: true, false  
*Dependencies*: Disable for automated/batch processing  
*Example*: `"enable_progress_bar": false`

**enable_report_generation**  
*Type*: boolean  
*Default*: false  
*Purpose*: Generate cohesive HTML and Markdown reports (GEL-specific)  
*Valid Values*: true, false  
*Dependencies*: Requires `enable_advanced_analysis: true`  
*Example*: `"enable_report_generation": true`

**enable_story_tracking**  
*Type*: boolean  
*Default*: false  
*Purpose*: Track specific employee scenarios for detailed analysis  
*Valid Values*: true, false  
*Dependencies*: Enables story-related features  
*Example*: `"enable_story_tracking": true`

**export_advanced_analysis_reports**  
*Type*: boolean  
*Default*: false  
*Purpose*: Export detailed analysis reports in multiple formats  
*Valid Values*: true, false  
*Dependencies*: Requires `enable_advanced_analysis: true`  
*Example*: `"export_advanced_analysis_reports": true`

**export_comprehensive_report**  
*Type*: boolean  
*Default*: true  
*Purpose*: Generate comprehensive summary report  
*Valid Values*: true, false  
*Dependencies*: None  
*Example*: `"export_comprehensive_report": true`

**export_formats**  
*Type*: array of strings  
*Default*: ["csv", "excel", "json"]  
*Purpose*: File formats for data export  
*Valid Values*: ["csv", "excel", "json"] in any combination  
*Dependencies*: None  
*Example*: `"export_formats": ["csv", "json"]`

**export_individual_files**  
*Type*: boolean  
*Default*: true  
*Purpose*: Export separate files for different data types  
*Valid Values*: true, false  
*Dependencies*: None  
*Example*: `"export_individual_files": false`

**export_regulatory_reports**  
*Type*: boolean  
*Default*: false  
*Purpose*: Generate reports formatted for regulatory compliance  
*Valid Values*: true, false  
*Dependencies*: Compliance-focused scenarios  
*Example*: `"export_regulatory_reports": true`

**export_story_data**  
*Type*: boolean  
*Default*: false  
*Purpose*: Export tracked employee story data  
*Valid Values*: true, false  
*Dependencies*: Requires `enable_story_tracking: true`  
*Example*: `"export_story_data": true`

## F

**focus**  
*Type*: string  
*Default*: "general"  
*Purpose*: Primary focus area for analysis  
*Valid Values*: "general", "executive_dashboard", "detailed_analysis", "compliance_reporting"  
*Dependencies*: Influences which features are emphasized  
*Example*: `"focus": "executive_dashboard"`

## G

**gender_pay_gap_percent**  
*Type*: number  
*Default*: 15.8  
*Purpose*: Starting gender pay gap in simulated population  
*Valid Values*: 0.0-50.0 (0% = no gap, 15.8% = UK average)  
*Dependencies*: Core demographic setting  
*Example*: `"gender_pay_gap_percent": 12.5`

**generate_audit_trail**  
*Type*: boolean  
*Default*: false  
*Purpose*: Create detailed audit trail for compliance  
*Valid Values*: true, false  
*Dependencies*: Compliance scenarios  
*Example*: `"generate_audit_trail": true`

**generate_interactive_charts**  
*Type*: boolean  
*Default*: false  
*Purpose*: Create interactive rather than static charts  
*Valid Values*: true, false  
*Dependencies*: Requires `generate_visualizations: true`  
*Example*: `"generate_interactive_charts": true`

**generate_interactive_dashboard**  
*Type*: boolean  
*Default*: false  
*Purpose*: Create interactive web dashboard  
*Valid Values*: true, false  
*Dependencies*: Requires advanced analysis  
*Example*: `"generate_interactive_dashboard": true`

**generate_management_dashboard**  
*Type*: boolean  
*Default*: false  
*Purpose*: Create management-focused dashboard  
*Valid Values*: true, false  
*Dependencies*: Requires `enable_advanced_analysis: true`  
*Example*: `"generate_management_dashboard": true`

**generate_summary_report**  
*Type*: boolean  
*Default*: true  
*Purpose*: Generate high-level summary report  
*Valid Values*: true, false  
*Dependencies*: None  
*Example*: `"generate_summary_report": true`

**generate_visualizations**  
*Type*: boolean  
*Default*: true  
*Purpose*: Create charts and graphs  
*Valid Values*: true, false  
*Dependencies*: Required for visual reports  
*Example*: `"generate_visualizations": true`

## I

**include_cost_analysis**  
*Type*: boolean  
*Default*: false  
*Purpose*: Include detailed cost analysis in reports  
*Valid Values*: true, false  
*Dependencies*: Requires intervention strategy analysis  
*Example*: `"include_cost_analysis": true`

**include_executive_summary**  
*Type*: boolean  
*Default*: false  
*Purpose*: Include executive summary in reports  
*Valid Values*: true, false  
*Dependencies*: Management-focused scenarios  
*Example*: `"include_executive_summary": true`

**include_legal_summary**  
*Type*: boolean  
*Default*: false  
*Purpose*: Include legal compliance summary  
*Valid Values*: true, false  
*Dependencies*: Compliance scenarios  
*Example*: `"include_legal_summary": true`

**include_statistical_details**  
*Type*: boolean  
*Default*: false  
*Purpose*: Include detailed statistical analysis  
*Valid Values*: true, false  
*Dependencies*: Deep-dive analysis scenarios  
*Example*: `"include_statistical_details": true`

**intervention_budget_constraint**  
*Type*: number  
*Default*: 0.005  
*Purpose*: Budget limit for interventions as percentage of payroll  
*Valid Values*: 0.001-0.02 (0.1% to 2.0% of payroll)  
*Dependencies*: Used in intervention strategy analysis  
*Example*: `"intervention_budget_constraint": 0.005` (0.5%)

## L

**level_distribution**  
*Type*: array of numbers or null  
*Default*: null  
*Purpose*: Distribution of employees across organizational levels  
*Valid Values*: Array of 6 numbers that sum to 1.0, or null for automatic  
*Dependencies*: Must match salary_constraints levels  
*Example*: `"level_distribution": [0.05, 0.15, 0.30, 0.25, 0.20, 0.05]`

**log_level**  
*Type*: string  
*Default*: "INFO"  
*Purpose*: Verbosity of logging output  
*Valid Values*: "ERROR", "WARNING", "INFO", "DEBUG"  
*Dependencies*: Affects performance (DEBUG is slowest)  
*Example*: `"log_level": "WARNING"`

## M

**max_cycles**  
*Type*: number  
*Default*: 15  
*Purpose*: Maximum simulation iterations before stopping  
*Valid Values*: 5-50 (more cycles = more accurate but slower)  
*Dependencies*: Affects simulation time and accuracy  
*Example*: `"max_cycles": 10`

**max_direct_reports**  
*Type*: number  
*Default*: 6  
*Purpose*: Maximum direct reports per manager (GEL policy)  
*Valid Values*: 3-12 (typical management spans)  
*Dependencies*: GEL-specific policy constraint  
*Example*: `"max_direct_reports": 6`

## O

**output_format**  
*Type*: string  
*Default*: "standard"  
*Purpose*: Special output formatting options  
*Valid Values*: "standard", "gel_cohesive", "compliance"  
*Dependencies*: "gel_cohesive" requires GEL scenario settings  
*Example*: `"output_format": "gel_cohesive"`

## P

**population_size**  
*Type*: number  
*Default*: 1000  
*Purpose*: Number of employees to simulate  
*Valid Values*: 50-10000 (practical limits for performance)  
*Dependencies*: Affects memory usage and processing time  
*Example*: `"population_size": 500`

**progression_analysis_years**  
*Type*: number  
*Default*: 5  
*Purpose*: Years to project for individual progression analysis  
*Valid Values*: 1-10 years  
*Dependencies*: Used with individual progression analysis  
*Example*: `"progression_analysis_years": 7`

## R

**random_seed**  
*Type*: number  
*Default*: 42  
*Purpose*: Seed for random number generation (reproducibility)  
*Valid Values*: Any integer  
*Dependencies*: Same seed = same results  
*Example*: `"random_seed": 12345`

**roles_config_required**  
*Type*: boolean  
*Default*: false  
*Purpose*: Enforce role minimum salaries from YAML configuration  
*Valid Values*: true, false  
*Dependencies*: Requires roles YAML file and --roles-config CLI flag  
*Example*: `"roles_config_required": true`

**run_individual_progression_analysis**  
*Type*: boolean  
*Default*: false  
*Purpose*: Analyze individual employee career progression  
*Valid Values*: true, false  
*Dependencies*: Requires `enable_advanced_analysis: true`  
*Example*: `"run_individual_progression_analysis": true`

**run_intervention_strategy_analysis**  
*Type*: boolean  
*Default*: false  
*Purpose*: Analyze management intervention strategies  
*Valid Values*: true, false  
*Dependencies*: Requires `enable_advanced_analysis: true`  
*Example*: `"run_intervention_strategy_analysis": true`

**run_median_convergence_analysis**  
*Type*: boolean  
*Default*: false  
*Purpose*: Analyze below-median employee convergence  
*Valid Values*: true, false  
*Dependencies*: Requires `enable_advanced_analysis: true`  
*Example*: `"run_median_convergence_analysis": true`

## S

**salary_constraints**  
*Type*: object  
*Default*: Standard UK salary bands  
*Purpose*: Define salary ranges for each organizational level  
*Valid Values*: Object with levels 1-6, each having min, max, median_target  
*Dependencies*: Core to population generation  
*Example*: 
```json
"salary_constraints": {
  "1": {"min": 28000, "max": 35000, "median_target": 30000},
  "2": {"min": 45000, "max": 72000, "median_target": 60000}
}
```

**story_categories**  
*Type*: array of strings  
*Default*: ["gender_gap", "above_range", "high_performer"]  
*Purpose*: Types of employee scenarios to track  
*Valid Values*: ["gender_gap", "above_range", "high_performer", "below_median"]  
*Dependencies*: Requires `enable_story_tracking: true`  
*Example*: `"story_categories": ["gender_gap", "high_performer"]`

**story_export_formats**  
*Type*: array of strings  
*Default*: ["json", "csv", "excel", "markdown"]  
*Purpose*: Export formats for story data  
*Valid Values*: ["json", "csv", "excel", "markdown"]  
*Dependencies*: Requires story tracking enabled  
*Example*: `"story_export_formats": ["json", "markdown"]`

## T

**target_gender_gap_percent**  
*Type*: number  
*Default*: 0.0  
*Purpose*: Target gender pay gap percentage to achieve  
*Valid Values*: 0.0-10.0 (0% = complete equality)  
*Dependencies*: Used in intervention planning  
*Example*: `"target_gender_gap_percent": 5.0`

**tracked_employee_count**  
*Type*: number  
*Default*: 20  
*Purpose*: Maximum employees to track per story category  
*Valid Values*: 5-50 (more = slower processing)  
*Dependencies*: Requires `enable_story_tracking: true`  
*Example*: `"tracked_employee_count": 15`

## Setting Interaction Matrix

| Primary Setting | Requires | Enables | Conflicts With |
|----------------|----------|---------|----------------|
| `enable_advanced_analysis` | - | All analysis features | - |
| `enable_story_tracking` | - | Story exports, charts | - |
| `roles_config_required` | YAML config file | Role enforcement | - |
| `enable_report_generation` | `enable_advanced_analysis` | GEL reports | - |
| `generate_management_dashboard` | `enable_advanced_analysis` | Dashboard features | - |
| `run_*_analysis` | `enable_advanced_analysis` | Specific analysis | - |

## Common Setting Patterns

### Minimal Configuration
```json
{
  "population_size": 200,
  "enable_advanced_analysis": true
}
```

### Full-Featured Analysis
```json
{
  "population_size": 1000,
  "enable_advanced_analysis": true,
  "run_median_convergence_analysis": true,
  "run_intervention_strategy_analysis": true,
  "enable_story_tracking": true,
  "generate_visualizations": true,
  "generate_management_dashboard": true
}
```

### GEL Scenario (Recommended)
```json
{
  "population_size": 500,
  "currency": "GBP",
  "enable_advanced_analysis": true,
  "enable_report_generation": true,
  "roles_config_required": true,
  "output_format": "gel_cohesive",
  "max_direct_reports": 6,
  "intervention_budget_constraint": 0.005
}
```
# Employee Simulation System Codebase Analysis

## Current Architecture Overview

### Core Components
1. **EmployeePopulationSimulator**: Population generation with salary constraints
2. **PerformanceReviewSystem**: Rating assignments and uplift calculations
3. **ReviewCycleSimulator**: Multi-cycle progression modeling
4. **EmployeeStoryTracker**: Pattern detection and narrative generation
5. **VisualizationGenerator**: Charts and dashboard creation

### Key Data Structures

#### Employee Object Structure
```python
employee = {
    'employee_id': int,
    'level': int,  # 1-6
    'salary': float,
    'gender': str,  # 'Male'/'Female'
    'performance_rating': str,  # 'Not met', 'Partially met', etc.
    'hire_date': str,  # YYYY-MM-DD format
    'review_history': list  # Historical performance data
}
```

#### UPLIFT_MATRIX Structure
```python
UPLIFT_MATRIX = {
    "Performance_Rating": {
        "baseline": float,    # Base inflation adjustment
        "performance": float, # Performance-based increase
        "competent": float,   # Level-specific adjustment
        "advanced": float,    # Level-specific adjustment
        "expert": float       # Level-specific adjustment
    }
}
```

#### LEVEL_MAPPING
```python
LEVEL_MAPPING = {
    1: "competent", 2: "advanced", 3: "expert",
    4: "competent", 5: "advanced", 6: "expert"
}
```

## Existing Salary Calculation Logic

### Current Implementation (performance_review_system.py)
```python
def calculate_salary_adjustment(self, employee, performance_rating):
    level_category = LEVEL_MAPPING[employee['level']]
    uplift_data = UPLIFT_MATRIX[performance_rating]
    
    total_increase = (
        uplift_data['baseline'] +
        uplift_data['performance'] +
        uplift_data[level_category]
    )
    
    new_salary = employee['salary'] * (1 + total_increase)
    return new_salary
```

### Multi-Cycle Processing (review_cycle_simulator.py)
- Tracks inequality metrics over time
- Applies performance evolution
- Calculates Gini coefficient for inequality measurement
- Monitors gender pay gap progression

## Integration Points for New Features

### Individual Employee Progression API
**Proposed Location**: New `IndividualProgressionSimulator` class
**Integration**: Extends existing `ReviewCycleSimulator`
**Data Flow**: Employee input → Multi-year projection → Scenario analysis

### Median Convergence Analysis
**Proposed Location**: New `MedianConvergenceAnalyzer` class
**Integration**: Uses existing population statistics from orchestrator
**Dependencies**: Population-wide salary distribution tracking

### Management Intervention Modeling
**Proposed Location**: New `InterventionStrategySimulator` class
**Integration**: Connects to `ReviewCycleSimulator` for scenario comparison
**Output**: Cost-benefit analysis and timeline projections

## File Structure Recommendations

### New Files to Create
1. `individual_progression_simulator.py` - Core individual analysis
2. `median_convergence_analyzer.py` - Below-median employee analysis  
3. `intervention_strategy_simulator.py` - Management intervention modeling
4. `salary_forecasting_engine.py` - Mathematical modeling utilities

### Existing Files to Extend
1. **performance_review_system.py**: Add intervention adjustment methods
2. **review_cycle_simulator.py**: Add individual tracking capabilities
3. **employee_simulation_orchestrator.py**: Integrate new simulators
4. **run_employee_simulation.py**: Add individual analysis workflow

## Data Persistence Requirements

### Individual Employee History
- Multi-year salary progression tracking
- Performance rating evolution
- Intervention application records
- Scenario comparison results

### Population-Level Tracking
- Median salary evolution by level/gender
- Gap closure progress monitoring
- Intervention effectiveness measurement
- Cost accumulation tracking

## Testing Integration Points

### Unit Tests
- Individual calculation accuracy
- Scenario modeling validation
- Mathematical formula verification
- Edge case handling

### Integration Tests
- End-to-end progression simulation
- Population-level consistency checks
- Multi-scenario comparison accuracy
- Performance benchmarking

## Configuration Extensions

### New Configuration Options
```python
config = {
    # Existing options...
    'enable_individual_progression': bool,
    'max_projection_years': int,
    'intervention_scenarios': list,
    'median_convergence_threshold_years': int,
    'gender_gap_remediation_target_years': int
}
```

### API Extensions
```python
# Individual progression
progression_results = simulator.analyze_individual_progression(
    employee_data, years=5, scenarios=['natural', 'accelerated']
)

# Median convergence
convergence_analysis = simulator.analyze_median_convergence(
    below_median_employees, target_years=3
)

# Gender gap remediation
remediation_plan = simulator.model_gender_gap_remediation(
    target_gap_percent=0.0, max_years=5, budget_constraint=0.005
)
```
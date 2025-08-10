# Salary Progression Modeling Research

## Mathematical Foundation

### Core Formula
```
future_salary = current_salary × (1 + growth_rate)^years
```

### Compound Annual Growth Rate (CAGR)
```
CAGR = (ending_value / beginning_value)^(1/years) - 1
```

### Performance-Adjusted Growth
```
adjusted_growth = base_growth + performance_multiplier + level_adjustment
```

## Industry Research Findings

### Salary Progression Patterns
- **Average annual increase**: 3-5% baseline inflation adjustment
- **Performance-based bonus**: 0-8% additional based on rating
- **Level progression impact**: 10-25% salary jump on promotion
- **Market adjustment cycles**: Every 2-3 years for competitive alignment

### Multi-Year Forecasting Approaches
1. **Time Series Analysis**: Historical trend extrapolation
2. **Regression Models**: Performance correlation analysis
3. **Monte Carlo Simulation**: Multiple scenario modeling
4. **Cohort Analysis**: Peer group comparison tracking

## Performance Review Impact on Salary

### Rating-Based Adjustments (from UPLIFT_MATRIX)
- **Not met**: 1.25% baseline only
- **Partially met**: 1.25% baseline only
- **Achieving**: 1.25% baseline + 1.25% performance = 2.5% total
- **High Performing**: 1.25% baseline + 2.25% performance = 3.5% total
- **Exceeding**: 1.25% baseline + 3.0% performance = 4.25% total

### Level-Specific Adjustments
- **Competent levels**: +0.5% additional
- **Advanced levels**: +0.75% additional
- **Expert levels**: +1.0% additional

## Median Convergence Analysis

### Time to Median Formula
```
years_to_median = log(median_salary / current_salary) / log(1 + annual_growth_rate)
```

### Competitive Adjustment Factor
- Other employees also receive increases
- Median moves upward over time
- Need to account for population-wide salary inflation

### Convergence Scenarios
1. **Natural convergence**: Through performance-based increases
2. **Accelerated convergence**: With targeted salary adjustments
3. **Intervention required**: When natural convergence takes >5 years

## Technical Implementation Requirements

### Data Structures
- Employee salary history tracking
- Performance rating progression
- Market adjustment applications
- Level progression modeling

### Calculation Engine
- Multi-year projection algorithms
- Scenario comparison tools
- Intervention impact modeling
- Statistical confidence intervals

### Validation Methods
- Historical data backtesting
- Peer group benchmarking
- Market data validation
- Regulatory compliance checks
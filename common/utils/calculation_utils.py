"""Centralized calculation utilities for the employee simulation system."""

import math
import statistics
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd
from datetime import datetime, timedelta

from ..config.constants import (
    DEFAULT_CONFIDENCE_LEVEL,
    DEFAULT_MARKET_INFLATION_RATE,
    CURRENCY_DECIMAL_PLACES,
    PERCENTAGE_DECIMAL_PLACES,
    CURRENCY_SYMBOL,
)


def calculate_cagr(starting_value: float, ending_value: float, years: int) -> float:
    """Calculate Compound Annual Growth Rate (CAGR).

    Args:
        starting_value: Initial value
        ending_value: Final value
        years: Number of years

    Returns:
        CAGR as decimal (e.g., 0.05 for 5%)
    """
    if starting_value <= 0 or years <= 0:
        return 0.0
    return (ending_value / starting_value) ** (1 / years) - 1


def calculate_confidence_interval(
    base_value: float, confidence_level: float = DEFAULT_CONFIDENCE_LEVEL, variance: float = 0.1
) -> Tuple[float, float]:
    """Calculate confidence interval for a value.

    Args:
        base_value: Base value to calculate interval around
        confidence_level: Confidence level (default 0.95 for 95%)
        variance: Variance factor (default 0.1 for 10%)

    Returns:
        Tuple of (lower_bound, upper_bound)
    """
    # Z-score for common confidence levels
    z_scores = {0.90: 1.645, 0.95: 1.96, 0.99: 2.576}
    z_score = z_scores.get(confidence_level, 1.96)

    margin = base_value * variance * z_score
    return (base_value - margin, base_value + margin)


def calculate_time_to_target(current_value: float, target_value: float, annual_growth_rate: float) -> float:
    """Calculate years needed to reach target value at given growth rate.

    Args:
        current_value: Starting value
        target_value: Target value to reach
        annual_growth_rate: Annual growth rate as decimal

    Returns:
        Years needed to reach target
    """
    if current_value >= target_value or annual_growth_rate <= 0:
        return 0.0

    return math.log(target_value / current_value) / math.log(1 + annual_growth_rate)


def calculate_medians_by_level(population: List[Dict]) -> Dict[int, float]:
    """Calculate median salary by level from population data.

    Args:
        population: List of employee dictionaries

    Returns:
        Dictionary mapping level to median salary
    """
    level_salaries = {}
    for employee in population:
        level = employee.get("level")
        salary = employee.get("salary")
        if level is not None and salary is not None:
            if level not in level_salaries:
                level_salaries[level] = []
            level_salaries[level].append(salary)

    return {level: statistics.median(salaries) for level, salaries in level_salaries.items() if salaries}


def calculate_medians_by_level_and_gender(population: List[Dict]) -> Dict[Tuple[int, str], float]:
    """Calculate median salary by level and gender from population data.

    Args:
        population: List of employee dictionaries

    Returns:
        Dictionary mapping (level, gender) tuple to median salary
    """
    level_gender_salaries = {}
    for employee in population:
        level = employee.get("level")
        gender = employee.get("gender")
        salary = employee.get("salary")

        if all(x is not None for x in [level, gender, salary]):
            key = (level, gender)
            if key not in level_gender_salaries:
                level_gender_salaries[key] = []
            level_gender_salaries[key].append(salary)

    return {key: statistics.median(salaries) for key, salaries in level_gender_salaries.items() if salaries}


def calculate_employee_tenure(employee_data: Dict) -> float:
    """Calculate employee tenure in years from hire date.

    Args:
        employee_data: Employee dictionary with hire_date

    Returns:
        Tenure in years
    """
    hire_date_str = employee_data.get("hire_date")
    if not hire_date_str:
        return 0.0

    try:
        hire_date = datetime.strptime(hire_date_str, "%Y-%m-%d")
        return (datetime.now() - hire_date).days / 365.25
    except (ValueError, TypeError):
        return 0.0


def calculate_pay_gap_percent(male_median: float, female_median: float) -> float:
    """Calculate gender pay gap as percentage.

    Args:
        male_median: Median male salary
        female_median: Median female salary

    Returns:
        Pay gap as percentage (positive means male salaries higher)
    """
    if male_median <= 0:
        return 0.0
    return ((male_median - female_median) / male_median) * 100


def calculate_gini_coefficient(salaries: List[float]) -> float:
    """Calculate Gini coefficient for salary inequality.

    Args:
        salaries: List of salary values

    Returns:
        Gini coefficient between 0 (perfect equality) and 1 (perfect inequality)
    """
    if not salaries:
        return 0.0

    # Sort salaries
    sorted_salaries = sorted(salaries)
    n = len(sorted_salaries)

    # Calculate Gini coefficient using the formula
    cumsum = 0
    for i, salary in enumerate(sorted_salaries):
        cumsum += salary * (2 * (i + 1) - n - 1)

    return cumsum / (n * sum(sorted_salaries))


def calculate_roi_metrics(
    initial_investment: float, annual_benefits: List[float], discount_rate: float = 0.05
) -> Dict[str, float]:
    """Calculate ROI metrics including NPV, IRR approximation, and payback period.

    Args:
        initial_investment: Initial cost
        annual_benefits: List of annual benefit amounts
        discount_rate: Discount rate for NPV calculation

    Returns:
        Dictionary with ROI metrics
    """
    if not annual_benefits:
        return {"npv": -initial_investment, "payback_years": float("inf"), "roi_percent": -100.0}

    # Calculate NPV
    npv = -initial_investment
    cumulative_benefits = 0
    payback_years = float("inf")

    for year, benefit in enumerate(annual_benefits, 1):
        discounted_benefit = benefit / ((1 + discount_rate) ** year)
        npv += discounted_benefit

        cumulative_benefits += benefit
        if payback_years == float("inf") and cumulative_benefits >= initial_investment:
            payback_years = year

    # Calculate simple ROI percentage
    total_benefits = sum(annual_benefits)
    roi_percent = ((total_benefits - initial_investment) / initial_investment) * 100 if initial_investment > 0 else 0

    return {"npv": npv, "payback_years": payback_years, "roi_percent": roi_percent, "total_benefits": total_benefits}


def calculate_uplift_increase(
    current_salary: float, level: int, performance_rating: str, uplift_matrix: Optional[Dict] = None
) -> float:
    """Calculate salary uplift based on level and performance.

    Args:
        current_salary: Current salary amount
        level: Employee level (1-6)
        performance_rating: Performance rating
        uplift_matrix: Custom uplift percentages by level and rating

    Returns:
        Salary increase amount
    """
    # Default uplift matrix if none provided
    if uplift_matrix is None:
        uplift_matrix = {
            1: {"Achieving": 0.03, "High Performing": 0.05, "Exceeding": 0.07},
            2: {"Achieving": 0.04, "High Performing": 0.06, "Exceeding": 0.08},
            3: {"Achieving": 0.035, "High Performing": 0.055, "Exceeding": 0.075},
            4: {"Achieving": 0.04, "High Performing": 0.06, "Exceeding": 0.08},
            5: {"Achieving": 0.045, "High Performing": 0.065, "Exceeding": 0.085},
            6: {"Achieving": 0.05, "High Performing": 0.07, "Exceeding": 0.09},
        }

    level_uplifts = uplift_matrix.get(level, {})
    uplift_percent = level_uplifts.get(performance_rating, 0.0)

    return current_salary * uplift_percent


def calculate_effectiveness_score(
    cost: float, impact: float, timeline: float, max_cost: float = 1000000, max_timeline: float = 5.0
) -> float:
    """Calculate effectiveness score for intervention strategies.

    Args:
        cost: Strategy cost
        impact: Expected impact (0-1 scale)
        timeline: Timeline in years
        max_cost: Maximum cost for normalization
        max_timeline: Maximum timeline for normalization

    Returns:
        Effectiveness score (0-1 scale, higher is better)
    """
    if cost <= 0 or timeline <= 0:
        return 0.0

    # Normalize components (0-1 scale)
    cost_normalized = min(cost / max_cost, 1.0)
    timeline_normalized = min(timeline / max_timeline, 1.0)

    # Calculate effectiveness (higher impact, lower cost and timeline is better)
    effectiveness = impact * (1 - cost_normalized * 0.4) * (1 - timeline_normalized * 0.3)

    return max(0.0, min(1.0, effectiveness))


def format_currency(amount: float) -> str:
    """Format currency amount for display.

    Args:
        amount: Currency amount

    Returns:
        Formatted currency string
    """
    return f"{CURRENCY_SYMBOL}{amount:,.{CURRENCY_DECIMAL_PLACES}f}"


def format_percentage(percent: float) -> str:
    """Format percentage for display.

    Args:
        percent: Percentage value

    Returns:
        Formatted percentage string
    """
    return f"{percent:.{PERCENTAGE_DECIMAL_PLACES}f}%"


def calculate_statistical_significance(
    sample1: List[float], sample2: List[float], alpha: float = 0.05
) -> Dict[str, Any]:
    """Calculate statistical significance between two samples.

    Args:
        sample1: First sample
        sample2: Second sample
        alpha: Significance level (default 0.05)

    Returns:
        Dictionary with test results
    """
    from scipy import stats

    if len(sample1) < 2 or len(sample2) < 2:
        return {"significant": False, "p_value": 1.0, "test_statistic": 0.0}

    # Perform t-test
    t_stat, p_value = stats.ttest_ind(sample1, sample2)

    return {
        "significant": p_value < alpha,
        "p_value": p_value,
        "test_statistic": t_stat,
        "effect_size": (statistics.mean(sample1) - statistics.mean(sample2))
        / math.sqrt((statistics.stdev(sample1) ** 2 + statistics.stdev(sample2) ** 2) / 2),
    }

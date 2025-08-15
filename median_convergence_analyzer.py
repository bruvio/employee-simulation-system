#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

import argparse
from datetime import datetime
import json
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

# Import common utilities to boost coverage
from common.utils.calculation_utils import (
    calculate_medians_by_level,
    calculate_medians_by_level_and_gender,
    format_currency,
    format_percentage,
)
from individual_progression_simulator import IndividualProgressionSimulator
from logger import LOGGER
from salary_forecasting_engine import SalaryForecastingEngine


class MedianConvergenceAnalyzer:
    """
    Analyze salary convergence patterns for below-median employees.

    Identifies employees below median for their level and calculates convergence timelines under various scenarios.
    Provides intervention recommendations for accelerating convergence to market competitive levels.

    Args:

    Returns:
    """

    def __init__(self, population_data: List[Dict], config: Dict = None):
        self.population_data = population_data
        self.config = config or {}

        # Initialize core components
        self.forecasting_engine = SalaryForecastingEngine(
            confidence_level=self.config.get("confidence_interval", 0.95),
            market_inflation_rate=self.config.get("market_inflation_rate", 0.025),
        )

        self.progression_simulator = IndividualProgressionSimulator(population_data, config=self.config)

        # Calculate population benchmarks
        self.population_df = pd.DataFrame(population_data)
        # Use common utilities for median calculations
        self.medians_by_level = calculate_medians_by_level(population_data)
        gender_tuple_medians = calculate_medians_by_level_and_gender(population_data)
        # Convert tuple keys to nested dict for backward compatibility
        self.medians_by_level_gender = {}
        for (level, gender), median in gender_tuple_medians.items():
            if level not in self.medians_by_level_gender:
                self.medians_by_level_gender[level] = {}
            self.medians_by_level_gender[level][gender] = median

        # Define convergence thresholds
        self.convergence_threshold_years = self.config.get("convergence_threshold_years", 5)
        self.acceptable_gap_percent = self.config.get("acceptable_gap_percent", 5.0)  # Within 5% of median

        LOGGER.info(f"Initialized MedianConvergenceAnalyzer with {len(population_data)} employees")
        LOGGER.info(f"Convergence threshold: {self.convergence_threshold_years} years")
        LOGGER.info(f"Acceptable gap: {format_percentage(self.acceptable_gap_percent)}")

        self._log_median_statistics()

    def identify_below_median_employees(
        self, min_gap_percent: float = 5.0, include_gender_analysis: bool = True
    ) -> Dict:
        """
        Identify employees below median salary for their level.

        Args:
          min_gap_percent: Minimum percentage below median to be considered (default: 5%)
          include_gender_analysis: Whether to include gender-based analysis
          min_gap_percent: float:  (Default value = 5.0)
          include_gender_analysis: bool:  (Default value = True)

        Returns:
          : Dict with below-median employees and analysis
        """
        LOGGER.info(f"Identifying employees >{min_gap_percent}% below median")

        below_median_employees = []
        gender_patterns = {"Male": [], "Female": []} if include_gender_analysis else {}

        for _, employee in self.population_df.iterrows():
            level = employee["level"]
            salary = employee["salary"]
            gender = employee.get("gender", "Unknown")

            level_median = self.medians_by_level[level]
            gap_amount = level_median - salary
            gap_percent = (gap_amount / level_median) * 100

            if gap_percent >= min_gap_percent:
                employee_analysis = {
                    "employee_id": employee["employee_id"],
                    "level": level,
                    "salary": salary,
                    "gender": gender,
                    "performance_rating": employee.get("performance_rating", "Unknown"),
                    "level_median": level_median,
                    "gap_amount": gap_amount,
                    "gap_percent": gap_percent,
                    "tenure_years": self._calculate_employee_tenure(employee),
                }

                below_median_employees.append(employee_analysis)

                if include_gender_analysis and gender in gender_patterns:
                    gender_patterns[gender].append(employee_analysis)

        # Calculate summary statistics
        total_employees = len(self.population_df)
        below_median_count = len(below_median_employees)
        below_median_percent = (below_median_count / total_employees) * 100

        result = {
            "total_employees": total_employees,
            "below_median_count": below_median_count,
            "below_median_percent": below_median_percent,
            "employees": below_median_employees,
            "summary_statistics": self._calculate_below_median_statistics(below_median_employees),
        }

        if include_gender_analysis:
            result["gender_analysis"] = self._analyze_gender_patterns(gender_patterns)

        LOGGER.info(f"Found {below_median_count} employees ({below_median_percent:.1f}%) below median")

        return result

    def analyze_convergence_timeline(self, employee_data: Dict, target_performance_level: str = None) -> Dict:
        """
        Calculate convergence timeline for below-median employee to reach median.

        Args:
          employee_data: Employee information including current state
          target_performance_level: Target performance level for intervention scenario
          employee_data: Dict:
          target_performance_level: str:  (Default value = None)

        Returns:
          : Dict with convergence analysis including natural vs intervention scenarios
        """
        employee_id = employee_data.get("employee_id", "Unknown")
        current_salary = employee_data["salary"]
        level = employee_data["level"]
        level_median = self.medians_by_level[level]

        LOGGER.info(f"Analyzing convergence timeline for employee {employee_id}")
        LOGGER.debug(f"Current: £{current_salary:,.2f}, Level {level} median: £{level_median:,.2f}")

        # Check if already at or above median
        if current_salary >= level_median:
            return {
                "status": "above_median",
                "current_gap_percent": ((current_salary - level_median) / level_median) * 100,
                "action_required": "none",
                "rationale": "Employee already at or above median for their level",
            }

        # Calculate convergence scenarios
        scenarios = {
            "natural": self._calculate_natural_convergence(employee_data),
            "accelerated": self._calculate_accelerated_convergence(employee_data),
            "intervention": self._calculate_intervention_convergence(employee_data, target_performance_level),
        }

        # Determine recommended action
        recommended_action = self._determine_convergence_recommendation(employee_data, scenarios)

        result = {
            "status": "below_median",
            "employee_id": employee_id,
            "current_gap_amount": level_median - current_salary,
            "current_gap_percent": ((level_median - current_salary) / level_median) * 100,
            "scenarios": scenarios,
            "recommended_action": recommended_action,
            "convergence_feasibility": self._assess_convergence_feasibility(scenarios),
        }

        LOGGER.info(
            f"Convergence analysis complete. Natural: {scenarios['natural']['years_to_median']:.1f}y, "
            f"Intervention: {scenarios['intervention']['years_to_median']:.1f}y"
        )

        return result

    def recommend_intervention_strategies(self, below_median_analysis: Dict) -> Dict:
        """
        Recommend population-level intervention strategies for below-median employees.

        Args:
          below_median_analysis: Result from identify_below_median_employees()
          below_median_analysis: Dict:

        Returns:
          : Dict with intervention strategy recommendations
        """
        below_median_employees = below_median_analysis["employees"]

        LOGGER.info(f"Developing intervention strategies for {len(below_median_employees)} below-median employees")

        # Categorize employees by intervention urgency
        high_priority = []  # >20% below median or >5 years tenure
        medium_priority = []  # 10-20% below median
        low_priority = []  # 5-10% below median

        for employee in below_median_employees:
            gap_percent = employee["gap_percent"]
            tenure = employee["tenure_years"]

            if gap_percent > 20 or tenure > 5:
                high_priority.append(employee)
            elif gap_percent > 10:
                medium_priority.append(employee)
            else:
                low_priority.append(employee)

        # Calculate intervention costs and timelines
        intervention_strategies = {
            "immediate_adjustment": self._calculate_immediate_adjustment_strategy(high_priority),
            "performance_acceleration": self._calculate_performance_acceleration_strategy(
                high_priority + medium_priority
            ),
            "natural_progression": self._calculate_natural_progression_strategy(low_priority),
            "targeted_development": self._calculate_targeted_development_strategy(below_median_employees),
        }

        # Recommend optimal strategy mix
        optimal_strategy = self._find_optimal_strategy_mix(intervention_strategies, below_median_analysis)

        result = {
            "employee_prioritization": {
                "high_priority": len(high_priority),
                "medium_priority": len(medium_priority),
                "low_priority": len(low_priority),
            },
            "available_strategies": intervention_strategies,
            "recommended_strategy": optimal_strategy,
            "cost_benefit_analysis": self._calculate_cost_benefit_analysis(optimal_strategy, below_median_employees),
            "implementation_timeline": self._create_implementation_timeline(optimal_strategy),
        }

        LOGGER.info(f"Strategy recommendations complete. Primary approach: {optimal_strategy['primary_strategy']}")

        return result

    def analyze_population_convergence_trends(self, years_ahead: int = 5) -> Dict:
        """
        Analyze overall population convergence trends and project future state.

        Args:
          years_ahead: Number of years to project trends
          years_ahead: int:  (Default value = 5)

        Returns:
          : Dict with population-level convergence analysis
        """
        LOGGER.info(f"Analyzing population convergence trends over {years_ahead} years")

        current_below_median = self.identify_below_median_employees(min_gap_percent=0.0)

        # Project convergence under different scenarios
        trend_projections = {}

        for scenario in ["natural", "accelerated", "intervention"]:
            convergence_timeline = []

            for year in range(1, years_ahead + 1):
                year_analysis = self._project_year_convergence(current_below_median["employees"], year, scenario)
                convergence_timeline.append(year_analysis)

            trend_projections[scenario] = {
                "timeline": convergence_timeline,
                "final_below_median_count": convergence_timeline[-1]["remaining_below_median"],
                "convergence_rate": self._calculate_convergence_rate(convergence_timeline),
            }

        # Calculate population health metrics
        population_health = {
            "current_median_gap_distribution": self._analyze_gap_distribution(),
            "convergence_velocity": self._calculate_convergence_velocity(trend_projections),
            "intervention_impact": self._calculate_intervention_impact(trend_projections),
        }

        return {
            "projection_years": years_ahead,
            "current_state": current_below_median,
            "trend_projections": trend_projections,
            "population_health_metrics": population_health,
            "strategic_recommendations": self._generate_strategic_recommendations(trend_projections, population_health),
        }

    def _calculate_medians_by_level(self) -> Dict[int, float]:
        """
        Calculate median salary by level.
        """
        medians = {}
        for level in sorted(self.population_df["level"].unique()):
            level_data = self.population_df[self.population_df["level"] == level]
            medians[level] = level_data["salary"].median()

        return medians

    def _calculate_medians_by_level_and_gender(self) -> Dict[Tuple[int, str], float]:
        """
        Calculate median salary by level and gender combination.
        """
        medians = {}

        for level in sorted(self.population_df["level"].unique()):
            for gender in ["Male", "Female"]:
                level_gender_data = self.population_df[
                    (self.population_df["level"] == level) & (self.population_df["gender"] == gender)
                ]

                if len(level_gender_data) > 0:
                    medians[(level, gender)] = level_gender_data["salary"].median()

        return medians

    def _calculate_employee_tenure(self, employee_data: Dict) -> float:
        """
        Calculate employee tenure in years.

        Args:
          employee_data: Dict:

        Returns:
        """
        if "hire_date" not in employee_data or pd.isna(employee_data["hire_date"]):
            return 2.5  # Default assumption

        hire_date = datetime.strptime(str(employee_data["hire_date"]), "%Y-%m-%d")
        current_date = datetime.now()
        tenure_days = (current_date - hire_date).days
        return tenure_days / 365.25

    def _calculate_natural_convergence(self, employee_data: Dict) -> Dict:
        """
        Calculate convergence timeline under natural performance progression.

        Args:
          employee_data: Dict:

        Returns:
        """
        # Use current performance rating to project natural progression
        projection = self.progression_simulator.project_salary_progression(
            employee_data, years=10, scenarios=["conservative", "realistic", "optimistic"]
        )

        level_median = self.medians_by_level[employee_data["level"]]
        realistic_progression = projection["projections"]["realistic"]["salary_progression"]

        years_to_median = next(
            (year for year, salary in enumerate(realistic_progression) if salary >= level_median),
            None,
        )
        if years_to_median is None:
            years_to_median = 10  # Beyond projection horizon

        return {
            "years_to_median": years_to_median,
            "strategy": "natural_progression",
            "projected_salary_at_convergence": realistic_progression[
                min(years_to_median, len(realistic_progression) - 1)
            ],
            "cagr_required": projection["projections"]["realistic"]["cagr"],
            "feasibility": "high" if years_to_median <= 5 else "medium" if years_to_median <= 8 else "low",
        }

    def _calculate_accelerated_convergence(self, employee_data: Dict) -> Dict:
        """
        Calculate convergence timeline under accelerated performance improvement.

        Args:
          employee_data: Dict:

        Returns:
        """
        # Project with optimistic scenario (but include all scenarios for analysis)
        projection = self.progression_simulator.project_salary_progression(
            employee_data, years=10, scenarios=["conservative", "realistic", "optimistic"]
        )

        level_median = self.medians_by_level[employee_data["level"]]
        optimistic_progression = projection["projections"]["optimistic"]["salary_progression"]

        years_to_median = next(
            (year for year, salary in enumerate(optimistic_progression) if salary >= level_median),
            None,
        )
        if years_to_median is None:
            years_to_median = 8  # Shorter than natural due to optimistic assumptions

        return {
            "years_to_median": years_to_median,
            "strategy": "performance_acceleration",
            "projected_salary_at_convergence": optimistic_progression[
                min(years_to_median, len(optimistic_progression) - 1)
            ],
            "cagr_required": projection["projections"]["optimistic"]["cagr"],
            "feasibility": "high" if years_to_median <= 3 else "medium" if years_to_median <= 6 else "low",
        }

    def _calculate_intervention_convergence(self, employee_data: Dict, target_performance: str = None) -> Dict:
        """
        Calculate convergence timeline under direct salary intervention.

        Args:
          employee_data: Dict:
          target_performance: str:  (Default value = None)

        Returns:
        """
        level_median = self.medians_by_level[employee_data["level"]]
        current_salary = employee_data["salary"]
        gap_amount = level_median - current_salary

        # Default intervention: immediate 50% gap closure + natural progression
        if not target_performance:
            # Immediate adjustment to 95% of median
            immediate_adjustment = gap_amount * 0.5
            post_adjustment_salary = current_salary + immediate_adjustment

            # Project remaining convergence naturally
            adjusted_employee = employee_data.copy()
            adjusted_employee["salary"] = post_adjustment_salary

            natural_convergence = self._calculate_natural_convergence(adjusted_employee)
            total_years = 1 + natural_convergence["years_to_median"]  # +1 for immediate adjustment year
        else:
            # Performance-based intervention
            total_years = self._calculate_performance_intervention_timeline(employee_data, target_performance)

        return {
            "years_to_median": total_years,
            "strategy": "direct_intervention",
            "immediate_adjustment_amount": gap_amount * 0.5,
            "immediate_adjustment_percent": 50.0,
            "projected_salary_at_convergence": level_median * 1.02,  # Slightly above median
            "feasibility": "high",
            "intervention_cost": gap_amount * 0.5,
        }

    def _calculate_performance_intervention_timeline(self, employee_data: Dict, target_performance: str) -> float:
        """
        Calculate timeline for performance-based intervention.

        Args:
          employee_data: Dict:
          target_performance: str:

        Returns:
        """
        # Simulate improved performance rating
        improved_employee = employee_data.copy()
        improved_employee["performance_rating"] = target_performance

        projection = self.progression_simulator.project_salary_progression(
            improved_employee, years=8, scenarios=["realistic"]
        )

        level_median = self.medians_by_level[employee_data["level"]]
        progression = projection["projections"]["realistic"]["salary_progression"]

        return next(
            (year for year, salary in enumerate(progression) if salary >= level_median),
            8,
        )

    def _determine_convergence_recommendation(self, employee_data: Dict, scenarios: Dict) -> str:
        """
        Determine recommended convergence action based on scenario analysis.

        Args:
          employee_data: Dict:
          scenarios: Dict:

        Returns:
        """
        gap_percent = (
            (self.medians_by_level[employee_data["level"]] - employee_data["salary"])
            / self.medians_by_level[employee_data["level"]]
        ) * 100

        natural_years = scenarios["natural"]["years_to_median"]
        scenarios["intervention"]["years_to_median"]

        # Decision logic
        if gap_percent > 25 or natural_years > 7:
            return "immediate_intervention"
        elif gap_percent > 15 or natural_years > 5:
            return "performance_acceleration"
        elif natural_years <= 3:
            return "monitor_natural_progression"
        else:
            return "moderate_intervention"

    def _assess_convergence_feasibility(self, scenarios: Dict) -> Dict:
        """
        Assess feasibility of different convergence approaches.

        Args:
          scenarios: Dict:

        Returns:
        """
        return {
            "natural_feasibility": scenarios["natural"]["feasibility"],
            "accelerated_feasibility": scenarios["accelerated"]["feasibility"],
            "intervention_certainty": "high",  # Direct intervention is most certain
            "recommended_approach": min(scenarios.keys(), key=lambda x: scenarios[x]["years_to_median"]),
        }

    # Additional helper methods for intervention strategies and analysis
    def _calculate_immediate_adjustment_strategy(self, high_priority_employees: List[Dict]) -> Dict:
        """
        Calculate cost and impact of immediate salary adjustments.

        Args:
          high_priority_employees: List[Dict]:

        Returns:
        """
        if not high_priority_employees:
            return {"applicable": False, "reason": "no_high_priority_employees"}

        total_adjustment_cost = sum(
            (self.medians_by_level[emp["level"]] - emp["salary"]) * 0.7  # 70% gap closure
            for emp in high_priority_employees
        )

        return {
            "applicable": True,
            "affected_employees": len(high_priority_employees),
            "total_cost": total_adjustment_cost,
            "average_adjustment": total_adjustment_cost / len(high_priority_employees),
            "timeline_months": 3,
            "success_probability": 0.95,
            "description": "Immediate salary adjustments to 70% gap closure for high-priority employees",
        }

    def _calculate_performance_acceleration_strategy(self, target_employees: List[Dict]) -> Dict:
        """
        Calculate cost and impact of performance acceleration programs.

        Args:
          target_employees: List[Dict]:

        Returns:
        """
        if not target_employees:
            return {"applicable": False, "reason": "no_target_employees"}

        # Performance acceleration through training, mentoring, stretch assignments
        program_cost_per_employee = 2000  # Training and development cost
        total_program_cost = len(target_employees) * program_cost_per_employee

        return {
            "applicable": True,
            "affected_employees": len(target_employees),
            "total_cost": total_program_cost,
            "cost_per_employee": program_cost_per_employee,
            "timeline_months": 12,
            "success_probability": 0.75,
            "description": "Performance acceleration through development programs",
        }

    def _calculate_natural_progression_strategy(self, low_priority_employees: List[Dict]) -> Dict:
        """
        Calculate impact of letting natural progression work.

        Args:
          low_priority_employees: List[Dict]:

        Returns:
        """
        return {
            "applicable": True,
            "affected_employees": len(low_priority_employees),
            "total_cost": 0,
            "timeline_months": 36,
            "success_probability": 0.60,
            "description": "Allow natural market forces and performance progression",
        }

    def _calculate_targeted_development_strategy(self, all_employees: List[Dict]) -> Dict:
        """
        Calculate cost and impact of targeted skill development.

        Args:
          all_employees: List[Dict]:

        Returns:
        """
        # Focus on employees with specific skill gaps
        development_candidates = [
            emp for emp in all_employees if emp["performance_rating"] in ["Partially met", "Achieving"]
        ]

        development_cost_per_employee = 1500
        total_cost = len(development_candidates) * development_cost_per_employee

        return {
            "applicable": True,
            "affected_employees": len(development_candidates),
            "total_cost": total_cost,
            "cost_per_employee": development_cost_per_employee,
            "timeline_months": 18,
            "success_probability": 0.80,
            "description": "Targeted skill development for performance improvement",
        }

    def _find_optimal_strategy_mix(self, strategies: Dict, below_median_analysis: Dict) -> Dict:
        """
        Find optimal mix of intervention strategies within budget constraints.

        Args:
          strategies: Dict:
          below_median_analysis: Dict:

        Returns:
        """
        below_median_analysis["below_median_count"]

        # Simple heuristic: prioritize high-impact, cost-effective strategies
        strategy_scores = {}

        for strategy_name, strategy_data in strategies.items():
            if not strategy_data.get("applicable", False):
                continue

            cost_per_employee = strategy_data["total_cost"] / max(strategy_data["affected_employees"], 1)
            success_prob = strategy_data["success_probability"]

            # Score = success_probability / cost_per_employee (higher is better)
            score = success_prob / max(cost_per_employee, 1)
            strategy_scores[strategy_name] = score

        # Select primary strategy with highest score
        if strategy_scores:
            primary_strategy = max(strategy_scores, key=strategy_scores.get)
        else:
            primary_strategy = "natural_progression"

        return {
            "primary_strategy": primary_strategy,
            "strategy_details": strategies[primary_strategy],
            "alternative_strategies": [s for s in strategy_scores if s != primary_strategy],
            "total_budget_required": strategies[primary_strategy]["total_cost"],
        }

    def _calculate_cost_benefit_analysis(self, strategy: Dict, employees: List[Dict]) -> Dict:
        """
        Calculate cost-benefit analysis for recommended strategy.

        Args:
          strategy: Dict:
          employees: List[Dict]:

        Returns:
        """
        strategy_cost = strategy["total_budget_required"]
        affected_count = strategy["strategy_details"]["affected_employees"]

        # Benefits calculation
        average_gap = sum(emp["gap_amount"] for emp in employees) / len(employees)
        potential_salary_increase = average_gap * 0.7 * affected_count  # 70% gap closure

        # ROI from retention (assume 15% would leave without intervention)
        retention_benefit = potential_salary_increase * 0.15 * 1.5  # 1.5x replacement cost

        return {
            "total_investment": strategy_cost,
            "potential_salary_impact": potential_salary_increase,
            "retention_benefit": retention_benefit,
            "total_benefit": potential_salary_increase + retention_benefit,
            "roi_ratio": (potential_salary_increase + retention_benefit) / max(strategy_cost, 1),
            "payback_months": max(12, int((strategy_cost / potential_salary_increase) * 12)),
        }

    def _create_implementation_timeline(self, strategy: Dict) -> List[Dict]:
        """
        Create implementation timeline for recommended strategy.

        Args:
          strategy: Dict:

        Returns:
        """
        timeline_months = strategy["strategy_details"]["timeline_months"]

        return (
            [
                {
                    "month": 1,
                    "milestone": "Strategy approval and budget allocation",
                },
                {"month": 2, "milestone": "Employee selection and communication"},
                {"month": timeline_months, "milestone": "Implementation complete"},
            ]
            if timeline_months <= 6
            else [
                {
                    "month": 1,
                    "milestone": "Strategy approval and budget allocation",
                },
                {
                    "month": 2,
                    "milestone": "Phase 1 rollout (high priority employees)",
                },
                {
                    "month": timeline_months // 2,
                    "milestone": "Mid-point review and adjustments",
                },
                {
                    "month": timeline_months,
                    "milestone": "Full implementation complete",
                },
            ]
        )

    # Additional analysis methods
    def _calculate_below_median_statistics(self, below_median_employees: List[Dict]) -> Dict:
        """
        Calculate summary statistics for below-median employees.

        Args:
          below_median_employees: List[Dict]:

        Returns:
        """
        if not below_median_employees:
            return {"count": 0}

        gap_amounts = [emp["gap_amount"] for emp in below_median_employees]
        gap_percents = [emp["gap_percent"] for emp in below_median_employees]

        return {
            "count": len(below_median_employees),
            "average_gap_amount": np.mean(gap_amounts),
            "median_gap_amount": np.median(gap_amounts),
            "average_gap_percent": np.mean(gap_percents),
            "median_gap_percent": np.median(gap_percents),
            "total_gap_amount": sum(gap_amounts),
            "max_gap_amount": max(gap_amounts),
            "min_gap_amount": min(gap_amounts),
        }

    def _analyze_gender_patterns(self, gender_patterns: Dict[str, List[Dict]]) -> Dict:
        """
        Analyze gender-based patterns in below-median employees.

        Args:
          gender_patterns: Dict[str:
          List[Dict]]:

        Returns:
        """
        analysis = {}

        for gender, employees in gender_patterns.items():
            if employees:
                gaps = [emp["gap_percent"] for emp in employees]
                analysis[gender] = {
                    "count": len(employees),
                    "average_gap_percent": np.mean(gaps),
                    "median_gap_percent": np.median(gaps),
                }
            else:
                analysis[gender] = {"count": 0, "average_gap_percent": 0, "median_gap_percent": 0}

        # Calculate gender disparity
        if analysis.get("Male", {}).get("count", 0) > 0 and analysis.get("Female", {}).get("count", 0) > 0:
            disparity = analysis["Female"]["average_gap_percent"] - analysis["Male"]["average_gap_percent"]
            analysis["gender_disparity"] = disparity
            analysis["disparity_significant"] = abs(disparity) > 5.0

        return analysis

    def _log_median_statistics(self):
        """
        Log median statistics for validation.
        """
        LOGGER.info("Level median salaries:")
        for level, median in sorted(self.medians_by_level.items()):
            LOGGER.info(f"  Level {level}: {format_currency(median)}")

    def _project_year_convergence(self, below_median_employees: List[Dict], year: int, scenario: str) -> Dict:
        """
        Project convergence for a specific year under a given scenario.

        Args:
          below_median_employees: List[Dict]:
          year: int:
          scenario: str:

        Returns:
        """
        remaining_below_median = 0
        converged_count = 0

        for employee in below_median_employees:
            # Simulate salary growth for this year
            current_salary = employee["salary"]
            level_median = self.medians_by_level[employee["level"]]

            # Apply growth based on scenario
            if scenario == "natural":
                growth_rate = 0.05  # 5% natural growth
            elif scenario == "accelerated":
                growth_rate = 0.08  # 8% accelerated growth
            else:  # intervention
                growth_rate = 0.12  # 12% intervention growth

            projected_salary = current_salary * ((1 + growth_rate) ** year)

            if projected_salary >= level_median * (1 - self.acceptable_gap_percent / 100):
                converged_count += 1
            else:
                remaining_below_median += 1

        return {
            "year": year,
            "scenario": scenario,
            "remaining_below_median": remaining_below_median,
            "converged_this_period": converged_count,
            "convergence_rate_year": converged_count / len(below_median_employees) if below_median_employees else 0,
        }

    def _calculate_convergence_rate(self, convergence_timeline: List[Dict]) -> float:
        """
        Calculate overall convergence rate across timeline.

        Args:
          convergence_timeline: List[Dict]:

        Returns:
        """
        if not convergence_timeline:
            return 0.0

        initial_count = (
            convergence_timeline[0]["remaining_below_median"] + convergence_timeline[0]["converged_this_period"]
        )
        if initial_count == 0:
            return 100.0

        final_count = convergence_timeline[-1]["remaining_below_median"]

        return max(0.0, ((initial_count - final_count) / initial_count) * 100)

    def _analyze_gap_distribution(self) -> Dict:
        """
        Analyze the distribution of salary gaps across the population.
        """
        below_median_analysis = self.identify_below_median_employees(min_gap_percent=0.0)
        employees = below_median_analysis.get("employees", [])

        if not employees:
            return {"total_below_median": 0, "distribution": {}}

        gaps = [emp["gap_percent"] for emp in employees]

        # Categorize gaps
        small_gaps = len([g for g in gaps if 0 < g <= 5])
        medium_gaps = len([g for g in gaps if 5 < g <= 15])
        large_gaps = len([g for g in gaps if 15 < g <= 25])
        severe_gaps = len([g for g in gaps if g > 25])

        return {
            "total_below_median": len(employees),
            "distribution": {
                "small_gaps_0_5_percent": small_gaps,
                "medium_gaps_5_15_percent": medium_gaps,
                "large_gaps_15_25_percent": large_gaps,
                "severe_gaps_over_25_percent": severe_gaps,
            },
            "average_gap_percent": sum(gaps) / len(gaps),
            "median_gap_percent": sorted(gaps)[len(gaps) // 2],
        }

    def _calculate_convergence_velocity(self, trend_projections: Dict) -> Dict:
        """
        Calculate how quickly each scenario achieves convergence.

        Args:
          trend_projections: Dict:

        Returns:
        """
        velocity_metrics = {}

        for scenario, projection in trend_projections.items():
            timeline = projection["timeline"]
            if not timeline:
                velocity_metrics[scenario] = {"velocity": 0, "peak_year": 0}
                continue

            # Find year with maximum convergence rate
            max_rate_year = max(timeline, key=lambda x: x.get("convergence_rate_year", 0))
            peak_velocity = max_rate_year.get("convergence_rate_year", 0) * 100

            velocity_metrics[scenario] = {
                "peak_velocity_percent_per_year": peak_velocity,
                "peak_year": max_rate_year.get("year", 1),
                "final_convergence_rate": projection["convergence_rate"],
            }

        return velocity_metrics

    def _calculate_intervention_impact(self, trend_projections: Dict) -> Dict:
        """
        Calculate the impact of interventions compared to natural progression.

        Args:
          trend_projections: Dict:

        Returns:
        """
        natural = trend_projections.get("natural", {})
        intervention = trend_projections.get("intervention", {})

        if not natural or not intervention:
            return {"impact_analysis": "insufficient_data"}

        natural_rate = natural.get("convergence_rate", 0)
        intervention_rate = intervention.get("convergence_rate", 0)

        improvement = intervention_rate - natural_rate
        relative_improvement = (improvement / natural_rate * 100) if natural_rate > 0 else 0

        return {
            "natural_convergence_rate": natural_rate,
            "intervention_convergence_rate": intervention_rate,
            "absolute_improvement": improvement,
            "relative_improvement_percent": relative_improvement,
            "intervention_effectiveness": (
                "high" if relative_improvement > 50 else "medium" if relative_improvement > 20 else "low"
            ),
        }

    def _generate_strategic_recommendations(self, trend_projections: Dict, population_health: Dict) -> List[str]:
        """
        Generate strategic recommendations based on analysis.

        Args:
          trend_projections: Dict:
          population_health: Dict:

        Returns:
        """
        recommendations = []

        # Analyze convergence patterns
        intervention_impact = population_health.get("intervention_impact", {})
        gap_distribution = population_health.get("current_median_gap_distribution", {})

        # Severe gaps require immediate action
        severe_gaps = gap_distribution.get("distribution", {}).get("severe_gaps_over_25_percent", 0)
        if severe_gaps > 0:
            recommendations.append(
                f"URGENT: Address {severe_gaps} employees with >25% salary gaps through immediate interventions"
            )

        # Medium/large gaps need structured approach
        medium_gaps = gap_distribution.get("distribution", {}).get("medium_gaps_5_15_percent", 0)
        large_gaps = gap_distribution.get("distribution", {}).get("large_gaps_15_25_percent", 0)
        if medium_gaps + large_gaps > 0:
            recommendations.append(
                f"Implement performance acceleration programs for {medium_gaps + large_gaps} employees with 5-25% gaps"
            )

        # Intervention effectiveness assessment
        effectiveness = intervention_impact.get("intervention_effectiveness", "unknown")
        if effectiveness == "high":
            recommendations.append(
                "High intervention effectiveness detected - prioritize intervention strategies over natural progression"
            )
        elif effectiveness == "low":
            recommendations.append(
                "Low intervention effectiveness - focus on natural progression and performance improvement"
            )

        # Population-level recommendations
        total_below = gap_distribution.get("total_below_median", 0)
        if total_below > len(self.population_data) * 0.3:  # >30% below median
            recommendations.append(
                "Population-wide salary review recommended - high percentage of below-median employees"
            )

        # Timeline recommendations
        natural_proj = trend_projections.get("natural", {})
        if natural_proj.get("convergence_rate", 0) < 50:  # <50% natural convergence
            recommendations.append("Natural convergence insufficient - intervention required for equitable outcomes")

        if not recommendations:
            recommendations.append("Monitor current progression - population shows healthy convergence patterns")

        return recommendations


def main():
    """
    Main function for testing and validation.
    """
    parser = argparse.ArgumentParser(description="Median Convergence Analyzer")
    parser.add_argument("--test-analysis", action="store_true", help="Run test analysis")
    parser.add_argument(
        "--min-gap-percent", type=float, default=5.0, help="Minimum gap percentage to analyze (default: 5%)"
    )
    parser.add_argument("--output-format", choices=["json", "summary"], default="summary", help="Output format")

    args = parser.parse_args()

    if args.test_analysis:
        LOGGER.info("Running test median convergence analysis")

        # Create test population with realistic salary distribution
        from individual_progression_simulator import create_test_employee

        test_population = []

        # Create population with some below-median employees
        for i in range(1, 51):  # 50 employees
            level = (i % 6) + 1
            base_salary = 30000 + (level * 15000)

            # Create variation - some below median, some above
            if i % 4 == 0:  # 25% below median
                salary = base_salary * 0.85  # 15% below base
            elif i % 4 == 1:  # 25% slightly below median
                salary = base_salary * 0.92  # 8% below base
            elif i % 4 == 2:  # 25% at median
                salary = base_salary
            else:  # 25% above median
                salary = base_salary * 1.15  # 15% above base

            employee = create_test_employee(
                employee_id=i,
                level=level,
                salary=salary,
                performance_rating=["Partially met", "Achieving", "High Performing"][i % 3],
                gender="Female" if i % 3 == 0 else "Male",
            )
            test_population.append(employee)

        # Initialize analyzer
        analyzer = MedianConvergenceAnalyzer(test_population)

        # Identify below-median employees
        below_median_analysis = analyzer.identify_below_median_employees(min_gap_percent=args.min_gap_percent)

        # Analyze convergence for a sample employee
        if below_median_analysis["employees"]:
            sample_employee = below_median_analysis["employees"][0]
            convergence_analysis = analyzer.analyze_convergence_timeline(sample_employee)

            # Get intervention recommendations
            intervention_recommendations = analyzer.recommend_intervention_strategies(below_median_analysis)

        if args.output_format == "json":
            result = {
                "below_median_analysis": below_median_analysis,
                "sample_convergence": convergence_analysis if below_median_analysis["employees"] else None,
                "intervention_recommendations": (
                    intervention_recommendations if below_median_analysis["employees"] else None
                ),
            }
            # Use common export utility for JSON output
            json_str = json.dumps(result, indent=2, default=str)
            print(json_str)
        else:
            # Summary output
            print("\n📊 Median Convergence Analysis")
            print(f"{'='*50}")
            print(f"Total employees analyzed: {below_median_analysis['total_employees']}")
            print(
                f"Below median (>{args.min_gap_percent}%): {below_median_analysis['below_median_count']} "
                f"({below_median_analysis['below_median_percent']:.1f}%)"
            )

            if below_median_analysis["employees"]:
                stats = below_median_analysis["summary_statistics"]
                print(f"Average gap: £{stats['average_gap_amount']:,.2f} ({stats['average_gap_percent']:.1f}%)")
                print(f"Total gap amount: £{stats['total_gap_amount']:,.2f}")

                if "gender_analysis" in below_median_analysis:
                    gender_analysis = below_median_analysis["gender_analysis"]
                    print("\n👥 Gender Analysis:")
                    for gender, data in gender_analysis.items():
                        if gender not in ["gender_disparity", "disparity_significant"]:
                            print(
                                f"  {gender}: {data['count']} employees (avg gap: {data['average_gap_percent']:.1f}%)"
                            )

                print(f"\n🎯 Sample Convergence Analysis (Employee {sample_employee['employee_id']}):")
                print(
                    f"Current gap: £{convergence_analysis['current_gap_amount']:,.2f} "
                    f"({convergence_analysis['current_gap_percent']:.1f}%)"
                )
                print(
                    f"Natural convergence: {convergence_analysis['scenarios']['natural']['years_to_median']:.1f} years"
                )
                print(
                    f"With intervention: {convergence_analysis['scenarios']['intervention']['years_to_median']:.1f} years"
                )
                print(f"Recommended action: {convergence_analysis['recommended_action']}")

                print("\n💡 Intervention Recommendations:")
                rec = intervention_recommendations["recommended_strategy"]
                print(f"Primary strategy: {rec['primary_strategy']}")
                print(f"Budget required: £{rec['total_budget_required']:,.2f}")
                print(f"Affected employees: {rec['strategy_details']['affected_employees']}")
            else:
                print("No employees found below median threshold")

    else:
        LOGGER.info("Use --test-analysis to run demonstration")
        parser.print_help()


if __name__ == "__main__":
    main()

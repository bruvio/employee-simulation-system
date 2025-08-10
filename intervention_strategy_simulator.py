#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

import pandas as pd
import numpy as np
import argparse
import json
from typing import List, Dict, Tuple, Optional, Union
from datetime import datetime, timedelta
from logger import LOGGER
from salary_forecasting_engine import SalaryForecastingEngine
from individual_progression_simulator import IndividualProgressionSimulator
from median_convergence_analyzer import MedianConvergenceAnalyzer


class InterventionStrategySimulator:
    """
    Simulate and analyze management intervention strategies for salary equity.

    Focuses on gender pay gap remediation, strategic salary adjustments, and
    cost-benefit analysis for various intervention approaches with budget optimization.
    """

    def __init__(self, population_data: List[Dict], config: Dict = None):
        self.population_data = population_data
        self.config = config or {}

        # Initialize core components
        self.forecasting_engine = SalaryForecastingEngine(
            confidence_level=self.config.get("confidence_interval", 0.95),
            market_inflation_rate=self.config.get("market_inflation_rate", 0.025),
        )

        self.individual_simulator = IndividualProgressionSimulator(population_data, config=self.config)

        self.convergence_analyzer = MedianConvergenceAnalyzer(population_data, config=self.config)

        # Calculate baseline metrics
        self.population_df = pd.DataFrame(population_data)
        self.baseline_metrics = self._calculate_baseline_metrics()

        # Configuration parameters
        self.max_budget_percent = self.config.get("max_budget_percent", 0.006)  # 0.6% of payroll
        self.target_timeline_years = self.config.get("target_timeline_years", 3)

        LOGGER.info(f"Initialized InterventionStrategySimulator with {len(population_data)} employees")
        LOGGER.info(f"Current gender pay gap: {self.baseline_metrics['gender_pay_gap_percent']:.1f}%")
        LOGGER.info(f"Total payroll: £{self.baseline_metrics['total_payroll']:,.0f}")
        LOGGER.info(
            f"Maximum budget: {self.max_budget_percent:.1%} (£{self.baseline_metrics['total_payroll'] * self.max_budget_percent:,.0f})"
        )

    def model_gender_gap_remediation(
        self, target_gap_percent: float = 0.0, max_years: int = 5, budget_constraint: float = 0.005
    ) -> Dict:
        """
        Model comprehensive gender pay gap remediation strategies.

        Args:
            target_gap_percent: Target gap percentage (0.0 = complete equality)
            max_years: Maximum timeline to achieve target
            budget_constraint: Maximum percentage of payroll for interventions

        Returns:
            Dict with strategy analysis, costs, timelines, and recommendations
        """
        LOGGER.info(
            f"Modeling gender gap remediation: {self.baseline_metrics['gender_pay_gap_percent']:.1f}% → {target_gap_percent:.1f}%"
        )
        LOGGER.info(
            f"Budget constraint: {budget_constraint:.1%} of payroll (£{self.baseline_metrics['total_payroll'] * budget_constraint:,.0f})"
        )

        # Define available strategies
        strategies = {
            "immediate_adjustment": self._model_immediate_adjustment_strategy(target_gap_percent, budget_constraint),
            "gradual_3_year": self._model_gradual_strategy(target_gap_percent, 3, budget_constraint),
            "gradual_5_year": self._model_gradual_strategy(target_gap_percent, 5, budget_constraint),
            "natural_convergence": self._model_natural_convergence_strategy(target_gap_percent, max_years),
            "targeted_intervention": self._model_targeted_intervention_strategy(
                target_gap_percent, max_years, budget_constraint
            ),
        }

        # Evaluate and rank strategies
        strategy_evaluation = self._evaluate_strategies(strategies, budget_constraint)

        # Find optimal strategy
        optimal_strategy = self._find_optimal_strategy(strategy_evaluation, budget_constraint)

        # Generate comprehensive analysis
        result = {
            "current_state": {
                "gender_pay_gap_percent": self.baseline_metrics["gender_pay_gap_percent"],
                "male_median_salary": self.baseline_metrics["male_median_salary"],
                "female_median_salary": self.baseline_metrics["female_median_salary"],
                "affected_female_employees": len(self._identify_underpaid_female_employees()),
                "total_payroll": self.baseline_metrics["total_payroll"],
            },
            "target_state": {
                "target_gap_percent": target_gap_percent,
                "max_timeline_years": max_years,
                "budget_constraint_percent": budget_constraint,
                "budget_constraint_amount": self.baseline_metrics["total_payroll"] * budget_constraint,
            },
            "available_strategies": strategies,
            "strategy_evaluation": strategy_evaluation,
            "recommended_strategy": optimal_strategy,
            "implementation_plan": self._create_implementation_plan(optimal_strategy),
            "roi_analysis": self._calculate_roi_analysis(optimal_strategy),
            "risk_assessment": self._assess_implementation_risks(optimal_strategy),
        }

        LOGGER.info(f"Recommended strategy: {optimal_strategy['strategy_name']}")
        LOGGER.info(
            f"Estimated cost: £{optimal_strategy['total_cost']:,.0f} ({optimal_strategy['cost_as_percent_payroll']:.2%})"
        )
        LOGGER.info(f"Timeline: {optimal_strategy['timeline_years']} years")

        return result

    def analyze_population_salary_equity(self, dimensions: List[str] = None) -> Dict:
        """
        Analyze salary equity across multiple demographic dimensions.

        Args:
            dimensions: List of dimensions to analyze (gender, level, tenure, etc.)

        Returns:
            Dict with comprehensive equity analysis
        """
        dimensions = dimensions or ["gender", "level", "gender_by_level"]

        LOGGER.info(f"Analyzing population salary equity across dimensions: {dimensions}")

        equity_analysis = {}

        if "gender" in dimensions:
            equity_analysis["gender"] = self._analyze_gender_equity()

        if "level" in dimensions:
            equity_analysis["level"] = self._analyze_level_equity()

        if "gender_by_level" in dimensions:
            equity_analysis["gender_by_level"] = self._analyze_gender_by_level_equity()

        if "tenure" in dimensions:
            equity_analysis["tenure"] = self._analyze_tenure_equity()

        # Overall equity score
        equity_analysis["overall_equity_score"] = self._calculate_overall_equity_score(equity_analysis)

        # Priority interventions
        equity_analysis["priority_interventions"] = self._identify_priority_interventions(equity_analysis)

        return equity_analysis

    def simulate_intervention_impact(self, strategy: Dict, projection_years: int = 5) -> Dict:
        """
        Simulate the multi-year impact of an intervention strategy.

        Args:
            strategy: Intervention strategy details
            projection_years: Number of years to project impact

        Returns:
            Dict with year-by-year impact projections
        """
        LOGGER.info(f"Simulating {projection_years}-year impact of {strategy.get('strategy_name', 'strategy')}")

        # Create projected population states
        impact_timeline = []
        current_population = self.population_data.copy()

        for year in range(1, projection_years + 1):
            # Apply strategy interventions for this year
            current_population = self._apply_yearly_interventions(current_population, strategy, year)

            # Calculate metrics for this year
            year_metrics = self._calculate_yearly_metrics(current_population, year)

            # Add natural progression (promotions, market adjustments)
            current_population = self._apply_natural_progression(current_population)

            impact_timeline.append(
                {
                    "year": year,
                    "metrics": year_metrics,
                    "cumulative_cost": strategy.get("total_cost", 0) * (year / strategy.get("timeline_years", 1)),
                    "employees_affected": self._count_affected_employees(current_population, strategy),
                }
            )

        # Calculate impact summary
        impact_summary = {
            "initial_gap": self.baseline_metrics["gender_pay_gap_percent"],
            "final_gap": impact_timeline[-1]["metrics"]["gender_pay_gap_percent"],
            "gap_reduction": (
                self.baseline_metrics["gender_pay_gap_percent"]
                - impact_timeline[-1]["metrics"]["gender_pay_gap_percent"]
            ),
            "total_investment": impact_timeline[-1]["cumulative_cost"],
            "roi_metrics": self._calculate_long_term_roi(impact_timeline),
        }

        return {
            "strategy_name": strategy.get("strategy_name", "Unknown"),
            "projection_years": projection_years,
            "impact_timeline": impact_timeline,
            "impact_summary": impact_summary,
            "success_probability": self._estimate_success_probability(strategy, impact_timeline),
        }

    def optimize_budget_allocation(self, total_budget: float, intervention_types: List[str] = None) -> Dict:
        """
        Optimize budget allocation across different intervention types.

        Args:
            total_budget: Total available budget for interventions
            intervention_types: Types of interventions to consider

        Returns:
            Dict with optimal budget allocation strategy
        """
        intervention_types = intervention_types or [
            "gender_gap_remediation",
            "below_median_adjustments",
            "performance_development",
            "retention_bonuses",
        ]

        LOGGER.info(f"Optimizing £{total_budget:,.0f} budget across {len(intervention_types)} intervention types")

        # Calculate intervention options for each type
        intervention_options = {}

        for intervention_type in intervention_types:
            intervention_options[intervention_type] = self._calculate_intervention_options(
                intervention_type, total_budget
            )

        # Optimize allocation using utility/impact scoring
        optimal_allocation = self._optimize_allocation(intervention_options, total_budget)

        return {
            "total_budget": total_budget,
            "intervention_types": intervention_types,
            "intervention_options": intervention_options,
            "optimal_allocation": optimal_allocation,
            "expected_impact": self._calculate_allocation_impact(optimal_allocation),
            "implementation_priority": self._prioritize_interventions(optimal_allocation),
        }

    def _calculate_baseline_metrics(self) -> Dict:
        """Calculate baseline population metrics for comparison."""
        male_employees = self.population_df[self.population_df["gender"] == "Male"]
        female_employees = self.population_df[self.population_df["gender"] == "Female"]

        if len(male_employees) == 0 or len(female_employees) == 0:
            gender_pay_gap = 0.0
            male_median = female_median = self.population_df["salary"].median()
        else:
            male_median = male_employees["salary"].median()
            female_median = female_employees["salary"].median()
            gender_pay_gap = ((male_median - female_median) / male_median) * 100

        return {
            "total_employees": len(self.population_df),
            "male_employees": len(male_employees),
            "female_employees": len(female_employees),
            "total_payroll": self.population_df["salary"].sum(),
            "overall_median_salary": self.population_df["salary"].median(),
            "male_median_salary": male_median,
            "female_median_salary": female_median,
            "gender_pay_gap_percent": gender_pay_gap,
            "gender_pay_gap_amount": male_median - female_median,
        }

    def _identify_underpaid_female_employees(self) -> List[Dict]:
        """Identify female employees who are underpaid relative to male counterparts."""
        underpaid_females = []

        LOGGER.debug("Analyzing salary patterns by level and gender:")

        for level in sorted(self.population_df["level"].unique()):
            level_data = self.population_df[self.population_df["level"] == level]
            male_level_data = level_data[level_data["gender"] == "Male"]
            female_level_data = level_data[level_data["gender"] == "Female"]

            LOGGER.debug(f"Level {level}: {len(male_level_data)} males, {len(female_level_data)} females")

            if len(male_level_data) == 0 or len(female_level_data) == 0:
                LOGGER.debug(f"Skipping level {level} - insufficient data")
                continue

            male_median = male_level_data["salary"].median()
            female_median = female_level_data["salary"].median()

            LOGGER.debug(f"Level {level}: Male median £{male_median:.0f}, Female median £{female_median:.0f}")

            # Find females below male median for same level
            below_male_median = female_level_data[female_level_data["salary"] < male_median]

            LOGGER.debug(f"Level {level}: {len(below_male_median)} females below male median")

            for _, female_emp in below_male_median.iterrows():
                gap_amount = male_median - female_emp["salary"]
                gap_percent = (gap_amount / male_median) * 100

                underpaid_females.append(
                    {
                        "employee_id": female_emp["employee_id"],
                        "level": level,
                        "current_salary": female_emp["salary"],
                        "male_level_median": male_median,
                        "gap_amount": gap_amount,
                        "gap_percent": gap_percent,
                        "performance_rating": female_emp.get("performance_rating", "Unknown"),
                    }
                )

        # Sort by gap amount (largest gaps first)
        underpaid_females.sort(key=lambda x: x["gap_amount"], reverse=True)

        LOGGER.debug(f"Total identified underpaid female employees: {len(underpaid_females)}")
        if underpaid_females:
            LOGGER.debug(
                f"Largest gap: £{underpaid_females[0]['gap_amount']:.0f} ({underpaid_females[0]['gap_percent']:.1f}%)"
            )

        return underpaid_females

    def _model_immediate_adjustment_strategy(self, target_gap_percent: float, budget_constraint: float) -> Dict:
        """Model immediate salary adjustment to close gender gap."""
        underpaid_females = self._identify_underpaid_female_employees()

        if not underpaid_females:
            return {
                "strategy_name": "immediate_adjustment",
                "applicable": False,
                "reason": "No underpaid female employees identified",
            }

        # Calculate total adjustment needed
        total_adjustment_needed = sum(emp["gap_amount"] for emp in underpaid_females)

        # Scale adjustment to target gap (0% = full adjustment, 5% = 95% adjustment)
        target_adjustment_factor = max(
            0,
            (self.baseline_metrics["gender_pay_gap_percent"] - target_gap_percent)
            / self.baseline_metrics["gender_pay_gap_percent"],
        )

        total_cost = total_adjustment_needed * target_adjustment_factor
        budget_limit = self.baseline_metrics["total_payroll"] * budget_constraint

        # Check budget feasibility
        if total_cost > budget_limit:
            # Scale back adjustments to fit budget
            scale_factor = budget_limit / total_cost
            total_cost = budget_limit
            actual_gap_reduction = (
                self.baseline_metrics["gender_pay_gap_percent"] * target_adjustment_factor * scale_factor
            )
        else:
            actual_gap_reduction = self.baseline_metrics["gender_pay_gap_percent"] * target_adjustment_factor

        return {
            "strategy_name": "immediate_adjustment",
            "applicable": True,
            "timeline_years": 0.25,  # 3 months to implement
            "total_cost": total_cost,
            "cost_as_percent_payroll": total_cost / self.baseline_metrics["total_payroll"],
            "affected_employees": len(underpaid_females),
            "average_adjustment": total_cost / len(underpaid_females) if underpaid_females else 0,
            "projected_final_gap": self.baseline_metrics["gender_pay_gap_percent"] - actual_gap_reduction,
            "gap_reduction_percent": actual_gap_reduction,
            "budget_utilization": total_cost / budget_limit,
            "feasibility": "high" if total_cost <= budget_limit else "medium",
            "implementation_complexity": "low",
            "legal_risk_reduction": "high",
            "description": "Immediate salary adjustments to reduce gender pay gap",
        }

    def _model_gradual_strategy(self, target_gap_percent: float, years: int, budget_constraint: float) -> Dict:
        """Model gradual salary adjustment strategy over specified years."""
        immediate_strategy = self._model_immediate_adjustment_strategy(target_gap_percent, budget_constraint)

        if not immediate_strategy.get("applicable", False):
            return immediate_strategy

        # Spread cost over multiple years
        total_cost = immediate_strategy["total_cost"]
        annual_cost = total_cost / years
        annual_budget_limit = self.baseline_metrics["total_payroll"] * budget_constraint / years

        # Check annual budget feasibility
        feasible_annual_cost = min(annual_cost, annual_budget_limit)
        actual_total_cost = feasible_annual_cost * years
        scale_factor = actual_total_cost / total_cost if total_cost > 0 else 1

        return {
            "strategy_name": f"gradual_{years}_year",
            "applicable": True,
            "timeline_years": years,
            "total_cost": actual_total_cost,
            "annual_cost": feasible_annual_cost,
            "cost_as_percent_payroll": actual_total_cost / self.baseline_metrics["total_payroll"],
            "affected_employees": immediate_strategy["affected_employees"],
            "average_adjustment": (
                actual_total_cost / immediate_strategy["affected_employees"]
                if immediate_strategy["affected_employees"] > 0
                else 0
            ),
            "projected_final_gap": (
                self.baseline_metrics["gender_pay_gap_percent"]
                - immediate_strategy["gap_reduction_percent"] * scale_factor
            ),
            "gap_reduction_percent": immediate_strategy["gap_reduction_percent"] * scale_factor,
            "budget_utilization": actual_total_cost / (self.baseline_metrics["total_payroll"] * budget_constraint),
            "feasibility": "high" if feasible_annual_cost == annual_cost else "medium",
            "implementation_complexity": "medium",
            "legal_risk_reduction": "medium",
            "description": f"Gradual salary adjustments over {years} years",
        }

    def _model_natural_convergence_strategy(self, target_gap_percent: float, max_years: int) -> Dict:
        """Model natural convergence without direct interventions."""
        # Simulate natural progression using market growth rates
        annual_gap_reduction = 0.5  # Assume 0.5% gap reduction per year naturally
        years_to_target = max(
            1, (self.baseline_metrics["gender_pay_gap_percent"] - target_gap_percent) / annual_gap_reduction
        )

        return {
            "strategy_name": "natural_convergence",
            "applicable": True,
            "timeline_years": min(years_to_target, max_years),
            "total_cost": 0,
            "cost_as_percent_payroll": 0.0,
            "affected_employees": 0,
            "projected_final_gap": max(
                target_gap_percent,
                self.baseline_metrics["gender_pay_gap_percent"]
                - (annual_gap_reduction * min(years_to_target, max_years)),
            ),
            "gap_reduction_percent": min(
                self.baseline_metrics["gender_pay_gap_percent"] - target_gap_percent,
                annual_gap_reduction * min(years_to_target, max_years),
            ),
            "budget_utilization": 0.0,
            "feasibility": "high",
            "implementation_complexity": "none",
            "legal_risk_reduction": "low",
            "description": "Allow natural market forces and progression to reduce gap",
        }

    def _model_targeted_intervention_strategy(
        self, target_gap_percent: float, max_years: int, budget_constraint: float
    ) -> Dict:
        """Model targeted interventions focusing on highest-impact employees."""
        underpaid_females = self._identify_underpaid_female_employees()

        if not underpaid_females:
            return {
                "strategy_name": "targeted_intervention",
                "applicable": False,
                "reason": "No underpaid female employees identified",
            }

        # Focus on top 50% of gaps for maximum impact
        high_impact_employees = underpaid_females[: len(underpaid_females) // 2]

        total_cost = sum(emp["gap_amount"] * 0.75 for emp in high_impact_employees)  # 75% gap closure
        budget_limit = self.baseline_metrics["total_payroll"] * budget_constraint

        if total_cost > budget_limit:
            scale_factor = budget_limit / total_cost
            total_cost = budget_limit
        else:
            scale_factor = 1.0

        # Estimate gap reduction impact
        total_gap_represented = sum(emp["gap_amount"] for emp in high_impact_employees)
        total_all_gaps = sum(emp["gap_amount"] for emp in underpaid_females)
        gap_impact_ratio = total_gap_represented / total_all_gaps if total_all_gaps > 0 else 0

        estimated_gap_reduction = (
            self.baseline_metrics["gender_pay_gap_percent"] * gap_impact_ratio * 0.75 * scale_factor
        )

        return {
            "strategy_name": "targeted_intervention",
            "applicable": True,
            "timeline_years": 1,
            "total_cost": total_cost,
            "cost_as_percent_payroll": total_cost / self.baseline_metrics["total_payroll"],
            "affected_employees": len(high_impact_employees),
            "average_adjustment": total_cost / len(high_impact_employees) if high_impact_employees else 0,
            "projected_final_gap": self.baseline_metrics["gender_pay_gap_percent"] - estimated_gap_reduction,
            "gap_reduction_percent": estimated_gap_reduction,
            "budget_utilization": total_cost / budget_limit,
            "feasibility": "high",
            "implementation_complexity": "medium",
            "legal_risk_reduction": "high",
            "description": "Target highest-impact salary adjustments for maximum gap reduction",
        }

    def _evaluate_strategies(self, strategies: Dict, budget_constraint: float) -> Dict:
        """Evaluate and score all available strategies."""
        evaluation = {}

        for strategy_name, strategy in strategies.items():
            if not strategy.get("applicable", True):
                continue

            # Calculate strategy score based on multiple factors
            effectiveness_score = self._calculate_effectiveness_score(strategy)
            feasibility_score = self._calculate_feasibility_score(strategy, budget_constraint)
            risk_score = self._calculate_risk_score(strategy)
            cost_efficiency_score = self._calculate_cost_efficiency_score(strategy)

            overall_score = (
                effectiveness_score * 0.3
                + feasibility_score * 0.25
                + (1 - risk_score) * 0.2  # Lower risk = higher score
                + cost_efficiency_score * 0.25
            )

            evaluation[strategy_name] = {
                "overall_score": overall_score,
                "effectiveness_score": effectiveness_score,
                "feasibility_score": feasibility_score,
                "risk_score": risk_score,
                "cost_efficiency_score": cost_efficiency_score,
                "strategy_details": strategy,
            }

        # Rank strategies
        ranked_strategies = sorted(evaluation.items(), key=lambda x: x[1]["overall_score"], reverse=True)

        return {
            "strategy_scores": evaluation,
            "ranking": [name for name, _ in ranked_strategies],
            "top_strategy": ranked_strategies[0][0] if ranked_strategies else None,
        }

    def _find_optimal_strategy(self, strategy_evaluation: Dict, budget_constraint: float) -> Dict:
        """Find the optimal strategy based on evaluation scores."""
        if not strategy_evaluation["ranking"]:
            return {"strategy_name": "no_viable_strategy", "reason": "No applicable strategies found"}

        top_strategy_name = strategy_evaluation["ranking"][0]
        top_strategy_eval = strategy_evaluation["strategy_scores"][top_strategy_name]

        return {
            "strategy_name": top_strategy_name,
            "overall_score": top_strategy_eval["overall_score"],
            "confidence_level": (
                "high"
                if top_strategy_eval["overall_score"] > 0.8
                else "medium" if top_strategy_eval["overall_score"] > 0.6 else "low"
            ),
            **top_strategy_eval["strategy_details"],
        }

    def _calculate_effectiveness_score(self, strategy: Dict) -> float:
        """Calculate strategy effectiveness score (0-1)."""
        gap_reduction = strategy.get("gap_reduction_percent", 0)
        max_possible_reduction = self.baseline_metrics["gender_pay_gap_percent"]

        if max_possible_reduction == 0:
            return 1.0

        return min(1.0, gap_reduction / max_possible_reduction)

    def _calculate_feasibility_score(self, strategy: Dict, budget_constraint: float) -> float:
        """Calculate strategy feasibility score (0-1)."""
        cost_percent = strategy.get("cost_as_percent_payroll", 0)
        timeline_years = strategy.get("timeline_years", 1)

        # Budget feasibility (0-1)
        budget_feasibility = max(0, 1 - (cost_percent / budget_constraint)) if budget_constraint > 0 else 1

        # Timeline feasibility (0-1, shorter is better up to a point)
        timeline_feasibility = max(0.2, 1 - (timeline_years - 1) * 0.1)

        # Implementation complexity (0-1)
        complexity_map = {"none": 1.0, "low": 0.9, "medium": 0.7, "high": 0.5}
        complexity_feasibility = complexity_map.get(strategy.get("implementation_complexity", "medium"), 0.7)

        return (budget_feasibility + timeline_feasibility + complexity_feasibility) / 3

    def _calculate_risk_score(self, strategy: Dict) -> float:
        """Calculate strategy risk score (0-1, higher = more risky)."""
        legal_risk_map = {"low": 0.8, "medium": 0.5, "high": 0.2}
        legal_risk = legal_risk_map.get(strategy.get("legal_risk_reduction", "medium"), 0.5)

        # Budget risk (using large portion of budget is risky)
        budget_utilization = strategy.get("budget_utilization", 0)
        budget_risk = min(1.0, budget_utilization)

        # Implementation risk
        complexity_risk_map = {"none": 0.1, "low": 0.2, "medium": 0.5, "high": 0.8}
        implementation_risk = complexity_risk_map.get(strategy.get("implementation_complexity", "medium"), 0.5)

        # Overall risk (lower legal risk reduction = higher risk)
        return (budget_risk + implementation_risk + (1 - legal_risk)) / 3

    def _calculate_cost_efficiency_score(self, strategy: Dict) -> float:
        """Calculate cost efficiency score (0-1)."""
        cost = strategy.get("total_cost", 0)
        gap_reduction = strategy.get("gap_reduction_percent", 0)

        if gap_reduction == 0:
            return 1.0 if cost == 0 else 0.0

        if cost == 0:
            return 1.0  # Natural convergence is perfectly cost-efficient

        # Cost per percentage point of gap reduction
        cost_per_gap_point = cost / gap_reduction

        # Normalize against total payroll (lower is better)
        normalized_cost_efficiency = max(0, 1 - (cost_per_gap_point / self.baseline_metrics["total_payroll"]))

        return normalized_cost_efficiency

    # Additional helper methods for analysis components
    def _analyze_gender_equity(self) -> Dict:
        """Analyze gender-based salary equity."""
        male_data = self.population_df[self.population_df["gender"] == "Male"]
        female_data = self.population_df[self.population_df["gender"] == "Female"]

        return {
            "male_median": male_data["salary"].median() if len(male_data) > 0 else 0,
            "female_median": female_data["salary"].median() if len(female_data) > 0 else 0,
            "pay_gap_percent": self.baseline_metrics["gender_pay_gap_percent"],
            "male_count": len(male_data),
            "female_count": len(female_data),
            "statistical_significance": self._calculate_pay_gap_significance(male_data, female_data),
        }

    def _analyze_level_equity(self) -> Dict:
        """Analyze salary equity by level."""
        level_equity = {}

        for level in sorted(self.population_df["level"].unique()):
            level_data = self.population_df[self.population_df["level"] == level]

            level_equity[level] = {
                "count": len(level_data),
                "median_salary": level_data["salary"].median(),
                "salary_std": level_data["salary"].std(),
                "coefficient_of_variation": (
                    level_data["salary"].std() / level_data["salary"].mean() if level_data["salary"].mean() > 0 else 0
                ),
            }

        return level_equity

    def _analyze_gender_by_level_equity(self) -> Dict:
        """Analyze gender equity within each level."""
        gender_level_equity = {}

        for level in sorted(self.population_df["level"].unique()):
            level_data = self.population_df[self.population_df["level"] == level]
            male_level = level_data[level_data["gender"] == "Male"]
            female_level = level_data[level_data["gender"] == "Female"]

            if len(male_level) > 0 and len(female_level) > 0:
                male_median = male_level["salary"].median()
                female_median = female_level["salary"].median()
                gap_percent = ((male_median - female_median) / male_median) * 100
            else:
                gap_percent = 0.0

            gender_level_equity[level] = {
                "male_count": len(male_level),
                "female_count": len(female_level),
                "male_median": male_level["salary"].median() if len(male_level) > 0 else 0,
                "female_median": female_level["salary"].median() if len(female_level) > 0 else 0,
                "gap_percent": gap_percent,
            }

        return gender_level_equity

    def _calculate_pay_gap_significance(self, male_data: pd.DataFrame, female_data: pd.DataFrame) -> str:
        """Calculate statistical significance of pay gap."""
        if len(male_data) < 5 or len(female_data) < 5:
            return "insufficient_data"

        # Simple significance test based on sample sizes and gap magnitude
        gap_percent = abs(self.baseline_metrics["gender_pay_gap_percent"])

        if gap_percent > 15 and len(male_data) > 10 and len(female_data) > 10:
            return "highly_significant"
        elif gap_percent > 10:
            return "significant"
        elif gap_percent > 5:
            return "moderately_significant"
        else:
            return "not_significant"

    def _analyze_tenure_equity(self) -> Dict:
        """Analyze salary equity by tenure."""
        # Add tenure calculation if not present
        current_date = datetime.now()
        tenure_data = []

        for _, employee in self.population_df.iterrows():
            if "hire_date" in employee and pd.notna(employee["hire_date"]):
                hire_date = datetime.strptime(str(employee["hire_date"]), "%Y-%m-%d")
                tenure_years = (current_date - hire_date).days / 365.25
            else:
                tenure_years = 2.5  # Default

            tenure_data.append(
                {
                    "salary": employee["salary"],
                    "tenure_bracket": (
                        "0-2 years" if tenure_years < 2 else "2-5 years" if tenure_years < 5 else "5+ years"
                    ),
                }
            )

        tenure_df = pd.DataFrame(tenure_data)
        tenure_analysis = {}

        for bracket in ["0-2 years", "2-5 years", "5+ years"]:
            bracket_data = tenure_df[tenure_df["tenure_bracket"] == bracket]
            if len(bracket_data) > 0:
                tenure_analysis[bracket] = {
                    "count": len(bracket_data),
                    "median_salary": bracket_data["salary"].median(),
                    "mean_salary": bracket_data["salary"].mean(),
                }

        return tenure_analysis

    def _calculate_overall_equity_score(self, equity_analysis: Dict) -> float:
        """Calculate overall equity score (0-1, higher is better)."""
        scores = []

        # Gender equity score
        if "gender" in equity_analysis:
            gap_percent = abs(equity_analysis["gender"]["pay_gap_percent"])
            gender_score = max(0, 1 - (gap_percent / 30))  # 30% gap = 0 score
            scores.append(gender_score)

        # Level equity score (based on coefficient of variation)
        if "level" in equity_analysis:
            level_cvs = [data["coefficient_of_variation"] for data in equity_analysis["level"].values()]
            avg_cv = np.mean(level_cvs) if level_cvs else 0
            level_score = max(0, 1 - avg_cv)  # Lower variation = higher score
            scores.append(level_score)

        return np.mean(scores) if scores else 0.5

    def _identify_priority_interventions(self, equity_analysis: Dict) -> List[Dict]:
        """Identify priority interventions based on equity analysis."""
        interventions = []

        # Gender gap intervention
        if "gender" in equity_analysis:
            gap = abs(equity_analysis["gender"]["pay_gap_percent"])
            if gap > 10:
                interventions.append(
                    {
                        "type": "gender_gap_remediation",
                        "priority": "high" if gap > 20 else "medium",
                        "description": f"Address {gap:.1f}% gender pay gap",
                        "estimated_cost_percent": min(0.008, gap * 0.0003),
                    }
                )

        # Level-based interventions
        if "gender_by_level" in equity_analysis:
            for level, data in equity_analysis["gender_by_level"].items():
                if abs(data["gap_percent"]) > 15:
                    interventions.append(
                        {
                            "type": "level_specific_adjustment",
                            "priority": "medium",
                            "description": f'Address Level {level} gender gap ({data["gap_percent"]:.1f}%)',
                            "estimated_cost_percent": 0.001,
                        }
                    )

        return sorted(interventions, key=lambda x: {"high": 3, "medium": 2, "low": 1}[x["priority"]], reverse=True)

    def _create_implementation_plan(self, strategy: Dict) -> List[Dict]:
        """Create detailed implementation plan for recommended strategy."""
        strategy_name = strategy.get("strategy_name", "unknown")
        timeline_years = strategy.get("timeline_years", 1)

        if strategy_name == "immediate_adjustment":
            return [
                {"phase": 1, "timeline_months": 1, "activity": "Legal and HR review of adjustments"},
                {"phase": 2, "timeline_months": 2, "activity": "Employee communication and adjustment implementation"},
                {"phase": 3, "timeline_months": 3, "activity": "Monitor impact and address any issues"},
            ]
        elif "gradual" in strategy_name:
            phases = []
            years = int(timeline_years)
            for year in range(1, years + 1):
                phases.append(
                    {
                        "phase": year,
                        "timeline_months": year * 12,
                        "activity": f"Year {year}: Implement {100/years:.0f}% of salary adjustments",
                    }
                )
            return phases
        elif strategy_name == "natural_convergence":
            return [
                {"phase": 1, "timeline_months": 12, "activity": "Monitor natural progression and market trends"},
                {"phase": 2, "timeline_months": 24, "activity": "Evaluate progress and adjust if needed"},
            ]
        else:
            return [
                {"phase": 1, "timeline_months": 3, "activity": "Strategy planning and approval"},
                {"phase": 2, "timeline_months": 12, "activity": "Implementation and monitoring"},
            ]

    def _calculate_roi_analysis(self, strategy: Dict) -> Dict:
        """Calculate return on investment analysis for strategy."""
        total_cost = strategy.get("total_cost", 0)
        affected_employees = strategy.get("affected_employees", 0)

        # Estimated benefits
        retention_improvement = 0.10 if strategy.get("legal_risk_reduction") == "high" else 0.05
        productivity_gain = 0.05 if affected_employees > 0 else 0
        legal_risk_reduction_value = total_cost * 0.5  # Conservative estimate

        # Calculate annual benefits
        avg_salary = self.baseline_metrics["total_payroll"] / self.baseline_metrics["total_employees"]
        retention_benefit = affected_employees * avg_salary * retention_improvement * 1.5  # 1.5x replacement cost
        productivity_benefit = affected_employees * avg_salary * productivity_gain

        total_annual_benefits = retention_benefit + productivity_benefit

        return {
            "total_investment": total_cost,
            "annual_benefits": total_annual_benefits,
            "payback_years": total_cost / total_annual_benefits if total_annual_benefits > 0 else float("inf"),
            "roi_3_year": ((total_annual_benefits * 3) - total_cost) / total_cost if total_cost > 0 else 0,
            "retention_benefit": retention_benefit,
            "productivity_benefit": productivity_benefit,
            "legal_risk_reduction_value": legal_risk_reduction_value,
        }

    def _assess_implementation_risks(self, strategy: Dict) -> Dict:
        """Assess implementation risks for strategy."""
        risks = []

        if strategy.get("budget_utilization", 0) > 0.8:
            risks.append("high_budget_utilization")

        if strategy.get("affected_employees", 0) > self.baseline_metrics["total_employees"] * 0.3:
            risks.append("large_employee_impact")

        if strategy.get("timeline_years", 0) < 0.5:
            risks.append("aggressive_timeline")

        complexity = strategy.get("implementation_complexity", "medium")
        if complexity == "high":
            risks.append("implementation_complexity")

        return {
            "risk_factors": risks,
            "overall_risk_level": "high" if len(risks) >= 3 else "medium" if len(risks) >= 1 else "low",
            "mitigation_strategies": self._suggest_risk_mitigation(risks),
        }

    def _suggest_risk_mitigation(self, risks: List[str]) -> List[str]:
        """Suggest risk mitigation strategies."""
        mitigations = []

        if "high_budget_utilization" in risks:
            mitigations.append("Consider phased implementation to spread costs")

        if "large_employee_impact" in risks:
            mitigations.append("Implement comprehensive change management and communication plan")

        if "aggressive_timeline" in risks:
            mitigations.append("Build buffer time and have contingency plans")

        if "implementation_complexity" in risks:
            mitigations.append("Engage external consultants and establish project management office")

        return mitigations

    # Placeholder methods for missing functionality
    def _apply_yearly_interventions(self, population: List[Dict], strategy: Dict, year: int) -> List[Dict]:
        """Apply strategy interventions for a specific year."""
        # Placeholder - would implement actual intervention logic
        return population

    def _calculate_yearly_metrics(self, population: List[Dict], year: int) -> Dict:
        """Calculate metrics for a specific year."""
        df = pd.DataFrame(population)
        male_median = df[df["gender"] == "Male"]["salary"].median()
        female_median = df[df["gender"] == "Female"]["salary"].median()
        gap = ((male_median - female_median) / male_median) * 100 if male_median > 0 else 0

        return {"gender_pay_gap_percent": gap, "male_median_salary": male_median, "female_median_salary": female_median}

    def _apply_natural_progression(self, population: List[Dict]) -> List[Dict]:
        """Apply natural salary progression for one year."""
        # Placeholder - would implement natural progression logic
        for employee in population:
            employee["salary"] *= 1.03  # 3% annual increase
        return population

    def _count_affected_employees(self, population: List[Dict], strategy: Dict) -> int:
        """Count employees affected by strategy."""
        return strategy.get("affected_employees", 0)

    def _calculate_long_term_roi(self, timeline: List[Dict]) -> Dict:
        """Calculate long-term ROI metrics."""
        return {"total_roi": 1.5, "annual_roi": 0.3}  # Placeholder

    def _estimate_success_probability(self, strategy: Dict, timeline: List[Dict]) -> float:
        """Estimate probability of strategy success."""
        feasibility_map = {"high": 0.9, "medium": 0.7, "low": 0.5}
        return feasibility_map.get(strategy.get("feasibility", "medium"), 0.7)

    def _calculate_intervention_options(self, intervention_type: str, budget: float) -> Dict:
        """Calculate intervention options for a specific type."""
        return {"cost": budget * 0.25, "impact_score": 0.8}  # Placeholder

    def _optimize_allocation(self, options: Dict, budget: float) -> Dict:
        """Optimize budget allocation across intervention types."""
        return {"allocation": {k: budget / len(options) for k in options.keys()}}  # Placeholder

    def _calculate_allocation_impact(self, allocation: Dict) -> Dict:
        """Calculate expected impact of budget allocation."""
        return {"total_impact_score": 0.85}  # Placeholder

    def _prioritize_interventions(self, allocation: Dict) -> List[str]:
        """Prioritize interventions by impact."""
        return list(allocation.get("allocation", {}).keys())  # Placeholder


    def model_equity_intervention(self, intervention_type: str = "comprehensive_equity", 
                                 budget_constraint: float = 0.005, 
                                 years_to_achieve: int = 5) -> Dict:
        """
        Model comprehensive equity intervention strategies.
        
        Args:
            intervention_type: Type of equity intervention to model
            budget_constraint: Maximum percentage of payroll to spend (default: 0.5%)
            years_to_achieve: Target years to achieve equity
            
        Returns:
            Dict with equity intervention analysis and recommendations
        """
        LOGGER.info(f"Modeling {intervention_type} intervention strategy")
        
        baseline = self._calculate_baseline_metrics()
        total_payroll = baseline["total_payroll"]
        max_budget = total_payroll * budget_constraint
        
        LOGGER.info(f"Budget constraint: £{max_budget:,.0f} ({budget_constraint:.1%} of £{total_payroll:,.0f} payroll)")
        
        # Identify equity gaps across different dimensions
        equity_gaps = self._analyze_comprehensive_equity_gaps()
        
        # Model different intervention approaches
        intervention_approaches = {
            "comprehensive_equity": self._model_comprehensive_equity_approach(equity_gaps, max_budget, years_to_achieve),
            "targeted_adjustment": self._model_targeted_adjustment_approach(equity_gaps, max_budget, years_to_achieve),
            "gradual_remediation": self._model_gradual_remediation_approach(equity_gaps, max_budget, years_to_achieve),
            "performance_based": self._model_performance_based_approach(equity_gaps, max_budget, years_to_achieve)
        }
        
        # Find optimal approach
        optimal_approach = self._select_optimal_equity_approach(intervention_approaches, budget_constraint)
        
        result = {
            "intervention_type": intervention_type,
            "baseline_metrics": baseline,
            "equity_gap_analysis": equity_gaps,
            "intervention_approaches": intervention_approaches,
            "optimal_approach": optimal_approach,
            "budget_constraint": {
                "percentage": budget_constraint,
                "amount": max_budget,
                "total_payroll": total_payroll
            },
            "timeline_years": years_to_achieve
        }
        
        LOGGER.info(f"Optimal approach: {optimal_approach['approach_name']} (£{optimal_approach['total_investment']:,.0f})")
        
        return result

    def _analyze_comprehensive_equity_gaps(self) -> Dict:
        """Analyze equity gaps across multiple dimensions."""
        gaps = {
            "gender_gap": self._calculate_baseline_metrics()["gender_pay_gap_percent"],
            "level_inequities": {},
            "performance_inequities": {},
            "tenure_inequities": {}
        }
        
        # Level-based inequities
        for level in sorted(self.population_df["level"].unique()):
            level_data = self.population_df[self.population_df["level"] == level]
            if len(level_data) > 1:
                salary_std = level_data["salary"].std()
                salary_mean = level_data["salary"].mean()
                cv = (salary_std / salary_mean) * 100 if salary_mean > 0 else 0
                gaps["level_inequities"][level] = {
                    "coefficient_variation": cv,
                    "salary_range": level_data["salary"].max() - level_data["salary"].min(),
                    "employee_count": len(level_data)
                }
        
        return gaps

    def _model_comprehensive_equity_approach(self, equity_gaps: Dict, max_budget: float, years: int) -> Dict:
        """Model comprehensive equity intervention approach."""
        # Address all equity dimensions simultaneously
        total_investment = min(max_budget, max_budget * 0.8)  # Use 80% of budget for comprehensive approach
        affected_employees = len(self.population_df) // 3  # Assume 1/3 of employees affected
        
        return {
            "approach_name": "comprehensive_equity",
            "description": "Address all equity gaps simultaneously across gender, level, and performance dimensions",
            "total_investment": total_investment,
            "affected_employees": affected_employees,
            "timeline_years": years,
            "expected_outcomes": {
                "gender_gap_reduction": min(equity_gaps["gender_gap"] * 0.8, 80),  # 80% reduction or 8pp max
                "level_inequity_reduction": 60,  # 60% reduction in level inequities
                "overall_equity_score": 85  # Target 85% equity score
            },
            "implementation_phases": [
                "Phase 1: Immediate high-priority adjustments (6 months)",
                "Phase 2: Performance-based interventions (18 months)", 
                "Phase 3: Long-term equity maintenance (remaining time)"
            ]
        }

    def _model_targeted_adjustment_approach(self, equity_gaps: Dict, max_budget: float, years: int) -> Dict:
        """Model targeted salary adjustment approach."""
        return {
            "approach_name": "targeted_adjustment",
            "description": "Focus on specific high-impact salary adjustments",
            "total_investment": min(max_budget * 0.6, max_budget),
            "affected_employees": len(self.population_df) // 5,
            "timeline_years": max(2, years - 2),  # Faster implementation
            "expected_outcomes": {
                "gender_gap_reduction": min(equity_gaps["gender_gap"] * 0.6, 60),
                "immediate_impact": "high",
                "sustainable_change": "medium"
            }
        }

    def _model_gradual_remediation_approach(self, equity_gaps: Dict, max_budget: float, years: int) -> Dict:
        """Model gradual remediation approach."""
        return {
            "approach_name": "gradual_remediation", 
            "description": "Spread equity improvements over extended timeline",
            "total_investment": max_budget,  # Use full budget over longer period
            "affected_employees": len(self.population_df) // 2,
            "timeline_years": years + 2,  # Extended timeline
            "expected_outcomes": {
                "gender_gap_reduction": min(equity_gaps["gender_gap"] * 0.9, 90),
                "sustainability": "high",
                "budget_efficiency": "high"
            }
        }

    def _model_performance_based_approach(self, equity_gaps: Dict, max_budget: float, years: int) -> Dict:
        """Model performance-based intervention approach."""
        return {
            "approach_name": "performance_based",
            "description": "Link equity improvements to performance development programs",
            "total_investment": max_budget * 0.7,  # 70% salary adjustments, 30% development
            "affected_employees": len(self.population_df) // 4,
            "timeline_years": years,
            "expected_outcomes": {
                "performance_improvement": "high",
                "equity_improvement": "medium",
                "retention_impact": "high"
            }
        }

    def _select_optimal_equity_approach(self, approaches: Dict, budget_constraint: float) -> Dict:
        """Select the optimal equity approach based on multiple criteria."""
        # Simple scoring based on expected outcomes and feasibility
        scores = {}
        
        for name, approach in approaches.items():
            outcomes = approach.get("expected_outcomes", {})
            
            # Score based on impact and feasibility
            impact_score = 0
            if "gender_gap_reduction" in outcomes:
                impact_score += min(outcomes["gender_gap_reduction"], 100) / 100 * 40
            if "overall_equity_score" in outcomes:
                impact_score += outcomes["overall_equity_score"] / 100 * 30
            
            # Feasibility score based on budget and timeline
            feasibility_score = 0
            if approach["total_investment"] <= budget_constraint * 10000:  # Rough payroll estimate
                feasibility_score += 30
            
            scores[name] = impact_score + feasibility_score
        
        # Select approach with highest score
        optimal_name = max(scores, key=scores.get)
        optimal_approach = approaches[optimal_name].copy()
        optimal_approach["selection_score"] = scores[optimal_name]
        optimal_approach["alternatives"] = {k: v for k, v in scores.items() if k != optimal_name}
        
        return optimal_approach


def main():
    """Main function for testing and validation."""
    parser = argparse.ArgumentParser(description="Intervention Strategy Simulator")
    parser.add_argument("--test-simulation", action="store_true", help="Run test simulation")
    parser.add_argument("--target-gap", type=float, default=0.0, help="Target gender gap percent (default: 0.0)")
    parser.add_argument("--max-years", type=int, default=3, help="Maximum years for intervention (default: 3)")
    parser.add_argument(
        "--budget-limit", type=float, default=0.005, help="Budget limit as % of payroll (default: 0.5%)"
    )
    parser.add_argument("--output-format", choices=["json", "summary"], default="summary", help="Output format")

    args = parser.parse_args()

    if args.test_simulation:
        LOGGER.info("Running test intervention strategy simulation")

        # Create test population with gender pay gap
        from individual_progression_simulator import create_test_employee

        test_population = []

        # Create population with realistic gender pay gap
        # Ensure both genders are represented at each level
        for level in range(1, 7):  # Levels 1-6
            for person_in_level in range(17):  # ~17 people per level (100/6 ≈ 17)
                if person_in_level >= 17:  # Handle the last 4 people for level 6
                    break

                i = (level - 1) * 17 + person_in_level + 1
                if i > 100:
                    break

                base_salary = 30000 + (level * 12000)

                # Alternate gender within each level to ensure both are represented
                if person_in_level % 2 == 0:  # ~50% female per level
                    # Create systematic underpayment pattern for females
                    if person_in_level % 8 == 0:  # Some significantly underpaid
                        salary = base_salary * 0.75  # 25% below base
                    elif person_in_level % 4 == 0:  # Some moderately underpaid
                        salary = base_salary * 0.85  # 15% below base
                    else:  # Others slightly underpaid
                        salary = base_salary * 0.92  # 8% below base
                    gender = "Female"
                else:  # ~50% male per level
                    # Males get salaries at or above base with variation
                    salary = base_salary * np.random.uniform(1.00, 1.20)  # 0-20% above base
                    gender = "Male"

                employee = create_test_employee(
                    employee_id=i,
                    level=level,
                    salary=salary,
                    performance_rating=["Partially met", "Achieving", "High Performing"][i % 3],
                    gender=gender,
                )
                test_population.append(employee)

        # Initialize simulator
        simulator = InterventionStrategySimulator(test_population)

        # Model gender gap remediation
        remediation_result = simulator.model_gender_gap_remediation(
            target_gap_percent=args.target_gap, max_years=args.max_years, budget_constraint=args.budget_limit
        )

        if args.output_format == "json":
            print(json.dumps(remediation_result, indent=2, default=str))
        else:
            # Summary output
            print(f"\n💼 Gender Pay Gap Remediation Analysis")
            print(f"{'='*60}")

            current = remediation_result["current_state"]
            print(f"Current State:")
            print(f"  Gender pay gap: {current['gender_pay_gap_percent']:.1f}%")
            print(f"  Male median: £{current['male_median_salary']:,.2f}")
            print(f"  Female median: £{current['female_median_salary']:,.2f}")
            print(f"  Affected employees: {current['affected_female_employees']}")
            print(f"  Total payroll: £{current['total_payroll']:,.0f}")

            target = remediation_result["target_state"]
            print(f"\nTarget State:")
            print(f"  Target gap: {target['target_gap_percent']:.1f}%")
            print(
                f"  Budget limit: £{target['budget_constraint_amount']:,.0f} ({target['budget_constraint_percent']:.1%})"
            )
            print(f"  Max timeline: {target['max_timeline_years']} years")

            recommended = remediation_result["recommended_strategy"]
            print(f"\n🎯 Recommended Strategy: {recommended['strategy_name']}")
            print(
                f"  Cost: £{recommended['total_cost']:,.0f} ({recommended['cost_as_percent_payroll']:.2%} of payroll)"
            )
            print(f"  Timeline: {recommended['timeline_years']} years")
            print(f"  Affected employees: {recommended['affected_employees']}")
            print(f"  Gap reduction: {recommended['gap_reduction_percent']:.1f}pp")
            print(f"  Final gap: {recommended['projected_final_gap']:.1f}%")
            print(f"  Feasibility: {recommended['feasibility']}")

            print(f"\n📊 Strategy Comparison:")
            for strategy_name, strategy in remediation_result["available_strategies"].items():
                if strategy.get("applicable", True):
                    print(
                        f"  {strategy_name}: £{strategy['total_cost']:,.0f}, "
                        + f"{strategy['timeline_years']}y, "
                        + f"{strategy['gap_reduction_percent']:.1f}pp reduction"
                    )

    else:
        LOGGER.info("Use --test-simulation to run demonstration")
        parser.print_help()


if __name__ == "__main__":
    main()

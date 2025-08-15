#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

import argparse
from datetime import datetime
import json
from typing import Dict, List

import pandas as pd

from employee_population_simulator import UPLIFT_MATRIX
from logger import LOGGER
from salary_forecasting_engine import SalaryForecastingEngine

# Import common utilities to boost coverage


class IndividualProgressionSimulator:
    """
    Individual employee salary progression simulator with multi-year forecasting.

    Provides scenario modeling, performance path generation, and detailed analysis for individual employees including
    confidence intervals and market adjustments.

    Args:

    Returns:
    """

    def __init__(self, population_data: List[Dict], uplift_matrix: Dict = None, config: Dict = None):
        self.population_data = population_data
        self.uplift_matrix = uplift_matrix or UPLIFT_MATRIX
        self.config = config or {}

        # Initialize forecasting engine
        self.forecasting_engine = SalaryForecastingEngine(
            confidence_level=self.config.get("confidence_interval", 0.95),
            market_inflation_rate=self.config.get("market_inflation_rate", 0.04),
        )

        # Calculate population benchmarks
        self.population_df = pd.DataFrame(population_data)
        self.level_medians = self._calculate_level_medians()
        self.market_trends = self._calculate_market_trends()

        LOGGER.info(f"Initialized IndividualProgressionSimulator with {len(population_data)} employees")
        LOGGER.info(f"Level medians: {[f'L{k}: £{v:,.0f}' for k, v in self.level_medians.items()]}")

    def project_salary_progression(
        self, employee_data: Dict, years: int = 5, scenarios: List[str] = None, include_market_adjustments: bool = True
    ) -> Dict:
        """
        Project individual employee salary progression over multiple years.

        Args:
          employee_data: Current employee state (level, salary, performance_rating, etc.)
          years: Number of years to project (default: 5)
          scenarios: Performance scenarios to model (default: conservative, realistic, optimistic)
          include_market_adjustments: Whether to include market adjustment cycles
          employee_data: Dict:
          years: int:  (Default value = 5)
          scenarios: List[str]:  (Default value = None)
          include_market_adjustments: bool:  (Default value = True)

        Returns:
          : Dict with detailed projections for each scenario
        """
        scenarios = scenarios or ["conservative", "realistic", "optimistic"]

        LOGGER.info(f"Projecting salary progression for employee {employee_data.get('employee_id', 'N/A')}")
        LOGGER.info(
            f"Current: Level {employee_data['level']}, £{employee_data['salary']:,.2f}, {employee_data['performance_rating']}"
        )

        projections = {}
        all_projections_list = []  # For confidence intervals

        for scenario in scenarios:
            LOGGER.debug(f"Computing {scenario} scenario")

            # Generate performance path for this scenario
            performance_path = self._generate_performance_path(employee_data, years, scenario)

            # Calculate salary path based on performance
            salary_path = self._calculate_salary_path(employee_data, performance_path)

            # Apply market adjustments if requested
            if include_market_adjustments:
                adjustment_years = self.config.get("market_adjustment_years", [2, 5, 8])  # 0-indexed
                salary_path = self.forecasting_engine.apply_market_adjustments(salary_path, adjustment_years)

            # Calculate derived metrics
            final_salary = salary_path[-1]
            total_increase = final_salary - employee_data["salary"]
            cagr = self.forecasting_engine.calculate_cagr(employee_data["salary"], final_salary, years)

            # Store projection
            projections[scenario] = {
                "salary_progression": salary_path,
                "performance_path": performance_path,
                "final_salary": final_salary,
                "total_increase": total_increase,
                "cagr": cagr,
                "years_projected": years,
            }

            all_projections_list.extend(salary_path)

        # Calculate confidence intervals across all scenarios
        confidence_interval = self.forecasting_engine.calculate_confidence_interval(all_projections_list)

        # Add summary analysis
        result = {
            "employee_id": employee_data.get("employee_id"),
            "current_state": {
                "level": employee_data["level"],
                "salary": employee_data["salary"],
                "performance_rating": employee_data["performance_rating"],
                "gender": employee_data.get("gender"),
                "years_at_company": self._calculate_tenure(employee_data),
            },
            "projections": projections,
            "analysis": {
                "confidence_interval_final": confidence_interval,
                "median_comparison": self._analyze_median_position(employee_data, projections),
                "market_competitiveness": self._analyze_market_competitiveness(employee_data, projections),
                "risk_factors": self._identify_risk_factors(employee_data, projections),
            },
            "recommendations": self._generate_recommendations(employee_data, projections),
        }

        LOGGER.info(
            f"Projection complete. Final salary range: £{min(p['final_salary'] for p in projections.values()):,.0f} - £{max(p['final_salary'] for p in projections.values()):,.0f}"
        )

        return result

    def analyze_multiple_employees(
        self, employee_ids: List[int], years: int = 5, output_format: str = "summary"
    ) -> Dict:
        """
        Analyze salary progression for multiple employees.

        Args:
          employee_ids: List of employee IDs to analyze
          years: Number of years to project
          output_format: 'summary' or 'detailed'
          employee_ids: List[int]:
          years: int:  (Default value = 5)
          output_format: str:  (Default value = "summary")

        Returns:
          : Dict with analysis for all requested employees
        """
        LOGGER.info(f"Analyzing progression for {len(employee_ids)} employees")

        results = {}
        employees_df = self.population_df.set_index("employee_id")

        for employee_id in employee_ids:
            if employee_id not in employees_df.index:
                LOGGER.warning(f"Employee {employee_id} not found in population data")
                continue

            employee_data = employees_df.loc[employee_id].to_dict()
            employee_data["employee_id"] = employee_id

            progression = self.project_salary_progression(employee_data, years)

            if output_format == "summary":
                # Extract key metrics for summary
                results[employee_id] = {
                    "current_salary": progression["current_state"]["salary"],
                    "projected_salary_realistic": progression["projections"]["realistic"]["final_salary"],
                    "cagr_realistic": progression["projections"]["realistic"]["cagr"],
                    "median_status": progression["analysis"]["median_comparison"]["current_status"],
                    "key_recommendation": progression["recommendations"]["primary_action"],
                }
            else:
                results[employee_id] = progression

        LOGGER.info(f"Multi-employee analysis complete for {len(results)} employees")
        return results

    def _generate_performance_path(self, employee_data: Dict, years: int, scenario: str) -> List[str]:
        """
        Generate realistic performance rating progression for specific scenario.

        Uses the existing forecasting engine's scenario generation with adaptations for individual context and career
        stage.

        Args:
          employee_data: Dict:
          years: int:
          scenario: str:

        Returns:
        """
        current_rating = employee_data["performance_rating"]
        level = employee_data["level"]
        tenure = self._calculate_tenure(employee_data)

        # Get base scenarios from forecasting engine
        base_scenarios = self.forecasting_engine.generate_performance_scenarios(current_rating)

        if scenario not in base_scenarios:
            scenario = "realistic"  # Fallback

        base_path = base_scenarios[scenario]

        # Adapt path based on individual context
        adapted_path = self._adapt_performance_path(base_path, level, tenure, years)

        # Ensure path is exactly the right length
        if len(adapted_path) > years:
            adapted_path = adapted_path[:years]
        elif len(adapted_path) < years:
            # Extend with stable performance
            last_rating = adapted_path[-1]
            while len(adapted_path) < years:
                adapted_path.append(last_rating)

        LOGGER.debug(f"Generated {scenario} performance path: {' → '.join(adapted_path)}")
        return adapted_path

    def _adapt_performance_path(self, base_path: List[str], level: int, tenure: float, target_years: int) -> List[str]:
        """
        Adapt base performance path based on individual context.

        Considers career stage, level, and tenure to make realistic adjustments.

        Args:
          base_path: List[str]:
          level: int:
          tenure: float:
          target_years: int:

        Returns:
        """
        adapted_path = base_path.copy()

        # Senior employees (Level 4+) have more stable performance
        if level >= 4:
            # Reduce volatility - less dramatic swings
            for i in range(1, len(adapted_path)):
                prev_rating = adapted_path[i - 1]
                curr_rating = adapted_path[i]

                # Limit rating changes for senior employees
                rating_order = ["Not met", "Partially met", "Achieving", "High Performing", "Exceeding"]
                prev_idx = rating_order.index(prev_rating) if prev_rating in rating_order else 2
                curr_idx = rating_order.index(curr_rating) if curr_rating in rating_order else 2

                # Limit to ±1 rating change per year for senior employees
                if abs(curr_idx - prev_idx) > 1:
                    if curr_idx > prev_idx:
                        adapted_path[i] = rating_order[min(prev_idx + 1, len(rating_order) - 1)]
                    else:
                        adapted_path[i] = rating_order[max(prev_idx - 1, 0)]

        # New employees (tenure < 2 years) may have more growth potential
        if tenure < 2.0 and level <= 3:
            # Slight bias towards improvement for new core employees
            for i in range(len(adapted_path)):
                if adapted_path[i] == "Partially met" and i < len(adapted_path) - 1:
                    adapted_path[i + 1] = "Achieving"  # Accelerate improvement

        # Long-tenure employees (tenure > 5 years) have more stable patterns
        if tenure > 5.0 and len(adapted_path) >= 3:
            for i in range(1, len(adapted_path) - 1):
                prev_rating = adapted_path[i - 1]
                next_rating = adapted_path[i + 1]
                if prev_rating == next_rating:
                    adapted_path[i] = prev_rating  # Smooth intermediate rating

        return adapted_path

    def _calculate_salary_path(self, employee_data: Dict, performance_path: List[str]) -> List[float]:
        """
        Calculate year-by-year salary progression based on performance path.

        Uses UPLIFT_MATRIX calculations with compound growth effects.

        Args:
          employee_data: Dict:
          performance_path: List[str]:

        Returns:
        """
        salary_path = [employee_data["salary"]]  # Start with current salary
        current_salary = employee_data["salary"]
        level = employee_data["level"]

        for year_performance in performance_path:
            # Calculate uplift for this year's performance
            new_salary = self.forecasting_engine.calculate_uplift_increase(current_salary, level, year_performance)

            salary_path.append(new_salary)
            current_salary = new_salary

            LOGGER.debug(f"Year {len(salary_path)-1}: {year_performance} → £{new_salary:,.2f}")

        return salary_path

    def _calculate_level_medians(self) -> Dict[int, float]:
        """
        Calculate median salary by level from population data.
        """
        medians = {}
        for level in sorted(self.population_df["level"].unique()):
            level_data = self.population_df[self.population_df["level"] == level]
            medians[level] = level_data["salary"].median()

        LOGGER.debug(f"Calculated level medians: {medians}")
        return medians

    def _calculate_market_trends(self) -> Dict:
        """
        Calculate market trends and benchmarks from population data.
        """
        return {
            "overall_median": self.population_df["salary"].median(),
            "overall_mean": self.population_df["salary"].mean(),
            "salary_std": self.population_df["salary"].std(),
            "level_ranges": {
                level: {
                    "min": group["salary"].min(),
                    "max": group["salary"].max(),
                    "q25": group["salary"].quantile(0.25),
                    "median": group["salary"].median(),
                    "q75": group["salary"].quantile(0.75),
                }
                for level, group in self.population_df.groupby("level")
            },
        }

    def _calculate_tenure(self, employee_data: Dict) -> float:
        """
        Calculate employee tenure in years.

        Args:
          employee_data: Dict:

        Returns:
        """
        if "hire_date" not in employee_data:
            return 2.5  # Default assumption

        hire_date = datetime.strptime(employee_data["hire_date"], "%Y-%m-%d")
        current_date = datetime.now()
        tenure_days = (current_date - hire_date).days
        return tenure_days / 365.25

    def _analyze_median_position(self, employee_data: Dict, projections: Dict) -> Dict:
        """
        Analyze employee's position relative to level median.

        Args:
          employee_data: Dict:
          projections: Dict:

        Returns:
        """
        current_salary = employee_data["salary"]
        level = employee_data["level"]
        level_median = self.level_medians[level]

        current_gap = current_salary - level_median
        current_gap_percent = (current_gap / level_median) * 100

        # Project median position
        realistic_final = projections["realistic"]["final_salary"]
        final_gap = realistic_final - level_median  # Assumes median stays constant (conservative)
        final_gap_percent = (final_gap / level_median) * 100

        return {
            "current_status": "above_median" if current_gap > 0 else "below_median",
            "current_gap_amount": current_gap,
            "current_gap_percent": current_gap_percent,
            "projected_status": "above_median" if final_gap > 0 else "below_median",
            "projected_gap_amount": final_gap,
            "projected_gap_percent": final_gap_percent,
        }

    def _analyze_market_competitiveness(self, employee_data: Dict, projections: Dict) -> Dict:
        """
        Analyze employee's market competitiveness.

        Args:
          employee_data: Dict:
          projections: Dict:

        Returns:
        """
        level = employee_data["level"]
        level_range = self.market_trends["level_ranges"][level]
        current_salary = employee_data["salary"]
        realistic_final = projections["realistic"]["final_salary"]

        # Current position in level range
        range_span = level_range["max"] - level_range["min"]
        if range_span > 0:
            current_percentile = ((current_salary - level_range["min"]) / range_span) * 100
            # Projected position (assumes range stays constant)
            projected_percentile = ((realistic_final - level_range["min"]) / range_span) * 100
        else:
            # Handle case where min == max (single employee at level)
            current_percentile = 50.0  # Middle of range
            projected_percentile = 50.0

        return {
            "current_percentile": max(0, min(100, current_percentile)),
            "projected_percentile": max(0, min(100, projected_percentile)),
            "current_quartile": self._get_quartile(current_salary, level_range),
            "projected_quartile": self._get_quartile(realistic_final, level_range),
        }

    def _get_quartile(self, salary: float, level_range: Dict) -> str:
        """
        Determine quartile position within level.

        Args:
          salary: float:
          level_range: Dict:

        Returns:
        """
        if salary <= level_range["q25"]:
            return "bottom_quartile"
        elif salary <= level_range["median"]:
            return "second_quartile"
        elif salary <= level_range["q75"]:
            return "third_quartile"
        else:
            return "top_quartile"

    def _identify_risk_factors(self, employee_data: Dict, projections: Dict) -> List[str]:
        """
        Identify potential risk factors for salary progression.

        Args:
          employee_data: Dict:
          projections: Dict:

        Returns:
        """
        risks = []

        # Performance consistency risk
        realistic_path = projections["realistic"]["performance_path"]
        if realistic_path.count("Not met") > 0:
            risks.append("performance_consistency")

        # Below-median risk
        median_analysis = self._analyze_median_position(employee_data, projections)
        if median_analysis["current_status"] == "below_median":
            risks.append("below_median_salary")

        # Low growth risk
        cagr = projections["realistic"]["cagr"]
        if cagr < 0.025:  # Below 2.5% annual growth
            risks.append("low_growth_trajectory")

        # Market competitiveness risk
        market_analysis = self._analyze_market_competitiveness(employee_data, projections)
        if market_analysis["current_percentile"] < 25:
            risks.append("low_market_position")

        # High tenure, low level risk
        tenure = self._calculate_tenure(employee_data)
        level = employee_data["level"]
        if tenure > 5.0 and level <= 3:
            risks.append("career_progression_stagnation")

        return risks

    def _generate_recommendations(self, employee_data: Dict, projections: Dict) -> Dict:
        """
        Generate actionable recommendations based on analysis.

        Args:
          employee_data: Dict:
          projections: Dict:

        Returns:
        """
        risks = self._identify_risk_factors(employee_data, projections)
        recommendations = {
            "primary_action": "monitor_progress",
            "secondary_actions": [],
            "timeline": "next_review_cycle",
            "rationale": "",
        }

        # Below-median salary
        if "below_median_salary" in risks:
            recommendations["primary_action"] = "salary_adjustment_review"
            recommendations["secondary_actions"].append("market_salary_benchmarking")
            recommendations["rationale"] = "Employee is below level median, requires salary review"

        # Performance consistency issues
        if "performance_consistency" in risks:
            recommendations["primary_action"] = "performance_improvement_plan"
            recommendations["secondary_actions"].extend(["skill_development", "mentoring_assignment"])
            recommendations["rationale"] = "Performance inconsistency detected, focus on development"

        # Career stagnation
        if "career_progression_stagnation" in risks:
            recommendations["primary_action"] = "career_development_discussion"
            recommendations["secondary_actions"].extend(["level_promotion_assessment", "role_expansion"])
            recommendations["timeline"] = "immediate"
            recommendations["rationale"] = "Long tenure with limited progression, needs career path review"

        # Low growth trajectory
        if "low_growth_trajectory" in risks:
            recommendations["secondary_actions"].append("performance_expectations_clarification")
            if recommendations["primary_action"] == "monitor_progress":
                recommendations["primary_action"] = "growth_acceleration_plan"

        # Strong performance - positive recommendations
        realistic_cagr = projections["realistic"]["cagr"]
        if realistic_cagr > 0.06 and not risks:  # High growth, no risks
            recommendations["primary_action"] = "recognition_and_retention"
            recommendations["secondary_actions"].extend(["stretch_assignments", "leadership_development"])
            recommendations["rationale"] = "Strong performer with high growth potential"

        return recommendations


def create_test_employee(
    employee_id: int = 123,
    level: int = 5,
    salary: float = 80692.50,
    performance_rating: str = "High Performing",
    gender: str = "Female",
) -> Dict:
    """
    Create test employee data for validation and testing.

    Args:
      employee_id: int:  (Default value = 123)
      level: int:  (Default value = 5)
      salary: float:  (Default value = 80692.50)
      performance_rating: str:  (Default value = "High Performing")
      gender: str:  (Default value = "Female")

    Returns:
    """
    return {
        "employee_id": employee_id,
        "level": level,
        "salary": salary,
        "performance_rating": performance_rating,
        "gender": gender,
        "hire_date": "2021-03-15",
        "review_history": [],
    }


def main():
    """
    Main function for testing and validation.
    """
    parser = argparse.ArgumentParser(description="Individual Employee Progression Simulator")
    parser.add_argument("--test-simulation", action="store_true", help="Run test simulation")
    parser.add_argument("--employee-id", type=int, help="Analyze specific employee")
    parser.add_argument("--years", type=int, default=5, help="Years to project (default: 5)")
    parser.add_argument(
        "--scenarios", nargs="*", default=["conservative", "realistic", "optimistic"], help="Scenarios to model"
    )
    parser.add_argument("--output-format", choices=["json", "summary"], default="summary", help="Output format")

    args = parser.parse_args()

    if args.test_simulation:
        LOGGER.info("Running test simulation with sample employee")

        # Create test population with sample data
        test_population = [
            create_test_employee(
                i,
                level=(i % 6) + 1,
                salary=30000 + (i * 1000),
                performance_rating=["Achieving", "High Performing", "Exceeding"][i % 3],
            )
            for i in range(1, 11)
        ]

        # Initialize simulator
        simulator = IndividualProgressionSimulator(test_population)

        # Test individual progression
        test_employee = create_test_employee()
        result = simulator.project_salary_progression(test_employee, args.years, args.scenarios)

        if args.output_format == "json":
            print(json.dumps(result, indent=2, default=str))
        else:
            # Summary output
            print("\n🧮 Individual Progression Analysis")
            print(f"{'='*50}")
            print(f"Employee ID: {result['employee_id']}")
            print(f"Current: Level {result['current_state']['level']}, £{result['current_state']['salary']:,.2f}")
            print(f"Performance: {result['current_state']['performance_rating']}")
            print("\n📈 5-Year Projections:")

            for scenario, projection in result["projections"].items():
                print(f"  {scenario.capitalize()}: £{projection['final_salary']:,.2f} (CAGR: {projection['cagr']:.2%})")

            print(f"\n💡 Primary Recommendation: {result['recommendations']['primary_action']}")
            print(f"Rationale: {result['recommendations']['rationale']}")

            if result["analysis"]["risk_factors"]:
                print(f"\n⚠️  Risk Factors: {', '.join(result['analysis']['risk_factors'])}")

    else:
        LOGGER.info("Use --test-simulation to run demonstration")
        parser.print_help()


if __name__ == "__main__":
    main()

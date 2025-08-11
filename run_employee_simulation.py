#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

"""
🏢 Employee Simulation Explorer
===============================

A comprehensive tool for generating and analyzing employee populations with
story tracking and advanced salary progression modeling. Designed to find specific
employee cases like:
- Level 5, £80,692.50, Exceeding performance

Run this script to:
1. Generate realistic employee population
2. Track interesting employee stories
3. Display human-readable analysis with narratives
4. Show population distribution graphs
5. Analyze individual salary progression (NEW)
6. Model management intervention strategies (NEW)
7. Generate gender pay gap remediation plans (NEW)
"""

import argparse
import json
from pathlib import Path
import sys
from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import pandas as pd

# Optional seaborn import
try:
    import seaborn as sns

    sns.set_palette("husl")
except ImportError:
    sns = None

# Try to import the orchestrator and new analysis modules
try:
    from employee_simulation_orchestrator import EmployeeSimulationOrchestrator
    from individual_progression_simulator import IndividualProgressionSimulator
    from intervention_strategy_simulator import InterventionStrategySimulator
    from logger import LOGGER
    from median_convergence_analyzer import MedianConvergenceAnalyzer
except ImportError as e:
    print(f"❌ Could not import required modules: {e}")
    print("Make sure you're running from the correct directory")
    sys.exit(1)


class EmployeeStoryExplorer:
    """Interactive employee story explorer with human-readable output."""

    def __init__(self):
        self.population_data = []
        self.tracked_stories = {}
        self.results = {}
        # New analysis components
        self.progression_simulator = None
        self.convergence_analyzer = None
        self.intervention_simulator = None

    def run_simulation(
        self,
        population_size=1000,
        random_seed=42,
        target_salary=80692.50,
        target_level=5,
        level_distribution=None,
        gender_pay_gap_percent=None,
        salary_constraints=None,
    ):
        """Run employee simulation and return human-readable analysis.

        Args:
          population_size:  (Default value = 1000)
          random_seed:  (Default value = 42)
          target_salary:  (Default value = 80692.50)
          target_level:  (Default value = 5)
          level_distribution:  (Default value = None)
          gender_pay_gap_percent:  (Default value = None)
          salary_constraints:  (Default value = None)

        Returns:
        """

        print("🏢 EMPLOYEE SIMULATION & STORY EXPLORER")
        print("=" * 60)
        print("🎯 Looking for employees similar to:")
        print(f"   Level: {target_level}")
        print(f"   Salary: £{target_salary:,.2f}")
        print("   Performance: High/Exceeding")
        print()

        # Configure simulation for clean output
        config = {
            "population_size": population_size,
            "random_seed": random_seed,
            "max_cycles": 3,
            "level_distribution": level_distribution,
            "gender_pay_gap_percent": gender_pay_gap_percent,
            "salary_constraints": salary_constraints,
            # Story tracking enabled
            "enable_story_tracking": True,
            "tracked_employee_count": 20,
            "export_story_data": False,  # No file exports
            # Disable all file generation for clean output
            "generate_interactive_dashboard": False,
            "create_individual_story_charts": False,
            "export_formats": [],  # No exports
            "story_export_formats": [],
            "generate_visualizations": False,
            "export_individual_files": False,
            "export_comprehensive_report": False,
            "generate_summary_report": False,
            # Minimal logging
            "log_level": "WARNING",  # Reduce noise
            "enable_progress_bar": False,
        }

        try:
            print("🔄 Generating employee population and running simulation...")
            orchestrator = EmployeeSimulationOrchestrator(config=config)

            # Get results - handle the orchestrator's return format
            raw_results = orchestrator.run_with_story_tracking()

            # Extract data safely regardless of return type
            if isinstance(raw_results, tuple):
                # If it returns a tuple, take the first element
                self.results = raw_results[0] if raw_results else {}
            else:
                self.results = raw_results or {}

            # Get population data from file if not in results
            self.population_data = self.results.get("population_data", [])

            if not self.population_data:
                # Try to load from generated files
                files = self.results.get("files_generated", {})
                pop_file = files.get("population")
                if pop_file and Path(pop_file).exists():
                    import json

                    with open(pop_file, "r") as f:
                        self.population_data = json.load(f)

            # Get tracked stories
            self.tracked_stories = self.results.get("employee_stories", {})

            print("✅ Simulation completed successfully!")
            print()

            # Initialize new analysis components
            self._initialize_analysis_components()

            # Generate analysis
            self._analyze_population(target_salary, target_level)
            self._analyze_tracked_stories()
            self._create_visualizations()

            return True

        except Exception as e:
            print(f"❌ Simulation failed: {e}")
            import traceback

            traceback.print_exc()
            return False

    def _analyze_population(self, target_salary, target_level):
        """Analyze the generated population with human narrative.

        Args:
          target_salary:
          target_level:

        Returns:
        """

        if not self.population_data:
            print("❌ No population data available for analysis")
            return

        df = pd.DataFrame(self.population_data)

        print("📊 POPULATION ANALYSIS")
        print("-" * 40)
        print(f"Generated {len(df)} employees across {df['level'].nunique()} levels")
        print()

        # Level distribution
        print("👥 Level Distribution:")
        level_dist = df["level"].value_counts().sort_index()
        for level, count in level_dist.items():
            pct = (count / len(df)) * 100
            print(f"   Level {level}: {count:,} employees ({pct:.1f}%)")
        print()

        # Target level analysis
        target_employees = df[df["level"] == target_level]
        print(f"🎯 Level {target_level} Employee Analysis:")
        print(f"   Total Level {target_level} employees: {len(target_employees)}")

        if len(target_employees) > 0:
            # Salary analysis
            salaries = target_employees["salary"]
            print(f"   Salary range: £{salaries.min():,.0f} - £{salaries.max():,.0f}")
            print(f"   Average salary: £{salaries.mean():,.0f}")
            print(f"   Median salary: £{salaries.median():,.0f}")

            # Target salary comparison
            diff_from_avg = target_salary - salaries.mean()
            pct_diff = (diff_from_avg / salaries.mean()) * 100
            print(f"   Target £{target_salary:,.0f} vs average: {pct_diff:+.1f}% ({diff_from_avg:+,.0f})")
            print()

            # Performance distribution
            print("   Performance Distribution:")
            perf_dist = target_employees["performance_rating"].value_counts()
            for perf, count in perf_dist.items():
                pct = (count / len(target_employees)) * 100
                print(f"     {perf}: {count} ({pct:.1f}%)")
            print()

            # Find closest matches
            target_employees_copy = target_employees.copy()
            target_employees_copy["salary_diff"] = abs(target_employees_copy["salary"] - target_salary)
            closest_matches = target_employees_copy.nsmallest(5, "salary_diff")

            print(f"💎 Closest Matches to Level {target_level}, £{target_salary:,.0f}:")
            for i, (_, emp) in enumerate(closest_matches.iterrows(), 1):
                diff = emp["salary_diff"]
                print(f"   {i}. Employee {emp['employee_id']}:")
                print(f"      Salary: £{emp['salary']:,.0f} (±£{diff:.0f})")
                print(f"      Performance: {emp['performance_rating']}")
                print(f"      Gender: {emp['gender']}")

                if is_tracked := self._is_employee_tracked(emp["employee_id"]):
                    print(f"      📚 TRACKED: {is_tracked}")
                print()

        # Gender analysis
        print("⚖️ Gender Pay Analysis:")
        gender_stats = df.groupby("gender")["salary"].agg(["mean", "median", "count"])
        for gender, stats in gender_stats.iterrows():
            print(f"   {gender}: {stats['count']} employees, avg £{stats['mean']:,.0f}, median £{stats['median']:,.0f}")

        if len(gender_stats) >= 2:
            gap = abs(gender_stats["median"].iloc[0] - gender_stats["median"].iloc[1])
            higher_gender = gender_stats["median"].idxmax()
            gap_pct = (gap / gender_stats["median"].max()) * 100
            print(f"   Gender pay gap: £{gap:.0f} ({gap_pct:.1f}%) favoring {higher_gender}")
        print()

    def _is_employee_tracked(self, employee_id):
        """Check if an employee is being tracked and return category.

        Args:
          employee_id:

        Returns:
        """
        for category, stories in self.tracked_stories.items():
            for story in stories:
                story_emp_id = getattr(story, "employee_id", None) or story.get("employee_id")
                if story_emp_id == employee_id:
                    return category.replace("_", " ").title()
        return None

    def _analyze_tracked_stories(self):
        """Analyze tracked employee stories with narrative."""

        if not self.tracked_stories:
            print("📚 No employee stories tracked")
            return

        total_tracked = sum(len(stories) for stories in self.tracked_stories.values())
        print("📚 TRACKED EMPLOYEE STORIES")
        print("-" * 40)
        print(f"Identified {total_tracked} employees across {len(self.tracked_stories)} categories:")
        print()

        for category, stories in self.tracked_stories.items():
            if not stories:
                continue

            category_name = category.replace("_", " ").title()
            print(f"🏷️ {category_name} ({len(stories)} employees):")

            # Category description
            descriptions = {
                "high_performer": "Top performers with exceptional ratings or salaries",
                "above_range": "Employees with salaries significantly above their level average",
                "gender_gap_affected": "Employees in groups with notable gender pay disparities",
            }

            desc = descriptions.get(category, "Employees meeting specific tracking criteria")
            print(f"   📝 {desc}")

            # Show a few examples
            for i, story in enumerate(stories[:3], 1):
                story_data = story.__dict__ if hasattr(story, "__dict__") else story
                emp_id = story_data.get("employee_id", "Unknown")
                current_salary = story_data.get("current_salary", 0)

                # Find employee in population for more details
                if self.population_data:
                    emp_detail = next((emp for emp in self.population_data if emp["employee_id"] == emp_id), {})
                    level = emp_detail.get("level", "Unknown")
                    performance = emp_detail.get("performance_rating", "Unknown")
                    gender = emp_detail.get("gender", "Unknown")

                    print(f"   {i}. Employee {emp_id}: Level {level}, £{current_salary:,.0f}, {performance}, {gender}")

            if len(stories) > 3:
                print(f"   ... and {len(stories) - 3} more employees")
            print()

    def _create_visualizations(self):
        """Create population distribution visualizations."""

        if not self.population_data:
            print("📊 No data available for visualizations")
            return

        print("📊 POPULATION VISUALIZATIONS")
        print("-" * 40)

        df = pd.DataFrame(self.population_data)

        # Set up the plotting style
        plt.style.use("default")
        if sns:
            sns.set_palette("husl")

        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle("Employee Population Analysis", fontsize=16, fontweight="bold")

        # 1. Salary distribution by level
        if sns:
            sns.boxplot(data=df, x="level", y="salary", ax=axes[0, 0])
        else:
            # Fallback to matplotlib boxplot
            level_groups = [group["salary"].values for name, group in df.groupby("level")]
            axes[0, 0].boxplot(level_groups)
            axes[0, 0].set_xticks(range(1, len(sorted(df["level"].unique())) + 1))
            axes[0, 0].set_xticklabels(sorted(df["level"].unique()))
        axes[0, 0].set_title("Salary Distribution by Level")
        axes[0, 0].set_ylabel("Salary (£)")
        axes[0, 0].set_xlabel("Level")
        axes[0, 0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"£{x/1000:.0f}K"))

        # 2. Performance rating distribution
        perf_counts = df["performance_rating"].value_counts()
        axes[0, 1].pie(perf_counts.values, labels=perf_counts.index, autopct="%1.1f%%", startangle=90)
        axes[0, 1].set_title("Performance Rating Distribution")

        # 3. Salary vs Performance
        perf_order = ["Not met", "Partially met", "Achieving", "High Performing", "Exceeding"]
        perf_numeric = df["performance_rating"].map({perf: i for i, perf in enumerate(perf_order)})

        scatter = axes[1, 0].scatter(perf_numeric, df["salary"], c=df["level"], cmap="viridis", alpha=0.6)
        axes[1, 0].set_title("Salary vs Performance Rating")
        axes[1, 0].set_xlabel("Performance Rating")
        axes[1, 0].set_ylabel("Salary (£)")
        axes[1, 0].set_xticks(range(len(perf_order)))
        axes[1, 0].set_xticklabels(perf_order, rotation=45)
        axes[1, 0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"£{x/1000:.0f}K"))

        cbar = plt.colorbar(scatter, ax=axes[1, 0])
        cbar.set_label("Level")

        # 4. Gender distribution by level
        gender_level = pd.crosstab(df["level"], df["gender"])
        gender_level.plot(kind="bar", ax=axes[1, 1], stacked=True)
        axes[1, 1].set_title("Gender Distribution by Level")
        axes[1, 1].set_xlabel("Level")
        axes[1, 1].set_ylabel("Number of Employees")
        axes[1, 1].legend(title="Gender")
        axes[1, 1].tick_params(axis="x", rotation=0)

        plt.tight_layout()

        # Save the plot
        plot_path = Path("employee_population_analysis.png")
        plt.savefig(plot_path, dpi=300, bbox_inches="tight")
        plt.show()

        print(f"📈 Population analysis chart saved as: {plot_path}")
        print()

        # Print key insights
        print("🔍 KEY INSIGHTS:")

        # Salary insight
        salary_by_level = df.groupby("level")["salary"].mean()
        highest_paid_level = salary_by_level.idxmax()
        print(f"• Highest average salary: Level {highest_paid_level} (£{salary_by_level.max():,.0f})")

        # Performance insight
        exceeding_count = len(df[df["performance_rating"] == "Exceeding"])
        exceeding_pct = (exceeding_count / len(df)) * 100
        print(f"• Exceeding performers: {exceeding_count} employees ({exceeding_pct:.1f}%)")

        # Gender insight
        gender_counts = df["gender"].value_counts()
        male_pct = (gender_counts.get("Male", 0) / len(df)) * 100
        print(f"• Gender split: {male_pct:.1f}% Male, {100-male_pct:.1f}% Female")

        # Tracked insight
        if self.tracked_stories:
            total_tracked = sum(len(stories) for stories in self.tracked_stories.values())
            tracked_pct = (total_tracked / len(df)) * 100
            print(f"• Story tracking: {total_tracked} employees ({tracked_pct:.1f}%) identified as interesting cases")

    def _initialize_analysis_components(self):
        """Initialize advanced analysis components with population data."""
        if not self.population_data:
            LOGGER.warning("No population data available for advanced analysis")
            return

        try:
            self.progression_simulator = IndividualProgressionSimulator(self.population_data)
            self.convergence_analyzer = MedianConvergenceAnalyzer(self.population_data)
            self.intervention_simulator = InterventionStrategySimulator(self.population_data)
            LOGGER.info("Advanced analysis components initialized")
        except Exception as e:
            LOGGER.error(f"Failed to initialize analysis components: {e}")

    def analyze_individual_progression(
        self, employee_id: int, years: int = 5, scenarios: List[str] = None
    ) -> Optional[Dict]:
        """Analyze individual employee salary progression.

        Args:
          employee_id: int:
          years: int:  (Default value = 5)
          scenarios: List[str]:  (Default value = None)

        Returns:
        """
        if not self.progression_simulator:
            print("❌ Individual progression analysis not available. Run simulation first.")
            return None

        # Find employee in population
        employee = next((emp for emp in self.population_data if emp["employee_id"] == employee_id), None)
        if not employee:
            print(f"❌ Employee {employee_id} not found in population")
            return None

        print("\n📈 INDIVIDUAL SALARY PROGRESSION ANALYSIS")
        print(f"={'='*60}")
        print(f"Analyzing Employee {employee_id}...")

        try:
            result = self.progression_simulator.project_salary_progression(
                employee, years=years, scenarios=scenarios or ["conservative", "realistic", "optimistic"]
            )

            # Display key results
            current = result["current_state"]
            projections = result["projections"]

            print("\n👤 CURRENT STATE:")
            print(f"   Level: {current['level']}")
            print(f"   Salary: £{current['salary']:,.2f}")
            print(f"   Performance: {current['performance_rating']}")
            print(f"   Gender: {current.get('gender', 'N/A')}")

            print(f"\n🎯 PROJECTIONS ({years}-YEAR):")
            for scenario, data in projections.items():
                cagr_pct = data["cagr"] * 100
                print(f"   {scenario.title()}: £{data['final_salary']:,.2f} (CAGR: {cagr_pct:.1f}%)")

            # Recommendations
            rec = result["recommendations"]
            print(f"\n💡 RECOMMENDATION: {rec['primary_action'].replace('_', ' ').title()}")
            if rec["rationale"]:
                print(f"   Rationale: {rec['rationale']}")

            return result

        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return None

    def analyze_median_convergence(self, min_gap_percent: float = 5.0) -> Optional[Dict]:
        """Analyze median salary convergence for below-median employees.

        Args:
          min_gap_percent: float:  (Default value = 5.0)

        Returns:
        """
        if not self.convergence_analyzer:
            print("❌ Median convergence analysis not available. Run simulation first.")
            return None

        print("\n📊 MEDIAN CONVERGENCE ANALYSIS")
        print(f"={'='*60}")
        print(f"Analyzing employees >{min_gap_percent}% below level median...")

        try:
            below_median_result = self.convergence_analyzer.identify_below_median_employees(
                min_gap_percent=min_gap_percent, include_gender_analysis=True
            )

            stats = below_median_result["summary_statistics"]
            print("\n📈 SUMMARY:")
            print(f"   Below-median employees: {below_median_result['below_median_count']} ")
            print(f"   ({below_median_result['below_median_percent']:.1f}% of population)")
            print(f"   Average gap: £{stats['average_gap_amount']:,.2f} ({stats['average_gap_percent']:.1f}%)")
            print(f"   Total gap amount: £{stats['total_gap_amount']:,.2f}")

            if "gender_analysis" in below_median_result:
                gender_analysis = below_median_result["gender_analysis"]
                print("\n👥 GENDER BREAKDOWN:")
                for gender, data in gender_analysis.items():
                    if gender not in ["gender_disparity", "disparity_significant"]:
                        print(f"   {gender}: {data['count']} employees (avg gap: {data['average_gap_percent']:.1f}%)")

            # Get intervention recommendations
            intervention_rec = self.convergence_analyzer.recommend_intervention_strategies(below_median_result)
            rec_strategy = intervention_rec["recommended_strategy"]

            print("\n💡 RECOMMENDED INTERVENTION:")
            print(f"   Strategy: {rec_strategy['primary_strategy'].replace('_', ' ').title()}")
            print(f"   Budget required: £{rec_strategy['total_budget_required']:,.2f}")
            print(f"   Affected employees: {rec_strategy['strategy_details']['affected_employees']}")

            return {"below_median_analysis": below_median_result, "intervention_recommendations": intervention_rec}

        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return None

    def model_gender_gap_remediation(
        self, target_gap: float = 0.0, max_years: int = 3, budget_limit: float = 0.5
    ) -> Optional[Dict]:
        """Model gender pay gap remediation strategies.

        Args:
          target_gap: float:  (Default value = 0.0)
          max_years: int:  (Default value = 3)
          budget_limit: float:  (Default value = 0.5)

        Returns:
        """
        if not self.intervention_simulator:
            print("❌ Gender gap remediation modeling not available. Run simulation first.")
            return None

        print("\n💼 GENDER PAY GAP REMEDIATION ANALYSIS")
        print(f"={'='*60}")
        print(
            f"Target gap: {target_gap:.1f}%, Max timeline: {max_years} years, Budget limit: {budget_limit:.1f}% of payroll"
        )

        try:
            result = self.intervention_simulator.model_gender_gap_remediation(
                target_gap_percent=target_gap, max_years=max_years, budget_constraint=budget_limit / 100.0
            )

            current = result["current_state"]
            recommended = result["recommended_strategy"]

            print("\n📊 CURRENT STATE:")
            print(f"   Gender pay gap: {current['gender_pay_gap_percent']:.1f}%")
            print(f"   Affected female employees: {current['affected_female_employees']}")
            print(f"   Total payroll: £{current['total_payroll']:,.2f}")

            print("\n✅ RECOMMENDED STRATEGY:")
            print(f"   Strategy: {recommended['strategy_name'].replace('_', ' ').title()}")
            print(
                f"   Total cost: £{recommended['total_cost']:,.2f} ({recommended['cost_as_percent_payroll']*100:.2f}% of payroll)"
            )
            print(f"   Timeline: {recommended['timeline_years']} years")
            print(f"   Gap reduction: {recommended['gap_reduction_percent']:.1f}%")
            print(f"   Final gap: {recommended['projected_final_gap']:.1f}%")

            # ROI Analysis
            roi = result["roi_analysis"]
            print("\n💰 ROI ANALYSIS:")
            print(f"   Investment: £{roi['total_investment']:,.2f}")
            print(f"   Payback period: {roi['payback_years']:.1f} years")
            print(f"   3-year ROI: {roi['roi_3_year']*100:.1f}%")

            return result

        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return None


def main():
    """Main execution function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Employee Simulation Explorer with Advanced Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic simulation with default scenario
  python run_employee_simulation.py

  # Individual progression analysis
  python run_employee_simulation.py --analyze-individual 123

  # Median convergence analysis
  python run_employee_simulation.py --analyze-convergence --min-gap 10.0

  # Gender gap remediation modeling
  python run_employee_simulation.py --model-gender-gap --target-gap 0.0 --budget-limit 0.5

  # Custom population with analysis
  python run_employee_simulation.py --population-size 2000 --analyze-individual 456 --years 10
        """,
    )

    # Population generation parameters
    parser.add_argument("--population-size", type=int, default=1000, help="Population size to generate (default: 1000)")
    parser.add_argument(
        "--random-seed", type=int, default=42, help="Random seed for reproducible results (default: 42)"
    )
    parser.add_argument(
        "--target-salary", type=float, default=80692.50, help="Target salary for analysis focus (default: 80692.50)"
    )
    parser.add_argument("--target-level", type=int, default=5, help="Target level for analysis focus (default: 5)")
    parser.add_argument(
        "--gender-pay-gap", type=float, default=15.8, help="Gender pay gap percentage to simulate (default: 15.8)"
    )

    # Advanced analysis options
    parser.add_argument(
        "--analyze-individual", type=int, metavar="EMPLOYEE_ID", help="Analyze individual employee salary progression"
    )
    parser.add_argument("--years", type=int, default=5, help="Years for progression analysis (default: 5)")
    parser.add_argument(
        "--scenarios",
        nargs="*",
        choices=["conservative", "realistic", "optimistic"],
        default=["conservative", "realistic", "optimistic"],
        help="Scenarios for progression modeling",
    )

    parser.add_argument("--analyze-convergence", action="store_true", help="Analyze median salary convergence")
    parser.add_argument(
        "--min-gap", type=float, default=5.0, help="Minimum gap percentage for convergence analysis (default: 5.0)"
    )

    parser.add_argument("--model-gender-gap", action="store_true", help="Model gender pay gap remediation strategies")
    parser.add_argument("--target-gap", type=float, default=0.0, help="Target gender gap percentage (default: 0.0)")
    parser.add_argument("--max-years", type=int, default=3, help="Maximum years for intervention (default: 3)")
    parser.add_argument(
        "--budget-limit", type=float, default=0.5, help="Budget limit as percentage of payroll (default: 0.5)"
    )

    # Output options
    parser.add_argument("--no-visualizations", action="store_true", help="Skip generating visualizations")
    parser.add_argument("--quiet", action="store_true", help="Reduce output verbosity")
    parser.add_argument("--output-json", action="store_true", help="Output analysis results in JSON format")

    # Backwards compatibility - run example scenarios when no args provided
    if len(sys.argv) == 1:
        run_example_scenarios()
        return

    args = parser.parse_args()

    explorer = EmployeeStoryExplorer()

    # Configure scenario based on arguments
    scenario = {
        "population_size": args.population_size,
        "random_seed": args.random_seed,
        "target_salary": args.target_salary,
        "target_level": args.target_level,
        "gender_pay_gap_percent": args.gender_pay_gap,
    }

    if not args.quiet:
        print(f"\n{'='*80}")
        print("🏢 EMPLOYEE SIMULATION EXPLORER - ADVANCED ANALYSIS")
        print(f"{'='*80}")
        print(f"Population: {args.population_size:,} employees")
        print(f"Analysis focus: Level {args.target_level}, £{args.target_salary:,.2f}")
        if args.analyze_individual:
            print(f"Individual analysis: Employee {args.analyze_individual} ({args.years}-year projection)")
        if args.analyze_convergence:
            print(f"Convergence analysis: >{args.min_gap}% below median")
        if args.model_gender_gap:
            print(f"Gender gap modeling: {args.target_gap}% target, {args.budget_limit}% budget")
        print(f"{'='*80}")

    # Run simulation
    success = explorer.run_simulation(**scenario)

    if not success:
        print("❌ Simulation failed")
        sys.exit(1)

    # Run advanced analysis based on arguments
    analysis_results = {}

    # Individual progression analysis
    if args.analyze_individual:
        if not args.quiet:
            print("\n🔍 Running individual progression analysis...")
        if result := explorer.analyze_individual_progression(
            args.analyze_individual, years=args.years, scenarios=args.scenarios
        ):
            analysis_results["individual_progression"] = result

    # Median convergence analysis
    if args.analyze_convergence:
        if not args.quiet:
            print("\n🔍 Running median convergence analysis...")
        if result := explorer.analyze_median_convergence(min_gap_percent=args.min_gap):
            analysis_results["median_convergence"] = result

    # Gender gap remediation modeling
    if args.model_gender_gap:
        if not args.quiet:
            print("\n🔍 Running gender gap remediation modeling...")
        if result := explorer.model_gender_gap_remediation(
            target_gap=args.target_gap,
            max_years=args.max_years,
            budget_limit=args.budget_limit,
        ):
            analysis_results["gender_gap_remediation"] = result

    # Output results
    if args.output_json and analysis_results:
        print("\n" + json.dumps(analysis_results, indent=2, default=str))

    # Create comprehensive report
    if not args.quiet:
        create_comprehensive_report(explorer, scenario, analysis_results)

    if not args.quiet:
        print("\n🎉 Employee Simulation and Analysis Complete!")
        print("📝 Check 'comprehensive_employee_analysis.md' for detailed analysis")
        if not args.no_visualizations:
            print("📊 Check 'employee_population_analysis.png' for visualizations")


def run_example_scenarios():
    """Run example scenarios for backwards compatibility."""
    print("🏢 EMPLOYEE SIMULATION EXPLORER")
    print("=" * 60)
    print("Running example scenarios...")
    print("💡 Use --help to see advanced analysis options!")
    print()

    explorer = EmployeeStoryExplorer()

    # Run with different scenarios - uncomment as needed
    scenarios = [
        {"population_size": 1000, "random_seed": 42, "target_salary": 80692.50, "target_level": 5},
        # Uncomment to run additional scenarios:
        # Example with level skewing - more Level 3 employees
        # {'population_size': 1000, 'random_seed': 42, 'target_salary': 80692.50, 'target_level': 5,
        #  'level_distribution': [0.20, 0.20, 0.35, 0.10, 0.10, 0.05]},  # 35% Level 3 vs 20% default
        # Example with 2024 UK gender pay gap simulation
        # {'population_size': 1000, 'random_seed': 42, 'target_salary': 80692.50, 'target_level': 5,
        #  'gender_pay_gap_percent': 15.8},  # 2024 UK average
        # Combined example: level skewing + gender pay gap
        # {'population_size': 1000, 'random_seed': 42, 'target_salary': 80692.50, 'target_level': 5,
        #  'level_distribution': [0.20, 0.20, 0.35, 0.10, 0.10, 0.05],
        #  'gender_pay_gap_percent': 15.8},
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{'='*60}")
        print(f"SCENARIO {i}: Population {scenario['population_size']:,}, Seed {scenario['random_seed']}")
        print(f"{'='*60}")

        success = explorer.run_simulation(**scenario)

        if not success:
            print(f"❌ Scenario {i} failed")
            continue

        # Create markdown report
        create_markdown_report(explorer, scenario)

        # Option to continue or exit
        if i < len(scenarios):
            try:
                response = input("\n🤔 Try another scenario? (y/n): ").strip().lower()
                if response != "y":
                    break
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user")
                break

    print("\n🎉 Employee Story Exploration Complete!")
    print("📝 Check 'employee_analysis_report.md' for detailed narrative analysis")
    print("📊 Check 'employee_population_analysis.png' for population visualizations")


def create_comprehensive_report(explorer, scenario, analysis_results):
    """Create a comprehensive markdown report with all analysis results.

    Args:
      explorer:
      scenario:
      analysis_results:

    Returns:
    """

    report_path = Path("comprehensive_employee_analysis.md")

    with open(report_path, "w") as f:
        f.write("# Comprehensive Employee Analysis Report\n\n")
        f.write("## Executive Summary\n\n")
        f.write(
            f"This comprehensive analysis examines a simulated employee population of {scenario['population_size']:,} employees "
            f"generated with random seed {scenario['random_seed']}. The analysis includes population overview, "
            f"story tracking, and advanced salary progression modeling.\n\n"
        )

        if analysis_results:
            f.write("### Advanced Analysis Completed\n\n")
            if "individual_progression" in analysis_results:
                emp_id = analysis_results["individual_progression"].get("employee_id", "N/A")
                f.write(f"- **Individual Progression Analysis**: Employee {emp_id}\n")
            if "median_convergence" in analysis_results:
                convergence = analysis_results["median_convergence"]["below_median_analysis"]
                f.write(
                    f"- **Median Convergence Analysis**: {convergence['below_median_count']} employees below median\n"
                )
            if "gender_gap_remediation" in analysis_results:
                gap_data = analysis_results["gender_gap_remediation"]["current_state"]
                f.write(f"- **Gender Gap Remediation**: {gap_data['gender_pay_gap_percent']:.1f}% current gap\n")
            f.write("\n")

        # Standard population analysis
        if explorer.population_data:
            df = pd.DataFrame(explorer.population_data)

            f.write("## Key Findings\n\n")

            # Population overview
            f.write(f"### Population Overview\n")
            f.write(f"- **Total Employees**: {len(df):,}\n")
            f.write(f"- **Organizational Levels**: {df['level'].nunique()}\n")
            f.write(f"- **Salary Range**: £{df['salary'].min():,.0f} - £{df['salary'].max():,.0f}\n")
            f.write(f"- **Average Salary**: £{df['salary'].mean():,.0f}\n\n")

            # Target level analysis
            target_employees = df[df["level"] == scenario["target_level"]]
            if len(target_employees) > 0:
                f.write(f"### Level {scenario['target_level']} Analysis\n")
                f.write(
                    f"- **Population**: {len(target_employees)} employees ({len(target_employees)/len(df)*100:.1f}% of total)\n"
                )
                f.write(
                    f"- **Salary Range**: £{target_employees['salary'].min():,.0f} - £{target_employees['salary'].max():,.0f}\n"
                )
                f.write(f"- **Average Salary**: £{target_employees['salary'].mean():,.0f}\n")

                # Performance breakdown
                perf_dist = target_employees["performance_rating"].value_counts()
                f.write(f"- **Performance Distribution**:\n")
                for perf, count in perf_dist.items():
                    pct = (count / len(target_employees)) * 100
                    f.write(f"  - {perf}: {count} employees ({pct:.1f}%)\n")
                f.write("\n")

        # Advanced analysis results section would continue here...
        f.write("## Methodology\n\n")
        f.write("This analysis uses a sophisticated employee simulation system with advanced analytics.\n")

        f.write("---\n")
        f.write("*Report generated by Employee Simulation Explorer with Advanced Analysis*\n")

    print(f"📝 Comprehensive analysis report saved as: {report_path}")


def create_markdown_report(explorer, scenario):
    """Create a markdown report with narrative analysis.

    Args:
      explorer:
      scenario:

    Returns:
    """

    report_path = Path("employee_analysis_report.md")

    with open(report_path, "w") as f:
        f.write("# Employee Population Analysis Report\n\n")
        f.write("## Executive Summary\n\n")
        f.write(
            f"This analysis examines a simulated employee population of {scenario['population_size']:,} employees "
            f"generated with random seed {scenario['random_seed']}. The simulation focuses on identifying "
            f"employees with profiles similar to: **Level {scenario['target_level']}, £{scenario['target_salary']:,.0f} salary, "
            f"with high performance ratings**.\n\n"
        )

        if explorer.population_data:
            df = pd.DataFrame(explorer.population_data)

            f.write("## Key Findings\n\n")

            # Population overview
            f.write(f"### Population Overview\n")
            f.write(f"- **Total Employees**: {len(df):,}\n")
            f.write(f"- **Organizational Levels**: {df['level'].nunique()}\n")
            f.write(f"- **Salary Range**: £{df['salary'].min():,.0f} - £{df['salary'].max():,.0f}\n")
            f.write(f"- **Average Salary**: £{df['salary'].mean():,.0f}\n\n")

            # Target level analysis
            target_employees = df[df["level"] == scenario["target_level"]]
            if len(target_employees) > 0:
                f.write(f"### Level {scenario['target_level']} Analysis\n")
                f.write(
                    f"- **Population**: {len(target_employees)} employees ({len(target_employees)/len(df)*100:.1f}% of total)\n"
                )
                f.write(
                    f"- **Salary Range**: £{target_employees['salary'].min():,.0f} - £{target_employees['salary'].max():,.0f}\n"
                )
                f.write(f"- **Average Salary**: £{target_employees['salary'].mean():,.0f}\n")

                # Performance breakdown
                perf_dist = target_employees["performance_rating"].value_counts()
                f.write(f"- **Performance Distribution**:\n")
                for perf, count in perf_dist.items():
                    pct = (count / len(target_employees)) * 100
                    f.write(f"  - {perf}: {count} employees ({pct:.1f}%)\n")
                f.write("\n")

        # Story tracking results
        if explorer.tracked_stories:
            f.write("## Story Tracking Results\n\n")
            f.write("The system identified several employees with interesting career patterns:\n\n")

            for category, stories in explorer.tracked_stories.items():
                if stories:
                    category_name = category.replace("_", " ").title()
                    f.write(f"### {category_name}\n")
                    f.write(f"Identified **{len(stories)} employees** in this category.\n\n")

        f.write("## Methodology\n\n")
        f.write("This analysis uses a sophisticated employee simulation system that:\n")
        f.write("1. Generates realistic employee populations with appropriate salary distributions\n")
        f.write("2. Applies performance review cycles with career progression\n")
        f.write("3. Identifies employees with interesting patterns (high performers, outliers, etc.)\n")
        f.write("4. Tracks individual employee stories across multiple review cycles\n\n")

        f.write("## Visualizations\n\n")
        f.write("See `employee_population_analysis.png` for comprehensive visual analysis including:\n")
        f.write("- Salary distribution by organizational level\n")
        f.write("- Performance rating distribution\n")
        f.write("- Correlation between salary and performance\n")
        f.write("- Gender distribution across levels\n\n")

        f.write("---\n")
        f.write("*Report generated by Employee Story Explorer*\n")

    print(f"📝 Detailed analysis report saved as: {report_path}")


if __name__ == "__main__":
    main()

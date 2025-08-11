#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

import pandas as pd
import argparse
import json
import sys
import os
from typing import List, Dict
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from logger import LOGGER
from intervention_strategy_simulator import InterventionStrategySimulator
from median_convergence_analyzer import MedianConvergenceAnalyzer
from employee_population_simulator import EmployeePopulationGenerator


def load_population_data(data_source: str) -> List[Dict]:
    """Load population data from various sources."""
    if data_source == "generate":
        LOGGER.info("Generating test population data")
        generator = EmployeePopulationGenerator(population_size=1000, random_seed=42)
        return generator.generate_population()

    elif data_source.endswith(".json"):
        LOGGER.info(f"Loading population data from JSON: {data_source}")
        with open(data_source, "r") as f:
            return json.load(f)

    elif data_source.endswith(".csv"):
        LOGGER.info(f"Loading population data from CSV: {data_source}")
        df = pd.read_csv(data_source)
        return df.to_dict("records")

    else:
        raise ValueError(f"Unsupported data source format: {data_source}")


def format_currency(amount: float) -> str:
    """Format currency amount for display."""
    return f"£{amount:,.2f}"


def format_percentage(percent: float) -> str:
    """Format percentage for display."""
    return f"{percent:.1f}%"


def create_gender_gap_report(remediation_result: Dict, output_format: str = "text") -> str:
    """Create formatted gender gap remediation report."""
    if output_format == "json":
        return json.dumps(remediation_result, indent=2, default=str)

    # Current State
    current = remediation_result["current_state"]
    report_lines = [
        "=" * 80,
        "💼 GENDER PAY GAP REMEDIATION ANALYSIS",
        "=" * 80,
        "",
        *[
            "📊 CURRENT STATE",
            "-" * 20,
            f"Gender Pay Gap: {format_percentage(current['gender_pay_gap_percent'])}",
            f"Male Median Salary: {format_currency(current['male_median_salary'])}",
            f"Female Median Salary: {format_currency(current['female_median_salary'])}",
            f"Affected Female Employees: {current['affected_female_employees']}",
            f"Total Payroll: {format_currency(current['total_payroll'])}",
            "",
        ],
    ]
    # Target State
    target = remediation_result["target_state"]
    report_lines.extend(
        [
            "🎯 TARGET STATE",
            "-" * 15,
            f"Target Gap: {format_percentage(target['target_gap_percent'])}",
            f"Maximum Timeline: {target['max_timeline_years']} years",
            f"Budget Constraint: {format_percentage(target['budget_constraint_percent'] * 100)} of payroll",
            f"Budget Limit: {format_currency(target['budget_constraint_amount'])}",
            "",
        ]
    )

    # Recommended Strategy
    recommended = remediation_result["recommended_strategy"]
    report_lines.extend(
        [
            "✅ RECOMMENDED STRATEGY",
            "-" * 25,
            f"Strategy: {recommended['strategy_name'].replace('_', ' ').title()}",
            f"Total Cost: {format_currency(recommended['total_cost'])}",
            f"Cost as % of Payroll: {format_percentage(recommended['cost_as_percent_payroll'] * 100)}",
            f"Timeline: {recommended['timeline_years']} years",
            f"Affected Employees: {recommended['affected_employees']}",
            f"Gap Reduction: {format_percentage(recommended['gap_reduction_percent'])}",
            f"Final Gap: {format_percentage(recommended['projected_final_gap'])}",
            f"Feasibility: {recommended['feasibility'].title()}",
            f"Implementation Complexity: {recommended['implementation_complexity'].title()}",
            "",
        ]
    )

    # Strategy Comparison
    strategies = remediation_result["available_strategies"]
    report_lines.extend(
        [
            "📋 STRATEGY COMPARISON",
            "-" * 25,
            f"{'Strategy':<20} {'Cost':<12} {'Timeline':<10} {'Gap Reduction':<15} {'Feasibility':<12}",
            "-" * 80,
        ]
    )
    for strategy_name, strategy in strategies.items():
        if not strategy.get("applicable", True):
            continue

        name = strategy_name.replace("_", " ").title()[:18]
        cost = format_currency(strategy["total_cost"])[:10]
        timeline = f"{strategy['timeline_years']}y"[:8]
        gap_reduction = format_percentage(strategy["gap_reduction_percent"])[:13]
        feasibility = strategy["feasibility"].title()[:10]

        report_lines.append(f"{name:<20} {cost:<12} {timeline:<10} {gap_reduction:<15} {feasibility:<12}")

    report_lines.append("")

    # Implementation Plan
    implementation = remediation_result["implementation_plan"]
    report_lines.extend(["📅 IMPLEMENTATION PLAN", "-" * 23])

    for phase in implementation:
        report_lines.append(f"Phase {phase['phase']}: {phase['activity']} (Month {phase['timeline_months']})")

    report_lines.append("")

    # ROI Analysis
    roi = remediation_result["roi_analysis"]
    report_lines.extend(
        [
            "💰 ROI ANALYSIS",
            "-" * 15,
            f"Total Investment: {format_currency(roi['total_investment'])}",
            f"Annual Benefits: {format_currency(roi['annual_benefits'])}",
            f"Payback Period: {roi['payback_years']:.1f} years",
            f"3-Year ROI: {format_percentage(roi['roi_3_year'] * 100)}",
            f"Retention Benefit: {format_currency(roi['retention_benefit'])}",
            f"Productivity Benefit: {format_currency(roi['productivity_benefit'])}",
            "",
        ]
    )

    # Risk Assessment
    risks = remediation_result["risk_assessment"]
    report_lines.extend(
        [
            "⚠️  RISK ASSESSMENT",
            "-" * 18,
            f"Overall Risk Level: {risks['overall_risk_level'].title()}",
            f"Risk Factors: {', '.join(risks['risk_factors']) if risks['risk_factors'] else 'None identified'}",
            "",
        ]
    )

    if risks["mitigation_strategies"]:
        report_lines.extend(
            ["Risk Mitigation Strategies:", *[f"• {mitigation}" for mitigation in risks["mitigation_strategies"]], ""]
        )

    report_lines.extend(
        [
            "=" * 80,
            f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "Generated by Employee Simulation System - Intervention Strategy Simulator",
            "=" * 80,
        ]
    )

    return "\n".join(report_lines)


def create_median_convergence_report(convergence_result: Dict, output_format: str = "text") -> str:
    """Create formatted median convergence analysis report."""
    if output_format == "json":
        return json.dumps(convergence_result, indent=2, default=str)

    # Summary Statistics
    stats = convergence_result["summary_statistics"]
    report_lines = [
        "=" * 70,
        "📊 MEDIAN CONVERGENCE ANALYSIS",
        "=" * 70,
        "",
        *[
            "📈 SUMMARY STATISTICS",
            "-" * 22,
            f"Total Employees Below Median: {stats['count']}",
            f"Average Gap Amount: {format_currency(stats['average_gap_amount'])}",
            f"Average Gap Percentage: {format_percentage(stats['average_gap_percent'])}",
            f"Total Gap Amount: {format_currency(stats['total_gap_amount'])}",
            f"Largest Individual Gap: {format_currency(stats['max_gap_amount'])}",
            "",
        ],
    ]
    # Gender Analysis (if available)
    if "gender_analysis" in convergence_result:
        gender_analysis = convergence_result["gender_analysis"]
        report_lines.extend(["👥 GENDER ANALYSIS", "-" * 18])

        for gender in ["Male", "Female"]:
            if gender in gender_analysis:
                data = gender_analysis[gender]
                report_lines.append(
                    f"{gender}: {data['count']} employees (avg gap: {format_percentage(data['average_gap_percent'])})"
                )

        if gender_analysis.get("disparity_significant"):
            disparity = gender_analysis["gender_disparity"]
            report_lines.append(f"Gender Disparity: {format_percentage(disparity)} (statistically significant)")

        report_lines.append("")

    # Sample convergence analysis (if available)
    if convergence_result["employees"] and len(convergence_result["employees"]) > 0:
        sample_employee = convergence_result["employees"][0]
        report_lines.extend(
            [
                "🎯 SAMPLE CONVERGENCE CASE",
                "-" * 26,
                f"Employee ID: {sample_employee['employee_id']}",
                f"Level: {sample_employee['level']}",
                f"Current Salary: {format_currency(sample_employee['salary'])}",
                f"Gap: {format_currency(sample_employee['gap_amount'])} ({format_percentage(sample_employee['gap_percent'])})",
                f"Performance: {sample_employee['performance_rating']}",
                "",
            ]
        )

    report_lines.extend(["=" * 70, f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "=" * 70])

    return "\n".join(report_lines)


def save_report(report_content: str, output_file: str, format_type: str):
    """Save report to file."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w") as f:
        f.write(report_content)

    LOGGER.info(f"Report saved to: {output_file}")


def run_gender_gap_analysis(population_data: List[Dict], args) -> Dict:
    """Run gender gap remediation analysis."""
    LOGGER.info("Running gender pay gap remediation analysis")

    simulator = InterventionStrategySimulator(population_data)

    return simulator.model_gender_gap_remediation(
        target_gap_percent=args.target_gap,
        max_years=args.max_years,
        budget_constraint=args.budget_limit
        / 100.0,  # Convert percentage to decimal
    )


def run_median_convergence_analysis(population_data: List[Dict], args) -> Dict:
    """Run median convergence analysis."""
    LOGGER.info("Running median convergence analysis")

    analyzer = MedianConvergenceAnalyzer(population_data)

    # Identify below-median employees
    below_median_result = analyzer.identify_below_median_employees(
        min_gap_percent=args.min_gap_percent, include_gender_analysis=True
    )

    # Get intervention recommendations
    intervention_recommendations = analyzer.recommend_intervention_strategies(below_median_result)

    return {**below_median_result, "intervention_recommendations": intervention_recommendations}


def run_equity_analysis(population_data: List[Dict], args) -> Dict:
    """Run comprehensive salary equity analysis."""
    LOGGER.info("Running comprehensive salary equity analysis")

    simulator = InterventionStrategySimulator(population_data)

    # Analyze across multiple dimensions
    dimensions = ["gender", "level", "gender_by_level"]
    if args.include_tenure:
        dimensions.append("tenure")

    return simulator.analyze_population_salary_equity(dimensions)


def create_equity_report(equity_result: Dict, output_format: str = "text") -> str:
    """Create formatted equity analysis report."""
    if output_format == "json":
        return json.dumps(equity_result, indent=2, default=str)

    # Overall Equity Score
    overall_score = equity_result["overall_equity_score"]
    score_label = (
        "Excellent"
        if overall_score > 0.8
        else "Good" if overall_score > 0.6 else "Fair" if overall_score > 0.4 else "Poor"
    )

    report_lines = [
        "=" * 70,
        "⚖️  SALARY EQUITY ANALYSIS",
        "=" * 70,
        "",
        *[
            "📊 OVERALL EQUITY ASSESSMENT",
            "-" * 28,
            f"Equity Score: {overall_score:.2f}/1.00 ({score_label})",
            "",
        ],
    ]
    # Gender Equity
    if "gender" in equity_result:
        gender = equity_result["gender"]
        report_lines.extend(
            [
                "👥 GENDER EQUITY",
                "-" * 16,
                f"Male Median: {format_currency(gender['male_median'])}",
                f"Female Median: {format_currency(gender['female_median'])}",
                f"Pay Gap: {format_percentage(gender['pay_gap_percent'])}",
                f"Statistical Significance: {gender['statistical_significance'].replace('_', ' ').title()}",
                "",
            ]
        )

    # Level Equity
    if "level" in equity_result:
        level_equity = equity_result["level"]
        report_lines.extend(["📈 LEVEL EQUITY", "-" * 14])

        for level, data in sorted(level_equity.items()):
            cv = data["coefficient_of_variation"]
            cv_label = "Low" if cv < 0.1 else "Moderate" if cv < 0.2 else "High"
            report_lines.append(
                f"Level {level}: {data['count']} employees, "
                f"median {format_currency(data['median_salary'])}, "
                f"variation: {cv_label}"
            )

        report_lines.append("")

    # Gender by Level Analysis
    if "gender_by_level" in equity_result:
        gender_level = equity_result["gender_by_level"]
        report_lines.extend(["🎯 GENDER EQUITY BY LEVEL", "-" * 25])

        for level, data in sorted(gender_level.items()):
            if data["gap_percent"] != 0:
                gap_status = "🔴" if abs(data["gap_percent"]) > 15 else "🟡" if abs(data["gap_percent"]) > 5 else "🟢"
                report_lines.append(
                    f"{gap_status} Level {level}: {format_percentage(data['gap_percent'])} gap "
                    f"(M:{data['male_count']}, F:{data['female_count']})"
                )

        report_lines.append("")

    # Priority Interventions
    if "priority_interventions" in equity_result:
        if interventions := equity_result["priority_interventions"]:
            report_lines.extend(["🚨 PRIORITY INTERVENTIONS", "-" * 23])

            for intervention in interventions:
                priority_symbol = "🔴" if intervention["priority"] == "high" else "🟡"
                cost_pct = format_percentage(intervention["estimated_cost_percent"] * 100)
                report_lines.append(f"{priority_symbol} {intervention['description']} (Est. cost: {cost_pct})")

            report_lines.append("")

    report_lines.extend(["=" * 70, f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "=" * 70])

    return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(
        description="Model management intervention strategies for salary equity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Gender gap remediation analysis
  python model_interventions.py --strategy gender-gap --data-source generate --target-gap 0.0 --budget-limit 0.5

  # Median convergence analysis
  python model_interventions.py --strategy median-convergence --data-source employees.csv --min-gap-percent 10.0

  # Comprehensive equity analysis
  python model_interventions.py --strategy equity-analysis --data-source data.json --include-tenure

  # Generate detailed report
  python model_interventions.py --strategy gender-gap --data-source generate --output-file reports/remediation_plan.txt --dry-run
        """,
    )

    # Data source
    parser.add_argument(
        "--data-source", required=True, help='Population data source: JSON file, CSV file, or "generate" for test data'
    )

    # Strategy selection
    parser.add_argument(
        "--strategy",
        required=True,
        choices=["gender-gap", "median-convergence", "equity-analysis"],
        help="Intervention strategy to model",
    )

    # Gender gap parameters
    parser.add_argument("--target-gap", type=float, default=0.0, help="Target gender gap percentage (default: 0.0)")

    parser.add_argument("--max-years", type=int, default=3, help="Maximum years for intervention (default: 3)")

    parser.add_argument(
        "--budget-limit", type=float, default=0.5, help="Budget limit as percentage of payroll (default: 0.5)"
    )

    # Median convergence parameters
    parser.add_argument(
        "--min-gap-percent", type=float, default=5.0, help="Minimum gap percentage to analyze (default: 5.0)"
    )

    # Equity analysis parameters
    parser.add_argument("--include-tenure", action="store_true", help="Include tenure analysis in equity assessment")

    # Output options
    parser.add_argument(
        "--output-format", choices=["text", "json"], default="text", help="Output format (default: text)"
    )

    parser.add_argument("--output-file", type=str, help="Save report to file")

    parser.add_argument(
        "--output-dir",
        type=str,
        default="intervention_reports",
        help="Output directory for reports (default: intervention_reports)",
    )

    # Analysis options
    parser.add_argument("--dry-run", action="store_true", help="Show analysis without actually implementing changes")

    parser.add_argument("--validate", action="store_true", help="Validate data and show summary statistics only")

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        LOGGER.setLevel(10)  # Debug level

    try:
        # Load population data
        LOGGER.info("Loading population data...")
        population_data = load_population_data(args.data_source)
        LOGGER.info(f"Loaded {len(population_data)} employees")

        # Validation mode
        if args.validate:
            LOGGER.info("Running in validation mode")

            df = pd.DataFrame(population_data)
            print("✅ Data validation successful")
            print(f"   Total employees: {len(df)}")
            print(f"   Levels: {sorted(df['level'].unique())}")
            print(f"   Gender distribution: {dict(df['gender'].value_counts())}")
            print(f"   Salary range: {format_currency(df['salary'].min())} - {format_currency(df['salary'].max())}")
            print(f"   Overall median: {format_currency(df['salary'].median())}")

            if "Male" in df["gender"].values and "Female" in df["gender"].values:
                male_median = df[df["gender"] == "Male"]["salary"].median()
                female_median = df[df["gender"] == "Female"]["salary"].median()
                gap = ((male_median - female_median) / male_median) * 100
                print(f"   Current gender gap: {format_percentage(gap)}")

            return

        # Run selected strategy analysis
        if args.strategy == "gender-gap":
            result = run_gender_gap_analysis(population_data, args)
            report = create_gender_gap_report(result, args.output_format)

        elif args.strategy == "median-convergence":
            result = run_median_convergence_analysis(population_data, args)
            report = create_median_convergence_report(result, args.output_format)

        elif args.strategy == "equity-analysis":
            result = run_equity_analysis(population_data, args)
            report = create_equity_report(result, args.output_format)

        # Dry run mode
        if args.dry_run:
            print("\n🔍 DRY RUN MODE - Analysis Results Preview:")
            print("-" * 50)

            if args.strategy == "gender-gap":
                recommended = result["recommended_strategy"]
                print(f"Recommended Strategy: {recommended['strategy_name']}")
                print(f"Estimated Cost: {format_currency(recommended['total_cost'])}")
                print(f"Timeline: {recommended['timeline_years']} years")
                print(f"Gap Reduction: {format_percentage(recommended['gap_reduction_percent'])}")
                print(f"Affected Employees: {recommended['affected_employees']}")

            print(f"\nFull analysis available. Use without --dry-run to see complete report.")
            return

        # Output handling
        if args.output_file:
            save_report(report, args.output_file, args.output_format)
        else:
            print(report)

    except FileNotFoundError as e:
        LOGGER.error(f"File not found: {e}")
        sys.exit(1)
    except ValueError as e:
        LOGGER.error(f"Invalid input: {e}")
        sys.exit(1)
    except Exception as e:
        LOGGER.error(f"Analysis failed: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

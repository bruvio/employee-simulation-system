#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

import argparse
from datetime import datetime
import json
import os
import sys
from typing import Dict, List, Optional

import pandas as pd

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from employee_population_simulator import EmployeePopulationGenerator
from individual_progression_simulator import IndividualProgressionSimulator
from logger import LOGGER


def load_population_data(data_source: str) -> List[Dict]:
    """Load population data from various sources.

    Args:
      data_source: Path to JSON/CSV file or 'generate' to create test data
      data_source: str:

    Returns:
      : List of employee dictionaries
    """
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


def find_employee_by_id(population_data: List[Dict], employee_id: int) -> Optional[Dict]:
    """Find employee by ID in population data.

    Args:
      population_data: List[Dict]:
      employee_id: int:

    Returns:
    """
    return next(
        (employee for employee in population_data if employee.get("employee_id") == employee_id),
        None,
    )


def format_currency(amount: float) -> str:
    """Format currency amount for display.

    Args:
      amount: float:

    Returns:
    """
    return f"£{amount:,.2f}"


def format_percentage(percent: float) -> str:
    """Format percentage for display.

    Args:
      percent: float:

    Returns:
    """
    return f"{percent:.1f}%"


def create_progression_report(progression_result: Dict, output_format: str = "text") -> str:
    """Create formatted progression analysis report.

    Args:
      progression_result: Dict:
      output_format: str:  (Default value = "text")

    Returns:
    """
    if output_format == "json":
        return json.dumps(progression_result, indent=2, default=str)

    # Employee Information
    current = progression_result["current_state"]
    employee_id = current.get("employee_id", progression_result.get("employee_id", "Unknown"))
    report_lines = [
        "=" * 70,
        "📈 INDIVIDUAL SALARY PROGRESSION ANALYSIS",
        "=" * 70,
        "",
        *[
            "👤 EMPLOYEE INFORMATION",
            "-" * 30,
            f"Employee ID: {employee_id}",
            f"Current Level: {current['level']}",
            f"Current Salary: {format_currency(current['salary'])}",
            f"Performance Rating: {current['performance_rating']}",
            f"Gender: {current.get('gender', 'Not specified')}",
            f"Years at Company: {current.get('years_at_company', 'N/A'):.1f}",
            "",
        ],
    ]
    # Projections
    projections = progression_result["projections"]
    report_lines.extend(["🎯 SALARY PROJECTIONS (5-Year)", "-" * 35])

    for scenario, data in projections.items():
        cagr_pct = format_percentage(data["cagr"] * 100)
        final_salary = format_currency(data["final_salary"])
        total_increase = format_currency(data["total_increase"])

        report_lines.extend(
            [
                f"{scenario.upper()} SCENARIO:",
                f"  Final Salary: {final_salary}",
                f"  Total Increase: {total_increase}",
                f"  Annual Growth (CAGR): {cagr_pct}",
                f"  Performance Path: {' → '.join(data['performance_path'])}",
                "",
            ]
        )

    # Analysis
    analysis = progression_result["analysis"]
    report_lines.extend(["📊 ANALYSIS", "-" * 15])

    # Median comparison
    median_comp = analysis["median_comparison"]
    report_lines.extend(
        [
            "Position vs Level Median:",
            f"  Current: {median_comp['current_status'].replace('_', ' ').title()}",
            f"  Gap: {format_percentage(median_comp['current_gap_percent'])} ({format_currency(median_comp['current_gap_amount'])})",
            f"  Projected: {median_comp['projected_status'].replace('_', ' ').title()}",
            "",
        ]
    )

    # Market competitiveness
    market_comp = analysis["market_competitiveness"]
    report_lines.extend(
        [
            "Market Position:",
            f"  Current Percentile: {market_comp['current_percentile']:.0f}th",
            f"  Current Quartile: {market_comp['current_quartile'].replace('_', ' ').title()}",
            f"  Projected Percentile: {market_comp['projected_percentile']:.0f}th",
            "",
        ]
    )

    # Risk factors
    if analysis["risk_factors"]:
        report_lines.extend(
            [
                "⚠️  Risk Factors:",
                *[f"  • {risk.replace('_', ' ').title()}" for risk in analysis["risk_factors"]],
                "",
            ]
        )

    # Recommendations
    recommendations = progression_result["recommendations"]
    report_lines.extend(
        [
            "💡 RECOMMENDATIONS",
            "-" * 20,
            f"Primary Action: {recommendations['primary_action'].replace('_', ' ').title()}",
            f"Timeline: {recommendations['timeline'].replace('_', ' ').title()}",
        ]
    )

    if recommendations["secondary_actions"]:
        report_lines.extend(
            [
                "Secondary Actions:",
                *[f"  • {action.replace('_', ' ').title()}" for action in recommendations["secondary_actions"]],
            ]
        )

    if recommendations["rationale"]:
        report_lines.extend([f"Rationale: {recommendations['rationale']}"])

    report_lines.extend(["", "=" * 70, f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "=" * 70])

    return "\n".join(report_lines)


def save_report(report_content: str, output_file: str, format_type: str):
    """Save report to file.

    Args:
      report_content: str:
      output_file: str:
      format_type: str:

    Returns:
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, "w") as f:
        f.write(report_content)

    LOGGER.info(f"Report saved to: {output_file}")


def analyze_multiple_employees(
    population_data: List[Dict], employee_ids: List[int], years: int, scenarios: List[str], output_format: str
) -> Dict:
    """Analyze multiple employees and create summary report.

    Args:
      population_data: List[Dict]:
      employee_ids: List[int]:
      years: int:
      scenarios: List[str]:
      output_format: str:

    Returns:
    """
    simulator = IndividualProgressionSimulator(population_data)

    all_results = {}
    summary_data = []

    for employee_id in employee_ids:
        employee = find_employee_by_id(population_data, employee_id)
        if not employee:
            LOGGER.warning(f"Employee {employee_id} not found")
            continue

        try:
            result = simulator.project_salary_progression(employee, years, scenarios)
            all_results[employee_id] = result

            # Extract key metrics for summary
            realistic = result["projections"]["realistic"]
            summary_data.append(
                {
                    "employee_id": employee_id,
                    "current_salary": employee["salary"],
                    "current_level": employee["level"],
                    "current_performance": employee.get("performance_rating", "Unknown"),
                    "projected_salary": realistic["final_salary"],
                    "salary_increase": realistic["total_increase"],
                    "cagr_percent": realistic["cagr"] * 100,
                    "median_status": result["analysis"]["median_comparison"]["current_status"],
                    "primary_recommendation": result["recommendations"]["primary_action"],
                }
            )

        except Exception as e:
            LOGGER.error(f"Error analyzing employee {employee_id}: {e}")

    return {
        "detailed_results": all_results,
        "summary": summary_data,
        "analysis_summary": create_multi_employee_summary(summary_data),
    }


def create_multi_employee_summary(summary_data: List[Dict]) -> Dict:
    """Create summary statistics for multiple employee analysis.

    Args:
      summary_data: List[Dict]:

    Returns:
    """
    if not summary_data:
        return {}

    df = pd.DataFrame(summary_data)

    return {
        "total_employees": len(df),
        "avg_current_salary": df["current_salary"].mean(),
        "avg_projected_salary": df["projected_salary"].mean(),
        "avg_cagr": df["cagr_percent"].mean(),
        "below_median_count": len(df[df["median_status"] == "below_median"]),
        "high_risk_count": len(
            df[df["primary_recommendation"].str.contains("intervention|adjustment", case=False, na=False)]
        ),
        "level_distribution": df["current_level"].value_counts().to_dict(),
        "performance_distribution": df["current_performance"].value_counts().to_dict(),
    }


def create_batch_report(multi_results: Dict, output_format: str = "text") -> str:
    """Create batch analysis report.

    Args:
      multi_results: Dict:
      output_format: str:  (Default value = "text")

    Returns:
    """
    if output_format == "json":
        return json.dumps(multi_results, indent=2, default=str)

    summary = multi_results["analysis_summary"]
    multi_results["detailed_results"]

    report_lines = [
        "=" * 80,
        "📊 BATCH EMPLOYEE PROGRESSION ANALYSIS",
        "=" * 80,
        "",
        "📈 SUMMARY STATISTICS",
        "-" * 25,
        f"Total Employees Analyzed: {summary['total_employees']}",
        f"Average Current Salary: {format_currency(summary['avg_current_salary'])}",
        f"Average Projected Salary: {format_currency(summary['avg_projected_salary'])}",
        f"Average Growth Rate (CAGR): {format_percentage(summary['avg_cagr'])}",
        f"Below Median: {summary['below_median_count']} ({summary['below_median_count'] / summary['total_employees'] * 100:.1f}%)",
        f"Requiring Intervention: {summary['high_risk_count']} ({summary['high_risk_count'] / summary['total_employees'] * 100:.1f}%)",
        "",
        *["👥 LEVEL DISTRIBUTION", "-" * 20],
    ]

    for level, count in sorted(summary["level_distribution"].items()):
        percentage = count / summary["total_employees"] * 100
        report_lines.append(f"Level {level}: {count} employees ({percentage:.1f}%)")

    report_lines.extend(["", "🎯 PERFORMANCE DISTRIBUTION", "-" * 25])
    for performance, count in summary["performance_distribution"].items():
        percentage = count / summary["total_employees"] * 100
        report_lines.append(f"{performance}: {count} employees ({percentage:.1f}%)")

    # Individual highlights
    report_lines.extend(["", "⭐ INDIVIDUAL HIGHLIGHTS", "-" * 25])

    summary_df = pd.DataFrame(multi_results["summary"])

    # Highest growth
    highest_growth = summary_df.loc[summary_df["cagr_percent"].idxmax()]
    report_lines.append(
        f"Highest Growth: Employee {highest_growth['employee_id']} ({format_percentage(highest_growth['cagr_percent'])} CAGR)"
    )

    # Largest increase
    largest_increase = summary_df.loc[summary_df["salary_increase"].idxmax()]
    report_lines.append(
        f"Largest Increase: Employee {largest_increase['employee_id']} (+{format_currency(largest_increase['salary_increase'])})"
    )

    # Most concerning
    concerning_employees = summary_df[
        (summary_df["median_status"] == "below_median") & (summary_df["cagr_percent"] < 3.0)
    ]
    if len(concerning_employees) > 0:
        report_lines.append(f"Requires Attention: {len(concerning_employees)} employees below median with <3% growth")

    report_lines.extend(["", "=" * 80, f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "=" * 80])

    return "\n".join(report_lines)


def main():
    """"""
    parser = argparse.ArgumentParser(
        description="Analyze individual employee salary progression",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze single employee from generated test data
  python analyze_individual_progression.py --data-source generate --employee-id 123

  # Analyze multiple employees from CSV file
  python analyze_individual_progression.py --data-source employees.csv --employee-id 123 456 789

  # Extended 10-year analysis with custom scenarios
  python analyze_individual_progression.py --data-source data.json --employee-id 123 --years 10 --scenarios conservative optimistic

  # Batch analysis with report output
  python analyze_individual_progression.py --data-source generate --employee-id 100-110 --output-file reports/batch_analysis.txt
        """,
    )

    # Data source
    parser.add_argument(
        "--data-source", required=True, help='Population data source: JSON file, CSV file, or "generate" for test data'
    )

    # Employee selection
    parser.add_argument(
        "--employee-id",
        nargs="+",
        required=True,
        help='Employee ID(s) to analyze. Use range format like "100-110" for batch analysis',
    )

    # Analysis parameters
    parser.add_argument("--years", type=int, default=5, help="Number of years to project (default: 5)")

    parser.add_argument(
        "--scenarios",
        nargs="+",
        choices=["conservative", "realistic", "optimistic"],
        default=["conservative", "realistic", "optimistic"],
        help="Scenarios to model (default: all)",
    )

    # Output options
    parser.add_argument(
        "--output-format", choices=["text", "json"], default="text", help="Output format (default: text)"
    )

    parser.add_argument("--output-file", type=str, help="Save report to file (auto-detects format from extension)")

    parser.add_argument(
        "--output-dir",
        type=str,
        default="analysis_reports",
        help="Output directory for reports (default: analysis_reports)",
    )

    # Validation and debugging
    parser.add_argument("--validate", action="store_true", help="Validate employee exists and show basic info only")

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    args = parser.parse_args()

    if args.verbose:
        LOGGER.setLevel(10)  # Debug level

    try:
        # Load population data
        LOGGER.info("Loading population data...")
        population_data = load_population_data(args.data_source)
        LOGGER.info(f"Loaded {len(population_data)} employees")

        # Parse employee IDs (handle ranges)
        employee_ids = []
        for id_spec in args.employee_id:
            if "-" in id_spec and id_spec.replace("-", "").isdigit():
                # Handle range like "100-110"
                start, end = map(int, id_spec.split("-"))
                employee_ids.extend(range(start, end + 1))
            else:
                employee_ids.append(int(id_spec))

        employee_ids = sorted(set(employee_ids))  # Remove duplicates and sort
        LOGGER.info(f"Analyzing {len(employee_ids)} employees: {employee_ids}")

        # Validation mode
        if args.validate:
            LOGGER.info("Running in validation mode")
            for emp_id in employee_ids:
                if employee := find_employee_by_id(population_data, emp_id):
                    print(
                        f"✅ Employee {emp_id}: Level {employee['level']}, "
                        f"{format_currency(employee['salary'])}, {employee.get('performance_rating', 'Unknown')}"
                    )
                else:
                    print(f"❌ Employee {emp_id}: Not found")
            return

        # Single employee analysis
        if len(employee_ids) == 1:
            employee_id = employee_ids[0]
            employee = find_employee_by_id(population_data, employee_id)

            if not employee:
                print(f"❌ Employee {employee_id} not found in population data")
                sys.exit(1)

            LOGGER.info(f"Analyzing employee {employee_id}")

            # Create simulator and analyze
            simulator = IndividualProgressionSimulator(population_data)
            result = simulator.project_salary_progression(employee, args.years, args.scenarios)

            # Ensure employee_id is in the result
            if "employee_id" not in result:
                result["employee_id"] = employee_id

            # Generate report
            report = create_progression_report(result, args.output_format)

            # Output handling
            if args.output_file:
                save_report(report, args.output_file, args.output_format)
            else:
                print(report)

        # Multi-employee analysis
        else:
            LOGGER.info(f"Performing batch analysis for {len(employee_ids)} employees")

            multi_results = analyze_multiple_employees(
                population_data, employee_ids, args.years, args.scenarios, args.output_format
            )

            # Generate batch report
            report = create_batch_report(multi_results, args.output_format)

            # Output handling
            if args.output_file:
                save_report(report, args.output_file, args.output_format)
            else:
                print(report)

            # Save detailed results if JSON format
            if args.output_format == "json" and args.output_file:
                detailed_file = args.output_file.replace(".json", "_detailed.json")
                save_report(json.dumps(multi_results["detailed_results"], indent=2, default=str), detailed_file, "json")

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

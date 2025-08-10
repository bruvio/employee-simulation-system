#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

import pandas as pd
import numpy as np
from datetime import datetime
import argparse
import json
from logger import LOGGER

# Import constants from population simulator
from employee_population_simulator import UPLIFT_MATRIX, LEVEL_MAPPING


class PerformanceReviewSystem:
    """
    Performance review system implementing industry-standard 5-point rating scale
    with level-based distributions and salary uplift calculations.
    """

    def __init__(self, random_seed=42):
        self.rng = np.random.default_rng(random_seed)
        self.performance_weights = {
            "core": {  # Levels 1-3
                "Not met": 0.05,
                "Partially met": 0.15,
                "Achieving": 0.55,
                "High Performing": 0.22,
                "Exceeding": 0.03,
            },
            "senior": {  # Levels 4-6
                "Not met": 0.02,
                "Partially met": 0.08,
                "Achieving": 0.40,
                "High Performing": 0.40,
                "Exceeding": 0.10,
            },
        }
        LOGGER.info("Initialized PerformanceReviewSystem with level-based rating distributions")

    def assign_performance_ratings(self, employees):
        """Assign performance ratings based on level-dependent distributions"""
        LOGGER.info(f"Assigning performance ratings for {len(employees)} employees")

        performance_counts = {"Not met": 0, "Partially met": 0, "Achieving": 0, "High Performing": 0, "Exceeding": 0}
        level_breakdown = {"core": {"total": 0}, "senior": {"total": 0}}

        # Shuffle employees to avoid any ordering bias
        employee_indices = list(range(len(employees)))
        self.rng.shuffle(employee_indices)

        for idx in employee_indices:
            employee = employees[idx]
            level = employee["level"]
            category = "senior" if level >= 4 else "core"

            weights = self.performance_weights[category]
            ratings = list(weights.keys())
            probabilities = list(weights.values())

            # Use fresh random choice for each employee
            rating = self.rng.choice(ratings, p=probabilities)
            employee["performance_rating"] = rating

            # Track statistics
            performance_counts[rating] += 1
            level_breakdown[category]["total"] += 1
            if rating not in level_breakdown[category]:
                level_breakdown[category][rating] = 0
            level_breakdown[category][rating] += 1

        self._log_performance_distribution(performance_counts, level_breakdown, len(employees))
        return employees

    def calculate_salary_uplift(self, employee):
        """Calculate salary uplift using provided matrix"""
        performance = employee["performance_rating"]
        level = employee["level"]
        current_salary = employee["salary"]

        # Get uplift components from the matrix
        uplift_data = UPLIFT_MATRIX[performance]
        level_tier = LEVEL_MAPPING[level]

        # Calculate individual uplift percentages
        baseline_uplift = uplift_data["baseline"]
        performance_uplift = uplift_data["performance"]
        career_uplift = uplift_data[level_tier]

        # Calculate total uplift percentage
        total_uplift = baseline_uplift + performance_uplift + career_uplift

        # Apply uplift to current salary
        new_salary = current_salary * (1 + total_uplift)

        uplift_result = {
            "old_salary": float(current_salary),
            "new_salary": float(new_salary),
            "uplift_percentage": float(total_uplift * 100),
            "baseline_uplift": float(baseline_uplift * 100),
            "performance_uplift": float(performance_uplift * 100),
            "career_uplift": float(career_uplift * 100),
        }

        return uplift_result

    def apply_annual_review(self, employees, review_year):
        """Apply annual performance review and salary adjustments"""
        LOGGER.info(f"Applying annual performance review for year {review_year}")

        # First, assign new performance ratings
        employees = self.assign_performance_ratings(employees)

        review_results = []
        total_old_salary = 0
        total_new_salary = 0
        uplift_stats = []

        for employee in employees:
            # Calculate uplift
            uplift_result = self.calculate_salary_uplift(employee)

            # Update employee salary
            employee["salary"] = uplift_result["new_salary"]

            # Create review record
            review_record = {
                "employee_id": employee["employee_id"],
                "review_year": review_year,
                "performance_rating": employee["performance_rating"],
                "level": employee["level"],
                "gender": employee["gender"],
                **uplift_result,
            }

            # Add to employee's history
            employee["review_history"].append(review_record)
            review_results.append(review_record)

            # Track statistics
            total_old_salary += uplift_result["old_salary"]
            total_new_salary += uplift_result["new_salary"]
            uplift_stats.append(uplift_result["uplift_percentage"])

        # Log review statistics
        total_increase = total_new_salary - total_old_salary
        avg_uplift = np.mean(uplift_stats)
        median_uplift = np.median(uplift_stats)

        LOGGER.info(f"Applied {len(review_results)} salary adjustments for year {review_year}")
        LOGGER.info(f"Total salary increase: £{total_increase:,.2f}")
        LOGGER.info(f"Average uplift: {avg_uplift:.2f}%, Median uplift: {median_uplift:.2f}%")

        return review_results

    def _log_performance_distribution(self, performance_counts, level_breakdown, total_employees):
        """Log performance rating distribution statistics"""
        LOGGER.info("Performance rating distribution:")

        for rating, count in performance_counts.items():
            percentage = count / total_employees * 100
            LOGGER.info(f"  {rating}: {count} employees ({percentage:.1f}%)")

        # Log by level category
        for category, data in level_breakdown.items():
            total_category = data["total"]
            if total_category > 0:
                LOGGER.info(f"{category.capitalize()} engineers ({total_category} employees):")
                for rating in performance_counts.keys():
                    count = data.get(rating, 0)
                    percentage = count / total_category * 100 if total_category > 0 else 0
                    LOGGER.info(f"  {rating}: {count} ({percentage:.1f}%)")

    def validate_uplift_calculations(self, test_cases=None):
        """Validate uplift calculations match the matrix exactly"""
        LOGGER.info("Validating uplift calculations")

        if test_cases is None:
            # Create comprehensive test cases
            test_cases = []
            for performance in UPLIFT_MATRIX.keys():
                for level in LEVEL_MAPPING.keys():
                    test_cases.append(
                        {
                            "employee_id": f"test_{performance}_{level}",
                            "level": level,
                            "salary": 85000.0,  # Standard test salary
                            "performance_rating": performance,
                            "gender": "Test",
                        }
                    )

        validation_results = []
        all_passed = True

        for test_case in test_cases:
            uplift_result = self.calculate_salary_uplift(test_case)

            # Calculate expected values manually
            performance = test_case["performance_rating"]
            level = test_case["level"]
            base_salary = test_case["salary"]

            expected_baseline = UPLIFT_MATRIX[performance]["baseline"] * 100
            expected_performance = UPLIFT_MATRIX[performance]["performance"] * 100
            expected_career = UPLIFT_MATRIX[performance][LEVEL_MAPPING[level]] * 100
            expected_total = expected_baseline + expected_performance + expected_career
            expected_new_salary = base_salary * (1 + expected_total / 100)

            # Check if calculations match
            tolerance = 0.01  # 1 cent tolerance
            baseline_match = abs(uplift_result["baseline_uplift"] - expected_baseline) < tolerance
            performance_match = abs(uplift_result["performance_uplift"] - expected_performance) < tolerance
            career_match = abs(uplift_result["career_uplift"] - expected_career) < tolerance
            total_match = abs(uplift_result["uplift_percentage"] - expected_total) < tolerance
            salary_match = abs(uplift_result["new_salary"] - expected_new_salary) < tolerance

            test_passed = all([baseline_match, performance_match, career_match, total_match, salary_match])
            if not test_passed:
                all_passed = False

            validation_result = {
                "performance": performance,
                "level": level,
                "base_salary": base_salary,
                "expected_total_uplift": expected_total,
                "actual_total_uplift": uplift_result["uplift_percentage"],
                "expected_new_salary": expected_new_salary,
                "actual_new_salary": uplift_result["new_salary"],
                "passed": test_passed,
            }

            validation_results.append(validation_result)

            if not test_passed:
                LOGGER.error(f"✗ Validation failed for {performance} at Level {level}")
                LOGGER.error(
                    f"  Expected uplift: {expected_total:.2f}%, Got: {uplift_result['uplift_percentage']:.2f}%"
                )
                LOGGER.error(f"  Expected salary: £{expected_new_salary:.2f}, Got: £{uplift_result['new_salary']:.2f}")

        if all_passed:
            LOGGER.info(f"✓ All {len(test_cases)} uplift calculations validated successfully")
        else:
            failed_count = sum(1 for r in validation_results if not r["passed"])
            LOGGER.error(f"✗ {failed_count} of {len(test_cases)} uplift calculations failed validation")

        return validation_results, all_passed

    def save_review_results(self, review_results, filename_prefix="review_results"):
        """Save review results following existing codebase patterns"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Create DataFrame
        df = pd.DataFrame(review_results)

        # Save to artifacts directory
        csv_filepath = f"/Users/brunoviola/bruvio-tools/artifacts/{filename_prefix}_{timestamp}.csv"
        df.to_csv(csv_filepath, index=False)
        LOGGER.info(f"Review results saved to {csv_filepath}")

        # Also save as JSON
        json_filepath = f"/Users/brunoviola/bruvio-tools/artifacts/{filename_prefix}_{timestamp}.json"
        with open(json_filepath, "w") as f:
            json.dump(review_results, f, indent=2, default=str)
        LOGGER.info(f"Review results saved to {json_filepath}")

        return csv_filepath, json_filepath


def test_uplift_matrix_accuracy():
    """Test function to validate uplift matrix calculations"""
    LOGGER.info("Testing uplift matrix accuracy")

    # Create test system
    review_system = PerformanceReviewSystem(random_seed=42)

    # Run validation
    validation_results, all_passed = review_system.validate_uplift_calculations()

    if all_passed:
        LOGGER.info("✓ Uplift matrix validation PASSED")
        return True
    else:
        LOGGER.error("✗ Uplift matrix validation FAILED")
        return False


def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(description="Performance review system for employee simulation")
    parser.add_argument("--test-uplift-calculation", action="store_true", help="Test uplift calculation accuracy")
    parser.add_argument("--apply-review", help="Apply review to population file (JSON format)")
    parser.add_argument("--review-year", type=int, default=1, help="Review year number (default: 1)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")

    return parser


def main():
    """Main function for performance review system"""
    parser = create_parser()
    args = parser.parse_args()

    if args.test_uplift_calculation:
        success = test_uplift_matrix_accuracy()
        return 0 if success else 1

    elif args.apply_review:
        LOGGER.info(f"Applying performance review from {args.apply_review}")

        # Load population data
        try:
            with open(args.apply_review, "r") as f:
                employees = json.load(f)
            LOGGER.info(f"Loaded {len(employees)} employees")
        except Exception as e:
            LOGGER.error(f"Failed to load population data: {e}")
            return 1

        # Create review system and apply review
        review_system = PerformanceReviewSystem(random_seed=args.seed)
        review_results = review_system.apply_annual_review(employees, args.review_year)

        # Save results
        csv_path, json_path = review_system.save_review_results(review_results, f"review_year_{args.review_year}")

        LOGGER.info(f"Performance review year {args.review_year} completed successfully")
        LOGGER.info(f"CSV: {csv_path}")
        LOGGER.info(f"JSON: {json_path}")

        return 0
    else:
        LOGGER.info("Use --test-uplift-calculation or --apply-review to run performance review system")
        parser.print_help()
        return 0


if __name__ == "__main__":
    exit(main())

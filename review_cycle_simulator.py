#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

import pandas as pd
import numpy as np
from datetime import datetime
import argparse
import json
import copy
from logger import LOGGER
from performance_review_system import PerformanceReviewSystem


class ReviewCycleSimulator:
    """
    Multi-cycle performance review simulator for analyzing inequality reduction.
    Tracks salary inequality metrics across multiple review cycles to determine
    how many cycles are needed to achieve salary equity.
    """

    def __init__(self, initial_population, random_seed=42):
        self.population = copy.deepcopy(initial_population)
        self.review_system = PerformanceReviewSystem(random_seed=random_seed)
        self.cycle_history = []
        self.random_seed = random_seed
        self.rng = np.random.default_rng(random_seed)

        LOGGER.info(f"Initialized ReviewCycleSimulator with {len(self.population)} employees")

        # Calculate initial inequality metrics
        initial_metrics = self._calculate_inequality_metrics(0)
        LOGGER.info(
            f"Initial inequality metrics - Gini: {initial_metrics['gini_coefficient']:.4f}, "
            f"Gender gap: {initial_metrics['gender_gap_percent']:.2f}%"
        )

    def simulate_multiple_cycles(self, num_cycles=5, performance_consistency=0.7):
        """
        Simulate multiple review cycles with performance evolution

        Args:
            num_cycles: Number of review cycles to simulate
            performance_consistency: Probability of maintaining similar performance (0.0-1.0)
        """
        LOGGER.info(f"Starting {num_cycles}-cycle simulation with {len(self.population)} employees")
        LOGGER.info(f"Performance consistency rate: {performance_consistency:.1%}")

        inequality_progression = []

        # Calculate initial state (cycle 0)
        initial_metrics = self._calculate_inequality_metrics(0)
        inequality_progression.append(initial_metrics)

        for cycle in range(1, num_cycles + 1):
            LOGGER.info(f"Processing review cycle {cycle}")

            # Evolve performance ratings with some consistency
            self._evolve_performance_ratings(cycle, performance_consistency)

            # Apply review and salary adjustments
            cycle_results = self.review_system.apply_annual_review(self.population, cycle)
            self.cycle_history.append(cycle_results)

            # Calculate inequality metrics after this cycle
            inequality_metrics = self._calculate_inequality_metrics(cycle)
            inequality_progression.append(inequality_metrics)

            # Log cycle summary
            LOGGER.info(f"Cycle {cycle} completed:")
            LOGGER.info(f"  Gini coefficient: {inequality_metrics['gini_coefficient']:.4f}")
            LOGGER.info(f"  Gender gap: {inequality_metrics['gender_gap_percent']:.2f}%")
            LOGGER.info(f"  Median salary: £{inequality_metrics['median_salary']:.2f}")
            LOGGER.info(f"  Performance-salary correlation: {inequality_metrics['performance_salary_correlation']:.3f}")

            # Check for convergence (inequality reduction plateaus)
            if self._check_inequality_convergence(inequality_progression, cycle):
                LOGGER.info(f"Inequality metrics have converged after {cycle} cycles")
                break

        # Analyze final results
        self._analyze_inequality_reduction(inequality_progression)

        return inequality_progression

    def _evolve_performance_ratings(self, cycle, consistency_rate):
        """Evolve performance ratings with some consistency between cycles"""
        LOGGER.debug(f"Evolving performance ratings for cycle {cycle}")

        consistency_count = 0
        change_count = 0

        for employee in self.population:
            level = employee["level"]
            current_rating = employee.get("performance_rating", "Achieving")

            # Determine if performance should be consistent or change
            if len(employee["review_history"]) > 0 and self.rng.random() < consistency_rate:
                # Maintain similar performance with slight variation
                consistent_rating = self._get_similar_performance(current_rating, level)
                employee["performance_rating"] = consistent_rating
                consistency_count += 1
            else:
                # Generate completely new performance rating
                category = "senior" if level >= 4 else "core"
                weights = self.review_system.performance_weights[category]

                ratings = list(weights.keys())
                probabilities = list(weights.values())
                new_rating = self.rng.choice(ratings, p=probabilities)
                employee["performance_rating"] = new_rating
                change_count += 1

        LOGGER.debug(f"Performance evolution: {consistency_count} consistent, {change_count} changed")

    def _get_similar_performance(self, current_rating, level):
        """Get a performance rating similar to current with small chance of change"""
        performance_order = ["Not met", "Partially met", "Achieving", "High Performing", "Exceeding"]
        current_index = performance_order.index(current_rating)

        # 80% chance to stay same, 10% chance to move up/down one level
        rand_val = self.rng.random()

        if rand_val < 0.8:
            # Stay the same
            return current_rating
        elif rand_val < 0.9 and current_index > 0:
            # Move down one level
            return performance_order[current_index - 1]
        elif current_index < len(performance_order) - 1:
            # Move up one level
            return performance_order[current_index + 1]
        else:
            # Stay the same if at boundaries
            return current_rating

    def _calculate_inequality_metrics(self, cycle):
        """Calculate comprehensive inequality metrics for current population state"""
        salaries = [emp["salary"] for emp in self.population]
        genders = [emp["gender"] for emp in self.population]
        levels = [emp["level"] for emp in self.population]
        performance_ratings = [emp.get("performance_rating", "Achieving") for emp in self.population]

        # Overall inequality metrics
        gini_coefficient = self._calculate_gini(salaries)
        coefficient_of_variation = np.std(salaries) / np.mean(salaries)
        salary_range = np.max(salaries) - np.min(salaries)
        median_salary = np.median(salaries)

        # Gender pay gap analysis
        male_salaries = [emp["salary"] for emp in self.population if emp["gender"] == "Male"]
        female_salaries = [emp["salary"] for emp in self.population if emp["gender"] == "Female"]

        if len(male_salaries) > 0 and len(female_salaries) > 0:
            male_median = np.median(male_salaries)
            female_median = np.median(female_salaries)
            gender_gap_percent = ((male_median - female_median) / male_median * 100) if male_median > 0 else 0

            # Gender gap by level
            level_gaps = {}
            for level in range(1, 7):
                level_males = [
                    emp["salary"] for emp in self.population if emp["gender"] == "Male" and emp["level"] == level
                ]
                level_females = [
                    emp["salary"] for emp in self.population if emp["gender"] == "Female" and emp["level"] == level
                ]

                if len(level_males) > 0 and len(level_females) > 0:
                    level_gap = (np.median(level_males) - np.median(level_females)) / np.median(level_males) * 100
                    level_gaps[level] = level_gap
        else:
            gender_gap_percent = 0
            level_gaps = {}

        # Performance-salary correlation
        perf_mapping = {"Not met": 1, "Partially met": 2, "Achieving": 3, "High Performing": 4, "Exceeding": 5}
        perf_numeric = [perf_mapping.get(rating, 3) for rating in performance_ratings]

        try:
            corr_matrix = np.corrcoef(perf_numeric, salaries)
            performance_correlation = (
                float(corr_matrix[0, 1]) if corr_matrix.shape == (2, 2) and len(perf_numeric) > 1 else 0.0
            )
        except:
            performance_correlation = 0.0

        try:
            corr_matrix = np.corrcoef(levels, salaries)
            level_correlation = float(corr_matrix[0, 1]) if corr_matrix.shape == (2, 2) and len(levels) > 1 else 0.0
        except:
            level_correlation = 0.0

        # Salary statistics by level
        level_stats = {}
        for level in range(1, 7):
            level_salaries = [emp["salary"] for emp in self.population if emp["level"] == level]
            if level_salaries:
                level_stats[level] = {
                    "count": len(level_salaries),
                    "median": np.median(level_salaries),
                    "mean": np.mean(level_salaries),
                    "std": np.std(level_salaries),
                }

        metrics = {
            "cycle": cycle,
            "gini_coefficient": float(gini_coefficient),
            "coefficient_of_variation": float(coefficient_of_variation),
            "median_salary": float(median_salary),
            "mean_salary": float(np.mean(salaries)),
            "salary_range": float(salary_range),
            "salary_std": float(np.std(salaries)),
            "gender_gap_percent": float(gender_gap_percent),
            "gender_gap_by_level": level_gaps,
            "performance_salary_correlation": float(performance_correlation),
            "level_salary_correlation": float(level_correlation),
            "level_statistics": level_stats,
            "population_size": len(self.population),
            "timestamp": datetime.now().isoformat(),
        }

        return metrics

    def _calculate_gini(self, salaries):
        """Calculate Gini coefficient for salary inequality measurement"""
        if len(salaries) == 0:
            return 0.0

        sorted_salaries = np.sort(salaries)
        n = len(salaries)
        cumsum = np.cumsum(sorted_salaries)

        # Gini coefficient formula
        gini = (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n
        return max(0.0, min(1.0, gini))  # Ensure Gini is between 0 and 1

    def _check_inequality_convergence(self, inequality_progression, current_cycle, lookback=3):
        """Check if inequality metrics have converged (stopped improving significantly)"""
        if current_cycle < lookback + 1:
            return False

        # Look at last few cycles to check for convergence
        recent_gini = [metrics["gini_coefficient"] for metrics in inequality_progression[-lookback:]]
        recent_gender_gap = [abs(metrics["gender_gap_percent"]) for metrics in inequality_progression[-lookback:]]

        # Check if Gini coefficient has stopped decreasing significantly
        gini_improvement = recent_gini[0] - recent_gini[-1]
        gender_gap_improvement = recent_gender_gap[0] - recent_gender_gap[-1]

        # Convergence thresholds
        gini_threshold = 0.001  # Less than 0.1% improvement
        gender_gap_threshold = 0.1  # Less than 0.1% improvement

        gini_converged = gini_improvement < gini_threshold
        gender_gap_converged = gender_gap_improvement < gender_gap_threshold

        if gini_converged and gender_gap_converged:
            LOGGER.debug(
                f"Convergence detected - Gini improvement: {gini_improvement:.6f}, "
                f"Gender gap improvement: {gender_gap_improvement:.2f}%"
            )
            return True

        return False

    def _analyze_inequality_reduction(self, inequality_progression):
        """Analyze the inequality reduction across all cycles"""
        LOGGER.info("Analyzing inequality reduction across cycles:")

        if len(inequality_progression) < 2:
            LOGGER.warning("Not enough data to analyze inequality reduction")
            return

        initial = inequality_progression[0]
        final = inequality_progression[-1]

        # Calculate total improvements
        gini_reduction = initial["gini_coefficient"] - final["gini_coefficient"]
        gini_reduction_pct = (
            (gini_reduction / initial["gini_coefficient"] * 100) if initial["gini_coefficient"] > 0 else 0
        )

        gender_gap_reduction = abs(initial["gender_gap_percent"]) - abs(final["gender_gap_percent"])

        median_salary_increase = final["median_salary"] - initial["median_salary"]
        median_salary_increase_pct = (
            (median_salary_increase / initial["median_salary"] * 100) if initial["median_salary"] > 0 else 0
        )

        # Performance-salary correlation improvement
        perf_correlation_improvement = (
            final["performance_salary_correlation"] - initial["performance_salary_correlation"]
        )

        LOGGER.info(f"Total improvement over {len(inequality_progression)-1} cycles:")
        LOGGER.info(
            f"  Gini coefficient: {initial['gini_coefficient']:.4f} → {final['gini_coefficient']:.4f} "
            f"(reduction: {gini_reduction:.4f}, {gini_reduction_pct:.1f}%)"
        )
        LOGGER.info(
            f"  Gender pay gap: {initial['gender_gap_percent']:.2f}% → {final['gender_gap_percent']:.2f}% "
            f"(reduction: {gender_gap_reduction:.2f}%)"
        )
        LOGGER.info(
            f"  Median salary: £{initial['median_salary']:.2f} → £{final['median_salary']:.2f} "
            f"(increase: £{median_salary_increase:.2f}, {median_salary_increase_pct:.1f}%)"
        )
        LOGGER.info(
            f"  Performance-salary correlation: {initial['performance_salary_correlation']:.3f} → "
            f"{final['performance_salary_correlation']:.3f} (improvement: {perf_correlation_improvement:.3f})"
        )

        # Determine cycles needed for significant inequality reduction
        significant_reduction_threshold = 0.5  # 50% reduction in Gini
        cycles_for_significant_reduction = self._find_cycles_for_threshold(
            inequality_progression, "gini_coefficient", initial["gini_coefficient"], significant_reduction_threshold
        )

        if cycles_for_significant_reduction:
            LOGGER.info(
                f"Significant inequality reduction (50%) achieved after {cycles_for_significant_reduction} cycles"
            )
        else:
            LOGGER.info("Significant inequality reduction not achieved within simulated cycles")

        # Determine cycles for gender pay gap elimination
        gender_gap_threshold = 1.0  # Within 1%
        cycles_for_gender_equality = self._find_cycles_for_gender_threshold(
            inequality_progression, gender_gap_threshold
        )

        if cycles_for_gender_equality:
            LOGGER.info(f"Gender pay gap reduced to <{gender_gap_threshold}% after {cycles_for_gender_equality} cycles")
        else:
            LOGGER.info(f"Gender pay gap not reduced to <{gender_gap_threshold}% within simulated cycles")

    def _find_cycles_for_threshold(self, progression, metric, initial_value, reduction_percentage):
        """Find the cycle where a metric reaches a threshold reduction"""
        target_value = initial_value * (1 - reduction_percentage)

        for i, metrics in enumerate(progression):
            if metrics[metric] <= target_value:
                return i

        return None

    def _find_cycles_for_gender_threshold(self, progression, threshold):
        """Find the cycle where gender gap falls below threshold"""
        for i, metrics in enumerate(progression):
            if abs(metrics["gender_gap_percent"]) <= threshold:
                return i

        return None

    def save_simulation_results(self, inequality_progression, filename_prefix="simulation_results"):
        """Save complete simulation results"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save inequality progression
        inequality_df = pd.DataFrame(inequality_progression)
        inequality_filepath = f"/Users/brunoviola/bruvio-tools/artifacts/{filename_prefix}_inequality_{timestamp}.csv"
        inequality_df.to_csv(inequality_filepath, index=False)
        LOGGER.info(f"Inequality progression saved to {inequality_filepath}")

        # Save complete cycle history
        all_reviews = []
        for cycle_data in self.cycle_history:
            all_reviews.extend(cycle_data)

        if all_reviews:
            reviews_df = pd.DataFrame(all_reviews)
            reviews_filepath = f"/Users/brunoviola/bruvio-tools/artifacts/{filename_prefix}_reviews_{timestamp}.csv"
            reviews_df.to_csv(reviews_filepath, index=False)
            LOGGER.info(f"Review history saved to {reviews_filepath}")

        # Save final population state
        population_df = pd.DataFrame(self.population)
        population_filepath = (
            f"/Users/brunoviola/bruvio-tools/artifacts/{filename_prefix}_final_population_{timestamp}.csv"
        )
        population_df.to_csv(population_filepath, index=False)
        LOGGER.info(f"Final population saved to {population_filepath}")

        # Save JSON summary
        summary_data = {
            "simulation_metadata": {
                "total_cycles": len(inequality_progression) - 1,
                "population_size": len(self.population),
                "random_seed": self.random_seed,
                "timestamp": timestamp,
            },
            "inequality_progression": inequality_progression,
            "final_analysis": self._get_final_analysis_summary(inequality_progression),
        }

        json_filepath = f"/Users/brunoviola/bruvio-tools/artifacts/{filename_prefix}_summary_{timestamp}.json"
        with open(json_filepath, "w") as f:
            json.dump(summary_data, f, indent=2, default=str)
        LOGGER.info(f"Simulation summary saved to {json_filepath}")

        return {
            "inequality_csv": inequality_filepath,
            "reviews_csv": reviews_filepath if all_reviews else None,
            "population_csv": population_filepath,
            "summary_json": json_filepath,
        }

    def _get_final_analysis_summary(self, inequality_progression):
        """Get final analysis summary for JSON export"""
        if len(inequality_progression) < 2:
            return {"error": "Insufficient data for analysis"}

        initial = inequality_progression[0]
        final = inequality_progression[-1]

        return {
            "total_cycles": len(inequality_progression) - 1,
            "initial_gini_coefficient": initial["gini_coefficient"],
            "final_gini_coefficient": final["gini_coefficient"],
            "gini_reduction_percentage": (
                ((initial["gini_coefficient"] - final["gini_coefficient"]) / initial["gini_coefficient"] * 100)
                if initial["gini_coefficient"] > 0
                else 0
            ),
            "initial_gender_gap": initial["gender_gap_percent"],
            "final_gender_gap": final["gender_gap_percent"],
            "gender_gap_reduction": abs(initial["gender_gap_percent"]) - abs(final["gender_gap_percent"]),
            "median_salary_increase": final["median_salary"] - initial["median_salary"],
            "performance_correlation_improvement": final["performance_salary_correlation"]
            - initial["performance_salary_correlation"],
        }


def validate_inequality_calculations():
    """Validate inequality calculation methods"""
    LOGGER.info("Validating inequality calculation methods")

    # Create a simple class to test the Gini calculation
    class GiniTester:
        def _calculate_gini(self, salaries):
            if len(salaries) == 0:
                return 0.0

            sorted_salaries = np.sort(salaries)
            n = len(salaries)
            cumsum = np.cumsum(sorted_salaries)

            # Gini coefficient formula
            gini = (n + 1 - 2 * np.sum(cumsum) / cumsum[-1]) / n
            return max(0.0, min(1.0, gini))  # Ensure Gini is between 0 and 1

    tester = GiniTester()

    # Test Gini coefficient calculation - truly equal distribution
    equal_salaries = [70000, 70000, 70000, 70000, 70000]  # Perfectly equal
    gini_equal = tester._calculate_gini(equal_salaries)

    # For perfectly equal distribution, Gini should be 0
    if gini_equal < 0.01:  # Very close to 0
        LOGGER.info(f"✓ Equal distribution Gini validation passed: {gini_equal:.4f}")
    else:
        LOGGER.error(f"✗ Equal distribution Gini validation failed: {gini_equal:.4f}")
        return False

    # Test with moderately unequal distribution
    moderate_salaries = [50000, 60000, 70000, 80000, 90000]
    gini_moderate = tester._calculate_gini(moderate_salaries)

    # Test with highly unequal distribution
    unequal_salaries = [40000, 50000, 60000, 100000, 150000]
    gini_unequal = tester._calculate_gini(unequal_salaries)

    if gini_unequal > gini_moderate > gini_equal:
        LOGGER.info(
            f"✓ Inequality detection validation passed: {gini_unequal:.4f} > {gini_moderate:.4f} > {gini_equal:.4f}"
        )
    else:
        LOGGER.error(
            f"✗ Inequality detection validation failed: {gini_unequal:.4f}, {gini_moderate:.4f}, {gini_equal:.4f}"
        )
        return False

    # Test edge cases
    empty_salaries = []
    gini_empty = tester._calculate_gini(empty_salaries)
    if gini_empty == 0.0:
        LOGGER.info(f"✓ Empty list validation passed: {gini_empty:.4f}")
    else:
        LOGGER.error(f"✗ Empty list validation failed: {gini_empty:.4f}")
        return False

    # Test single salary
    single_salary = [75000]
    gini_single = tester._calculate_gini(single_salary)
    if gini_single == 0.0:
        LOGGER.info(f"✓ Single value validation passed: {gini_single:.4f}")
    else:
        LOGGER.error(f"✗ Single value validation failed: {gini_single:.4f}")
        return False

    LOGGER.info("✓ All inequality calculations validated successfully")
    return True


def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(description="Multi-cycle review simulation for inequality analysis")
    parser.add_argument("--cycles", type=int, default=5, help="Number of review cycles (default: 5)")
    parser.add_argument("--population-file", help="JSON file with initial population data (required for simulation)")
    parser.add_argument(
        "--consistency", type=float, default=0.7, help="Performance consistency rate 0.0-1.0 (default: 0.7)"
    )
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--validate-calculations", action="store_true", help="Validate inequality calculation methods")
    parser.add_argument(
        "--output-prefix", default="simulation_results", help="Output file prefix (default: simulation_results)"
    )

    return parser


def main():
    """Main function for review cycle simulation"""
    parser = create_parser()
    args = parser.parse_args()

    if args.validate_calculations:
        success = validate_inequality_calculations()
        return 0 if success else 1

    if not args.population_file:
        LOGGER.error("--population-file is required for simulation")
        parser.print_help()
        return 1

    LOGGER.info(f"Starting multi-cycle simulation with {args.cycles} cycles")

    # Load population data
    try:
        with open(args.population_file, "r") as f:
            initial_population = json.load(f)
        LOGGER.info(f"Loaded {len(initial_population)} employees from {args.population_file}")
    except Exception as e:
        LOGGER.error(f"Failed to load population data: {e}")
        return 1

    # Create simulator and run simulation
    simulator = ReviewCycleSimulator(initial_population, random_seed=args.seed)
    inequality_progression = simulator.simulate_multiple_cycles(
        num_cycles=args.cycles, performance_consistency=args.consistency
    )

    # Save results
    file_paths = simulator.save_simulation_results(inequality_progression, args.output_prefix)

    LOGGER.info(f"Multi-cycle simulation completed successfully")
    LOGGER.info(f"Results saved:")
    for key, path in file_paths.items():
        if path:
            LOGGER.info(f"  {key}: {path}")

    return 0


if __name__ == "__main__":
    exit(main())

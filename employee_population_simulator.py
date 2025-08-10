#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import argparse
import json
from enum import Enum
from logger import LOGGER

# Performance Review Uplift Matrix from PRP requirements
UPLIFT_MATRIX = {
    "Not met": {"baseline": 0.0125, "performance": 0.00, "competent": 0.00, "advanced": 0.0075, "expert": 0.01},
    "Partially met": {"baseline": 0.0125, "performance": 0.00, "competent": 0.00, "advanced": 0.0075, "expert": 0.01},
    "Achieving": {"baseline": 0.0125, "performance": 0.0125, "competent": 0.005, "advanced": 0.0075, "expert": 0.01},
    "High Performing": {"baseline": 0.0125, "performance": 0.0225, "competent": 0.005, "advanced": 0.0075, "expert": 0.01},
    "Exceeding": {"baseline": 0.0125, "performance": 0.030, "competent": 0.005, "advanced": 0.0075, "expert": 0.01}
}

LEVEL_MAPPING = {
    1: "competent", 2: "advanced", 3: "expert",
    4: "competent", 5: "advanced", 6: "expert"
}

class EmployeeLevel(Enum):
    """Employee level enumeration following existing codebase patterns"""
    CORE_COMPETENT = 1
    CORE_ADVANCED = 2
    CORE_EXPERT = 3
    SENIOR_COMPETENT = 4
    SENIOR_ADVANCED = 5
    SENIOR_EXPERT = 6

class EmployeePopulationGenerator:
    """
    Generate realistic employee population for tech company simulation.
    Implements salary constraints, level distributions, and inequality patterns.
    """
    
    def __init__(self, population_size=1000, random_seed=42, level_distribution=None, gender_pay_gap_percent=None, salary_constraints=None):
        self.population_size = population_size
        self.rng = np.random.default_rng(random_seed)
        self.random_seed = random_seed
        
        # Default level distribution (weighted towards lower levels)
        self.default_level_distribution = [0.25, 0.25, 0.20, 0.15, 0.10, 0.05]
        
        # Use custom distribution if provided, otherwise use default
        if level_distribution is not None:
            if len(level_distribution) != 6:
                raise ValueError("Level distribution must have exactly 6 values for levels 1-6")
            if abs(sum(level_distribution) - 1.0) > 0.001:
                raise ValueError(f"Level distribution must sum to 1.0, got {sum(level_distribution)}")
            self.level_distribution = level_distribution
        else:
            self.level_distribution = self.default_level_distribution
        
        # Realistic salary constraints by level
        self.default_salary_constraints = {
            1: {'min': 28000, 'max': 35000, 'median_target': 30000},  # Graduate level
            2: {'min': 45000, 'max': 72000, 'median_target': 60000},  # Junior with some hand-holding
            3: {'min': 72000, 'max': 95000, 'median_target': 83939},  # Standard hire level
            4: {'min': 76592, 'max': 103624, 'median_target': 90108}, # Senior competent
            5: {'min': 76592, 'max': 103624, 'median_target': 90108}, # Senior advanced  
            6: {'min': 76592, 'max': 103624, 'median_target': 90108}  # Senior expert
        }
        
        self.salary_constraints = salary_constraints if salary_constraints is not None else self.default_salary_constraints
        
        # Negotiation dynamics - percentage of people who negotiate hard
        self.negotiation_rates = {
            1: 0.05,  # 5% of graduates negotiate hard (rare)
            2: 0.15,  # 15% of level 2s negotiate hard
            3: 0.30,  # 30% of level 3s negotiate hard (frequent as you mentioned)
            4: 0.25,  # 25% of level 4s negotiate hard
            5: 0.20,  # 20% of level 5s negotiate hard
            6: 0.15   # 15% of level 6s negotiate hard
        }
        
        # Gender pay gap configuration (2024 UK average is 15.8%)
        self.gender_pay_gap_percent = gender_pay_gap_percent
        if self.gender_pay_gap_percent is not None:
            if not (0 <= self.gender_pay_gap_percent <= 50):
                raise ValueError(f"Gender pay gap percent must be between 0 and 50, got {self.gender_pay_gap_percent}")
            
        LOGGER.info(f"Initializing population generator for {population_size} employees with seed {random_seed}")
        LOGGER.info(f"Level distribution: {[f'L{i+1}: {p:.1%}' for i, p in enumerate(self.level_distribution)]}")
        LOGGER.info(f"Salary constraints: L1: £{self.salary_constraints[1]['min']:,}-£{self.salary_constraints[1]['max']:,}, L2: £{self.salary_constraints[2]['min']:,}-£{self.salary_constraints[2]['max']:,}, L3: £{self.salary_constraints[3]['min']:,}-£{self.salary_constraints[3]['max']:,}")
        if self.gender_pay_gap_percent is not None:
            LOGGER.info(f"Target gender pay gap: {self.gender_pay_gap_percent:.1f}%")
    
    def generate_population(self):
        """Generate complete employee population with realistic distributions"""
        LOGGER.info("Generating employee population with realistic distributions")
        employees = []
        
        # Level distribution using custom or default distribution
        levels = self.rng.choice([1, 2, 3, 4, 5, 6], size=self.population_size, 
                                p=self.level_distribution)
        
        # Gender distribution (tech industry realistic split)
        genders = self.rng.choice(['Male', 'Female'], size=self.population_size, 
                                 p=[0.65, 0.35])
        
        # Generate salaries with level-based constraints
        salaries = self._generate_constrained_salaries(levels)
        
        # Apply realistic inequality patterns while preserving median constraints
        salaries = self._apply_inequality_patterns(salaries, genders, levels)
        
        # Re-validate and adjust senior median after inequality patterns
        salaries = self._ensure_senior_median_constraint(salaries, levels)
        
        # Generate hire dates (spread over last 5 years)
        hire_dates = self._generate_hire_dates()
        
        for i in range(self.population_size):
            employees.append({
                'employee_id': i + 1,
                'level': int(levels[i]),
                'salary': float(salaries[i]),
                'gender': genders[i],
                'performance_rating': self._assign_initial_performance(levels[i]),
                'hire_date': hire_dates[i],
                'review_history': []
            })
        
        LOGGER.info(f"Generated {len(employees)} employees")
        self._log_population_statistics(employees)
        
        return employees
    
    def _generate_constrained_salaries(self, levels):
        """Generate salaries with realistic constraints and negotiation dynamics"""
        LOGGER.info("Generating salary distributions with realistic constraints and negotiation simulation")
        salaries = np.zeros(len(levels))
        
        for level in [1, 2, 3, 4, 5, 6]:
            level_mask = levels == level
            level_count = np.sum(level_mask)
            
            if level_count == 0:
                continue
            
            constraints = self.salary_constraints[level]
            min_salary = constraints['min']
            max_salary = constraints['max'] 
            median_target = constraints['median_target']
            
            # Generate base salaries around median target
            level_salaries = self._generate_median_constrained(
                target_median=median_target,
                size=level_count,
                min_salary=min_salary,
                max_salary=max_salary
            )
            
            # Apply negotiation dynamics
            level_salaries = self._apply_negotiation_effects(level_salaries, level, level_count)
            
            salaries[level_mask] = level_salaries
            
            LOGGER.debug(f"Level {level}: {level_count} employees, range £{level_salaries.min():.0f}-£{level_salaries.max():.0f}, median £{np.median(level_salaries):.0f}")
        
        return salaries
    
    def _apply_negotiation_effects(self, salaries, level, count):
        """Apply negotiation dynamics - some people negotiate hard for higher salaries"""
        negotiation_rate = self.negotiation_rates[level]
        hard_negotiators_count = int(count * negotiation_rate)
        
        if hard_negotiators_count == 0:
            return salaries
        
        # Select random employees who negotiate hard
        hard_negotiator_indices = self.rng.choice(count, size=hard_negotiators_count, replace=False)
        
        # Hard negotiators get salary boosts
        if level == 1:
            # Graduate hard negotiators might get up to £5k more
            boost_amounts = self.rng.uniform(2000, 5000, hard_negotiators_count)
        elif level == 2:  
            # Level 2 hard negotiators might get up to £8k more
            boost_amounts = self.rng.uniform(3000, 8000, hard_negotiators_count)
        elif level == 3:
            # Level 3 hard negotiators (frequent) might negotiate up to £18k more (can reach ~90k as you mentioned)
            boost_amounts = self.rng.uniform(5000, 18000, hard_negotiators_count)
        else:
            # Senior levels negotiate for moderate boosts
            boost_amounts = self.rng.uniform(2000, 10000, hard_negotiators_count)
        
        # Apply boosts but respect maximum constraints
        constraints = self.salary_constraints[level]
        max_negotiated = constraints['max'] + (boost_amounts.max() if level == 3 else 0)  # Allow Level 3 to exceed normal max
        
        salaries[hard_negotiator_indices] += boost_amounts
        salaries[hard_negotiator_indices] = np.clip(salaries[hard_negotiator_indices], 
                                                   constraints['min'], 
                                                   max_negotiated)
        
        LOGGER.debug(f"Level {level}: {hard_negotiators_count} hard negotiators got salary boosts (avg £{boost_amounts.mean():.0f})")
        
        return salaries
    
    def _generate_median_constrained(self, target_median, size, min_salary, max_salary):
        """Generate distribution with exact median constraint"""
        LOGGER.debug(f"Generating {size} salaries with target median £{target_median:.2f}")
        
        # Start with normal distribution centered on target median
        salaries = self.rng.normal(target_median, (max_salary - min_salary) / 6, size)
        
        # Iterative adjustment to meet median constraint
        max_iterations = 100
        tolerance = 50  # £50 tolerance
        
        for iteration in range(max_iterations):
            current_median = np.median(salaries)
            difference = abs(current_median - target_median)
            
            if difference < tolerance:
                LOGGER.debug(f"Converged after {iteration + 1} iterations")
                break
            
            # Adjust salaries gradually towards target median
            adjustment = (target_median - current_median) * 0.1
            salaries += adjustment
            
            # Ensure bounds are respected
            salaries = np.clip(salaries, min_salary, max_salary)
            
            if iteration == max_iterations - 1:
                LOGGER.warning(f"Did not fully converge to target median. Final: £{current_median:.2f}, Target: £{target_median:.2f}")
        
        final_median = np.median(salaries)
        LOGGER.debug(f"Final median: £{final_median:.2f} (target: £{target_median:.2f}, difference: £{abs(final_median - target_median):.2f})")
        
        return salaries
    
    def _ensure_senior_median_constraint(self, salaries, levels):
        """Ensure senior median constraint is maintained after inequality adjustments"""
        senior_mask = np.isin(levels, [4, 5, 6])
        if np.sum(senior_mask) == 0:
            return salaries
        
        senior_salaries = salaries[senior_mask]
        current_median = np.median(senior_salaries)
        target_median = 90108.00
        tolerance = 50.0
        
        if abs(current_median - target_median) > tolerance:
            LOGGER.debug(f"Adjusting senior median from £{current_median:.2f} to £{target_median:.2f}")
            
            # Apply uniform adjustment to all senior salaries
            adjustment = target_median - current_median
            salaries[senior_mask] += adjustment
            
            # Ensure bounds are still respected
            salaries[senior_mask] = np.clip(salaries[senior_mask], 76591.80, 103624.20)
            
            final_median = np.median(salaries[senior_mask])
            LOGGER.debug(f"Final senior median after adjustment: £{final_median:.2f}")
        
        return salaries
    
    def _apply_inequality_patterns(self, salaries, genders, levels):
        """Apply realistic gender and level-based inequality"""
        LOGGER.info("Applying realistic inequality patterns")
        adjusted_salaries = salaries.copy()
        
        # Apply specific gender pay gap if configured
        if self.gender_pay_gap_percent is not None:
            adjusted_salaries = self._apply_specific_gender_gap(adjusted_salaries, genders, levels)
        else:
            # Default random inequality patterns
            male_indices = np.where(genders == 'Male')[0]
            female_indices = np.where(genders == 'Female')[0]
            
            # Random advantages/disadvantages affecting subset of population
            advantage_male_mask = self.rng.random(len(male_indices)) < 0.3  # 30% of males get advantage
            disadvantage_female_mask = self.rng.random(len(female_indices)) < 0.2  # 20% of females get disadvantage
            
            inequality_factor = 0.05  # 5% typical tech industry gap
            adjusted_salaries[male_indices[advantage_male_mask]] *= (1 + inequality_factor)
            adjusted_salaries[female_indices[disadvantage_female_mask]] *= (1 - inequality_factor)
        
        # Level-based exceptions (some core outperform seniors, some seniors underperform)
        adjusted_salaries = self._add_level_exceptions(adjusted_salaries, levels)
        
        LOGGER.debug(f"Applied inequality patterns to population")
        
        return adjusted_salaries
    
    def _apply_specific_gender_gap(self, salaries, genders, levels):
        """Apply a specific gender pay gap percentage"""
        LOGGER.info(f"Applying specific gender pay gap: {self.gender_pay_gap_percent:.1f}%")
        
        adjusted_salaries = salaries.copy()
        male_indices = np.where(genders == 'Male')[0]
        female_indices = np.where(genders == 'Female')[0]
        
        if len(male_indices) == 0 or len(female_indices) == 0:
            LOGGER.warning("Cannot apply gender pay gap - missing male or female employees")
            return adjusted_salaries
        
        # Calculate current gap to understand baseline
        current_male_median = np.median(adjusted_salaries[male_indices])
        current_female_median = np.median(adjusted_salaries[female_indices])
        
        # Target: Male median should be higher by the specified percentage
        # Formula: male_median = female_median / (1 - gap_percent/100)
        target_gap_factor = self.gender_pay_gap_percent / 100.0
        
        # We'll adjust by level to make it more realistic
        for level in [1, 2, 3, 4, 5, 6]:
            level_male_mask = (genders == 'Male') & (levels == level)
            level_female_mask = (genders == 'Female') & (levels == level)
            
            level_male_indices = np.where(level_male_mask)[0]
            level_female_indices = np.where(level_female_mask)[0]
            
            if len(level_male_indices) == 0 or len(level_female_indices) == 0:
                continue
            
            # Apply proportional adjustments to achieve target gap
            # Slightly increase male salaries and decrease female salaries
            male_adjustment = 1 + (target_gap_factor * 0.6)  # 60% of adjustment to male increase
            female_adjustment = 1 - (target_gap_factor * 0.4)  # 40% of adjustment to female decrease
            
            adjusted_salaries[level_male_indices] *= male_adjustment
            adjusted_salaries[level_female_indices] *= female_adjustment
        
        # Verify the final gap
        final_male_median = np.median(adjusted_salaries[male_indices])
        final_female_median = np.median(adjusted_salaries[female_indices])
        actual_gap = ((final_male_median - final_female_median) / final_male_median) * 100
        
        LOGGER.info(f"Applied gender pay gap: {actual_gap:.1f}% (target: {self.gender_pay_gap_percent:.1f}%)")
        LOGGER.debug(f"Male median: £{final_male_median:.2f}, Female median: £{final_female_median:.2f}")
        
        return adjusted_salaries
    
    def _add_level_exceptions(self, salaries, levels):
        """Add realistic exceptions where level doesn't perfectly correlate with salary"""
        # 10% of core engineers outperform their level
        core_mask = np.isin(levels, [1, 2, 3])
        core_indices = np.where(core_mask)[0]
        
        if len(core_indices) > 0:
            high_performing_core_count = max(1, int(len(core_indices) * 0.1))
            high_performing_core = self.rng.choice(core_indices, size=high_performing_core_count, replace=False)
            bonus_amounts = self.rng.normal(5000, 2000, len(high_performing_core))
            salaries[high_performing_core] += bonus_amounts
            
            LOGGER.debug(f"Applied bonuses to {len(high_performing_core)} high-performing core engineers")
        
        # 15% of senior engineers underperform
        senior_mask = np.isin(levels, [4, 5, 6])
        senior_indices = np.where(senior_mask)[0]
        
        if len(senior_indices) > 0:
            underperforming_senior_count = max(1, int(len(senior_indices) * 0.15))
            underperforming_senior = self.rng.choice(senior_indices, size=underperforming_senior_count, replace=False)
            penalty_amounts = self.rng.normal(8000, 3000, len(underperforming_senior))
            salaries[underperforming_senior] -= penalty_amounts
            
            LOGGER.debug(f"Applied penalties to {len(underperforming_senior)} underperforming senior engineers")
        
        return salaries
    
    def _assign_initial_performance(self, level):
        """Assign initial performance rating based on level"""
        # Performance weights based on level (senior engineers perform better on average)
        if level >= 4:  # Senior engineers
            performance_weights = {
                'Not met': 0.02, 'Partially met': 0.08, 'Achieving': 0.40,
                'High Performing': 0.40, 'Exceeding': 0.10
            }
        else:  # Core engineers
            performance_weights = {
                'Not met': 0.05, 'Partially met': 0.15, 'Achieving': 0.55,
                'High Performing': 0.22, 'Exceeding': 0.03
            }
        
        ratings = list(performance_weights.keys())
        probabilities = list(performance_weights.values())
        
        return self.rng.choice(ratings, p=probabilities)
    
    def _assign_initial_performance(self, level):
        """Assign realistic initial performance rating based on level"""
        category = 'senior' if level >= 4 else 'core'
        performance_weights = {
            'core': {
                'Not met': 0.05, 'Partially met': 0.10, 'Achieving': 0.60, 
                'High Performing': 0.20, 'Exceeding': 0.05
            },
            'senior': {
                'Not met': 0.02, 'Partially met': 0.08, 'Achieving': 0.50, 
                'High Performing': 0.30, 'Exceeding': 0.10
            }
        }
        
        weights = performance_weights[category]
        ratings = list(weights.keys())
        probabilities = list(weights.values())
        
        return self.rng.choice(ratings, p=probabilities)
    
    def _generate_hire_dates(self):
        """Generate realistic hire dates spread over last 5 years"""
        start_date = datetime.now() - timedelta(days=5*365)
        end_date = datetime.now() - timedelta(days=30)  # No one hired in last month
        
        hire_dates = []
        for _ in range(self.population_size):
            # Random date between start and end
            days_diff = (end_date - start_date).days
            random_days = int(self.rng.integers(0, days_diff))
            hire_date = start_date + timedelta(days=random_days)
            hire_dates.append(hire_date.strftime("%Y-%m-%d"))
        
        return hire_dates
    
    def _log_population_statistics(self, employees):
        """Log key population statistics for validation"""
        df = pd.DataFrame(employees)
        
        # Overall statistics
        LOGGER.info(f"Population Statistics:")
        LOGGER.info(f"Total employees: {len(employees)}")
        LOGGER.info(f"Salary range: £{df['salary'].min():.2f} - £{df['salary'].max():.2f}")
        LOGGER.info(f"Overall median salary: £{df['salary'].median():.2f}")
        
        # Level distribution
        level_counts = df['level'].value_counts().sort_index()
        LOGGER.info("Level distribution:")
        for level, count in level_counts.items():
            percentage = count / len(employees) * 100
            LOGGER.info(f"  Level {level}: {count} employees ({percentage:.1f}%)")
        
        # Gender distribution
        gender_counts = df['gender'].value_counts()
        LOGGER.info("Gender distribution:")
        for gender, count in gender_counts.items():
            percentage = count / len(employees) * 100
            LOGGER.info(f"  {gender}: {count} employees ({percentage:.1f}%)")
        
        # Salary by level
        LOGGER.info("Salary statistics by level:")
        for level in sorted(df['level'].unique()):
            level_df = df[df['level'] == level]
            category = "Senior" if level >= 4 else "Core"
            LOGGER.info(f"  Level {level} ({category}): median £{level_df['salary'].median():.2f}, "
                       f"mean £{level_df['salary'].mean():.2f}")
        
        # Gender pay gap analysis
        male_salaries = df[df['gender'] == 'Male']['salary']
        female_salaries = df[df['gender'] == 'Female']['salary']
        
        if len(male_salaries) > 0 and len(female_salaries) > 0:
            male_median = male_salaries.median()
            female_median = female_salaries.median()
            gap_percentage = (male_median - female_median) / male_median * 100
            
            LOGGER.info(f"Gender pay gap:")
            LOGGER.info(f"  Male median: £{male_median:.2f}")
            LOGGER.info(f"  Female median: £{female_median:.2f}")
            LOGGER.info(f"  Gap: {gap_percentage:.2f}%")
    
    def save_population_data(self, employees, filename_prefix="employee_population"):
        """Save population data following existing codebase patterns"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create DataFrame
        df = pd.DataFrame(employees)
        
        # Save to artifacts directory following aws_cost.py pattern
        filepath = f"/Users/brunoviola/bruvio-tools/artifacts/{filename_prefix}_{timestamp}.csv"
        df.to_csv(filepath, index=False)
        LOGGER.info(f"Population data saved to {filepath}")
        
        # Also save as JSON for programmatic access
        json_filepath = f"/Users/brunoviola/bruvio-tools/artifacts/{filename_prefix}_{timestamp}.json"
        with open(json_filepath, 'w') as f:
            json.dump(employees, f, indent=2, default=str)
        LOGGER.info(f"Population data saved to {json_filepath}")
        
        return filepath, json_filepath

def validate_salary_constraints(employees):
    """Validate that salary constraints are met"""
    LOGGER.info("Validating salary constraints")
    df = pd.DataFrame(employees)
    
    # Check senior engineer median constraint
    senior_employees = df[df['level'].isin([4, 5, 6])]
    if len(senior_employees) > 0:
        senior_median = senior_employees['salary'].median()
        target_median = 90108.00
        tolerance = 50.0
        
        difference = abs(senior_median - target_median)
        if difference <= tolerance:
            LOGGER.info(f"✓ Senior median salary constraint met: £{senior_median:.2f} (target: £{target_median:.2f})")
            return True
        else:
            LOGGER.error(f"✗ Senior median salary constraint failed: £{senior_median:.2f} (target: £{target_median:.2f}, diff: £{difference:.2f})")
            return False
    else:
        LOGGER.warning("No senior employees found for validation")
        return False

def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(description="Generate employee population simulation data")
    parser.add_argument("--generate", action="store_true", help="Generate new employee population")
    parser.add_argument("--size", type=int, default=1000, help="Population size (default: 1000)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    parser.add_argument("--validate", action="store_true", help="Validate salary constraints")
    parser.add_argument("--output-prefix", default="employee_population", help="Output file prefix")
    
    return parser

def main():
    """Main function for employee population simulation"""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.generate:
        LOGGER.info(f"Generating employee population with size {args.size} and seed {args.seed}")
        
        # Create generator and generate population
        generator = EmployeePopulationGenerator(population_size=args.size, random_seed=args.seed)
        employees = generator.generate_population()
        
        # Validate constraints
        if validate_salary_constraints(employees):
            LOGGER.info("✓ All salary constraints validated successfully")
        else:
            LOGGER.error("✗ Salary constraints validation failed")
            return 1
        
        # Save data
        csv_path, json_path = generator.save_population_data(employees, args.output_prefix)
        LOGGER.info(f"Population generation completed successfully")
        LOGGER.info(f"CSV: {csv_path}")
        LOGGER.info(f"JSON: {json_path}")
        
        return 0
    else:
        LOGGER.info("Use --generate to create employee population data")
        parser.print_help()
        return 0

if __name__ == "__main__":
    exit(main())
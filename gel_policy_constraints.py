#!/usr/bin/env python3

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from logger import LOGGER


class GELPolicyConstraints:
    """
    Policy-constrained intervention logic for GEL scenario.

    Implements manager-level constraints:
    - Maximum 6 direct reports per manager
    - 0.5% budget cap per manager (based on team payroll)
    - Priority to below-median high performers
    """

    def __init__(self, population_data: List[Dict], config: Optional[Dict] = None):
        self.population_data = population_data
        self.population_df = pd.DataFrame(population_data)
        self.config = config or {}

        # Policy parameters
        self.max_direct_reports = self.config.get("max_direct_reports", 6)
        self.inequality_budget_percent = self.config.get("inequality_budget_percent", 0.5) / 100  # Convert to decimal
        self.high_performer_threshold = self.config.get("high_performer_threshold", 4.0)

        self.logger = LOGGER
        self.logger.info(f"Initialized GEL policy constraints with {len(population_data)} employees")

    def identify_managers_and_teams(self) -> Dict[int, Dict[str, Any]]:
        """
        Identify managers and their teams with policy compliance analysis.

        Returns:
            Dictionary mapping manager IDs to team information and constraints
        """
        managers = {}

        # Group employees by manager
        if "manager_id" not in self.population_df.columns:
            self.logger.warning("No manager_id column found, generating synthetic hierarchy")
            self.population_df["manager_id"] = self._generate_synthetic_hierarchy()

        for manager_id, team_df in self.population_df.groupby("manager_id"):
            if pd.isna(manager_id) or manager_id == -1:
                continue  # Skip employees without managers (e.g., CEO)

            team_size = len(team_df)
            team_salaries = team_df["salary"].tolist()
            team_payroll = sum(team_salaries)

            # Calculate manager's intervention budget
            intervention_budget = team_payroll * self.inequality_budget_percent

            # Assess policy compliance
            compliant = team_size <= self.max_direct_reports

            # Find manager details
            manager_info = self.population_df[self.population_df["employee_id"] == manager_id]
            if len(manager_info) > 0:
                manager_level = manager_info.iloc[0].get("level", "Unknown")
                manager_salary = manager_info.iloc[0].get("salary", 0)
            else:
                manager_level = "Unknown"
                manager_salary = 0

            managers[manager_id] = {
                "team_size": team_size,
                "team_employees": team_df["employee_id"].tolist(),
                "team_payroll": team_payroll,
                "intervention_budget": intervention_budget,
                "budget_percent": self.inequality_budget_percent,
                "compliant_team_size": compliant,
                "over_limit_by": max(0, team_size - self.max_direct_reports),
                "manager_level": manager_level,
                "manager_salary": manager_salary,
                "team_data": team_df.to_dict("records"),
            }

        self.logger.info(f"Identified {len(managers)} managers")
        compliant_count = sum(1 for m in managers.values() if m["compliant_team_size"])
        self.logger.info(f"Policy compliant managers: {compliant_count}/{len(managers)}")

        return managers

    def prioritize_interventions(self, manager_teams: Dict[int, Dict]) -> Dict[int, List[Dict]]:
        """
        Prioritize intervention opportunities for each manager's team.

        Priority order:
        1. Below-median AND high performer
        2. Below-median employees
        3. High performers (above median)
        4. Other employees

        Args:
            manager_teams: Manager team information from identify_managers_and_teams

        Returns:
            Dictionary mapping manager IDs to prioritized intervention lists
        """
        all_interventions = {}

        # Calculate level and gender medians for comparison
        level_gender_medians = self._calculate_level_gender_medians()

        for manager_id, team_info in manager_teams.items():
            team_df = pd.DataFrame(team_info["team_data"])
            if len(team_df) == 0:
                continue

            interventions = []

            for _, employee in team_df.iterrows():
                # Determine employee characteristics
                is_below_median = self._is_below_median(employee, level_gender_medians)
                is_high_performer = employee.get("performance_rating", 3.0) >= self.high_performer_threshold

                # Calculate potential intervention impact
                intervention_info = self._calculate_intervention_potential(
                    employee, level_gender_medians, team_info["intervention_budget"]
                )

                # Assign priority
                if is_below_median and is_high_performer:
                    priority = 1
                    priority_reason = "Below-median high performer"
                elif is_below_median:
                    priority = 2
                    priority_reason = "Below-median employee"
                elif is_high_performer:
                    priority = 3
                    priority_reason = "High performer (above median)"
                else:
                    priority = 4
                    priority_reason = "Standard employee"

                interventions.append(
                    {
                        "employee_id": employee["employee_id"],
                        "priority": priority,
                        "priority_reason": priority_reason,
                        "is_below_median": is_below_median,
                        "is_high_performer": is_high_performer,
                        "current_salary": employee["salary"],
                        "level": employee.get("level", 1),
                        "gender": employee.get("gender", "Unknown"),
                        "performance_rating": employee.get("performance_rating", 3.0),
                        **intervention_info,
                    }
                )

            # Sort by priority, then by intervention impact
            interventions.sort(key=lambda x: (x["priority"], -x["intervention_impact"]))
            all_interventions[manager_id] = interventions

        return all_interventions

    def optimize_budget_allocation(self, manager_interventions: Dict[int, List[Dict]]) -> Dict[int, Dict[str, Any]]:
        """
        Optimize budget allocation within manager constraints.

        Args:
            manager_interventions: Prioritized interventions from prioritize_interventions

        Returns:
            Dictionary with optimized allocations per manager
        """
        optimized_allocations = {}
        total_cost = 0
        total_employees_affected = 0

        for manager_id, interventions in manager_interventions.items():
            manager_budget = interventions[0]["available_budget"] if interventions else 0

            # Greedy allocation: prioritize highest impact within budget
            selected_interventions = []
            remaining_budget = manager_budget

            for intervention in interventions:
                intervention_cost = intervention["recommended_adjustment"]

                if intervention_cost <= remaining_budget and intervention_cost > 0:
                    # Can afford this intervention
                    selected_interventions.append(intervention)
                    remaining_budget -= intervention_cost
                    total_cost += intervention_cost
                    total_employees_affected += 1

                    self.logger.debug(
                        f"Manager {manager_id}: Selected intervention for employee {intervention['employee_id']} "
                        f"(£{intervention_cost:,.2f}, remaining budget: £{remaining_budget:,.2f})"
                    )

                # Stop if budget is exhausted
                if remaining_budget <= 100:  # Minimum meaningful adjustment
                    break

            # Calculate impact metrics
            budget_utilization = (manager_budget - remaining_budget) / manager_budget if manager_budget > 0 else 0

            optimized_allocations[manager_id] = {
                "total_budget": manager_budget,
                "allocated_budget": manager_budget - remaining_budget,
                "remaining_budget": remaining_budget,
                "budget_utilization": budget_utilization,
                "selected_interventions": selected_interventions,
                "total_interventions": len(selected_interventions),
                "employees_affected": len(selected_interventions),
                "average_adjustment": np.mean([i["recommended_adjustment"] for i in selected_interventions])
                if selected_interventions
                else 0,
            }

        self.logger.info("Budget optimization complete:")
        self.logger.info(f"  Total employees affected: {total_employees_affected}")
        self.logger.info(f"  Total intervention cost: £{total_cost:,.2f}")
        self.logger.info(
            f"  Managers with allocations: {len([a for a in optimized_allocations.values() if a['total_interventions'] > 0])}"
        )

        return optimized_allocations

    def _generate_synthetic_hierarchy(self) -> List[int]:
        """Generate synthetic manager hierarchy for testing."""
        # Simple algorithm: assign managers based on levels
        manager_ids = []
        next_manager_id = 1000  # Start manager IDs at 1000

        for _, employee in self.population_df.iterrows():
            level = employee.get("level", 1)

            if level <= 2:
                # Junior employees: assign to manager based on groups
                manager_id = next_manager_id + (employee["employee_id"] // 6)  # 6 people per manager
            elif level <= 4:
                # Mid-level: assign to senior managers
                manager_id = next_manager_id + 100 + (employee["employee_id"] // 8)  # 8 people per senior manager
            else:
                # Senior level: report to executive (or no manager)
                manager_id = -1  # No manager (executive level)

            manager_ids.append(manager_id)

        return manager_ids

    def _calculate_level_gender_medians(self) -> Dict[Tuple[int, str], float]:
        """Calculate median salaries by level and gender."""
        medians = {}

        for (level, gender), group in self.population_df.groupby(["level", "gender"]):
            medians[(level, gender)] = group["salary"].median()

        return medians

    def _is_below_median(self, employee: pd.Series, medians: Dict[Tuple[int, str], float]) -> bool:
        """Check if employee is below median for their level and gender."""
        level = employee.get("level", 1)
        gender = employee.get("gender", "Unknown")
        median_key = (level, gender)

        if median_key in medians:
            return employee["salary"] < medians[median_key]

        # Fallback: check against level median regardless of gender
        level_medians = {k[0]: v for k, v in medians.items() if k[0] == level}
        if level_medians:
            level_median = np.median(list(level_medians.values()))
            return employee["salary"] < level_median

        return False

    def _calculate_intervention_potential(
        self, employee: pd.Series, medians: Dict[Tuple[int, str], float], available_budget: float
    ) -> Dict[str, Any]:
        """Calculate intervention potential for an employee."""
        level = employee.get("level", 1)
        gender = employee.get("gender", "Unknown")
        current_salary = employee["salary"]

        # Find target salary (median for level/gender)
        median_key = (level, gender)
        if median_key in medians:
            target_salary = medians[median_key]
        else:
            # Fallback to level median
            level_medians = {k[0]: v for k, v in medians.items() if k[0] == level}
            target_salary = np.median(list(level_medians.values())) if level_medians else current_salary

        # Calculate potential adjustment
        if current_salary < target_salary:
            recommended_adjustment = min(
                target_salary - current_salary,  # Gap to median
                available_budget * 0.1,  # Max 10% of manager's budget per employee
                current_salary * 0.15,  # Max 15% salary increase
            )
        else:
            recommended_adjustment = min(
                current_salary * 0.05,  # 5% performance-based increase
                available_budget * 0.05,  # Max 5% of budget for above-median employees
            )

        # Calculate impact metrics
        gap_to_median = max(0, target_salary - current_salary)
        gap_closure_percent = (recommended_adjustment / gap_to_median * 100) if gap_to_median > 0 else 0
        salary_increase_percent = (recommended_adjustment / current_salary * 100) if current_salary > 0 else 0

        # Calculate intervention impact score
        performance_weight = employee.get("performance_rating", 3.0) / 5.0
        gap_weight = min(gap_to_median / current_salary, 0.5)  # Cap at 50% gap
        intervention_impact = (gap_closure_percent * gap_weight + salary_increase_percent) * performance_weight

        return {
            "target_salary": target_salary,
            "gap_to_median": gap_to_median,
            "recommended_adjustment": recommended_adjustment,
            "gap_closure_percent": gap_closure_percent,
            "salary_increase_percent": salary_increase_percent,
            "intervention_impact": intervention_impact,
            "available_budget": available_budget,
        }

    def generate_policy_summary(
        self, manager_teams: Dict[int, Dict], optimized_allocations: Dict[int, Dict]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive policy compliance and impact summary.
        """
        # Manager compliance analysis
        total_managers = len(manager_teams)
        compliant_managers = sum(1 for team in manager_teams.values() if team["compliant_team_size"])
        over_limit_managers = total_managers - compliant_managers

        # Budget utilization analysis
        total_budget = sum(team["intervention_budget"] for team in manager_teams.values())
        total_allocated = sum(alloc.get("allocated_budget", 0) for alloc in optimized_allocations.values())
        budget_utilization = (total_allocated / total_budget * 100) if total_budget > 0 else 0

        # Employee impact analysis
        total_employees_affected = sum(alloc.get("employees_affected", 0) for alloc in optimized_allocations.values())
        total_population = len(self.population_data)

        # Priority distribution
        priority_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        for alloc in optimized_allocations.values():
            for intervention in alloc.get("selected_interventions", []):
                priority_counts[intervention["priority"]] += 1

        return {
            "policy_compliance": {
                "total_managers": total_managers,
                "compliant_managers": compliant_managers,
                "over_limit_managers": over_limit_managers,
                "compliance_rate": (compliant_managers / total_managers * 100) if total_managers > 0 else 0,
                "max_direct_reports_policy": self.max_direct_reports,
                "budget_percent_policy": self.inequality_budget_percent * 100,
            },
            "budget_analysis": {
                "total_available_budget": total_budget,
                "total_allocated_budget": total_allocated,
                "total_remaining_budget": total_budget - total_allocated,
                "budget_utilization_percent": budget_utilization,
            },
            "intervention_impact": {
                "total_employees_affected": total_employees_affected,
                "total_population": total_population,
                "intervention_rate": (total_employees_affected / total_population * 100) if total_population > 0 else 0,
                "priority_distribution": {
                    "priority_1_below_median_high_performers": priority_counts[1],
                    "priority_2_below_median": priority_counts[2],
                    "priority_3_high_performers": priority_counts[3],
                    "priority_4_standard": priority_counts[4],
                },
            },
            "recommendations": self._generate_policy_recommendations(
                manager_teams, optimized_allocations, total_managers, compliant_managers
            ),
        }

    def _generate_policy_recommendations(
        self, manager_teams: Dict, optimized_allocations: Dict, total_managers: int, compliant_managers: int
    ) -> List[Dict[str, str]]:
        """
        Generate policy recommendations based on analysis.
        """
        recommendations = []

        # Team size recommendations
        compliance_rate = (compliant_managers / total_managers * 100) if total_managers > 0 else 100
        if compliance_rate < 80:
            recommendations.append(
                {
                    "type": "organizational_structure",
                    "priority": "high",
                    "recommendation": f"Restructure {total_managers - compliant_managers} teams exceeding 6 direct reports limit",
                    "rationale": "Policy compliance requires maximum 6 direct reports per manager",
                }
            )

        # Budget utilization recommendations
        avg_budget_utilization = (
            np.mean([alloc.get("budget_utilization", 0) for alloc in optimized_allocations.values()])
            if optimized_allocations
            else 0
        )

        if avg_budget_utilization < 0.5:  # Less than 50% utilization
            recommendations.append(
                {
                    "type": "budget_optimization",
                    "priority": "medium",
                    "recommendation": "Consider increasing intervention scope or adjusting budget allocation methodology",
                    "rationale": f"Current budget utilization is {avg_budget_utilization:.1%}, suggesting underutilization of available resources",
                }
            )

        # Priority-based recommendations
        high_priority_unaddressed = 0
        for alloc in optimized_allocations.values():
            for intervention in alloc.get("selected_interventions", []):
                if intervention["priority"] <= 2 and intervention["recommended_adjustment"] == 0:
                    high_priority_unaddressed += 1

        if high_priority_unaddressed > 0:
            recommendations.append(
                {
                    "type": "intervention_prioritization",
                    "priority": "high",
                    "recommendation": f"Address {high_priority_unaddressed} high-priority below-median employees in future cycles",
                    "rationale": "Below-median employees should be prioritized for equity interventions",
                }
            )

        return recommendations


if __name__ == "__main__":
    # Test with sample data
    sample_population = [
        {
            "employee_id": 1,
            "level": 2,
            "gender": "Female",
            "salary": 55000,
            "performance_rating": 4.2,
            "manager_id": 1001,
        },
        {
            "employee_id": 2,
            "level": 2,
            "gender": "Male",
            "salary": 62000,
            "performance_rating": 3.8,
            "manager_id": 1001,
        },
        {
            "employee_id": 3,
            "level": 2,
            "gender": "Female",
            "salary": 58000,
            "performance_rating": 4.5,
            "manager_id": 1001,
        },
        {
            "employee_id": 4,
            "level": 3,
            "gender": "Male",
            "salary": 78000,
            "performance_rating": 3.9,
            "manager_id": 1002,
        },
        {
            "employee_id": 5,
            "level": 3,
            "gender": "Female",
            "salary": 72000,
            "performance_rating": 4.1,
            "manager_id": 1002,
        },
    ]

    config = {"max_direct_reports": 6, "inequality_budget_percent": 0.5, "high_performer_threshold": 4.0}  # 0.5%

    # Test the policy constraints
    policy = GELPolicyConstraints(sample_population, config)

    # Analyze managers and teams
    managers = policy.identify_managers_and_teams()
    print("Managers:", managers)

    # Prioritize interventions
    interventions = policy.prioritize_interventions(managers)
    print("Prioritized interventions:", interventions)

    # Optimize allocations
    allocations = policy.optimize_budget_allocation(interventions)
    print("Optimized allocations:", allocations)

    # Generate summary
    summary = policy.generate_policy_summary(managers, allocations)
    print("Policy summary:", summary)

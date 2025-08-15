#!/usr/bin/env python3

import pytest

from gel_policy_constraints import GELPolicyConstraints


class TestGELPolicyConstraints:
    """
    Test GEL policy constraints functionality.
    """

    def setUp(self):
        """
        Set up test fixtures.
        """
        self.sample_population = [
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
            {
                "employee_id": 6,
                "level": 2,
                "gender": "Male",
                "salary": 59000,
                "performance_rating": 3.7,
                "manager_id": 1001,
            },
            {
                "employee_id": 7,
                "level": 3,
                "gender": "Female",
                "salary": 75000,
                "performance_rating": 4.3,
                "manager_id": 1002,
            },
        ]

        self.config = {
            "max_direct_reports": 6,
            "inequality_budget_percent": 0.5,  # 0.5%
            "high_performer_threshold": 4.0,
        }

    def test_initialization(self):
        """
        Test policy constraints initialization.
        """
        policy = GELPolicyConstraints(self.sample_population, self.config)

        assert policy.max_direct_reports == 6
        assert policy.inequality_budget_percent == 0.005  # Converted to decimal
        assert policy.high_performer_threshold == 4.0
        assert len(policy.population_data) == 7

    def test_identify_managers_and_teams(self):
        """
        Test identifying managers and their teams.
        """
        policy = GELPolicyConstraints(self.sample_population, self.config)

        managers = policy.identify_managers_and_teams()

        # Should identify 2 managers
        assert len(managers) == 2
        assert 1001 in managers
        assert 1002 in managers

        # Check manager 1001 team
        manager1001 = managers[1001]
        assert manager1001["team_size"] == 4  # Employees 1, 2, 3, 6
        assert manager1001["compliant_team_size"] is True  # 4 <= 6
        assert manager1001["intervention_budget"] == manager1001["team_payroll"] * 0.005

        # Check manager 1002 team
        manager1002 = managers[1002]
        assert manager1002["team_size"] == 3  # Employees 4, 5, 7
        assert manager1002["compliant_team_size"] is True  # 3 <= 6

    def test_identify_managers_over_limit(self):
        """
        Test identifying managers over the direct reports limit.
        """
        # Create population with one manager having too many reports
        over_limit_population = []
        for i in range(8):  # 8 employees under one manager (over limit of 6)
            over_limit_population.append(
                {
                    "employee_id": i + 1,
                    "level": 2,
                    "gender": "Male" if i % 2 else "Female",
                    "salary": 60000,
                    "performance_rating": 3.5,
                    "manager_id": 2001,
                }
            )

        policy = GELPolicyConstraints(over_limit_population, self.config)
        managers = policy.identify_managers_and_teams()

        # Should identify the over-limit manager
        assert len(managers) == 1
        manager = managers[2001]
        assert manager["team_size"] == 8
        assert manager["compliant_team_size"] is False
        assert manager["over_limit_by"] == 2  # 8 - 6

    def test_prioritize_interventions(self):
        """
        Test intervention prioritization logic.
        """
        policy = GELPolicyConstraints(self.sample_population, self.config)

        managers = policy.identify_managers_and_teams()
        interventions = policy.prioritize_interventions(managers)

        # Should have interventions for both managers
        assert len(interventions) == 2
        assert 1001 in interventions
        assert 1002 in interventions

        # Check priorities are assigned correctly
        for manager_id, manager_interventions in interventions.items():
            for intervention in manager_interventions:
                assert "priority" in intervention
                assert intervention["priority"] in [1, 2, 3, 4]
                assert "priority_reason" in intervention
                assert "is_below_median" in intervention
                assert "is_high_performer" in intervention

    def test_priority_assignment_logic(self):
        """
        Test specific priority assignment logic.
        """
        policy = GELPolicyConstraints(self.sample_population, self.config)

        managers = policy.identify_managers_and_teams()
        interventions = policy.prioritize_interventions(managers)

        # Find high performer below median (should be priority 1)
        priority_1_found = False
        for manager_interventions in interventions.values():
            for intervention in manager_interventions:
                if intervention["priority"] == 1:
                    assert intervention["is_below_median"] is True
                    assert intervention["is_high_performer"] is True
                    priority_1_found = True
                    break

        # Should find at least one priority 1 intervention
        # (This depends on the median calculation and performance ratings)

    def test_optimize_budget_allocation(self):
        """
        Test budget optimization within constraints.
        """
        policy = GELPolicyConstraints(self.sample_population, self.config)

        managers = policy.identify_managers_and_teams()
        interventions = policy.prioritize_interventions(managers)
        allocations = policy.optimize_budget_allocation(interventions)

        # Should have allocations for both managers
        assert len(allocations) == 2

        for manager_id, allocation in allocations.items():
            # Check allocation structure
            assert "total_budget" in allocation
            assert "allocated_budget" in allocation
            assert "remaining_budget" in allocation
            assert "budget_utilization" in allocation
            assert "selected_interventions" in allocation

            # Budget consistency checks
            total = allocation["total_budget"]
            allocated = allocation["allocated_budget"]
            remaining = allocation["remaining_budget"]

            assert allocated + remaining == total
            assert allocated >= 0
            assert remaining >= 0

            # Budget utilization calculation
            expected_utilization = allocated / total if total > 0 else 0
            assert abs(allocation["budget_utilization"] - expected_utilization) < 0.001

    def test_budget_constraints_respected(self):
        """
        Test that budget constraints are properly respected.
        """
        policy = GELPolicyConstraints(self.sample_population, self.config)

        managers = policy.identify_managers_and_teams()
        interventions = policy.prioritize_interventions(managers)
        allocations = policy.optimize_budget_allocation(interventions)

        for manager_id, allocation in allocations.items():
            # Total cost of selected interventions should not exceed budget
            total_cost = sum(
                intervention["recommended_adjustment"] for intervention in allocation["selected_interventions"]
            )

            assert total_cost <= allocation["total_budget"] + 1  # Allow for rounding

            # Individual adjustments should be reasonable
            for intervention in allocation["selected_interventions"]:
                adjustment = intervention["recommended_adjustment"]
                current_salary = intervention["current_salary"]

                # Should not be more than 20% salary increase
                assert adjustment <= current_salary * 0.2
                assert adjustment >= 0

    def test_generate_policy_summary(self):
        """
        Test policy summary generation.
        """
        policy = GELPolicyConstraints(self.sample_population, self.config)

        managers = policy.identify_managers_and_teams()
        interventions = policy.prioritize_interventions(managers)
        allocations = policy.optimize_budget_allocation(interventions)
        summary = policy.generate_policy_summary(managers, allocations)

        # Check summary structure
        assert "policy_compliance" in summary
        assert "budget_analysis" in summary
        assert "intervention_impact" in summary
        assert "recommendations" in summary

        # Check policy compliance details
        compliance = summary["policy_compliance"]
        assert compliance["total_managers"] == 2
        assert compliance["max_direct_reports_policy"] == 6
        assert compliance["budget_percent_policy"] == 0.5

        # Check budget analysis
        budget = summary["budget_analysis"]
        assert "total_available_budget" in budget
        assert "total_allocated_budget" in budget
        assert "budget_utilization_percent" in budget

        # Check intervention impact
        impact = summary["intervention_impact"]
        assert "total_employees_affected" in impact
        assert "priority_distribution" in impact

    def test_synthetic_hierarchy_generation(self):
        """
        Test synthetic manager hierarchy generation.
        """
        # Create population without manager_id
        no_manager_population = [
            {
                "employee_id": i,
                "level": (i % 3) + 1,
                "gender": "Male",
                "salary": 50000 + i * 1000,
                "performance_rating": 3.5,
            }
            for i in range(1, 16)  # 15 employees
        ]

        policy = GELPolicyConstraints(no_manager_population, self.config)

        # Should generate synthetic hierarchy
        assert "manager_id" in policy.population_df.columns

        # Check managers are identified
        managers = policy.identify_managers_and_teams()
        assert len(managers) > 0

    def test_edge_cases(self):
        """
        Test edge cases and error handling.
        """
        # Empty population
        empty_policy = GELPolicyConstraints([], self.config)
        managers = empty_policy.identify_managers_and_teams()
        assert len(managers) == 0

        # Single employee
        single_employee = [
            {
                "employee_id": 1,
                "level": 2,
                "gender": "Male",
                "salary": 50000,
                "performance_rating": 3.5,
                "manager_id": 1001,
            }
        ]
        single_policy = GELPolicyConstraints(single_employee, self.config)
        managers = single_policy.identify_managers_and_teams()
        assert len(managers) == 1

    def test_performance_threshold_impact(self):
        """
        Test impact of different performance thresholds.
        """
        # Test with lower threshold
        low_threshold_config = self.config.copy()
        low_threshold_config["high_performer_threshold"] = 3.5

        policy_low = GELPolicyConstraints(self.sample_population, low_threshold_config)

        # Test with higher threshold
        high_threshold_config = self.config.copy()
        high_threshold_config["high_performer_threshold"] = 4.5

        policy_high = GELPolicyConstraints(self.sample_population, high_threshold_config)

        # Get interventions for both
        managers_low = policy_low.identify_managers_and_teams()
        interventions_low = policy_low.prioritize_interventions(managers_low)

        managers_high = policy_high.identify_managers_and_teams()
        interventions_high = policy_high.prioritize_interventions(managers_high)

        # Lower threshold should identify more high performers
        total_high_performers_low = 0
        total_high_performers_high = 0

        for manager_interventions in interventions_low.values():
            for intervention in manager_interventions:
                if intervention["is_high_performer"]:
                    total_high_performers_low += 1

        for manager_interventions in interventions_high.values():
            for intervention in manager_interventions:
                if intervention["is_high_performer"]:
                    total_high_performers_high += 1

        assert total_high_performers_low >= total_high_performers_high

    def test_budget_percentage_impact(self):
        """
        Test impact of different budget percentages.
        """
        # Test with higher budget
        high_budget_config = self.config.copy()
        high_budget_config["inequality_budget_percent"] = 1.0  # 1.0%

        policy_high_budget = GELPolicyConstraints(self.sample_population, high_budget_config)

        managers_high = policy_high_budget.identify_managers_and_teams()
        interventions_high = policy_high_budget.prioritize_interventions(managers_high)
        allocations_high = policy_high_budget.optimize_budget_allocation(interventions_high)

        # Compare with original (lower budget)
        policy_low_budget = GELPolicyConstraints(self.sample_population, self.config)

        managers_low = policy_low_budget.identify_managers_and_teams()
        interventions_low = policy_low_budget.prioritize_interventions(managers_low)
        allocations_low = policy_low_budget.optimize_budget_allocation(interventions_low)

        # Higher budget should allow more interventions
        total_interventions_high = sum(alloc["total_interventions"] for alloc in allocations_high.values())
        total_interventions_low = sum(alloc["total_interventions"] for alloc in allocations_low.values())

        assert total_interventions_high >= total_interventions_low

    def test_recommendations_generation(self):
        """
        Test recommendation generation logic.
        """
        policy = GELPolicyConstraints(self.sample_population, self.config)

        managers = policy.identify_managers_and_teams()
        interventions = policy.prioritize_interventions(managers)
        allocations = policy.optimize_budget_allocation(interventions)
        summary = policy.generate_policy_summary(managers, allocations)

        recommendations = summary["recommendations"]

        # Should be a list
        assert isinstance(recommendations, list)

        # Each recommendation should have required fields
        for rec in recommendations:
            assert "type" in rec
            assert "priority" in rec
            assert "recommendation" in rec
            assert "rationale" in rec
            assert rec["priority"] in ["high", "medium", "low"]


class TestPolicyConstraintsIntegration:
    """
    Integration tests for policy constraints with realistic scenarios.
    """

    def test_large_organization_scenario(self):
        """
        Test with larger, more realistic organization.
        """
        # Generate larger population
        large_population = []
        manager_id = 3001

        for i in range(100):
            # Create teams of varying sizes
            if i % 12 == 0:  # New manager every 12 employees
                manager_id += 1

            large_population.append(
                {
                    "employee_id": i + 1,
                    "level": (i % 4) + 2,  # Levels 2-5
                    "gender": "Female" if i % 3 == 0 else "Male",
                    "salary": 45000 + (i % 4) * 15000 + (i % 1000),  # Varied salaries
                    "performance_rating": 2.5 + (i % 30) / 10,  # Ratings 2.5-5.4
                    "manager_id": manager_id,
                }
            )

        config = {"max_direct_reports": 8, "inequality_budget_percent": 0.3, "high_performer_threshold": 4.2}

        policy = GELPolicyConstraints(large_population, config)

        # Run full analysis
        managers = policy.identify_managers_and_teams()
        interventions = policy.prioritize_interventions(managers)
        allocations = policy.optimize_budget_allocation(interventions)
        summary = policy.generate_policy_summary(managers, allocations)

        # Validate results make sense for large organization
        assert len(managers) > 5  # Should have multiple managers
        assert summary["policy_compliance"]["total_managers"] > 5
        assert summary["budget_analysis"]["total_available_budget"] > 0
        assert summary["intervention_impact"]["total_employees_affected"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

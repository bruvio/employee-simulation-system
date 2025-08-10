#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

import ipywidgets as widgets
from IPython.display import display, clear_output
import numpy as np
from logger import LOGGER

# Import constants from employee population simulator
from employee_population_simulator import UPLIFT_MATRIX, LEVEL_MAPPING


class InteractiveSalaryCalculator:
    """
    Interactive salary calculator widget using IPython widgets.
    Provides real-time calculation of salary uplifts based on performance and level.
    """

    def __init__(self):
        self.setup_widgets()
        LOGGER.info("Initialized InteractiveSalaryCalculator with IPython widgets")

    def setup_widgets(self):
        """Create interactive widgets following existing pattern from pdr.md"""

        # Base salary input
        self.salary_input = widgets.FloatText(
            value=85000.0,
            description="Base Salary (£):",
            min=50000.0,
            max=150000.0,
            step=1000.0,
            style={"description_width": "initial"},
        )

        # Performance rating dropdown
        performance_options = ["Not met", "Partially met", "Achieving", "High Performing", "Exceeding"]
        self.rating_dropdown = widgets.Dropdown(
            options=performance_options,
            value="Achieving",
            description="Performance Rating:",
            style={"description_width": "initial"},
        )

        # Level dropdown
        level_options = [
            ("Level 1 (Core/Competent)", 1),
            ("Level 2 (Core/Advanced)", 2),
            ("Level 3 (Core/Expert)", 3),
            ("Level 4 (Senior/Competent)", 4),
            ("Level 5 (Senior/Advanced)", 5),
            ("Level 6 (Senior/Expert)", 6),
        ]
        self.level_dropdown = widgets.Dropdown(
            options=level_options, value=3, description="Employee Level:", style={"description_width": "initial"}
        )

        # Output widget for calculation results
        self.output = widgets.Output()

        # Additional information section
        self.info_output = widgets.Output()

        # Set up observers for real-time updates
        for widget in [self.salary_input, self.rating_dropdown, self.level_dropdown]:
            widget.observe(self.update_calculation, names="value")

        LOGGER.debug("Setup interactive widgets with observers")

    def update_calculation(self, change=None):
        """Update salary calculation when inputs change"""
        with self.output:
            clear_output()

            try:
                base_salary = float(self.salary_input.value)
                performance = self.rating_dropdown.value
                level = self.level_dropdown.value

                # Calculate uplift using same logic as main system
                uplift_data = UPLIFT_MATRIX[performance]
                level_tier = LEVEL_MAPPING[level]

                baseline_uplift = uplift_data["baseline"] * 100
                performance_uplift = uplift_data["performance"] * 100
                career_uplift = uplift_data[level_tier] * 100
                total_uplift = baseline_uplift + performance_uplift + career_uplift

                new_salary = base_salary * (1 + total_uplift / 100)
                salary_increase = new_salary - base_salary

                # Format and display results
                print("📊 SALARY CALCULATION RESULTS")
                print("=" * 40)
                print(f"Performance Rating: {performance}")
                print(f"Employee Level:     Level {level} ({self._get_level_description(level)})")
                print()
                print("💰 UPLIFT BREAKDOWN:")
                print(f"  Baseline uplift:    {baseline_uplift:.2f}%")
                print(f"  Performance uplift: {performance_uplift:.2f}%")
                print(f"  Career level uplift: {career_uplift:.2f}%")
                print(f"  ➤ TOTAL UPLIFT:     {total_uplift:.2f}%")
                print()
                print("💷 SALARY DETAILS:")
                print(f"  Current salary:     £{base_salary:,.2f}")
                print(f"  New salary:         £{new_salary:,.2f}")
                print(f"  Increase:           £{salary_increase:,.2f}")
                print()
                print(f"📈 Annual increase:   £{salary_increase:,.2f} ({total_uplift:.2f}%)")

            except Exception as e:
                print(f"❌ Error in calculation: {e}")
                LOGGER.error(f"Calculator error: {e}")

    def _get_level_description(self, level):
        """Get level description string"""
        level_descriptions = {
            1: "Core/Competent",
            2: "Core/Advanced",
            3: "Core/Expert",
            4: "Senior/Competent",
            5: "Senior/Advanced",
            6: "Senior/Expert",
        }
        return level_descriptions.get(level, "Unknown")

    def update_info_section(self, change=None):
        """Update information section with matrix details"""
        with self.info_output:
            clear_output()

            performance = self.rating_dropdown.value
            level = self.level_dropdown.value

            print("ℹ️ UPLIFT MATRIX INFORMATION")
            print("=" * 40)
            print(f"Performance: {performance}")
            print(f"Level: {level} ({self._get_level_description(level)})")
            print()

            # Show matrix values for current selection
            uplift_data = UPLIFT_MATRIX[performance]
            level_tier = LEVEL_MAPPING[level]

            print("📋 Matrix Values:")
            print(f"  Baseline:     {uplift_data['baseline']:.4f} ({uplift_data['baseline']*100:.2f}%)")
            print(f"  Performance:  {uplift_data['performance']:.4f} ({uplift_data['performance']*100:.2f}%)")
            print(
                f"  {level_tier.capitalize()}:      {uplift_data[level_tier]:.4f} ({uplift_data[level_tier]*100:.2f}%)"
            )
            print()

            # Show comparison with other performance levels for same level
            print(f"🔍 Other performance ratings at Level {level}:")
            for rating in UPLIFT_MATRIX.keys():
                if rating != performance:
                    other_data = UPLIFT_MATRIX[rating]
                    other_total = (other_data["baseline"] + other_data["performance"] + other_data[level_tier]) * 100
                    print(f"  {rating:15}: {other_total:.2f}% total uplift")

    def display(self):
        """Display the interactive calculator"""
        LOGGER.info("Displaying interactive salary calculator")

        # Create title
        title = widgets.HTML(
            value="<h2>🧮 Interactive Salary Calculator</h2><p>Calculate salary uplifts based on performance ratings and employee levels</p>",
        )

        # Create main input section
        input_section = widgets.VBox(
            [
                widgets.HTML(value="<h3>📝 Input Parameters</h3>"),
                self.salary_input,
                self.rating_dropdown,
                self.level_dropdown,
            ]
        )

        # Create results section
        results_section = widgets.VBox([widgets.HTML(value="<h3>📊 Calculation Results</h3>"), self.output])

        # Create information section
        info_section = widgets.VBox([widgets.HTML(value="<h3>ℹ️ Uplift Matrix Details</h3>"), self.info_output])

        # Create tabs for organized display
        tab_contents = [widgets.VBox([input_section, results_section]), info_section, self.create_comparison_tool()]

        tabs = widgets.Tab(children=tab_contents)
        tabs.set_title(0, "Calculator")
        tabs.set_title(1, "Matrix Info")
        tabs.set_title(2, "Compare Scenarios")

        # Display the complete interface
        display(widgets.VBox([title, tabs]))

        # Initial calculations
        self.update_calculation()
        self.update_info_section()

        # Set up info section observer
        for widget in [self.rating_dropdown, self.level_dropdown]:
            widget.observe(self.update_info_section, names="value")

    def create_comparison_tool(self):
        """Create a tool to compare different scenarios"""

        # Scenario A inputs
        scenario_a_salary = widgets.FloatText(value=85000, description="Scenario A Salary:")
        scenario_a_perf = widgets.Dropdown(
            options=["Not met", "Partially met", "Achieving", "High Performing", "Exceeding"],
            value="Achieving",
            description="Performance:",
        )
        scenario_a_level = widgets.Dropdown(
            options=[("Level 1", 1), ("Level 2", 2), ("Level 3", 3), ("Level 4", 4), ("Level 5", 5), ("Level 6", 6)],
            value=3,
            description="Level:",
        )

        # Scenario B inputs
        scenario_b_salary = widgets.FloatText(value=85000, description="Scenario B Salary:")
        scenario_b_perf = widgets.Dropdown(
            options=["Not met", "Partially met", "Achieving", "High Performing", "Exceeding"],
            value="High Performing",
            description="Performance:",
        )
        scenario_b_level = widgets.Dropdown(
            options=[("Level 1", 1), ("Level 2", 2), ("Level 3", 3), ("Level 4", 4), ("Level 5", 5), ("Level 6", 6)],
            value=4,
            description="Level:",
        )

        # Comparison output
        comparison_output = widgets.Output()

        def update_comparison(change=None):
            with comparison_output:
                clear_output()

                # Calculate Scenario A
                a_uplift_data = UPLIFT_MATRIX[scenario_a_perf.value]
                a_level_tier = LEVEL_MAPPING[scenario_a_level.value]
                a_total_uplift = (
                    a_uplift_data["baseline"] + a_uplift_data["performance"] + a_uplift_data[a_level_tier]
                ) * 100
                a_new_salary = scenario_a_salary.value * (1 + a_total_uplift / 100)

                # Calculate Scenario B
                b_uplift_data = UPLIFT_MATRIX[scenario_b_perf.value]
                b_level_tier = LEVEL_MAPPING[scenario_b_level.value]
                b_total_uplift = (
                    b_uplift_data["baseline"] + b_uplift_data["performance"] + b_uplift_data[b_level_tier]
                ) * 100
                b_new_salary = scenario_b_salary.value * (1 + b_total_uplift / 100)

                print("🔄 SCENARIO COMPARISON")
                print("=" * 50)
                print(f"{'Metric':<20} {'Scenario A':<15} {'Scenario B':<15} {'Difference':<15}")
                print("-" * 65)
                print(
                    f"{'Base Salary':<20} £{scenario_a_salary.value:<14,.2f} £{scenario_b_salary.value:<14,.2f} £{scenario_b_salary.value - scenario_a_salary.value:<14,.2f}"
                )
                print(f"{'Performance':<20} {scenario_a_perf.value:<15} {scenario_b_perf.value:<15} {'-':<15}")
                print(
                    f"{'Level':<20} {scenario_a_level.value:<15} {scenario_b_level.value:<15} {scenario_b_level.value - scenario_a_level.value:<15}"
                )
                print(
                    f"{'Total Uplift':<20} {a_total_uplift:<14.2f}% {b_total_uplift:<14.2f}% {b_total_uplift - a_total_uplift:<14.2f}%"
                )
                print(
                    f"{'New Salary':<20} £{a_new_salary:<14,.2f} £{b_new_salary:<14,.2f} £{b_new_salary - a_new_salary:<14,.2f}"
                )
                print(
                    f"{'Increase':<20} £{a_new_salary - scenario_a_salary.value:<14,.2f} £{b_new_salary - scenario_b_salary.value:<14,.2f} £{(b_new_salary - scenario_b_salary.value) - (a_new_salary - scenario_a_salary.value):<14,.2f}"
                )

                if b_new_salary > a_new_salary:
                    print(f"\n🏆 Scenario B results in £{b_new_salary - a_new_salary:.2f} higher salary")
                elif a_new_salary > b_new_salary:
                    print(f"\n🏆 Scenario A results in £{a_new_salary - b_new_salary:.2f} higher salary")
                else:
                    print(f"\n⚖️ Both scenarios result in the same salary")

        # Set up observers
        widgets_to_observe = [
            scenario_a_salary,
            scenario_a_perf,
            scenario_a_level,
            scenario_b_salary,
            scenario_b_perf,
            scenario_b_level,
        ]
        for widget in widgets_to_observe:
            widget.observe(update_comparison, names="value")

        # Initial comparison
        update_comparison()

        return widgets.VBox(
            [
                widgets.HTML(value="<h4>📊 Compare Two Scenarios</h4>"),
                widgets.HBox(
                    [
                        widgets.VBox(
                            [
                                widgets.HTML(value="<b>Scenario A</b>"),
                                scenario_a_salary,
                                scenario_a_perf,
                                scenario_a_level,
                            ]
                        ),
                        widgets.VBox(
                            [
                                widgets.HTML(value="<b>Scenario B</b>"),
                                scenario_b_salary,
                                scenario_b_perf,
                                scenario_b_level,
                            ]
                        ),
                    ]
                ),
                comparison_output,
            ]
        )


def create_salary_calculator():
    """Factory function to create and return salary calculator"""
    LOGGER.info("Creating interactive salary calculator")
    return InteractiveSalaryCalculator()


def main():
    """Main function - primarily for testing"""
    print("Interactive Salary Calculator")
    print("This module is designed to be used in Jupyter notebooks.")
    print("\nTo use:")
    print("1. Import the module: from interactive_salary_calculator import create_salary_calculator")
    print("2. Create calculator: calc = create_salary_calculator()")
    print("3. Display calculator: calc.display()")


if __name__ == "__main__":
    main()

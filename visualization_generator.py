#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import argparse
import json
from logger import LOGGER

# Set plotting style
plt.style.use("default")
plt.rcParams["axes.grid"] = True


class VisualizationGenerator:
    """
    Comprehensive visualization generator for employee population simulation.
    Creates statistical plots and interactive visualizations for salary analysis.
    Enhanced with story tracking capabilities.
    """

    def __init__(self, population_data=None, inequality_progression=None, story_tracker=None):
        self.population = population_data
        self.inequality_data = inequality_progression
        self.story_tracker = story_tracker
        self.tracked_employees = {}
        self.employee_stories = {}

        # Initialize story data if tracker is provided
        if self.story_tracker:
            self.tracked_employees = self.story_tracker.tracked_categories
            self._load_employee_stories()
            LOGGER.info(
                f"Story tracking enabled with {sum(len(employees) for employees in self.tracked_employees.values())} tracked employees"
            )

        self.setup_plotting_style()

        LOGGER.info(
            f"Initialized VisualizationGenerator with {len(population_data) if population_data else 0} employees"
        )

    def setup_plotting_style(self):
        """Setup consistent plotting style"""
        # Color palette for consistency
        self.colors = {
            "male": "#2E86AB",
            "female": "#A23B72",
            "core": "#F18F01",
            "senior": "#C73E1D",
            "primary": "#1f77b4",
            "secondary": "#ff7f0e",
        }

        # Matplotlib settings
        plt.rcParams["figure.figsize"] = (12, 8)
        plt.rcParams["font.size"] = 10
        plt.rcParams["axes.titlesize"] = 12
        plt.rcParams["axes.labelsize"] = 11
        plt.rcParams["legend.fontsize"] = 10

        # Story tracking colors
        self.story_colors = {
            "gender_gap_affected": "#E74C3C",
            "above_range": "#F39C12",
            "high_performers": "#27AE60",
            "tracked_employee": "#8E44AD",
            "normal_employee": "#BDC3C7",
        }

        LOGGER.debug("Setup plotting style and color palette")

    def _load_employee_stories(self):
        """Load employee stories from story tracker"""
        if not self.story_tracker:
            return

        try:
            # Generate stories for all tracked employees
            for category, employee_ids in self.tracked_employees.items():
                category_stories = []
                for emp_id in employee_ids:
                    if story := self.story_tracker.generate_employee_story(
                        emp_id, category
                    ):
                        category_stories.append(story)
                self.employee_stories[category] = category_stories

            total_stories = sum(len(stories) for stories in self.employee_stories.values())
            LOGGER.debug(f"Loaded {total_stories} employee stories across {len(self.employee_stories)} categories")
        except Exception as e:
            LOGGER.warning(f"Error loading employee stories: {e}")

    def generate_complete_analysis(self):
        """Generate all visualization components"""
        LOGGER.info("Generating complete visualization analysis")

        visualizations = {}

        if self.population:
            # Population overview
            pop_fig = self.plot_population_overview()
            visualizations["population_overview"] = self.save_figure(pop_fig, "population_overview")

            # Gender pay gap analysis
            gender_fig = self.plot_gender_analysis()
            visualizations["gender_analysis"] = self.save_figure(gender_fig, "gender_pay_gap_analysis")

            # Performance analysis
            perf_fig = self.plot_performance_analysis()
            visualizations["performance_analysis"] = self.save_figure(perf_fig, "performance_analysis")

            # Salary distribution analysis
            salary_fig = self.plot_salary_distributions()
            visualizations["salary_distributions"] = self.save_figure(salary_fig, "salary_distributions")

        if self.inequality_data:
            # Inequality reduction analysis
            inequality_fig = self.plot_inequality_reduction()
            visualizations["inequality_reduction"] = self.save_figure(inequality_fig, "inequality_reduction_analysis")

            # Review cycle progression
            cycle_fig = self.plot_review_cycle_progression()
            visualizations["review_cycles"] = self.save_figure(cycle_fig, "review_cycle_progression")

        # Story-aware visualizations (if story tracking is enabled)
        if self.story_tracker and self.tracked_employees:
            LOGGER.info("Generating story-aware visualizations")

            # Story-enhanced salary distributions
            story_salary_fig = self.plot_story_salary_distributions()
            visualizations["story_salary_distributions"] = self.save_figure(
                story_salary_fig, "story_salary_distributions"
            )

            # Employee progression timelines
            progression_fig = self.plot_employee_progression_timelines()
            visualizations["employee_progressions"] = self.save_figure(progression_fig, "employee_progressions")

            if interactive_dashboard := self.create_interactive_story_dashboard():
                visualizations["interactive_dashboard"] = interactive_dashboard

        LOGGER.info(f"Generated {len(visualizations)} visualizations")
        return visualizations

    def plot_population_overview(self):
        """Create population overview visualization"""
        LOGGER.debug("Creating population overview visualization")

        df = pd.DataFrame(self.population)
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle("Employee Population Overview", fontsize=16, fontweight="bold")

        # Level distribution
        level_counts = df["level"].value_counts().sort_index()
        bars1 = axes[0, 0].bar(
            level_counts.index,
            level_counts.values,
            color=[self.colors["core"] if level <= 3 else self.colors["senior"] for level in level_counts.index],
            alpha=0.7,
        )
        axes[0, 0].set_title("Distribution by Level")
        axes[0, 0].set_xlabel("Level")
        axes[0, 0].set_ylabel("Number of Employees")
        axes[0, 0].grid(True, alpha=0.3)

        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            axes[0, 0].text(bar.get_x() + bar.get_width() / 2.0, height + 5, f"{int(height)}", ha="center", va="bottom")

        # Gender distribution
        gender_counts = df["gender"].value_counts()
        colors_gender = [self.colors["male"], self.colors["female"]]
        wedges, texts, autotexts = axes[0, 1].pie(
            gender_counts.values, labels=gender_counts.index, autopct="%1.1f%%", colors=colors_gender, startangle=90
        )
        axes[0, 1].set_title("Gender Distribution")

        # Salary distribution histogram
        axes[1, 0].hist(df["salary"], bins=30, alpha=0.7, color=self.colors["primary"], edgecolor="black")
        axes[1, 0].axvline(
            df["salary"].median(),
            color="red",
            linestyle="--",
            linewidth=2,
            label=f'Median: £{df["salary"].median():,.0f}',
        )
        axes[1, 0].axvline(
            df["salary"].mean(), color="orange", linestyle="--", linewidth=2, label=f'Mean: £{df["salary"].mean():,.0f}'
        )
        axes[1, 0].set_title("Salary Distribution")
        axes[1, 0].set_xlabel("Salary (£)")
        axes[1, 0].set_ylabel("Frequency")
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)

        # Performance distribution
        perf_counts = df["performance_rating"].value_counts()
        perf_order = ["Not met", "Partially met", "Achieving", "High Performing", "Exceeding"]
        perf_ordered = [perf_counts.get(p, 0) for p in perf_order]

        bars2 = axes[1, 1].bar(perf_order, perf_ordered, alpha=0.7, color=self.colors["secondary"])
        axes[1, 1].set_title("Performance Rating Distribution")
        axes[1, 1].set_xlabel("Performance Rating")
        axes[1, 1].set_ylabel("Number of Employees")
        axes[1, 1].tick_params(axis="x", rotation=45)
        axes[1, 1].grid(True, alpha=0.3)

        # Add value labels
        for bar in bars2:
            height = bar.get_height()
            if height > 0:
                axes[1, 1].text(
                    bar.get_x() + bar.get_width() / 2.0, height + 5, f"{int(height)}", ha="center", va="bottom"
                )

        plt.tight_layout()
        return fig

    def plot_gender_analysis(self):
        """Create gender pay gap analysis visualization"""
        LOGGER.debug("Creating gender pay gap analysis")

        df = pd.DataFrame(self.population)
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle("Gender Pay Gap Analysis", fontsize=16, fontweight="bold")

        # Overall salary comparison by gender
        male_salaries = df[df["gender"] == "Male"]["salary"]
        female_salaries = df[df["gender"] == "Female"]["salary"]

        box_data = [male_salaries, female_salaries]
        box_plot = axes[0, 0].boxplot(box_data, labels=["Male", "Female"], patch_artist=True)
        box_plot["boxes"][0].set_facecolor(self.colors["male"])
        box_plot["boxes"][1].set_facecolor(self.colors["female"])
        axes[0, 0].set_title("Salary Distribution by Gender")
        axes[0, 0].set_ylabel("Salary (£)")
        axes[0, 0].grid(True, alpha=0.3)

        # Add median values as text
        male_median = male_salaries.median()
        female_median = female_salaries.median()
        gap_pct = (male_median - female_median) / male_median * 100
        axes[0, 0].text(
            0.5,
            0.95,
            f"Pay Gap: {gap_pct:.1f}%",
            transform=axes[0, 0].transAxes,
            ha="center",
            fontweight="bold",
            bbox=dict(boxstyle="round", facecolor="wheat"),
        )

        # Histogram overlay
        axes[0, 1].hist(male_salaries, alpha=0.6, label="Male", bins=25, color=self.colors["male"], density=True)
        axes[0, 1].hist(female_salaries, alpha=0.6, label="Female", bins=25, color=self.colors["female"], density=True)
        axes[0, 1].set_title("Salary Distribution Overlay")
        axes[0, 1].set_xlabel("Salary (£)")
        axes[0, 1].set_ylabel("Density")
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)

        # Median salary by level and gender
        level_gender_medians = df.groupby(["level", "gender"])["salary"].median().unstack()
        if "Male" in level_gender_medians.columns and "Female" in level_gender_medians.columns:
            x = np.arange(len(level_gender_medians.index))
            width = 0.35

            male_medians = level_gender_medians["Male"].values
            female_medians = level_gender_medians["Female"].values

            axes[1, 0].bar(x - width / 2, male_medians, width, label="Male", color=self.colors["male"], alpha=0.7)
            axes[1, 0].bar(x + width / 2, female_medians, width, label="Female", color=self.colors["female"], alpha=0.7)

            axes[1, 0].set_xlabel("Level")
            axes[1, 0].set_ylabel("Median Salary (£)")
            axes[1, 0].set_title("Median Salary by Level and Gender")
            axes[1, 0].set_xticks(x)
            axes[1, 0].set_xticklabels([f"L{i}" for i in level_gender_medians.index])
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)

            # Pay gap percentage by level
            gap_percentages = []
            levels_with_both = []
            for level in level_gender_medians.index:
                if not pd.isna(male_medians[level - 1]) and not pd.isna(female_medians[level - 1]):
                    gap = (male_medians[level - 1] - female_medians[level - 1]) / male_medians[level - 1] * 100
                    gap_percentages.append(gap)
                    levels_with_both.append(level)

            if gap_percentages:
                bars = axes[1, 1].bar(
                    levels_with_both,
                    gap_percentages,
                    alpha=0.7,
                    color=["red" if gap > 0 else "green" for gap in gap_percentages],
                )
                axes[1, 1].set_xlabel("Level")
                axes[1, 1].set_ylabel("Pay Gap (%)")
                axes[1, 1].set_title("Gender Pay Gap by Level")
                axes[1, 1].axhline(y=0, color="black", linestyle="-", alpha=0.3)
                axes[1, 1].grid(True, alpha=0.3)

                # Add value labels
                for bar, gap in zip(bars, gap_percentages):
                    height = bar.get_height()
                    axes[1, 1].text(
                        bar.get_x() + bar.get_width() / 2.0,
                        height + (0.2 if height > 0 else -0.2),
                        f"{gap:.1f}%",
                        ha="center",
                        va="bottom" if height > 0 else "top",
                    )

        plt.tight_layout()
        return fig

    def plot_performance_analysis(self):
        """Create comprehensive performance analysis plots"""
        LOGGER.debug("Creating performance analysis visualization")

        df = pd.DataFrame(self.population)
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle("Performance Analysis", fontsize=16, fontweight="bold")

        # Performance distribution pie chart
        perf_counts = df["performance_rating"].value_counts()
        colors_perf = plt.cm.Set3(np.linspace(0, 1, len(perf_counts)))
        wedges, texts, autotexts = axes[0, 0].pie(
            perf_counts.values, labels=perf_counts.index, autopct="%1.1f%%", colors=colors_perf, startangle=90
        )
        axes[0, 0].set_title("Performance Rating Distribution")

        # Salary by performance violin plot
        perf_order = ["Not met", "Partially met", "Achieving", "High Performing", "Exceeding"]
        perf_salary_data = [
            df[df["performance_rating"] == perf]["salary"].values
            for perf in perf_order
            if perf in df["performance_rating"].values
        ]
        perf_labels = [perf for perf in perf_order if perf in df["performance_rating"].values]

        if perf_salary_data:
            axes[0, 1].violinplot(perf_salary_data, positions=range(len(perf_salary_data)))
            axes[0, 1].set_xticks(range(len(perf_labels)))
            axes[0, 1].set_xticklabels(perf_labels, rotation=45)
            axes[0, 1].set_title("Salary Distribution by Performance Rating")
            axes[0, 1].set_ylabel("Salary (£)")
            axes[0, 1].grid(True, alpha=0.3)

        # Performance by level heatmap
        level_perf_crosstab = pd.crosstab(df["level"], df["performance_rating"], normalize="index") * 100

        # Reorder columns to match performance order
        available_perfs = [p for p in perf_order if p in level_perf_crosstab.columns]
        level_perf_crosstab = level_perf_crosstab[available_perfs]

        im = axes[1, 0].imshow(level_perf_crosstab.values, cmap="YlOrRd", aspect="auto")
        axes[1, 0].set_title("Performance Distribution by Level (%)")
        axes[1, 0].set_xlabel("Performance Rating")
        axes[1, 0].set_ylabel("Level")
        axes[1, 0].set_xticks(range(len(available_perfs)))
        axes[1, 0].set_xticklabels(available_perfs, rotation=45)
        axes[1, 0].set_yticks(range(len(level_perf_crosstab.index)))
        axes[1, 0].set_yticklabels([f"Level {i}" for i in level_perf_crosstab.index])

        # Add colorbar
        cbar = plt.colorbar(im, ax=axes[1, 0])
        cbar.set_label("Percentage")

        # Salary vs Performance scatter plot
        perf_mapping = {"Not met": 1, "Partially met": 2, "Achieving": 3, "High Performing": 4, "Exceeding": 5}
        df["perf_numeric"] = df["performance_rating"].map(perf_mapping)

        scatter = axes[1, 1].scatter(df["perf_numeric"], df["salary"], c=df["level"], cmap="viridis", alpha=0.6, s=50)
        axes[1, 1].set_xlabel("Performance Rating (Numeric)")
        axes[1, 1].set_ylabel("Salary (£)")
        axes[1, 1].set_title("Salary vs Performance (colored by Level)")
        axes[1, 1].set_xticks(range(1, 6))
        axes[1, 1].set_xticklabels(
            ["Not met", "Partially\nmet", "Achieving", "High\nPerforming", "Exceeding"], rotation=45
        )
        axes[1, 1].grid(True, alpha=0.3)

        # Add colorbar for levels
        cbar = plt.colorbar(scatter, ax=axes[1, 1])
        cbar.set_label("Level")

        plt.tight_layout()
        return fig

    def plot_salary_distributions(self):
        """Create detailed salary distribution analysis"""
        LOGGER.debug("Creating salary distribution analysis")

        df = pd.DataFrame(self.population)
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle("Salary Distribution Analysis", fontsize=16, fontweight="bold")

        # Overall distribution with statistics
        axes[0, 0].hist(df["salary"], bins=40, alpha=0.7, color=self.colors["primary"], edgecolor="black", density=True)

        # Add statistical lines
        mean_sal = df["salary"].mean()
        median_sal = df["salary"].median()
        std_sal = df["salary"].std()

        axes[0, 0].axvline(mean_sal, color="red", linestyle="-", linewidth=2, label=f"Mean: £{mean_sal:,.0f}")
        axes[0, 0].axvline(median_sal, color="orange", linestyle="--", linewidth=2, label=f"Median: £{median_sal:,.0f}")
        axes[0, 0].axvline(mean_sal - std_sal, color="gray", linestyle=":", alpha=0.7, label=f"±1σ: £{std_sal:,.0f}")
        axes[0, 0].axvline(mean_sal + std_sal, color="gray", linestyle=":", alpha=0.7)

        axes[0, 0].set_title("Overall Salary Distribution")
        axes[0, 0].set_xlabel("Salary (£)")
        axes[0, 0].set_ylabel("Density")
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # Distribution by level
        core_salaries = df[df["level"].isin([1, 2, 3])]["salary"]
        senior_salaries = df[df["level"].isin([4, 5, 6])]["salary"]

        axes[0, 1].hist(
            core_salaries,
            alpha=0.6,
            label=f"Core (L1-3): n={len(core_salaries)}",
            bins=25,
            color=self.colors["core"],
            density=True,
        )
        axes[0, 1].hist(
            senior_salaries,
            alpha=0.6,
            label=f"Senior (L4-6): n={len(senior_salaries)}",
            bins=25,
            color=self.colors["senior"],
            density=True,
        )
        axes[0, 1].set_title("Salary Distribution by Level Category")
        axes[0, 1].set_xlabel("Salary (£)")
        axes[0, 1].set_ylabel("Density")
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)

        # Box plot by individual levels
        level_salary_data = [df[df["level"] == level]["salary"].values for level in range(1, 7)]
        box_plot = axes[1, 0].boxplot(level_salary_data, labels=[f"L{i}" for i in range(1, 7)], patch_artist=True)

        # Color boxes by category
        for i, box in enumerate(box_plot["boxes"]):
            if i < 3:  # Core levels
                box.set_facecolor(self.colors["core"])
            else:  # Senior levels
                box.set_facecolor(self.colors["senior"])
            box.set_alpha(0.7)

        axes[1, 0].set_title("Salary Distribution by Level (Detailed)")
        axes[1, 0].set_xlabel("Level")
        axes[1, 0].set_ylabel("Salary (£)")
        axes[1, 0].grid(True, alpha=0.3)

        # Q-Q plot for normality check
        from scipy import stats

        stats.probplot(df["salary"], dist="norm", plot=axes[1, 1])
        axes[1, 1].set_title("Q-Q Plot (Normality Check)")
        axes[1, 1].grid(True, alpha=0.3)

        plt.tight_layout()
        return fig

    def plot_inequality_reduction(self):
        """Create inequality reduction analysis visualization"""
        LOGGER.debug("Creating inequality reduction analysis")

        if not self.inequality_data:
            LOGGER.warning("No inequality data available for plotting")
            return None

        df = pd.DataFrame(self.inequality_data)
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle("Inequality Reduction Analysis", fontsize=16, fontweight="bold")

        cycles = df["cycle"]

        # Gini coefficient over time
        axes[0, 0].plot(
            cycles,
            df["gini_coefficient"],
            "o-",
            linewidth=2,
            markersize=8,
            color=self.colors["primary"],
            label="Gini Coefficient",
        )
        axes[0, 0].set_xlabel("Review Cycle")
        axes[0, 0].set_ylabel("Gini Coefficient")
        axes[0, 0].set_title("Gini Coefficient Over Time")
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].legend()

        # Add trend line
        z = np.polyfit(cycles, df["gini_coefficient"], 1)
        p = np.poly1d(z)
        axes[0, 0].plot(
            cycles,
            p(cycles),
            "--",
            alpha=0.7,
            color="red",
            label=f'Trend: {"↗" if z[0] > 0 else "↘"} {abs(z[0]):.6f}/cycle',
        )
        axes[0, 0].legend()

        # Gender pay gap over time
        axes[0, 1].plot(
            cycles,
            df["gender_gap_percent"].abs(),
            "s-",
            linewidth=2,
            markersize=8,
            color=self.colors["secondary"],
            label="Gender Pay Gap",
        )
        axes[0, 1].set_xlabel("Review Cycle")
        axes[0, 1].set_ylabel("Gender Pay Gap (%)")
        axes[0, 1].set_title("Gender Pay Gap Over Time")
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].legend()

        # Median salary progression
        axes[1, 0].plot(
            cycles, df["median_salary"], "^-", linewidth=2, markersize=8, color="green", label="Median Salary"
        )
        axes[1, 0].set_xlabel("Review Cycle")
        axes[1, 0].set_ylabel("Median Salary (£)")
        axes[1, 0].set_title("Median Salary Progression")
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].legend()

        # Format y-axis as currency
        axes[1, 0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"£{x:,.0f}"))

        # Performance-salary correlation
        axes[1, 1].plot(
            cycles,
            df["performance_salary_correlation"],
            "d-",
            linewidth=2,
            markersize=8,
            color="purple",
            label="Performance-Salary Correlation",
        )
        axes[1, 1].set_xlabel("Review Cycle")
        axes[1, 1].set_ylabel("Correlation Coefficient")
        axes[1, 1].set_title("Performance-Salary Correlation Over Time")
        axes[1, 1].grid(True, alpha=0.3)
        axes[1, 1].legend()
        axes[1, 1].axhline(y=0, color="black", linestyle="-", alpha=0.3)

        plt.tight_layout()
        return fig

    def plot_review_cycle_progression(self):
        """Create review cycle progression analysis"""
        LOGGER.debug("Creating review cycle progression analysis")

        if not self.inequality_data:
            LOGGER.warning("No inequality data available for plotting")
            return None

        df = pd.DataFrame(self.inequality_data)
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle("Review Cycle Progression Analysis", fontsize=16, fontweight="bold")

        cycles = df["cycle"]

        # Multiple inequality metrics
        axes[0, 0].plot(cycles, df["gini_coefficient"], "o-", label="Gini Coefficient", linewidth=2)
        axes[0, 0].plot(cycles, df["coefficient_of_variation"], "s-", label="Coefficient of Variation", linewidth=2)
        axes[0, 0].set_xlabel("Review Cycle")
        axes[0, 0].set_ylabel("Inequality Metric")
        axes[0, 0].set_title("Multiple Inequality Metrics")
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)

        # Salary statistics evolution
        axes[0, 1].plot(cycles, df["mean_salary"], "o-", label="Mean Salary", linewidth=2)
        axes[0, 1].plot(cycles, df["median_salary"], "s-", label="Median Salary", linewidth=2)
        axes[0, 1].set_xlabel("Review Cycle")
        axes[0, 1].set_ylabel("Salary (£)")
        axes[0, 1].set_title("Salary Statistics Evolution")
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"£{x:,.0f}"))

        # Salary range and standard deviation
        axes[1, 0].plot(cycles, df["salary_range"], "^-", label="Salary Range", linewidth=2, color="red")
        axes[1, 0].set_xlabel("Review Cycle")
        axes[1, 0].set_ylabel("Salary Range (£)")
        axes[1, 0].set_title("Salary Range Over Time")
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"£{x:,.0f}"))

        # Create twin axis for standard deviation
        ax2 = axes[1, 0].twinx()
        ax2.plot(cycles, df["salary_std"], "v-", label="Standard Deviation", linewidth=2, color="orange")
        ax2.set_ylabel("Salary Std Dev (£)", color="orange")
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"£{x:,.0f}"))

        # Add legends
        lines1, labels1 = axes[1, 0].get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        axes[1, 0].legend(lines1 + lines2, labels1 + labels2)

        # Improvement rates (cycle-over-cycle changes)
        if len(df) > 1:
            gini_changes = df["gini_coefficient"].diff()[1:]  # Skip first NaN
            gender_gap_changes = df["gender_gap_percent"].abs().diff()[1:]

            change_cycles = cycles[1:]  # Skip first cycle

            axes[1, 1].bar(change_cycles - 0.2, gini_changes, 0.4, label="Gini Change", alpha=0.7)
            axes[1, 1].bar(change_cycles + 0.2, gender_gap_changes, 0.4, label="Gender Gap Change", alpha=0.7)
            axes[1, 1].set_xlabel("Review Cycle")
            axes[1, 1].set_ylabel("Change from Previous Cycle")
            axes[1, 1].set_title("Cycle-over-Cycle Changes")
            axes[1, 1].legend()
            axes[1, 1].grid(True, alpha=0.3)
            axes[1, 1].axhline(y=0, color="black", linestyle="-", alpha=0.5)

        plt.tight_layout()
        return fig

    def plot_story_salary_distributions(self):
        """Create salary distribution charts with individual employee highlights"""
        LOGGER.debug("Creating story-enhanced salary distribution charts")

        if not self.population or not self.tracked_employees:
            LOGGER.warning("No population data or tracked employees for story salary distributions")
            return None

        df = pd.DataFrame(self.population)

        # Create subplots for each level
        levels = sorted(df["level"].unique())
        n_levels = len(levels)

        fig, axes = plt.subplots(2, 3, figsize=(20, 12))
        fig.suptitle("Salary Distributions by Level with Employee Story Highlights", fontsize=16, fontweight="bold")
        axes = axes.flatten()

        for i, level in enumerate(levels):
            if i >= len(axes):
                break

            level_data = df[df["level"] == level]
            ax = axes[i]

            # Basic salary distribution
            ax.hist(
                level_data["salary"],
                bins=15,
                alpha=0.6,
                color=self.colors["primary"],
                edgecolor="black",
                label="All employees",
            )

            # Highlight tracked employees
            for category, employee_ids in self.tracked_employees.items():
                if not employee_ids:
                    continue

                # Get salary data for tracked employees at this level
                tracked_at_level = []
                for emp_id in employee_ids:
                    emp_data = df[df["employee_id"] == emp_id]
                    if not emp_data.empty and emp_data["level"].iloc[0] == level:
                        tracked_at_level.append(emp_data["salary"].iloc[0])

                if tracked_at_level:
                    ax.scatter(
                        tracked_at_level,
                        [0.5] * len(tracked_at_level),
                        color=self.story_colors[category],
                        s=100,
                        alpha=0.8,
                        marker="o",
                        label=f'{category.replace("_", " ").title()} ({len(tracked_at_level)})',
                        zorder=5,
                    )

            # Add median line
            median_salary = level_data["salary"].median()
            ax.axvline(median_salary, color="red", linestyle="--", linewidth=2, label=f"Median: £{median_salary:,.0f}")

            ax.set_title(f"Level {level} Salary Distribution\n({len(level_data)} employees)")
            ax.set_xlabel("Salary (£)")
            ax.set_ylabel("Frequency")
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
            ax.tick_params(axis="x", rotation=45)

        # Hide unused subplots
        for i in range(n_levels, len(axes)):
            axes[i].set_visible(False)

        plt.tight_layout()
        return fig

    def plot_employee_progression_timelines(self):
        """Create employee progression dashboards and timeline visualizations"""
        LOGGER.debug("Creating employee progression timeline visualizations")

        if not self.story_tracker:
            LOGGER.warning("No story tracker available for progression timelines")
            return None

        # Get timeline data from story tracker
        timeline_df = self.story_tracker.create_story_timeline()
        if timeline_df.empty:
            LOGGER.warning("No timeline data available")
            return None

        # Create timeline visualizations for each category
        n_categories = len(self.tracked_employees)
        if n_categories == 0:
            return None

        fig, axes = plt.subplots(n_categories, 1, figsize=(16, 4 * n_categories))
        if n_categories == 1:
            axes = [axes]

        fig.suptitle("Employee Progression Timelines by Category", fontsize=16, fontweight="bold")

        for i, (category, employee_ids) in enumerate(self.tracked_employees.items()):
            if not employee_ids or i >= len(axes):
                continue

            ax = axes[i]
            category_data = timeline_df[timeline_df["category"] == category]

            if category_data.empty:
                ax.text(
                    0.5,
                    0.5,
                    f'No data for {category.replace("_", " ").title()}',
                    ha="center",
                    va="center",
                    transform=ax.transAxes,
                    fontsize=12,
                )
                ax.set_title(f'{category.replace("_", " ").title()} - No Data')
                continue

            # Plot salary progression for each employee
            for emp_id in employee_ids:
                emp_data = category_data[category_data["employee_id"] == emp_id]
                if not emp_data.empty:
                    emp_data_sorted = emp_data.sort_values("cycle")
                    ax.plot(
                        emp_data_sorted["cycle"],
                        emp_data_sorted["salary"],
                        marker="o",
                        linewidth=2,
                        alpha=0.7,
                        label=f"Employee {emp_id}",
                    )

            # Calculate and show average progression
            avg_by_cycle = category_data.groupby("cycle")["salary"].mean()
            ax.plot(
                avg_by_cycle.index,
                avg_by_cycle.values,
                color="black",
                linewidth=3,
                linestyle="--",
                label="Category Average",
                alpha=0.8,
            )

            ax.set_title(f'{category.replace("_", " ").title()} Progression ({len(employee_ids)} employees)')
            ax.set_xlabel("Review Cycle")
            ax.set_ylabel("Salary (£)")
            ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
            ax.grid(True, alpha=0.3)

            # Format y-axis to show currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"£{x:,.0f}"))

        plt.tight_layout()
        return fig

    def create_interactive_story_dashboard(self):
        """Create interactive HTML dashboard with story tracking"""
        LOGGER.debug("Creating interactive story dashboard")

        if not self.story_tracker or not self.tracked_employees:
            LOGGER.warning("No story tracker or tracked employees for interactive dashboard")
            return None

        try:
            # Create Plotly subplots
            import plotly.express as px

            # Get timeline data
            timeline_df = self.story_tracker.create_story_timeline()
            if timeline_df.empty:
                return None

            # Create interactive salary progression chart
            fig = px.line(
                timeline_df,
                x="cycle",
                y="salary",
                color="category",
                hover_data=["employee_id", "performance_rating", "level"],
                title="Interactive Employee Story Dashboard - Salary Progression by Category",
                labels={"cycle": "Review Cycle", "salary": "Salary (£)", "category": "Employee Category"},
            )

            # Update layout for better interactivity
            fig.update_layout(
                title_x=0.5, hovermode="x unified", legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
            )

            # Add individual employee markers
            fig.update_traces(mode="lines+markers")

            # Save as HTML
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_path = f"images/employee_simulation_interactive_dashboard_{timestamp}.html"
            fig.write_html(html_path)

            LOGGER.info(f"Interactive dashboard saved to: {html_path}")
            return html_path

        except Exception as e:
            LOGGER.error(f"Error creating interactive dashboard: {e}")
            return None

    def save_figure(self, fig, filename):
        """Save figure following existing codebase pattern"""
        if fig is None:
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save as PNG
        png_filepath = f"/Users/brunoviola/bruvio-tools/images/employee_simulation_{filename}_{timestamp}.png"
        fig.savefig(png_filepath, dpi=300, bbox_inches="tight", facecolor="white", edgecolor="none")

        # Also save as HTML using plotly for interactivity (if possible)
        html_filepath = f"/Users/brunoviola/bruvio-tools/images/employee_simulation_{filename}_{timestamp}.html"

        try:
            # Convert matplotlib to plotly for interactivity
            import plotly.tools as tls

            plotly_fig = tls.mpl_to_plotly(fig)
            plotly_fig.write_html(html_filepath)
            LOGGER.debug(f"Saved interactive version: {html_filepath}")
        except Exception as e:
            LOGGER.debug(f"Could not create interactive version: {e}")
            html_filepath = None

        # Close matplotlib figure to free memory
        plt.close(fig)

        LOGGER.debug(f"Visualization saved: {png_filepath}")
        return png_filepath

    def create_interactive_dashboard(self):
        """Create interactive Plotly dashboard"""
        LOGGER.debug("Creating interactive dashboard")

        if not self.population:
            LOGGER.warning("No population data for dashboard")
            return None

        df = pd.DataFrame(self.population)

        # Create subplot figure
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=("Salary by Level", "Gender Distribution", "Performance Analysis", "Salary Distribution"),
            specs=[[{"secondary_y": False}, {"type": "pie"}], [{"secondary_y": False}, {"secondary_y": False}]],
        )

        # Salary by level box plot
        for level in sorted(df["level"].unique()):
            level_data = df[df["level"] == level]["salary"]
            fig.add_trace(go.Box(y=level_data, name=f"Level {level}", boxpoints="outliers"), row=1, col=1)

        # Gender pie chart
        gender_counts = df["gender"].value_counts()
        fig.add_trace(go.Pie(labels=gender_counts.index, values=gender_counts.values, name="Gender"), row=1, col=2)

        # Performance scatter plot
        perf_mapping = {"Not met": 1, "Partially met": 2, "Achieving": 3, "High Performing": 4, "Exceeding": 5}
        df["perf_numeric"] = df["performance_rating"].map(perf_mapping)

        fig.add_trace(
            go.Scatter(
                x=df["perf_numeric"],
                y=df["salary"],
                mode="markers",
                text=df["performance_rating"],
                hovertemplate="%{text}<br>Salary: £%{y:,.0f}",
                marker=dict(color=df["level"], colorscale="viridis", showscale=True, colorbar=dict(title="Level")),
                name="Performance vs Salary",
            ),
            row=2,
            col=1,
        )

        # Salary histogram
        fig.add_trace(go.Histogram(x=df["salary"], nbinsx=30, name="Salary Distribution"), row=2, col=2)

        # Update layout
        fig.update_layout(title_text="Employee Population Interactive Dashboard", showlegend=False, height=800)

        # Save interactive dashboard
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dashboard_filepath = f"/Users/brunoviola/bruvio-tools/images/employee_simulation_dashboard_{timestamp}.html"
        fig.write_html(dashboard_filepath)

        LOGGER.info(f"Interactive dashboard saved: {dashboard_filepath}")
        return dashboard_filepath


def create_parser():
    """Create command line argument parser"""
    parser = argparse.ArgumentParser(description="Generate visualizations for employee simulation")
    parser.add_argument("--population-file", help="JSON file with population data")
    parser.add_argument("--inequality-file", help="CSV file with inequality progression data")
    parser.add_argument(
        "--output-dir", default="/Users/brunoviola/bruvio-tools/images/", help="Output directory for visualizations"
    )
    parser.add_argument("--interactive", action="store_true", help="Create interactive dashboard")

    return parser


def main():
    """Main function for visualization generation"""
    parser = create_parser()
    args = parser.parse_args()

    # Load data
    population_data = None
    inequality_data = None

    if args.population_file:
        try:
            with open(args.population_file, "r") as f:
                population_data = json.load(f)
            LOGGER.info(f"Loaded population data: {len(population_data)} employees")
        except Exception as e:
            LOGGER.error(f"Failed to load population data: {e}")

    if args.inequality_file:
        try:
            inequality_data = pd.read_csv(args.inequality_file).to_dict("records")
            LOGGER.info(f"Loaded inequality data: {len(inequality_data)} cycles")
        except Exception as e:
            LOGGER.error(f"Failed to load inequality data: {e}")

    if not population_data and not inequality_data:
        LOGGER.error("No data provided for visualization")
        parser.print_help()
        return 1

    # Generate visualizations
    generator = VisualizationGenerator(population_data, inequality_data)
    visualizations = generator.generate_complete_analysis()

    # Create interactive dashboard if requested
    if args.interactive:
        if dashboard_path := generator.create_interactive_dashboard():
            visualizations["interactive_dashboard"] = dashboard_path

    LOGGER.info("Visualization generation completed")
    LOGGER.info("Generated visualizations:")
    for name, path in visualizations.items():
        if path:
            LOGGER.info(f"  {name}: {path}")

    return 0


if __name__ == "__main__":
    exit(main())

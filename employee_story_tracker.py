#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from logger import LOGGER


@dataclass
class EmployeeStory:
    """Data structure representing an individual employee's story across review cycles."""

    employee_id: int
    category: str
    initial_salary: float
    current_salary: float
    salary_history: List[Tuple[int, float]]
    performance_history: List[Tuple[int, str]]
    total_growth_percent: float
    key_events: List[str]
    story_summary: str
    recommendations: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert EmployeeStory to dictionary for serialization."""
        return {
            "employee_id": self.employee_id,
            "category": self.category,
            "initial_salary": self.initial_salary,
            "current_salary": self.current_salary,
            "salary_history": self.salary_history,
            "performance_history": self.performance_history,
            "total_growth_percent": self.total_growth_percent,
            "key_events": self.key_events,
            "story_summary": self.story_summary,
            "recommendations": self.recommendations,
        }


class EmployeeStoryTracker:
    """Efficient employee story tracking using pandas operations.

    Track individual employee journeys across multiple review cycles.
    """

    def __init__(self):
        self.employee_histories: Dict[int, List[Dict]] = {}
        self.tracked_categories: Dict[str, List[int]] = {}
        self.cycle_data: Dict[int, pd.DataFrame] = {}
        self.population_stats: Dict[int, Dict] = {}

        LOGGER.info("Initialized EmployeeStoryTracker")

    def add_cycle_data(self, cycle_num: int, employee_data: List[Dict]):
        """Add employee data for a specific cycle using vectorized operations."""
        LOGGER.debug(f"Adding cycle {cycle_num} data with {len(employee_data)} employees")

        cycle_df = pd.DataFrame(employee_data)
        self.cycle_data[cycle_num] = cycle_df

        # Update population statistics for benchmarking
        self.population_stats[cycle_num] = {
            "median_salary_by_level": cycle_df.groupby("level")["salary"].median().to_dict(),
            "gender_medians": cycle_df.groupby("gender")["salary"].median().to_dict(),
            "level_ranges": self._calculate_level_ranges(cycle_df),
            "total_employees": len(cycle_df),
        }

        # Update individual employee histories
        for _, employee in cycle_df.iterrows():
            emp_id = employee["employee_id"]
            if emp_id not in self.employee_histories:
                self.employee_histories[emp_id] = []

            self.employee_histories[emp_id].append(
                {
                    "cycle": cycle_num,
                    "salary": employee["salary"],
                    "performance_rating": employee["performance_rating"],
                    "level": employee["level"],
                    "gender": employee["gender"],
                    "hire_date": employee.get("hire_date", "Unknown"),
                }
            )

        LOGGER.debug(f"Population stats updated for cycle {cycle_num}")

    def _calculate_level_ranges(self, df: pd.DataFrame) -> Dict[int, Dict[str, float]]:
        """Calculate salary ranges for each level."""
        level_ranges = {}
        for level in df["level"].unique():
            level_data = df[df["level"] == level]["salary"]
            level_ranges[level] = {
                "min": level_data.min(),
                "max": level_data.max(),
                "median": level_data.median(),
                "q75": level_data.quantile(0.75),
                "q25": level_data.quantile(0.25),
            }
        return level_ranges

    def identify_tracked_employees(self, max_per_category: int = 10) -> Dict[str, List[int]]:
        """Identify employees for tracking using efficient pandas operations."""
        if not self.cycle_data:
            LOGGER.warning("No cycle data available for employee identification")
            return {}

        # Use most recent cycle for identification
        latest_cycle = max(self.cycle_data.keys())
        df = self.cycle_data[latest_cycle]

        tracked = {"gender_gap_affected": [], "above_range": [], "high_performers": []}

        LOGGER.info(f"Identifying tracked employees from cycle {latest_cycle} with {len(df)} employees")

        # Gender gap affected: Female employees below male median for their level
        try:
            male_medians = df[df["gender"] == "Male"].groupby("level")["salary"].median()
            female_employees = df[df["gender"] == "Female"]

            for _, employee in female_employees.iterrows():
                level_male_median = male_medians.get(employee["level"], float("inf"))
                if pd.notna(level_male_median) and employee["salary"] < level_male_median * 0.95:  # 5% threshold
                    tracked["gender_gap_affected"].append(employee["employee_id"])

            LOGGER.debug(f"Identified {len(tracked['gender_gap_affected'])} gender gap affected employees")
        except Exception as e:
            LOGGER.warning(f"Error identifying gender gap affected employees: {e}")

        # Above range employees: Salary exceeds level 75th percentile significantly
        try:
            level_ranges = self.population_stats[latest_cycle]["level_ranges"]
            above_range_employees = []

            for _, employee in df.iterrows():
                level_q75 = level_ranges.get(employee["level"], {}).get("q75", float("inf"))
                if pd.notna(level_q75) and employee["salary"] > level_q75 * 1.1:  # 10% above 75th percentile
                    above_range_employees.append(employee["employee_id"])

            tracked["above_range"] = above_range_employees
            LOGGER.debug(f"Identified {len(tracked['above_range'])} above-range employees")
        except Exception as e:
            LOGGER.warning(f"Error identifying above-range employees: {e}")

        # High performers: Consistent high ratings with above-average growth
        try:
            high_perf_mask = df["performance_rating"].isin(["High Performing", "Exceeding"])
            potential_high_performers = df[high_perf_mask]["employee_id"].tolist()

            # Filter by growth rate if we have historical data
            if len(self.cycle_data) > 1:
                high_performers_filtered = []
                for emp_id in potential_high_performers:
                    growth_rate = self._calculate_employee_growth_rate(emp_id)
                    if growth_rate is not None and growth_rate > 0.05:  # 5% growth threshold
                        high_performers_filtered.append(emp_id)
                tracked["high_performers"] = high_performers_filtered
            else:
                tracked["high_performers"] = potential_high_performers

            LOGGER.debug(f"Identified {len(tracked['high_performers'])} high performers")
        except Exception as e:
            LOGGER.warning(f"Error identifying high performers: {e}")

        # Limit to max per category
        for category in tracked:
            if len(tracked[category]) > max_per_category:
                # Sort by some criteria before limiting (e.g., salary difference for gender gap)
                if category == "gender_gap_affected" and tracked[category]:
                    # Sort by largest gap from male median
                    category_employees = df[df["employee_id"].isin(tracked[category])]
                    male_medians = df[df["gender"] == "Male"].groupby("level")["salary"].median()

                    gaps = []
                    for _, emp in category_employees.iterrows():
                        male_median = male_medians.get(emp["level"], emp["salary"])
                        gap = (male_median - emp["salary"]) / male_median if male_median > 0 else 0
                        gaps.append((emp["employee_id"], gap))

                    gaps.sort(key=lambda x: x[1], reverse=True)
                    tracked[category] = [emp_id for emp_id, _ in gaps[:max_per_category]]
                else:
                    tracked[category] = tracked[category][:max_per_category]

        # Store tracked categories for later use
        self.tracked_categories = tracked

        total_tracked = sum(len(employees) for employees in tracked.values())
        LOGGER.info(f"Total tracked employees: {total_tracked} across {len(tracked)} categories")

        return tracked

    def _calculate_employee_growth_rate(self, employee_id: int) -> Optional[float]:
        """Calculate employee's salary growth rate across all cycles."""
        if employee_id not in self.employee_histories:
            return None

        history = self.employee_histories[employee_id]
        if len(history) < 2:
            return None

        # Sort by cycle number
        history_sorted = sorted(history, key=lambda x: x["cycle"])
        initial_salary = history_sorted[0]["salary"]
        if initial_salary <= 0:
            return None

        num_cycles = len(history_sorted) - 1
        if num_cycles <= 0:
            return None

        current_salary = history_sorted[-1]["salary"]

        return (current_salary / initial_salary - 1) / num_cycles

    def generate_employee_story(self, employee_id: int, category: str) -> Optional[EmployeeStory]:
        """Generate narrative story for a specific employee."""
        if employee_id not in self.employee_histories:
            LOGGER.warning(f"No history found for employee {employee_id}")
            return None

        history = sorted(self.employee_histories[employee_id], key=lambda x: x["cycle"])
        if len(history) < 1:
            return None

        initial_data = history[0]
        current_data = history[-1]

        # Calculate metrics
        initial_salary = initial_data["salary"]
        current_salary = current_data["salary"]
        total_growth_percent = ((current_salary - initial_salary) / initial_salary * 100) if initial_salary > 0 else 0

        salary_history = [(h["cycle"], h["salary"]) for h in history]
        performance_history = [(h["cycle"], h["performance_rating"]) for h in history]

        # Generate key events
        key_events = self._identify_key_events(history)

        # Generate story summary based on category
        story_summary = self._generate_story_summary(employee_id, category, history, total_growth_percent)

        # Generate recommendations
        recommendations = self._generate_recommendations(employee_id, category, history, current_data)

        return EmployeeStory(
            employee_id=employee_id,
            category=category,
            initial_salary=initial_salary,
            current_salary=current_salary,
            salary_history=salary_history,
            performance_history=performance_history,
            total_growth_percent=total_growth_percent,
            key_events=key_events,
            story_summary=story_summary,
            recommendations=recommendations,
        )

    def _identify_key_events(self, history: List[Dict]) -> List[str]:
        """Identify key events in employee's history."""
        events = []

        for i in range(1, len(history)):
            prev = history[i - 1]
            curr = history[i]

            # Significant salary increase
            if curr["salary"] > prev["salary"] * 1.1:
                pct_increase = (curr["salary"] - prev["salary"]) / prev["salary"] * 100
                events.append(f"Cycle {curr['cycle']}: {pct_increase:.1f}% salary increase")

            # Performance rating change
            if curr["performance_rating"] != prev["performance_rating"]:
                events.append(
                    f"Cycle {curr['cycle']}: Performance changed from '{prev['performance_rating']}' to '{curr['performance_rating']}'"
                )

            # Level change (if applicable)
            if curr["level"] != prev["level"]:
                events.append(f"Cycle {curr['cycle']}: Level changed from {prev['level']} to {curr['level']}")

        return events

    def _generate_story_summary(
        self, employee_id: int, category: str, history: List[Dict], total_growth_percent: float
    ) -> str:
        """Generate narrative story summary based on category and history."""
        current_data = history[-1]
        initial_data = history[0]

        if category == "gender_gap_affected":
            return (
                f"Employee {employee_id} is a female employee who started at Level {initial_data['level']} "
                f"with a salary of £{initial_data['salary']:,.0f}. Despite {len(history)} review cycles, "
                f"her current salary of £{current_data['salary']:,.0f} ({total_growth_percent:+.1f}% growth) "
                f"remains below the male median for her level, indicating potential gender pay gap impact."
            )

        elif category == "above_range":
            return (
                f"Employee {employee_id} at Level {current_data['level']} has a salary of "
                f"£{current_data['salary']:,.0f}, which significantly exceeds the typical range "
                f"for their level. Over {len(history)} cycles, they've achieved {total_growth_percent:+.1f}% "
                f"growth, likely requiring COLA-only adjustments to maintain equity."
            )

        elif category == "high_performers":
            return (
                f"Employee {employee_id} is a high performer at Level {current_data['level']} "
                f"with consistent excellent ratings. Their salary has grown {total_growth_percent:+.1f}% "
                f"over {len(history)} cycles, from £{initial_data['salary']:,.0f} to "
                f"£{current_data['salary']:,.0f}, reflecting strong performance-based progression."
            )

        else:
            return (
                f"Employee {employee_id} has been tracked for {len(history)} review cycles, "
                f"with salary growth of {total_growth_percent:+.1f}% from £{initial_data['salary']:,.0f} "
                f"to £{current_data['salary']:,.0f}."
            )

    def _generate_recommendations(
        self, employee_id: int, category: str, history: List[Dict], current_data: Dict
    ) -> List[str]:
        """Generate actionable recommendations based on employee category and performance."""
        recommendations = []

        if category == "gender_gap_affected":
            recommendations.extend(
                [
                    "Review salary against male peers at same level for equity adjustment",
                    "Consider accelerated progression pathway if performance warrants",
                    "Monitor for continued gap closure in future cycles",
                ]
            )

        elif category == "above_range":
            recommendations.extend(
                [
                    "Limit future increases to COLA adjustments only",
                    "Consider promotion to next level if performance and role complexity justify",
                    "Use as benchmark for level salary range review",
                ]
            )

        elif category == "high_performers":
            recommendations.extend(
                [
                    "Consider for promotion to next level",
                    "Provide stretch assignments and development opportunities",
                    "Ensure competitive retention package",
                ]
            )

        # Performance-based recommendations
        latest_performance = current_data["performance_rating"]
        if latest_performance in ["High Performing", "Exceeding"]:
            if "Consider for promotion" not in str(recommendations):
                recommendations.append("Strong candidate for advancement opportunities")
        elif latest_performance in ["Not met", "Partially met"]:
            recommendations.append("Requires performance improvement plan and additional support")

        return recommendations

    def create_story_timeline(self) -> pd.DataFrame:
        """Create comprehensive timeline of all tracked employee stories."""
        timeline_data = []

        for category, employee_ids in self.tracked_categories.items():
            for emp_id in employee_ids:
                if emp_id in self.employee_histories:
                    history = self.employee_histories[emp_id]
                    timeline_data.extend(
                        {
                            "employee_id": emp_id,
                            "category": category,
                            "cycle": record["cycle"],
                            "salary": record["salary"],
                            "performance_rating": record["performance_rating"],
                            "level": record["level"],
                            "gender": record["gender"],
                        }
                        for record in history
                    )
        if timeline_data:
            timeline_df = pd.DataFrame(timeline_data)
            LOGGER.info(f"Created story timeline with {len(timeline_df)} records")
            return timeline_df
        else:
            LOGGER.warning("No timeline data available")
            return pd.DataFrame()

    def get_tracked_employee_summary(self) -> Dict[str, Any]:
        """Get summary statistics of tracked employees."""
        summary = {
            "total_tracked": sum(len(employees) for employees in self.tracked_categories.values()),
            "categories": {},
            "cycles_tracked": len(self.cycle_data),
            "total_population": (
                sum(stats["total_employees"] for stats in self.population_stats.values()) // len(self.population_stats)
                if self.population_stats
                else 0
            ),
        }

        for category, employee_ids in self.tracked_categories.items():
            category_summary = {"count": len(employee_ids), "employee_ids": employee_ids}

            # Calculate average growth rate for this category
            growth_rates = []
            for emp_id in employee_ids:
                growth_rate = self._calculate_employee_growth_rate(emp_id)
                if growth_rate is not None:
                    growth_rates.append(growth_rate)

            if growth_rates:
                category_summary["average_growth_rate"] = np.mean(growth_rates)
                category_summary["median_growth_rate"] = np.median(growth_rates)

            summary["categories"][category] = category_summary

        return summary

    def export_stories_to_dict(self) -> Dict[str, Any]:
        """Export all employee stories to dictionary format for serialization."""
        stories_dict = {
            "metadata": {
                "generation_timestamp": datetime.now().isoformat(),
                "cycles_tracked": len(self.cycle_data),
                "total_tracked_employees": sum(len(employees) for employees in self.tracked_categories.values()),
            },
            "categories": {},
        }

        for category, employee_ids in self.tracked_categories.items():
            category_stories = []
            for emp_id in employee_ids:
                if story := self.generate_employee_story(emp_id, category):
                    category_stories.append(story.to_dict())

            stories_dict["categories"][category] = category_stories

        return stories_dict

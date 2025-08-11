#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class InteractiveDashboardGenerator:
    """Advanced interactive dashboard generator for comprehensive employee story exploration.

    Implements Phase 4 PRP requirements for interactive data exploration.
    """

    def __init__(self, story_tracker=None, smart_logger=None):
        self.story_tracker = story_tracker
        self.smart_logger = smart_logger
        self.dashboard_components = {}
        self.layout_config = {
            "theme": "plotly_white",
            "font_family": "Arial, sans-serif",
            "title_font_size": 18,
            "axis_font_size": 12,
            "height": 500,
            "margin": dict(l=50, r=50, t=50, b=50),
        }

    def _log(self, message: str, level: str = "info"):
        """Helper method for logging."""
        if self.smart_logger:
            getattr(self.smart_logger, f"log_{level}")(message)
        else:
            print(f"[{level.upper()}] {message}")

    def create_salary_distribution_explorer(self, population_data: List[Dict]) -> Dict[str, Any]:
        """Create interactive salary distribution explorer with filtering capabilities.

        Args:
            population_data: Employee population data

        Returns:
            Dictionary containing Plotly figure and metadata
        """
        df = pd.DataFrame(population_data)

        # Ensure numeric columns are properly typed
        df["salary"] = pd.to_numeric(df["salary"], errors="coerce")
        df["performance_rating"] = pd.to_numeric(df["performance_rating"], errors="coerce")
        df["level"] = pd.to_numeric(df["level"], errors="coerce")

        # Create subplot with multiple views
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=[
                "Salary Distribution by Level",
                "Gender Gap Analysis",
                "Performance vs Salary Correlation",
                "Department Salary Comparison",
            ],
            specs=[[{"secondary_y": True}, {"type": "box"}], [{"type": "scatter"}, {"type": "bar"}]],
            vertical_spacing=0.12,
            horizontal_spacing=0.1,
        )

        # 1. Salary Distribution by Level (with histogram overlay)
        for level in sorted(df["level"].unique()):
            level_data = df[df["level"] == level]
            fig.add_trace(
                go.Histogram(x=level_data["salary"], name=f"Level {level}", opacity=0.7, nbinsx=20, showlegend=True),
                row=1,
                col=1,
            )

        # Add median lines
        for level in sorted(df["level"].unique()):
            level_data = df[df["level"] == level]
            median_salary = level_data["salary"].median()
            fig.add_vline(
                x=median_salary, line_dash="dash", line_color="red", annotation_text=f"L{level} Median", row=1, col=1
            )

        # 2. Gender Gap Analysis (Box plots)
        for gender in df["gender"].unique():
            gender_data = df[df["gender"] == gender]
            fig.add_trace(
                go.Box(
                    y=gender_data["salary"], name=f"{gender.title()}", boxpoints="outliers", jitter=0.3, pointpos=-1.8
                ),
                row=1,
                col=2,
            )

        # 3. Performance vs Salary Correlation
        fig.add_trace(
            go.Scatter(
                x=df["performance_rating"],
                y=df["salary"],
                mode="markers",
                marker=dict(
                    size=8,
                    color=df["level"],
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(title="Level", x=0.45, y=0.25, len=0.4),
                ),
                text=[
                    f"ID: {emp['employee_id']}<br>Level: {emp['level']}<br>Gender: {emp['gender']}"
                    for emp in population_data
                ],
                hovertemplate="Performance: %{x}<br>Salary: £%{y:,.0f}<br>%{text}<extra></extra>",
                name="Employees",
                showlegend=False,
            ),
            row=2,
            col=1,
        )

        # Add trend line (with error handling for numerical stability)
        try:
            # Filter out any NaN values for trend calculation
            valid_data = df.dropna(subset=["performance_rating", "salary"])
            if len(valid_data) > 10:  # Only add trend line if enough data points
                z = np.polyfit(valid_data["performance_rating"], valid_data["salary"], 1)
                p = np.poly1d(z)
                x_trend = np.linspace(
                    valid_data["performance_rating"].min(), valid_data["performance_rating"].max(), 100
                )
                fig.add_trace(
                    go.Scatter(
                        x=x_trend,
                        y=p(x_trend),
                        mode="lines",
                        line=dict(color="red", dash="dash"),
                        name="Trend",
                        showlegend=False,
                    ),
                    row=2,
                    col=1,
                )
        except (np.linalg.LinAlgError, ValueError) as e:
            # Skip trend line if numerical issues occur
            self._log(f"Skipping trend line due to numerical instability: {e}", "warning")

        # 4. Department Salary Comparison (if department data exists)
        if "department" in df.columns:
            dept_stats = df.groupby("department")["salary"].agg(["mean", "median", "std"]).reset_index()
            fig.add_trace(
                go.Bar(
                    x=dept_stats["department"],
                    y=dept_stats["mean"],
                    error_y=dict(type="data", array=dept_stats["std"]),
                    name="Mean Salary",
                    marker_color="lightblue",
                    showlegend=False,
                ),
                row=2,
                col=2,
            )
        else:
            # Alternative: Salary range by level
            level_stats = df.groupby("level")["salary"].agg(["mean", "std"]).reset_index()
            fig.add_trace(
                go.Bar(
                    x=[f"Level {lvl}" for lvl in level_stats["level"]],
                    y=level_stats["mean"],
                    error_y=dict(type="data", array=level_stats["std"]),
                    name="Mean Salary by Level",
                    marker_color="lightcoral",
                    showlegend=False,
                ),
                row=2,
                col=2,
            )

        # Update layout
        fig.update_layout(
            title=dict(
                text="Employee Salary Distribution Explorer", x=0.5, font_size=self.layout_config["title_font_size"]
            ),
            template=self.layout_config["theme"],
            height=800,
            showlegend=True,
            legend=dict(x=0.02, y=0.98),
            font_family=self.layout_config["font_family"],
        )

        # Update axis labels
        fig.update_xaxes(title_text="Salary (£)", row=1, col=1)
        fig.update_yaxes(title_text="Frequency", row=1, col=1)
        fig.update_yaxes(title_text="Salary (£)", row=1, col=2)
        fig.update_xaxes(title_text="Performance Rating", row=2, col=1)
        fig.update_yaxes(title_text="Salary (£)", row=2, col=1)
        fig.update_yaxes(title_text="Mean Salary (£)", row=2, col=2)

        return {
            "figure": fig,
            "component_type": "salary_distribution_explorer",
            "data_points": len(population_data),
            "levels_analyzed": len(df["level"].unique()),
            "gender_groups": len(df["gender"].unique()),
        }

    def create_employee_story_timeline(
        self, tracked_employees: Dict[str, List], cycle_data: Optional[pd.DataFrame] = None
    ) -> Dict[str, Any]:
        """Create interactive timeline showing employee progression stories.

        Args:
            tracked_employees: Tracked employees by category
            cycle_data: Cycle progression data

        Returns:
            Dictionary containing Plotly figure and metadata
        """
        if not tracked_employees or not any(tracked_employees.values()):
            self._log("No tracked employees available for timeline creation", "warning")
            return self._create_empty_component("No employee stories available")

        fig = go.Figure()

        colors = {"gender_gap": "#FF6B6B", "above_range": "#4ECDC4", "high_performer": "#45B7D1", "other": "#96CEB4"}

        y_position = 0
        employee_positions = {}

        # Process each category
        for category, employees in tracked_employees.items():
            if not employees:
                continue

            category_color = colors.get(category, colors["other"])

            for employee in employees:
                # Extract employee data
                emp_data = employee.__dict__ if hasattr(employee, "__dict__") else employee
                emp_id = emp_data.get("employee_id", "Unknown")
                employee_positions[emp_id] = y_position

                # Create progression line if cycle data available
                if cycle_data is not None and not cycle_data.empty:
                    emp_cycles = cycle_data[cycle_data["employee_id"] == emp_id]

                    if not emp_cycles.empty:
                        fig.add_trace(
                            go.Scatter(
                                x=emp_cycles["cycle"],
                                y=[y_position] * len(emp_cycles),
                                mode="lines+markers",
                                line=dict(color=category_color, width=3),
                                marker=dict(
                                    size=[8 + (salary / 10000) for salary in emp_cycles["salary"]],
                                    color=emp_cycles["salary"],
                                    colorscale="Viridis",
                                    showscale=False,
                                    opacity=0.8,
                                ),
                                name=f"{category.replace('_', ' ').title()} - Employee {emp_id}",
                                text=[
                                    f"Cycle {cycle}<br>Salary: £{salary:,.0f}<br>Level: {level}<br>Performance: {perf}"
                                    for cycle, salary, level, perf in zip(
                                        emp_cycles["cycle"],
                                        emp_cycles["salary"],
                                        emp_cycles["level"],
                                        emp_cycles["performance_rating"],
                                    )
                                ],
                                hovertemplate="%{text}<extra></extra>",
                                showlegend=True,
                            )
                        )
                else:
                    # Static point if no cycle data
                    fig.add_trace(
                        go.Scatter(
                            x=[0],
                            y=[y_position],
                            mode="markers",
                            marker=dict(size=12, color=category_color),
                            name=f"{category.replace('_', ' ').title()} - Employee {emp_id}",
                            text=f"Employee {emp_id}<br>Category: {category}",
                            hovertemplate="%{text}<extra></extra>",
                            showlegend=True,
                        )
                    )

                y_position += 1

        # Update layout
        fig.update_layout(
            title=dict(
                text="Employee Story Timeline Explorer",
                x=0.5,
                font_size=self.layout_config["title_font_size"],
            ),
            xaxis=dict(title="Review Cycle", showgrid=True, zeroline=True),
            yaxis=dict(
                title="Employee Stories",
                tickmode="array",
                tickvals=list(range(len(employee_positions))),
                ticktext=[f"Emp {emp_id}" for emp_id in employee_positions],
                showgrid=True,
            ),
            template=self.layout_config["theme"],
            height=max(400, len(employee_positions) * 50 + 200),
            hovermode="closest",
            legend=dict(x=1.02, y=1),
            font_family=self.layout_config["font_family"],
        )

        return {
            "figure": fig,
            "component_type": "employee_story_timeline",
            "total_stories": sum(len(emps) for emps in tracked_employees.values()),
            "categories": list(tracked_employees.keys()),
            "employee_positions": employee_positions,
        }

    def create_comparative_analysis_dashboard(
        self, population_data: List[Dict], tracked_employees: Dict[str, List]
    ) -> Dict[str, Any]:
        """Create comparative analysis dashboard across different employee categories.

        Args:
            population_data: Full employee population data
            tracked_employees: Tracked employees by category

        Returns:
            Dictionary containing Plotly figure and metadata
        """
        df = pd.DataFrame(population_data)

        # Create comprehensive comparison dashboard
        fig = make_subplots(
            rows=3,
            cols=2,
            subplot_titles=[
                "Salary Distribution Comparison",
                "Performance Rating Distribution",
                "Career Progression Velocity",
                "Gender Representation",
                "Level Distribution Analysis",
                "Category Overlap Analysis",
            ],
            specs=[
                [{"type": "violin"}, {"type": "histogram"}],
                [{"type": "scatter"}, {"type": "pie"}],
                [{"type": "bar"}, {"type": "scatter"}],
            ],
            vertical_spacing=0.08,
            horizontal_spacing=0.1,
        )

        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4", "#FECA57"]

        # Extract tracked employee IDs by category
        tracked_ids_by_category = {}
        all_tracked_ids = set()

        for category, employees in tracked_employees.items():
            if employees:
                ids = []
                for emp in employees:
                    emp_id = emp.employee_id if hasattr(emp, "employee_id") else emp.get("employee_id")
                    if emp_id:
                        ids.append(emp_id)
                        all_tracked_ids.add(emp_id)
                tracked_ids_by_category[category] = ids

        # 1. Salary Distribution Comparison (Violin plots)
        category_idx = 0
        for category, emp_ids in tracked_ids_by_category.items():
            if emp_ids:
                category_data = df[df["employee_id"].isin(emp_ids)]
                fig.add_trace(
                    go.Violin(
                        y=category_data["salary"],
                        name=category.replace("_", " ").title(),
                        box_visible=True,
                        meanline_visible=True,
                        fillcolor=colors[category_idx % len(colors)],
                        opacity=0.6,
                    ),
                    row=1,
                    col=1,
                )
                category_idx += 1

        # Add general population comparison
        general_pop = df[~df["employee_id"].isin(all_tracked_ids)]
        if not general_pop.empty:
            fig.add_trace(
                go.Violin(
                    y=general_pop["salary"],
                    name="General Population",
                    box_visible=True,
                    meanline_visible=True,
                    fillcolor="lightgray",
                    opacity=0.4,
                ),
                row=1,
                col=1,
            )

        # 2. Performance Rating Distribution
        for category, emp_ids in tracked_ids_by_category.items():
            if emp_ids:
                category_data = df[df["employee_id"].isin(emp_ids)]
                fig.add_trace(
                    go.Histogram(
                        x=category_data["performance_rating"],
                        name=category.replace("_", " ").title(),
                        opacity=0.7,
                        nbinsx=10,
                        showlegend=False,
                    ),
                    row=1,
                    col=2,
                )

        # 3. Career Progression Velocity (simplified - using level vs performance)
        for category, emp_ids in tracked_ids_by_category.items():
            if emp_ids:
                category_data = df[df["employee_id"].isin(emp_ids)]
                fig.add_trace(
                    go.Scatter(
                        x=category_data["level"],
                        y=category_data["performance_rating"],
                        mode="markers",
                        marker=dict(size=10, opacity=0.7),
                        name=category.replace("_", " ").title(),
                        text=[f"Emp {emp_id}" for emp_id in category_data["employee_id"]],
                        hovertemplate="Level: %{x}<br>Performance: %{y}<br>%{text}<extra></extra>",
                        showlegend=False,
                    ),
                    row=2,
                    col=1,
                )

        # 4. Gender Representation (Pie chart)
        gender_counts = {}
        for category, emp_ids in tracked_ids_by_category.items():
            if emp_ids:
                category_data = df[df["employee_id"].isin(emp_ids)]
                gender_dist = category_data["gender"].value_counts()
                for gender, count in gender_dist.items():
                    key = f"{category}_{gender}"
                    gender_counts[key] = count

        if gender_counts:
            fig.add_trace(
                go.Pie(
                    labels=list(gender_counts.keys()),
                    values=list(gender_counts.values()),
                    name="Gender Distribution",
                    showlegend=False,
                ),
                row=2,
                col=2,
            )

        # 5. Level Distribution Analysis
        level_analysis = {}
        for category, emp_ids in tracked_ids_by_category.items():
            if emp_ids:
                category_data = df[df["employee_id"].isin(emp_ids)]
                level_counts = category_data["level"].value_counts().sort_index()
                for level, count in level_counts.items():
                    if level not in level_analysis:
                        level_analysis[level] = {}
                    level_analysis[level][category] = count

        for category in tracked_ids_by_category:
            levels = sorted(level_analysis.keys())
            counts = [level_analysis.get(level, {}).get(category, 0) for level in levels]
            fig.add_trace(
                go.Bar(
                    x=[f"Level {level}" for level in levels],
                    y=counts,
                    name=category.replace("_", " ").title(),
                    showlegend=False,
                ),
                row=3,
                col=1,
            )

        # 6. Category Overlap Analysis
        if len(tracked_ids_by_category) >= 2:
            # Create scatter plot showing overlap between categories
            categories = list(tracked_ids_by_category.keys())
            if len(categories) >= 2:
                cat1, cat2 = categories[0], categories[1]
                ids1 = set(tracked_ids_by_category[cat1])
                ids2 = set(tracked_ids_by_category[cat2])

                # Plot employees with overlap indication
                for emp_id in ids1.union(ids2):
                    emp_data = df[df["employee_id"] == emp_id].iloc[0]

                    if emp_id in ids1 and emp_id in ids2:
                        marker_color = "red"
                        category_label = "Both Categories"
                    elif emp_id in ids1:
                        marker_color = colors[0]
                        category_label = cat1.replace("_", " ").title()
                    else:
                        marker_color = colors[1]
                        category_label = cat2.replace("_", " ").title()

                    fig.add_trace(
                        go.Scatter(
                            x=[emp_data["salary"]],
                            y=[emp_data["performance_rating"]],
                            mode="markers",
                            marker=dict(size=12, color=marker_color, opacity=0.7),
                            name=category_label,
                            text=f"Employee {emp_id}",
                            hovertemplate="Salary: £%{x:,.0f}<br>Performance: %{y}<br>%{text}<extra></extra>",
                            showlegend=False,
                        ),
                        row=3,
                        col=2,
                    )

        # Update layout
        fig.update_layout(
            title=dict(text="Comparative Analysis Dashboard", x=0.5, font_size=self.layout_config["title_font_size"]),
            template=self.layout_config["theme"],
            height=1200,
            showlegend=True,
            legend=dict(x=1.02, y=1),
            font_family=self.layout_config["font_family"],
        )

        # Update axis labels
        fig.update_yaxes(title_text="Salary (£)", row=1, col=1)
        fig.update_xaxes(title_text="Performance Rating", row=1, col=2)
        fig.update_yaxes(title_text="Frequency", row=1, col=2)
        fig.update_xaxes(title_text="Level", row=2, col=1)
        fig.update_yaxes(title_text="Performance Rating", row=2, col=1)
        fig.update_xaxes(title_text="Level", row=3, col=1)
        fig.update_yaxes(title_text="Employee Count", row=3, col=1)
        fig.update_xaxes(title_text="Salary (£)", row=3, col=2)
        fig.update_yaxes(title_text="Performance Rating", row=3, col=2)

        return {
            "figure": fig,
            "component_type": "comparative_analysis_dashboard",
            "categories_analyzed": len(tracked_ids_by_category),
            "total_tracked_employees": len(all_tracked_ids),
            "comparison_dimensions": 6,
        }

    def _create_empty_component(self, message: str) -> Dict[str, Any]:
        """Create empty component with message."""
        fig = go.Figure()
        fig.add_annotation(text=message, xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False, font=dict(size=16))
        fig.update_layout(template=self.layout_config["theme"], height=self.layout_config["height"])

        return {"figure": fig, "component_type": "empty", "message": message}

    def generate_comprehensive_dashboard(
        self,
        population_data: List[Dict],
        tracked_employees: Dict[str, List],
        cycle_data: Optional[pd.DataFrame] = None,
        output_path: Optional[str] = None,
    ) -> str:
        """Generate comprehensive interactive dashboard combining all components.

        Args:
            population_data: Full employee population data
            tracked_employees: Tracked employees by category
            cycle_data: Optional cycle progression data
            output_path: Optional custom output path

        Returns:
            Path to generated HTML dashboard
        """
        self._log("Starting comprehensive dashboard generation")

        # Generate all dashboard components
        components = {}

        try:
            # 1. Salary Distribution Explorer
            self._log("Creating salary distribution explorer")
            components["salary_explorer"] = self.create_salary_distribution_explorer(population_data)

            # 2. Employee Story Timeline
            if tracked_employees:
                self._log("Creating employee story timeline")
                components["story_timeline"] = self.create_employee_story_timeline(tracked_employees, cycle_data)

            # 3. Comparative Analysis Dashboard
            if tracked_employees:
                self._log("Creating comparative analysis dashboard")
                components["comparative_analysis"] = self.create_comparative_analysis_dashboard(
                    population_data, tracked_employees
                )

            # Generate HTML dashboard
            dashboard_html = self._generate_dashboard_html(components, population_data, tracked_employees)

            # Save to file
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"comprehensive_employee_dashboard_{timestamp}.html"

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(dashboard_html)

            self._log(f"Comprehensive dashboard generated: {output_path}")
            return str(output_file)

        except Exception as e:
            self._log(f"Failed to generate comprehensive dashboard: {e}", "error")
            raise

    def _generate_dashboard_html(
        self, components: Dict[str, Dict], population_data: List[Dict], tracked_employees: Dict[str, List]
    ) -> str:
        """Generate HTML dashboard with all components."""

        # Convert Plotly figures to HTML
        plots_html = []

        for comp_name, comp_data in components.items():
            if "figure" in comp_data:
                fig_html = comp_data["figure"].to_html(include_plotlyjs=False, div_id=f"{comp_name}_plot")
                plots_html.append(f'<div class="dashboard-component">{fig_html}</div>')

        # Generate summary statistics
        df = pd.DataFrame(population_data)
        total_tracked = sum(len(employees) for employees in tracked_employees.values()) if tracked_employees else 0

        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Employee Simulation Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .dashboard-header {{
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .dashboard-header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .dashboard-header .subtitle {{
            margin: 10px 0 0 0;
            font-size: 1.2em;
            opacity: 0.9;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin: 0;
        }}
        .stat-label {{
            color: #666;
            margin: 5px 0 0 0;
            font-size: 0.9em;
        }}
        .dashboard-component {{
            background: white;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            overflow: hidden;
        }}
        .dashboard-component > div {{
            padding: 0;
        }}
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: #666;
            border-top: 1px solid #ddd;
        }}
        @media (max-width: 768px) {{
            .dashboard-header h1 {{
                font-size: 2em;
            }}
            .stats-grid {{
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            }}
        }}
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1>Employee Simulation Dashboard</h1>
        <div class="subtitle">Interactive Analysis & Story Exploration</div>
    </div>

    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{len(population_data):,}</div>
            <div class="stat-label">Total Employees</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{total_tracked:,}</div>
            <div class="stat-label">Tracked Stories</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(df['level'].unique())}</div>
            <div class="stat-label">Career Levels</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">£{df['salary'].median():,.0f}</div>
            <div class="stat-label">Median Salary</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(tracked_employees) if tracked_employees else 0}</div>
            <div class="stat-label">Story Categories</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(components)}</div>
            <div class="stat-label">Interactive Components</div>
        </div>
    </div>

    {''.join(plots_html)}

    <div class="footer">
        <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Employee Simulation Dashboard v1.0</p>
        <p>🤖 Generated with Enhanced Employee Simulator</p>
    </div>
</body>
</html>"""

    def get_dashboard_metadata(self) -> Dict[str, Any]:
        """Get metadata about generated dashboard components."""
        return {
            "components_available": list(self.dashboard_components.keys()),
            "layout_config": self.layout_config,
            "generation_timestamp": datetime.now().isoformat(),
            "version": "1.0",
        }

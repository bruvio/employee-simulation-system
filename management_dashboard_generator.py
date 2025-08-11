#!/usr/bin/env python3
"""Management Dashboard Generator for Employee Simulation System.

Transforms technical analysis results into executive-friendly visualizations and dashboards.
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import webbrowser
import pandas as pd
import plotly.graph_objects as go
import plotly.offline as pyo
from plotly.subplots import make_subplots

from smart_logging_manager import get_smart_logger


class ManagementDashboardGenerator:
    """Generates executive-friendly management dashboards from technical analysis results.

    Transforms complex salary equity analysis into actionable visual insights for non-technical stakeholders and
    management decision-making.
    """

    def __init__(
        self, analysis_results: Dict[str, Any], population_data: List[Dict], config: Dict[str, Any], smart_logger=None
    ):
        """Initialize management dashboard generator.

        Args:
            analysis_results: Results from advanced analysis pipeline
            population_data: Employee population data
            config: Configuration settings
            smart_logger: Smart logging manager instance
        """
        self.analysis_results = analysis_results
        self.population_data = population_data
        self.config = config
        self.logger = smart_logger or get_smart_logger()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Dashboard styling configuration
        self.theme_config = {
            "executive": {
                "color_scheme": ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"],
                "font_family": "Arial, sans-serif",
                "background_color": "#ffffff",
                "grid_color": "#e6e6e6",
                "title_size": 18,
                "axis_size": 12,
            }
        }

        # Get current theme
        self.theme = self.theme_config.get("executive")

        self.logger.log_info("Initialized ManagementDashboardGenerator for executive reporting")

    def generate_executive_dashboard(self) -> Dict[str, str]:
        """Generate comprehensive executive dashboard with all management components.

        Returns:
            Dictionary containing paths to generated dashboard files
        """
        self.logger.log_info("🎯 Generating executive management dashboard")

        dashboard_components = {}

        try:
            # 1. Executive Summary Panel
            executive_summary = self._create_executive_summary()
            dashboard_components["executive_summary"] = executive_summary

            # 2. Salary Equity Overview
            equity_overview = self._create_salary_equity_overview()
            dashboard_components["equity_overview"] = equity_overview

            # 3. Gap Analysis Visualization
            gap_analysis_chart = self._create_gap_analysis_chart()
            dashboard_components["gap_analysis"] = gap_analysis_chart

            # 4. Intervention Impact Simulator
            intervention_simulator = self._create_intervention_simulator()
            dashboard_components["intervention_simulator"] = intervention_simulator

            # 5. Action Priority Matrix
            action_matrix = self._create_action_priority_matrix()
            dashboard_components["action_matrix"] = action_matrix

            # 6. Risk Assessment Panel
            risk_assessment = self._create_risk_assessment()
            dashboard_components["risk_assessment"] = risk_assessment

            # Assemble complete dashboard
            dashboard_files = self._assemble_dashboard(dashboard_components)

            self.logger.log_success(f"✅ Executive dashboard generated: {len(dashboard_components)} components")
            return dashboard_files

        except Exception as e:
            self.logger.log_error(f"Failed to generate executive dashboard: {e}")
            raise

    def _create_executive_summary(self) -> Dict[str, Any]:
        """Create executive summary panel with key insights and metrics."""

        df = pd.DataFrame(self.population_data)

        # Calculate key metrics
        total_employees = len(df)

        # Gender pay gap calculation
        male_median = df[df["gender"] == "Male"]["salary"].median()
        female_median = df[df["gender"] == "Female"]["salary"].median()
        gender_gap = ((male_median - female_median) / male_median) * 100

        # Below median employees
        level_medians = df.groupby("level")["salary"].median()
        below_median_count = 0
        for _, emp in df.iterrows():
            if emp["salary"] < level_medians[emp["level"]]:
                below_median_count += 1
        below_median_percent = (below_median_count / total_employees) * 100

        # Risk assessment
        if gender_gap > 20:
            risk_level = "HIGH"
            risk_color = "#d62728"
        elif gender_gap > 10:
            risk_level = "MEDIUM"
            risk_color = "#ff7f0e"
        else:
            risk_level = "LOW"
            risk_color = "#2ca02c"

        # Get intervention cost from analysis results
        intervention_results = self.analysis_results.get("analysis_results", {}).get("intervention_strategies", {})
        equity_analysis = intervention_results.get("equity_analysis", {})
        estimated_cost = equity_analysis.get("optimal_approach", {}).get("total_investment", 0)

        summary = {
            "key_metrics": {
                "total_employees": total_employees,
                "gender_gap_percent": f"{gender_gap:.1f}%",
                "employees_below_median": f"{below_median_count} ({below_median_percent:.1f}%)",
                "estimated_remediation_cost": f"£{estimated_cost:,.0f}",
                "regulatory_risk_level": risk_level,
                "risk_color": risk_color,
            },
            "key_insights": [
                f"Found {below_median_count} employees ({below_median_percent:.1f}%) earning below median for their level",
                f"Gender pay gap of {gender_gap:.1f}% requires {'immediate' if gender_gap > 15 else 'management'} attention",
                f"Estimated £{estimated_cost:,.0f} investment needed for comprehensive equity improvement",
            ],
            "recommended_actions": [
                f"Immediate review of {min(below_median_count, 15)} highest-priority cases (>20% below median)",
                "Implement structured salary review process for affected employees",
                f"Budget £{estimated_cost:,.0f} for {'immediate' if gender_gap > 15 else 'gradual'} remediation strategy",
            ],
        }

        return summary

    def _create_salary_equity_overview(self) -> Dict[str, Any]:
        """Create salary equity overview with visual KPIs."""

        df = pd.DataFrame(self.population_data)

        # Create KPI visualization
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=[
                "Gender Pay Gap",
                "Employees Below Median",
                "Salary Distribution by Level",
                "Risk Assessment",
            ],
            specs=[[{"type": "indicator"}, {"type": "indicator"}], [{"type": "bar"}, {"type": "indicator"}]],
        )

        # Gender pay gap indicator
        male_median = df[df["gender"] == "Male"]["salary"].median()
        female_median = df[df["gender"] == "Female"]["salary"].median()
        gender_gap = ((male_median - female_median) / male_median) * 100

        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=gender_gap,
                title={"text": "Gender Pay Gap %"},
                gauge={
                    "axis": {"range": [None, 30]},
                    "bar": {"color": "#d62728" if gender_gap > 15 else "#ff7f0e"},
                    "steps": [{"range": [0, 5], "color": "#2ca02c"}, {"range": [5, 15], "color": "#ff7f0e"}],
                    "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": 15},
                },
            ),
            row=1,
            col=1,
        )

        # Below median employees
        level_medians = df.groupby("level")["salary"].median()
        below_median_count = sum(1 for _, emp in df.iterrows() if emp["salary"] < level_medians[emp["level"]])
        below_median_percent = (below_median_count / len(df)) * 100

        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=below_median_percent,
                title={"text": "% Below Median"},
                number={"suffix": "%"},
                delta={"reference": 25, "valueformat": ".1f"},
            ),
            row=1,
            col=2,
        )

        # Salary distribution by level
        level_stats = df.groupby("level")["salary"].agg(["mean", "median"]).reset_index()

        fig.add_trace(
            go.Bar(
                x=level_stats["level"],
                y=level_stats["median"],
                name="Median Salary",
                marker_color=self.theme["color_scheme"][0],
            ),
            row=2,
            col=1,
        )

        # Risk assessment indicator
        risk_score = min(100, gender_gap * 3 + (below_median_percent * 2))

        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=risk_score,
                title={"text": "Overall Risk Score"},
                gauge={
                    "axis": {"range": [None, 100]},
                    "bar": {"color": "#d62728" if risk_score > 60 else "#ff7f0e" if risk_score > 30 else "#2ca02c"},
                    "steps": [{"range": [0, 30], "color": "#2ca02c"}, {"range": [30, 60], "color": "#ff7f0e"}],
                },
            ),
            row=2,
            col=2,
        )

        fig.update_layout(
            title="Salary Equity Overview - Key Performance Indicators",
            height=600,
            font=dict(family=self.theme["font_family"]),
        )

        return {
            "chart": fig,
            "summary_stats": {
                "gender_gap": gender_gap,
                "below_median_percent": below_median_percent,
                "risk_score": risk_score,
                "total_employees": len(df),
            },
        }

    def _create_gap_analysis_chart(self) -> Dict[str, Any]:
        """Create comprehensive gap analysis visualization."""

        df = pd.DataFrame(self.population_data)

        # Create salary distribution comparison
        fig = go.Figure()

        # Gender salary distributions
        for i, gender in enumerate(df["gender"].unique()):
            gender_data = df[df["gender"] == gender]
            fig.add_trace(
                go.Histogram(
                    x=gender_data["salary"],
                    name=f"{gender} Employees",
                    opacity=0.7,
                    nbinsx=30,
                    marker_color=self.theme["color_scheme"][i],
                )
            )

        # Add median lines
        male_median = df[df["gender"] == "Male"]["salary"].median()
        female_median = df[df["gender"] == "Female"]["salary"].median()

        fig.add_vline(
            x=male_median,
            line_dash="dash",
            line_color=self.theme["color_scheme"][0],
            annotation_text=f"Male Median: £{male_median:,.0f}",
        )
        fig.add_vline(
            x=female_median,
            line_dash="dash",
            line_color=self.theme["color_scheme"][1],
            annotation_text=f"Female Median: £{female_median:,.0f}",
        )

        fig.update_layout(
            title="Salary Distribution by Gender - Identifying Pay Gaps",
            xaxis_title="Salary (£)",
            yaxis_title="Number of Employees",
            barmode="overlay",
            showlegend=True,
            height=500,
            font=dict(family=self.theme["font_family"]),
        )

        # Calculate gap statistics
        gap_amount = male_median - female_median
        gap_percent = (gap_amount / male_median) * 100

        return {
            "chart": fig,
            "gap_analysis": {
                "male_median": male_median,
                "female_median": female_median,
                "gap_amount": gap_amount,
                "gap_percent": gap_percent,
                "interpretation": f"Male employees earn £{gap_amount:,.0f} ({gap_percent:.1f}%) more on average",
            },
        }

    def _create_intervention_simulator(self) -> Dict[str, Any]:
        """Create intervention strategy cost-benefit simulator."""

        # Get intervention analysis results
        # intervention_results = self.analysis_results.get("analysis_results", {}).get("intervention_strategies", {})
        # gender_gap_data = intervention_results.get("gender_gap_remediation", {})

        # Create intervention comparison chart
        strategies = ["No Action", "Gradual (3-year)", "Accelerated (1-year)", "Comprehensive"]
        costs = [0, 30000, 60000, 90000]  # Example costs
        timelines = [0, 36, 12, 6]  # Months to close gap
        risk_reduction = [0, 40, 70, 90]  # % risk reduction

        fig = make_subplots(
            rows=1,
            cols=3,
            subplot_titles=["Implementation Cost", "Timeline to Results", "Risk Reduction"],
            specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]],
        )

        # Cost comparison
        fig.add_trace(
            go.Bar(x=strategies, y=costs, name="Cost (£)", marker_color=self.theme["color_scheme"][0]), row=1, col=1
        )

        # Timeline comparison
        fig.add_trace(
            go.Bar(x=strategies, y=timelines, name="Months", marker_color=self.theme["color_scheme"][1]), row=1, col=2
        )

        # Risk reduction
        fig.add_trace(
            go.Bar(x=strategies, y=risk_reduction, name="Risk Reduction %", marker_color=self.theme["color_scheme"][2]),
            row=1,
            col=3,
        )

        fig.update_layout(
            title="Intervention Strategy Comparison - Cost vs. Impact Analysis",
            height=400,
            font=dict(family=self.theme["font_family"]),
            showlegend=False,
        )

        return {
            "chart": fig,
            "recommendations": {
                "preferred_strategy": "Gradual (3-year)",
                "rationale": "Optimal balance of cost-effectiveness and timeline",
                "estimated_cost": "£30,000",
                "expected_timeline": "36 months",
                "risk_mitigation": "40% reduction in compliance risk",
            },
        }

    def _create_action_priority_matrix(self) -> Dict[str, Any]:
        """Create action priority matrix with recommended next steps."""

        df = pd.DataFrame(self.population_data)

        # Identify high-priority employees (>20% below median)
        level_medians = df.groupby("level")["salary"].median()
        high_priority_employees = []

        for _, emp in df.iterrows():
            level_median = level_medians[emp["level"]]
            gap_percent = ((level_median - emp["salary"]) / level_median) * 100

            if gap_percent > 20:  # More than 20% below median
                high_priority_employees.append(
                    {
                        "employee_id": emp["employee_id"],
                        "level": emp["level"],
                        "salary": emp["salary"],
                        "median": level_median,
                        "gap_percent": gap_percent,
                        "gap_amount": level_median - emp["salary"],
                    }
                )

        # Sort by gap size
        high_priority_employees.sort(key=lambda x: x["gap_percent"], reverse=True)

        # Create priority matrix visualization
        if high_priority_employees:
            top_priorities = high_priority_employees[:10]  # Top 10 cases

            fig = go.Figure()

            fig.add_trace(
                go.Scatter(
                    x=[emp["gap_percent"] for emp in top_priorities],
                    y=[emp["gap_amount"] for emp in top_priorities],
                    mode="markers",
                    marker=dict(size=[15] * len(top_priorities), color=self.theme["color_scheme"][0], opacity=0.7),
                    text=[
                        f"Employee {emp['employee_id']}<br>Level {emp['level']}<br>Gap: £{emp['gap_amount']:,.0f}"
                        for emp in top_priorities
                    ],
                    hovertemplate="<b>%{text}</b><br>Gap: %{x:.1f}%<br>Amount: £%{y:,.0f}<extra></extra>",
                )
            )

            fig.update_layout(
                title="High-Priority Cases Requiring Immediate Attention",
                xaxis_title="Gap Percentage (%)",
                yaxis_title="Gap Amount (£)",
                height=400,
                font=dict(family=self.theme["font_family"]),
            )
        else:
            # No high-priority cases
            fig = go.Figure()
            fig.add_annotation(
                text="No employees identified with >20% salary gap<br>System operating within acceptable parameters",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=16, color="green"),
            )
            fig.update_layout(
                title="Priority Analysis - No Critical Issues Identified",
                height=400,
                font=dict(family=self.theme["font_family"]),
            )

        return {
            "chart": fig,
            "priority_actions": [
                f"Review {len(high_priority_employees)} employees with >20% salary gap",
                "Conduct salary benchmarking for affected positions",
                "Prepare business case for salary adjustments",
                "Schedule management review meetings for top 5 priority cases",
            ],
            "high_priority_count": len(high_priority_employees),
            "estimated_cost": sum(emp["gap_amount"] * 0.5 for emp in high_priority_employees),  # 50% gap closure
        }

    def _create_risk_assessment(self) -> Dict[str, Any]:
        """Create risk assessment panel with compliance indicators."""

        df = pd.DataFrame(self.population_data)

        # Calculate various risk factors
        male_median = df[df["gender"] == "Male"]["salary"].median()
        female_median = df[df["gender"] == "Female"]["salary"].median()
        gender_gap = ((male_median - female_median) / male_median) * 100

        # Risk assessment scoring
        risks = {
            "Legal Compliance Risk": {
                "score": min(100, gender_gap * 4),  # Gender gap drives legal risk
                "level": "HIGH" if gender_gap > 15 else "MEDIUM" if gender_gap > 8 else "LOW",
                "description": f"{gender_gap:.1f}% gender pay gap may trigger regulatory scrutiny",
            },
            "Employee Retention Risk": {
                "score": min(
                    100,
                    (len(df[df["performance_rating"].isin(["High Performing", "Exceeding"])]) / len(df)) * gender_gap,
                ),
                "level": "MEDIUM" if gender_gap > 12 else "LOW",
                "description": "High-performing employees may seek opportunities elsewhere",
            },
            "Reputation Risk": {
                "score": min(100, gender_gap * 2.5),
                "level": "HIGH" if gender_gap > 18 else "MEDIUM" if gender_gap > 10 else "LOW",
                "description": "Public disclosure of pay gaps could impact employer brand",
            },
            "Productivity Risk": {
                "score": min(100, gender_gap * 1.5),
                "level": "MEDIUM" if gender_gap > 15 else "LOW",
                "description": "Pay inequality may reduce employee engagement and productivity",
            },
        }

        # Create risk dashboard
        risk_names = list(risks.keys())
        risk_scores = [risks[name]["score"] for name in risk_names]
        risk_colors = [
            "#d62728"
            if risks[name]["level"] == "HIGH"
            else "#ff7f0e"
            if risks[name]["level"] == "MEDIUM"
            else "#2ca02c"
            for name in risk_names
        ]

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                y=risk_names,
                x=risk_scores,
                orientation="h",
                marker_color=risk_colors,
                text=[f"{score:.0f}% - {risks[name]['level']}" for name, score in zip(risk_names, risk_scores)],
                textposition="inside",
            )
        )

        fig.update_layout(
            title="Risk Assessment Dashboard - Compliance & Business Impact",
            xaxis_title="Risk Score (0-100)",
            height=400,
            font=dict(family=self.theme["font_family"]),
        )

        return {
            "chart": fig,
            "risk_summary": risks,
            "overall_risk_level": "HIGH"
            if any(risks[r]["level"] == "HIGH" for r in risks)
            else "MEDIUM"
            if any(risks[r]["level"] == "MEDIUM" for r in risks)
            else "LOW",
        }

    def _assemble_dashboard(self, components: Dict[str, Any]) -> Dict[str, str]:
        """Assemble all components into a cohesive HTML dashboard."""

        # Create dashboard HTML
        html_content = self._create_dashboard_html(components)

        # Save dashboard file
        dashboard_dir = Path("artifacts/advanced_analysis")
        dashboard_dir.mkdir(parents=True, exist_ok=True)

        dashboard_file = dashboard_dir / f"management_dashboard_{self.timestamp}.html"

        with open(dashboard_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Save individual chart files
        chart_files = {}
        charts_dir = dashboard_dir / "charts"
        charts_dir.mkdir(exist_ok=True)

        for component_name, component_data in components.items():
            if "chart" in component_data:
                chart_file = charts_dir / f"{component_name}_{self.timestamp}.html"
                pyo.plot(component_data["chart"], filename=str(chart_file), auto_open=False)
                chart_files[component_name] = str(chart_file)

        # Auto-open dashboard if configured
        if self.config.get("auto_open_dashboard", True):
            self.logger.log_info("🌐 Opening executive dashboard in browser...")
            webbrowser.open(f"file://{dashboard_file.absolute()}")

        return {
            "main_dashboard": str(dashboard_file),
            "individual_charts": chart_files,
            "components_generated": len(components),
        }

    def _create_dashboard_html(self, components: Dict[str, Any]) -> str:
        """Create comprehensive HTML dashboard with all components."""

        executive_summary = components.get("executive_summary", {})

        html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Executive Salary Equity Dashboard - {self.timestamp}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: {self.theme['font_family']};
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .dashboard-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            text-align: center;
        }}
        .dashboard-header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .dashboard-header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.2em;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .metric-label {{
            color: #666;
            margin-top: 5px;
        }}
        .risk-high {{ color: #d62728; }}
        .risk-medium {{ color: #ff7f0e; }}
        .risk-low {{ color: #2ca02c; }}
        .chart-container {{
            background: white;
            margin-bottom: 30px;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .insights-panel {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
        }}
        .insights-panel h3 {{
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .insight-item {{
            margin: 15px 0;
            padding: 15px;
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            border-radius: 0 5px 5px 0;
        }}
        .action-item {{
            margin: 10px 0;
            padding: 12px;
            background: #e8f4fd;
            border-left: 4px solid #1f77b4;
            border-radius: 0 5px 5px 0;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 50px;
            padding: 20px;
            border-top: 1px solid #ddd;
        }}
    </style>
</head>
<body>
    <div class="dashboard-header">
        <h1>📊 Executive Salary Equity Dashboard</h1>
        <p>Comprehensive Analysis & Management Recommendations</p>
        <p style="font-size: 0.9em; opacity: 0.8;">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
    </div>
    
    <!-- Key Metrics Overview -->
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value">{executive_summary.get('key_metrics', {}).get('total_employees', 'N/A')}</div>
            <div class="metric-label">Total Employees</div>
        </div>
        <div class="metric-card">
            <div class="metric-value risk-{executive_summary.get('key_metrics', {}).get('regulatory_risk_level', 'low').lower()}">{executive_summary.get('key_metrics', {}).get('gender_gap_percent', 'N/A')}</div>
            <div class="metric-label">Gender Pay Gap</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{executive_summary.get('key_metrics', {}).get('employees_below_median', 'N/A')}</div>
            <div class="metric-label">Below Median Salary</div>
        </div>
        <div class="metric-card">
            <div class="metric-value">{executive_summary.get('key_metrics', {}).get('estimated_remediation_cost', 'N/A')}</div>
            <div class="metric-label">Remediation Cost</div>
        </div>
    </div>
    
    <!-- Executive Insights -->
    <div class="insights-panel">
        <h3>🎯 Key Insights</h3>
        {''.join(f'<div class="insight-item">💡 {insight}</div>' for insight in executive_summary.get('key_insights', []))}
    </div>
    
    <!-- Recommended Actions -->
    <div class="insights-panel">
        <h3>⚡ Immediate Action Items</h3>
        {''.join(f'<div class="action-item">🔸 {action}</div>' for action in executive_summary.get('recommended_actions', []))}
    </div>
    
    <!-- Charts will be embedded here -->
    <div id="salary-equity-overview" class="chart-container"></div>
    <div id="gap-analysis" class="chart-container"></div>
    <div id="intervention-simulator" class="chart-container"></div>
    <div id="action-priority" class="chart-container"></div>
    <div id="risk-assessment" class="chart-container"></div>
    
    <div class="footer">
        <p>
  🤖
  <a href="https://github.com/bruvio/employee-simulation-system" target="_blank" rel="noopener noreferrer">
    Generated by Employee Simulation System Advanced Analytics by bruvio
  </a>
  🔗
</p>
        <p>For technical details and raw data, see the artifacts/advanced_analysis/ directory</p>
    </div>
    
    <script>
        // Embed Plotly charts
        {self._generate_chart_embeddings(components)}
    </script>
</body>
</html>
"""
        return html_template

    def _generate_chart_embeddings(self, components: Dict[str, Any]) -> str:
        """Generate JavaScript code to embed Plotly charts in dashboard."""

        embeddings = []

        chart_mappings = {
            "equity_overview": "salary-equity-overview",
            "gap_analysis": "gap-analysis",
            "intervention_simulator": "intervention-simulator",
            "action_matrix": "action-priority",
            "risk_assessment": "risk-assessment",
        }

        for component_key, div_id in chart_mappings.items():
            if component_key in components and "chart" in components[component_key]:
                chart_json = components[component_key]["chart"].to_json()
                embeddings.append(
                    f"""
                    var chart_{component_key} = {chart_json};
                    Plotly.newPlot('{div_id}', chart_{component_key}.data, chart_{component_key}.layout);
                """
                )

        return "\n".join(embeddings)

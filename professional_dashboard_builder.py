#!/usr/bin/env python3
"""
Professional Dashboard Builder for Employee Simulation System

Creates comprehensive, interactive dashboards with scenario overview,
KPIs, visualizations, and file browser for all generated outputs.
"""

import base64
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import mimetypes

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from logger import LOGGER


class ProfessionalDashboardBuilder:
    """Creates professional, comprehensive dashboards for simulation results."""

    def __init__(self, output_dir: Union[str, Path] = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = LOGGER

    def build_comprehensive_dashboard(
        self,
        analysis_payload: Dict[str, Any],
        manifest: Dict[str, Any],
        run_directory: Path,
        scenario_config: Dict[str, Any],
        output_file: str = "professional_dashboard.html",
    ) -> Path:
        """Build comprehensive professional dashboard.

        Args:
            analysis_payload: Complete analysis results from orchestrator
            manifest: Run manifest with metadata and KPIs
            run_directory: Path to run directory with all generated files
            scenario_config: Scenario configuration details
            output_file: Output filename

        Returns:
            Path to generated dashboard HTML file
        """
        self.logger.info("Building professional comprehensive dashboard")

        dashboard_path = run_directory / output_file

        # Collect all generated files
        generated_files = self._discover_generated_files(run_directory)

        # Extract key metrics
        key_metrics = self._extract_key_metrics(analysis_payload, manifest)

        # Generate interactive charts
        charts = self._generate_interactive_charts(analysis_payload, generated_files)

        # Build HTML dashboard
        html_content = self._build_dashboard_html(
            analysis_payload, manifest, scenario_config, key_metrics, charts, generated_files
        )

        with open(dashboard_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        self.logger.info(f"Generated professional dashboard: {dashboard_path}")
        return dashboard_path

    def _discover_generated_files(self, run_directory: Path) -> Dict[str, List[Dict[str, Any]]]:
        """Discover all generated files and organize by type."""
        files = {"visualizations": [], "data_exports": [], "reports": [], "analysis": [], "other": []}

        for file_path in run_directory.rglob("*"):
            if file_path.is_file():
                file_info = {
                    "name": file_path.name,
                    "path": str(file_path.relative_to(run_directory)),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime),
                    "type": file_path.suffix.lower(),
                }

                # Categorize files
                if (
                    file_path.suffix.lower() in [".png", ".svg", ".jpg", ".jpeg", ".html"]
                    and "chart" in file_path.name.lower()
                ):
                    files["visualizations"].append(file_info)
                elif file_path.suffix.lower() in [".csv", ".json", ".xlsx"]:
                    if "analysis" in file_path.name.lower() or "advanced" in file_path.name.lower():
                        files["analysis"].append(file_info)
                    else:
                        files["data_exports"].append(file_info)
                elif file_path.suffix.lower() in [".md", ".txt"] or "report" in file_path.name.lower():
                    files["reports"].append(file_info)
                else:
                    files["other"].append(file_info)

        return files

    def _extract_key_metrics(self, analysis_payload: Dict[str, Any], manifest: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key performance indicators and metrics."""
        population_data = analysis_payload.get("population_data", [])

        metrics = {
            "population_size": len(population_data),
            "median_salary": manifest.get("median_salary", 0),
            "gender_gap_pct": manifest.get("gender_gap_pct", 0),
            "below_median_pct": manifest.get("below_median_pct", 0),
            "intervention_budget_pct": manifest.get("intervention_budget_pct", 0),
            "scenario": manifest.get("scenario", "Unknown"),
            "org": manifest.get("org", "Unknown"),
            "timestamp": manifest.get("timestamp_utc", datetime.utcnow().isoformat()),
            "currency": manifest.get("currency", "GBP"),
        }

        # Calculate additional metrics if population data available
        if population_data:
            df = pd.DataFrame(population_data)

            # Level distribution
            level_dist = df["level"].value_counts().sort_index()
            metrics["level_distribution"] = level_dist.to_dict()

            # Gender distribution
            gender_dist = df["gender"].value_counts()
            metrics["gender_distribution"] = gender_dist.to_dict()

            # Performance distribution
            if "performance_rating" in df.columns:
                perf_dist = df["performance_rating"].value_counts()
                metrics["performance_distribution"] = perf_dist.to_dict()

            # Salary statistics
            metrics["salary_stats"] = {
                "min": df["salary"].min(),
                "max": df["salary"].max(),
                "mean": df["salary"].mean(),
                "std": df["salary"].std(),
            }

        return metrics

    def _generate_interactive_charts(
        self, analysis_payload: Dict[str, Any], generated_files: Dict[str, List]
    ) -> Dict[str, str]:
        """Generate interactive Plotly charts."""
        charts = {}
        population_data = analysis_payload.get("population_data", [])

        if not population_data:
            return charts

        df = pd.DataFrame(population_data)

        # 1. Population Overview Chart
        fig_pop = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=["Level Distribution", "Gender Distribution", "Salary by Level", "Performance Distribution"],
            specs=[[{"type": "bar"}, {"type": "pie"}], [{"type": "box"}, {"type": "bar"}]],
        )

        # Level distribution
        level_counts = df["level"].value_counts().sort_index()
        fig_pop.add_trace(
            go.Bar(x=[f"Level {i}" for i in level_counts.index], y=level_counts.values, name="Employees"), row=1, col=1
        )

        # Gender distribution
        gender_counts = df["gender"].value_counts()
        fig_pop.add_trace(go.Pie(labels=gender_counts.index, values=gender_counts.values, name="Gender"), row=1, col=2)

        # Salary by level
        for level in sorted(df["level"].unique()):
            level_data = df[df["level"] == level]["salary"]
            fig_pop.add_trace(go.Box(y=level_data, name=f"L{level}", showlegend=False), row=2, col=1)

        # Performance distribution
        if "performance_rating" in df.columns:
            perf_counts = df["performance_rating"].value_counts()
            fig_pop.add_trace(
                go.Bar(x=perf_counts.index, y=perf_counts.values, name="Count", showlegend=False), row=2, col=2
            )

        fig_pop.update_layout(height=600, title_text="Population Overview Dashboard")
        charts["population_overview"] = fig_pop.to_html(include_plotlyjs=False, div_id="population_overview")

        # 2. Gender Pay Gap Analysis
        if len(df["gender"].unique()) > 1:
            fig_gap = go.Figure()

            for gender in df["gender"].unique():
                gender_data = df[df["gender"] == gender]
                fig_gap.add_trace(go.Box(y=gender_data["salary"], name=gender, boxpoints="outliers"))

            fig_gap.update_layout(title="Gender Pay Gap Analysis", yaxis_title="Salary (£)", height=400)
            charts["gender_gap"] = fig_gap.to_html(include_plotlyjs=False, div_id="gender_gap")

        # 3. Salary Distribution by Level
        fig_salary = px.violin(
            df,
            x="level",
            y="salary",
            color="gender",
            title="Salary Distribution by Level and Gender",
            labels={"level": "Level", "salary": "Salary (£)"},
        )
        fig_salary.update_layout(height=400)
        charts["salary_distribution"] = fig_salary.to_html(include_plotlyjs=False, div_id="salary_distribution")

        return charts

    def _build_dashboard_html(
        self,
        analysis_payload: Dict[str, Any],
        manifest: Dict[str, Any],
        scenario_config: Dict[str, Any],
        key_metrics: Dict[str, Any],
        charts: Dict[str, str],
        generated_files: Dict[str, List],
    ) -> str:
        """Build the complete HTML dashboard."""
        org = key_metrics.get("org", "Unknown")
        scenario = key_metrics.get("scenario", "Unknown")
        timestamp = datetime.fromisoformat(
            key_metrics.get("timestamp", datetime.utcnow().isoformat()).replace("Z", "+00:00")
        )

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{org} - {scenario} Scenario Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    {self._get_dashboard_styles()}
</head>
<body>
    <nav class="navbar navbar-dark bg-primary">
        <div class="container-fluid">
            <span class="navbar-brand mb-0 h1">
                <i class="fas fa-chart-line me-2"></i>
                {org} Employee Simulation Dashboard
            </span>
            <span class="badge bg-light text-dark fs-6">{scenario} Scenario</span>
        </div>
    </nav>

    <div class="container-fluid py-4">
        <!-- Scenario Overview Section -->
        {self._build_scenario_overview(key_metrics, scenario_config)}
        
        <!-- KPI Cards -->
        {self._build_kpi_cards(key_metrics)}
        
        <!-- Charts Section -->
        {self._build_charts_section(charts)}
        
        <!-- File Browser Section -->
        {self._build_file_browser(generated_files)}
        
        <!-- Analysis Summary -->
        {self._build_analysis_summary(analysis_payload, key_metrics)}
    </div>

    {self._get_dashboard_scripts()}
</body>
</html>"""

    def _get_dashboard_styles(self) -> str:
        """Get custom CSS styles for the dashboard."""
        return """
    <style>
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 15px;
            padding: 1.5rem;
            height: 120px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
        }
        
        .metric-value {
            font-size: 2rem;
            font-weight: bold;
        }
        
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        .chart-container {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        
        .file-item {
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 1rem;
            margin-bottom: 0.5rem;
            border-radius: 0 8px 8px 0;
            transition: all 0.3s ease;
        }
        
        .file-item:hover {
            background: #e9ecef;
            border-left-color: #0056b3;
        }
        
        .scenario-header {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
        }
        
        .status-badge {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        
        .status-success {
            background-color: #d4edda;
            color: #155724;
        }
        
        .status-warning {
            background-color: #fff3cd;
            color: #856404;
        }
        
        .status-danger {
            background-color: #f8d7da;
            color: #721c24;
        }
    </style>"""

    def _build_scenario_overview(self, key_metrics: Dict[str, Any], scenario_config: Dict[str, Any]) -> str:
        """Build scenario overview section."""
        org = key_metrics.get("org", "Unknown")
        scenario = key_metrics.get("scenario", "Unknown")
        timestamp = key_metrics.get("timestamp", "")

        return f"""
        <div class="scenario-header">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1 class="display-6 mb-2">
                        <i class="fas fa-building me-3"></i>
                        {org} Organization Analysis
                    </h1>
                    <p class="lead mb-0">
                        Comprehensive employee simulation analysis for the {scenario} scenario
                    </p>
                    <small class="opacity-75">
                        <i class="far fa-clock me-1"></i>
                        Generated on {datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime('%B %d, %Y at %I:%M %p')}
                    </small>
                </div>
                <div class="col-md-4 text-end">
                    <div class="d-flex flex-column align-items-end">
                        <span class="status-badge status-success mb-2">
                            <i class="fas fa-check-circle me-1"></i>
                            Analysis Complete
                        </span>
                        <span class="badge bg-light text-dark fs-6">
                            Population: {key_metrics.get('population_size', 0):,} employees
                        </span>
                    </div>
                </div>
            </div>
        </div>"""

    def _build_kpi_cards(self, key_metrics: Dict[str, Any]) -> str:
        """Build KPI cards section."""
        currency = key_metrics.get("currency", "GBP")
        currency_symbol = "£" if currency == "GBP" else "$"

        def get_status_class(value, good_threshold, warning_threshold):
            if value <= good_threshold:
                return "status-success"
            elif value <= warning_threshold:
                return "status-warning"
            else:
                return "status-danger"

        gender_gap_status = get_status_class(key_metrics.get("gender_gap_pct", 0), 5, 10)
        below_median_status = get_status_class(key_metrics.get("below_median_pct", 0), 25, 40)

        return f"""
        <div class="row mb-4">
            <div class="col-md-3 mb-3">
                <div class="metric-card">
                    <div>
                        <div class="metric-value">{currency_symbol}{key_metrics.get('median_salary', 0):,.0f}</div>
                        <div class="metric-label">Median Salary</div>
                    </div>
                    <i class="fas fa-pound-sign fa-2x opacity-75"></i>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="metric-card">
                    <div>
                        <div class="metric-value">{key_metrics.get('gender_gap_pct', 0):.1f}%</div>
                        <div class="metric-label">Gender Pay Gap</div>
                        <span class="status-badge {gender_gap_status} mt-1">
                            {'Good' if gender_gap_status == 'status-success' else 'Needs Attention' if gender_gap_status == 'status-warning' else 'Critical'}
                        </span>
                    </div>
                    <i class="fas fa-venus-mars fa-2x opacity-75"></i>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="metric-card">
                    <div>
                        <div class="metric-value">{key_metrics.get('below_median_pct', 0):.1f}%</div>
                        <div class="metric-label">Below Median</div>
                        <span class="status-badge {below_median_status} mt-1">
                            {'Good' if below_median_status == 'status-success' else 'Moderate' if below_median_status == 'status-warning' else 'High Risk'}
                        </span>
                    </div>
                    <i class="fas fa-chart-line fa-2x opacity-75"></i>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="metric-card">
                    <div>
                        <div class="metric-value">{key_metrics.get('intervention_budget_pct', 0):.1f}%</div>
                        <div class="metric-label">Budget Allocation</div>
                    </div>
                    <i class="fas fa-wallet fa-2x opacity-75"></i>
                </div>
            </div>
        </div>"""

    def _build_charts_section(self, charts: Dict[str, str]) -> str:
        """Build interactive charts section."""
        if not charts:
            return "<div class='alert alert-info'>No charts available for this analysis.</div>"

        section = """
        <div class="row mb-4">
            <div class="col-12">
                <h2 class="mb-3">
                    <i class="fas fa-chart-bar me-2"></i>
                    Interactive Analysis
                </h2>
            </div>
        </div>"""

        for chart_name, chart_html in charts.items():
            section += f"""
            <div class="chart-container">
                <h4 class="mb-3">{chart_name.replace('_', ' ').title()}</h4>
                {chart_html}
            </div>"""

        return section

    def _build_file_browser(self, generated_files: Dict[str, List]) -> str:
        """Build file browser section."""

        def format_file_size(size_bytes):
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024**2:
                return f"{size_bytes/1024:.1f} KB"
            else:
                return f"{size_bytes/(1024**2):.1f} MB"

        def get_file_icon(file_type):
            icons = {
                ".png": "fas fa-image text-success",
                ".jpg": "fas fa-image text-success",
                ".jpeg": "fas fa-image text-success",
                ".svg": "fas fa-image text-success",
                ".html": "fab fa-html5 text-danger",
                ".csv": "fas fa-table text-info",
                ".json": "fas fa-code text-warning",
                ".xlsx": "fas fa-file-excel text-success",
                ".md": "fab fa-markdown text-primary",
                ".txt": "fas fa-file-alt text-secondary",
            }
            return icons.get(file_type, "fas fa-file text-muted")

        section = """
        <div class="row mb-4">
            <div class="col-12">
                <h2 class="mb-3">
                    <i class="fas fa-folder-open me-2"></i>
                    Generated Files & Resources
                </h2>
            </div>
        </div>
        
        <div class="row">"""

        for category, files in generated_files.items():
            if files:  # Only show categories that have files
                section += f"""
                <div class="col-lg-6 mb-4">
                    <div class="card">
                        <div class="card-header bg-primary text-white">
                            <h5 class="mb-0">
                                <i class="fas fa-folder me-2"></i>
                                {category.replace('_', ' ').title()} ({len(files)} files)
                            </h5>
                        </div>
                        <div class="card-body p-0">"""

                for file_info in files[:10]:  # Limit to first 10 files per category
                    section += f"""
                            <div class="file-item">
                                <div class="d-flex justify-content-between align-items-center">
                                    <div class="d-flex align-items-center">
                                        <i class="{get_file_icon(file_info['type'])} me-3"></i>
                                        <div>
                                            <div class="fw-bold">{file_info['name']}</div>
                                            <small class="text-muted">{file_info['path']}</small>
                                        </div>
                                    </div>
                                    <div class="text-end">
                                        <div class="fw-bold">{format_file_size(file_info['size'])}</div>
                                        <small class="text-muted">{file_info['modified'].strftime('%H:%M')}</small>
                                    </div>
                                </div>
                            </div>"""

                if len(files) > 10:
                    section += f"""
                            <div class="p-2 text-center text-muted">
                                <small>... and {len(files) - 10} more files</small>
                            </div>"""

                section += """
                        </div>
                    </div>
                </div>"""

        section += "</div>"
        return section

    def _build_analysis_summary(self, analysis_payload: Dict[str, Any], key_metrics: Dict[str, Any]) -> str:
        """Build analysis summary section."""
        return f"""
        <div class="row">
            <div class="col-12">
                <div class="card">
                    <div class="card-header bg-info text-white">
                        <h3 class="mb-0">
                            <i class="fas fa-clipboard-list me-2"></i>
                            Executive Summary
                        </h3>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-6">
                                <h5>Key Findings</h5>
                                <ul class="list-unstyled">
                                    <li class="mb-2">
                                        <i class="fas fa-users text-primary me-2"></i>
                                        Analyzed <strong>{key_metrics.get('population_size', 0):,} employees</strong> across 6 levels
                                    </li>
                                    <li class="mb-2">
                                        <i class="fas fa-chart-line text-success me-2"></i>
                                        Current median salary: <strong>£{key_metrics.get('median_salary', 0):,.0f}</strong>
                                    </li>
                                    <li class="mb-2">
                                        <i class="fas fa-exclamation-triangle text-warning me-2"></i>
                                        Gender pay gap: <strong>{key_metrics.get('gender_gap_pct', 0):.1f}%</strong>
                                    </li>
                                    <li class="mb-2">
                                        <i class="fas fa-arrow-down text-danger me-2"></i>
                                        Employees below median: <strong>{key_metrics.get('below_median_pct', 0):.1f}%</strong>
                                    </li>
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h5>Recommendations</h5>
                                <div class="alert alert-light">
                                    <ul class="mb-0">
                                        <li>Focus intervention efforts on gender pay gap reduction</li>
                                        <li>Review salary bands for employees below median</li>
                                        <li>Implement targeted performance improvement programs</li>
                                        <li>Monitor progress through regular simulation cycles</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>"""

    def _get_dashboard_scripts(self) -> str:
        """Get JavaScript for dashboard interactivity."""
        return """
    <script>
        // Add smooth scrolling
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
        
        // Add tooltips
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
        
        // File item click handlers
        document.querySelectorAll('.file-item').forEach(item => {
            item.addEventListener('click', function() {
                const fileName = this.querySelector('.fw-bold').textContent;
                const filePath = this.querySelector('.text-muted').textContent;
                alert(`File: ${fileName}\\nPath: ${filePath}`);
            });
        });
    </script>"""


if __name__ == "__main__":
    # Example usage
    builder = ProfessionalDashboardBuilder()
    print("Professional Dashboard Builder initialized")

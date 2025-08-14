#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

import base64
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.offline as offline
from plotly.subplots import make_subplots

from logger import LOGGER


class HTMLReportBuilder:
    """HTML report builder for GEL scenario single consolidated reports.
    
    Creates self-contained HTML files with embedded charts, tables, and styling.
    Follows the same narrative structure as the Markdown report.
    """
    
    def __init__(self, output_dir: Union[str, Path] = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = LOGGER
        
    def build_gel_report(
        self, 
        analysis_payload: Dict[str, Any], 
        manifest: Dict[str, Any],
        assets_dir: Optional[Path] = None,
        output_file: str = "index.html"
    ) -> Path:
        """Build comprehensive GEL scenario HTML report with embedded charts.
        
        Args:
            analysis_payload: Complete analysis results from orchestrator
            manifest: Run manifest with metadata and KPIs
            assets_dir: Optional assets directory for external chart references
            output_file: Output filename
            
        Returns:
            Path to generated HTML report file
        """
        self.logger.info("Building GEL scenario HTML report")
        
        report_path = self.output_dir / output_file
        
        # Generate embedded charts
        charts = self._generate_charts(analysis_payload, manifest, assets_dir)
        
        # Build HTML content
        html_content = self._build_html_structure(
            analysis_payload, manifest, charts
        )
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Generated HTML report: {report_path}")
        return report_path
    
    def _build_html_structure(
        self, 
        analysis_payload: Dict[str, Any], 
        manifest: Dict[str, Any],
        charts: Dict[str, str]
    ) -> str:
        """Build complete HTML document structure."""
        org = manifest.get("org", "Unknown")
        timestamp = manifest.get("timestamp_utc", datetime.utcnow().isoformat())
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{org} Employee Analysis Report - GEL Scenario</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    {self._get_css_styles()}
</head>
<body>
    <div class="container">
        {self._generate_html_header(manifest)}
        {self._generate_toc()}
        {self._generate_overview_section(manifest, analysis_payload)}
        {self._generate_data_flow_section()}
        {self._generate_population_section(analysis_payload, charts)}
        {self._generate_inequality_section(analysis_payload, manifest, charts)}
        {self._generate_high_performers_section(analysis_payload, manifest, charts)}
        {self._generate_budget_allocation_section(manifest)}
        {self._generate_recommendations_section(analysis_payload, manifest)}
        {self._generate_appendix_section(manifest, analysis_payload)}
        {self._generate_footer()}
    </div>
    
    <script>
        // Initialize Mermaid
        mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
        
        // Initialize interactive charts
        {charts.get('plotly_init', '')}
    </script>
</body>
</html>"""
    
    def _get_css_styles(self) -> str:
        """Generate embedded CSS styles."""
        return """<style>
        :root {
            --primary-color: #2c5aa0;
            --secondary-color: #34a853;
            --accent-color: #fbbc04;
            --danger-color: #ea4335;
            --bg-light: #f8f9fa;
            --bg-white: #ffffff;
            --text-dark: #343a40;
            --text-muted: #6c757d;
            --border-color: #dee2e6;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--text-dark);
            background-color: var(--bg-light);
            margin: 0;
            padding: 0;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: var(--bg-white);
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            min-height: 100vh;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px 0;
            border-bottom: 3px solid var(--primary-color);
        }
        
        .header h1 {
            color: var(--primary-color);
            margin: 0 0 15px 0;
            font-size: 2.5rem;
            font-weight: 300;
        }
        
        .header .meta {
            color: var(--text-muted);
            font-size: 1.1rem;
        }
        
        .toc {
            background-color: var(--bg-light);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        
        .toc h3 {
            margin-top: 0;
            color: var(--primary-color);
        }
        
        .toc ul {
            list-style: none;
            padding-left: 0;
        }
        
        .toc li {
            margin: 8px 0;
        }
        
        .toc a {
            text-decoration: none;
            color: var(--primary-color);
            font-weight: 500;
        }
        
        .toc a:hover {
            text-decoration: underline;
        }
        
        .section {
            margin-bottom: 50px;
            padding-bottom: 30px;
            border-bottom: 1px solid var(--border-color);
        }
        
        .section:last-child {
            border-bottom: none;
        }
        
        .section h2 {
            color: var(--primary-color);
            font-size: 1.8rem;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--accent-color);
        }
        
        .section h3 {
            color: var(--text-dark);
            font-size: 1.3rem;
            margin-top: 25px;
            margin-bottom: 15px;
        }
        
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        
        .kpi-card {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        
        .kpi-card .value {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .kpi-card .label {
            font-size: 0.9rem;
            opacity: 0.9;
        }
        
        .chart-container {
            margin: 30px 0;
            padding: 20px;
            background-color: var(--bg-white);
            border: 1px solid var(--border-color);
            border-radius: 8px;
        }
        
        .mermaid {
            text-align: center;
            background-color: var(--bg-white);
            padding: 20px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            margin: 20px 0;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: var(--bg-white);
        }
        
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }
        
        th {
            background-color: var(--bg-light);
            font-weight: 600;
            color: var(--primary-color);
        }
        
        tr:hover {
            background-color: rgba(44, 90, 160, 0.05);
        }
        
        .recommendation {
            background-color: var(--bg-light);
            border-left: 4px solid var(--secondary-color);
            padding: 15px;
            margin: 15px 0;
            border-radius: 0 8px 8px 0;
        }
        
        .recommendation h4 {
            margin-top: 0;
            color: var(--secondary-color);
        }
        
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        
        .alert-info {
            background-color: #e3f2fd;
            border-left: 4px solid #2196f3;
            color: #0d47a1;
        }
        
        .alert-warning {
            background-color: #fff3e0;
            border-left: 4px solid #ff9800;
            color: #e65100;
        }
        
        .alert-success {
            background-color: #e8f5e8;
            border-left: 4px solid #4caf50;
            color: #2e7d32;
        }
        
        .footer {
            margin-top: 50px;
            padding-top: 30px;
            border-top: 2px solid var(--border-color);
            text-align: center;
            color: var(--text-muted);
            font-size: 0.9rem;
        }
        
        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }
            
            .header h1 {
                font-size: 2rem;
            }
            
            .kpi-grid {
                grid-template-columns: 1fr;
            }
            
            table {
                font-size: 0.9rem;
            }
            
            th, td {
                padding: 8px;
            }
        }
    </style>"""
    
    def _generate_html_header(self, manifest: Dict[str, Any]) -> str:
        """Generate HTML header section."""
        org = manifest.get("org", "Unknown")
        timestamp = manifest.get("timestamp_utc", "Unknown")
        scenario = manifest.get("scenario", "GEL")
        
        return f"""
    <div class="header">
        <h1>{org} Employee Analysis Report</h1>
        <div class="meta">
            <strong>Scenario:</strong> {scenario} | 
            <strong>Generated:</strong> {timestamp} | 
            <strong>Organization:</strong> {org}
        </div>
    </div>"""
    
    def _generate_toc(self) -> str:
        """Generate table of contents."""
        return """
    <div class="toc">
        <h3>Table of Contents</h3>
        <ul>
            <li><a href="#overview">1. Overview & Inputs</a></li>
            <li><a href="#dataflow">2. Data Flow Overview</a></li>
            <li><a href="#stratification">3. Population Stratification</a></li>
            <li><a href="#inequality">4. Inequality & Risk Analysis</a></li>
            <li><a href="#highperformers">5. High-Performer Recognition</a></li>
            <li><a href="#budgetallocation">6. Manager Budget Allocation</a></li>
            <li><a href="#recommendations">7. Targeted Recommendations</a></li>
            <li><a href="#appendix">8. Appendix</a></li>
        </ul>
    </div>"""
    
    def _generate_overview_section(
        self, 
        manifest: Dict[str, Any], 
        analysis_payload: Dict[str, Any]
    ) -> str:
        """Generate overview and inputs section."""
        population = manifest.get("population", 0)
        median_salary = manifest.get("median_salary", 0)
        below_median_pct = manifest.get("below_median_pct", 0)
        gender_gap_pct = manifest.get("gender_gap_pct", 0)
        budget_pct = manifest.get("intervention_budget_pct", 0.5)
        
        return f"""
    <div class="section" id="overview">
        <h2>1. Overview & Inputs</h2>
        
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="value">{population:,}</div>
                <div class="label">Total Employees</div>
            </div>
            <div class="kpi-card">
                <div class="value">£{median_salary:,.0f}</div>
                <div class="label">Median Salary</div>
            </div>
            <div class="kpi-card">
                <div class="value">{below_median_pct:.1f}%</div>
                <div class="label">Below Median</div>
            </div>
            <div class="kpi-card">
                <div class="value">{gender_gap_pct:.1f}%</div>
                <div class="label">Gender Pay Gap</div>
            </div>
        </div>
        
        <h3>Scenario Configuration</h3>
        <table>
            <tr><th>Parameter</th><th>Value</th></tr>
            <tr><td>Scenario Type</td><td>{manifest.get("scenario", "GEL")}</td></tr>
            <tr><td>Analysis Date</td><td>{manifest.get("timestamp_utc", "Unknown")}</td></tr>
            <tr><td>Random Seed</td><td>{manifest.get("random_seed", "Unknown")}</td></tr>
            <tr><td>Currency</td><td>{manifest.get("currency", "GBP")}</td></tr>
            <tr><td>Intervention Budget</td><td>{budget_pct}% of payroll per manager</td></tr>
            <tr><td>Max Direct Reports</td><td>{manifest.get("max_direct_reports", 6)}</td></tr>
        </table>
    </div>"""
    
    def _generate_data_flow_section(self) -> str:
        """Generate data flow section with Mermaid diagram."""
        return """
    <div class="section" id="dataflow">
        <h2>2. Data Flow Overview</h2>
        
        <p>The following diagram illustrates how data flows through the GEL scenario analysis:</p>
        
        <div class="mermaid">
            flowchart LR
                A[Population Generation] --> B[Role Minimums Validation]
                B --> C[Simulation Engine]
                C --> D[Analysis Modules]
                D --> E[Policy Constraints]
                E --> F[Manager Budget Allocation]
                F --> G[Report Builder]
                G --> H[index.html]
                G --> I[report.md]
                
                subgraph "Analysis Modules"
                    D1[Median Convergence]
                    D2[Gender Gap Analysis] 
                    D3[High Performer Identification]
                    D4[Intervention Modeling]
                end
                
                subgraph "Policy Constraints"
                    E1[≤ 6 Direct Reports]
                    E2[0.5% Budget Cap]
                    E3[Role Minimum Compliance]
                end
        </div>
    </div>"""
    
    def _generate_population_section(
        self, 
        analysis_payload: Dict[str, Any], 
        charts: Dict[str, str]
    ) -> str:
        """Generate population stratification section."""
        stratification = analysis_payload.get("population_stratification", {})
        
        content = """
    <div class="section" id="stratification">
        <h2>3. Population Stratification</h2>
        
        <h3>By Level and Role</h3>"""
        
        # Add level distribution table
        if "by_level" in stratification:
            content += """
        <table>
            <thead>
                <tr><th>Level</th><th>Count</th><th>Median Salary</th><th>Gender Split</th></tr>
            </thead>
            <tbody>"""
            
            for level, data in stratification["by_level"].items():
                count = data.get("count", 0)
                median = data.get("median_salary", 0)
                gender_split = data.get("gender_split", "N/A")
                content += f"""
                <tr>
                    <td>{level}</td>
                    <td>{count:,}</td>
                    <td>£{median:,.2f}</td>
                    <td>{gender_split}</td>
                </tr>"""
            
            content += """
            </tbody>
        </table>"""
        
        # Add population chart if available
        if "population_chart" in charts:
            content += f"""
        <div class="chart-container">
            <h4>Population Distribution Chart</h4>
            {charts["population_chart"]}
        </div>"""
        
        # Add manager distribution
        manager_data = stratification.get("managers", {})
        if manager_data:
            total_managers = manager_data.get("total_managers", 0)
            avg_reports = manager_data.get("average_direct_reports", 0)
            max_reports = manager_data.get("max_direct_reports", 0)
            at_limit = manager_data.get("at_policy_limit", 0)
            
            content += f"""
        <div class="alert alert-info">
            <h4>Manager Distribution Summary</h4>
            <ul>
                <li><strong>Total Managers:</strong> {total_managers:,}</li>
                <li><strong>Average Direct Reports:</strong> {avg_reports:.1f}</li>
                <li><strong>Maximum Direct Reports:</strong> {max_reports}</li>
                <li><strong>Managers at Policy Limit (6):</strong> {at_limit}</li>
            </ul>
        </div>"""
        
        content += """
    </div>"""
        
        return content
    
    def _generate_inequality_section(
        self, 
        analysis_payload: Dict[str, Any], 
        manifest: Dict[str, Any],
        charts: Dict[str, str]
    ) -> str:
        """Generate inequality and risk analysis section."""
        inequality_data = analysis_payload.get("inequality_analysis", {})
        below_median_pct = manifest.get("below_median_pct", 0)
        gender_gap_pct = manifest.get("gender_gap_pct", 0)
        
        # Determine risk level
        if below_median_pct > 40:
            risk_level = "High"
            risk_class = "alert-warning"
        elif below_median_pct > 25:
            risk_level = "Medium"
            risk_class = "alert-info"
        else:
            risk_level = "Low"
            risk_class = "alert-success"
        
        content = f"""
    <div class="section" id="inequality">
        <h2>4. Inequality & Risk Analysis</h2>
        
        <div class="alert {risk_class}">
            <h4>Key Findings - Risk Level: {risk_level}</h4>
            <ul>
                <li><strong>Below-Median Population:</strong> {below_median_pct:.1f}% of employees earn below their level median</li>
                <li><strong>Gender Pay Gap:</strong> {gender_gap_pct:.1f}% overall gap requiring attention</li>
            </ul>
        </div>"""
        
        # Role minimum compliance
        role_compliance = inequality_data.get("role_minimum_compliance", {})
        if role_compliance:
            violations = role_compliance.get("violations", 0)
            total_checked = role_compliance.get("total_employees", 0)
            compliance_rate = (total_checked - violations) / max(total_checked, 1) * 100
            
            content += f"""
        <h3>Role Minimum Compliance</h3>
        <table>
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Employees Below Role Minimums</td><td>{violations}</td></tr>
            <tr><td>Total Employees Checked</td><td>{total_checked}</td></tr>
            <tr><td>Compliance Rate</td><td>{compliance_rate:.1f}%</td></tr>
        </table>"""
        
        # Gap analysis by segment
        segments = inequality_data.get("segments", {})
        if segments:
            content += """
        <h3>Gap Analysis by Segment</h3>
        <table>
            <thead>
                <tr><th>Segment</th><th>Affected Employees</th><th>Average Gap</th><th>Total Cost to Close</th></tr>
            </thead>
            <tbody>"""
            
            for segment_name, segment_data in segments.items():
                affected = segment_data.get("affected_count", 0)
                avg_gap = segment_data.get("average_gap", 0)
                total_cost = segment_data.get("total_cost", 0)
                content += f"""
                <tr>
                    <td>{segment_name}</td>
                    <td>{affected}</td>
                    <td>£{avg_gap:,.2f}</td>
                    <td>£{total_cost:,.2f}</td>
                </tr>"""
            
            content += """
            </tbody>
        </table>"""
        
        # Add inequality chart if available
        if "inequality_chart" in charts:
            content += f"""
        <div class="chart-container">
            <h4>Inequality Analysis Chart</h4>
            {charts["inequality_chart"]}
        </div>"""
        
        content += """
    </div>"""
        
        return content
    
    def _generate_high_performers_section(
        self, 
        analysis_payload: Dict[str, Any], 
        manifest: Dict[str, Any],
        charts: Dict[str, str]
    ) -> str:
        """Generate high performer recognition section."""
        high_performers = analysis_payload.get("high_performers", {})
        budget_pct = manifest.get("intervention_budget_pct", 0.5)
        
        total_high_performers = high_performers.get("total_identified", 0)
        eligible_for_uplift = high_performers.get("eligible_for_uplift", 0)
        estimated_cost = high_performers.get("estimated_uplift_cost_pct", 0)
        
        budget_utilization = (estimated_cost / budget_pct * 100) if budget_pct > 0 else 0
        
        content = f"""
    <div class="section" id="highperformers">
        <h2>5. High-Performer Recognition (within constraints)</h2>
        
        <div class="alert alert-info">
            <h4>Policy Framework</h4>
            <ul>
                <li><strong>Budget Constraint:</strong> {budget_pct}% of payroll per manager</li>
                <li><strong>Manager Limit:</strong> Maximum 6 direct reports per manager</li>
                <li><strong>Priority:</strong> Below-median high performers receive first consideration</li>
            </ul>
        </div>
        
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="value">{total_high_performers:,}</div>
                <div class="label">High Performers Identified</div>
            </div>
            <div class="kpi-card">
                <div class="value">{eligible_for_uplift:,}</div>
                <div class="label">Eligible for Uplift</div>
            </div>
            <div class="kpi-card">
                <div class="value">{estimated_cost:.2f}%</div>
                <div class="label">Estimated Cost</div>
            </div>
            <div class="kpi-card">
                <div class="value">{budget_utilization:.1f}%</div>
                <div class="label">Budget Utilization</div>
            </div>
        </div>"""
        
        # Trade-offs within budget
        trade_offs = high_performers.get("trade_offs", [])
        if trade_offs:
            content += """
        <h3>Budget Trade-offs</h3>
        <p>The following trade-offs were considered within the budget constraint:</p>
        <table>
            <thead>
                <tr><th>Employee ID</th><th>Current Salary</th><th>Proposed Uplift</th><th>Impact</th></tr>
            </thead>
            <tbody>"""
            
            for i, trade_off in enumerate(trade_offs[:10], 1):  # Show top 10
                employee_id = trade_off.get("employee_id", f"EMP{i}")
                current_salary = trade_off.get("current_salary", 0)
                proposed_uplift = trade_off.get("proposed_uplift", 0)
                impact = trade_off.get("inequality_impact", "Unknown")
                
                content += f"""
                <tr>
                    <td>{employee_id}</td>
                    <td>£{current_salary:,.2f}</td>
                    <td>£{proposed_uplift:,.2f}</td>
                    <td>{impact}</td>
                </tr>"""
            
            content += """
            </tbody>
        </table>"""
        
        # Add high performers chart if available
        if "high_performers_chart" in charts:
            content += f"""
        <div class="chart-container">
            <h4>High Performers Analysis</h4>
            {charts["high_performers_chart"]}
        </div>"""
        
        content += """
    </div>"""
        
        return content
    
    def _generate_budget_allocation_section(self, manifest: Dict[str, Any]) -> str:
        """Generate budget allocation section with Mermaid diagram."""
        max_reports = manifest.get("max_direct_reports", 6)
        budget_pct = manifest.get("intervention_budget_pct", 0.5)
        
        return f"""
    <div class="section" id="budgetallocation">
        <h2>6. Manager Budget Allocation Process</h2>
        
        <p>The following diagram shows how budget allocation decisions are made for each manager:</p>
        
        <div class="mermaid">
            flowchart TD
                M[Manager with ≤ {max_reports} directs] --> B{{"{budget_pct}% budget available?"}}
                
                B -->|Yes| P{{Identify priorities}}
                B -->|No| N1[No budget available]
                
                P --> P1{{"Below-median employees?"}}
                P --> P2{{"High performers?"}}
                
                P1 -->|Yes| HP1{{"Also high performer?"}}
                P1 -->|No| P3[Standard progression]
                
                P2 -->|Yes| HP2{{"Below median salary?"}}
                P2 -->|No| P4[Performance bonus only]
                
                HP1 -->|Yes| A1[Priority 1: Recommend Uplift]
                HP1 -->|No| A2[Priority 2: Monitor closely]
                
                HP2 -->|Yes| A1
                HP2 -->|No| A3[Priority 3: Recognition only]
                
                A1 --> R[Recalculate Inequality KPIs]
                A2 --> R
                A3 --> R
                
                R --> R1{{Within budget cap?}}
                
                R1 -->|Yes| OK[Accept recommendations]
                R1 -->|No| T[Trim recommendations to fit budget]
                
                T --> S[Stage remaining for next cycle]
                
                style A1 fill:#c8e6c9
                style OK fill:#4caf50
                style T fill:#fff3e0
                style N1 fill:#ffcdd2
        </div>
    </div>"""
    
    def _generate_recommendations_section(
        self, 
        analysis_payload: Dict[str, Any], 
        manifest: Dict[str, Any]
    ) -> str:
        """Generate targeted recommendations section."""
        recommendations = analysis_payload.get("recommendations", {})
        
        content = """
    <div class="section" id="recommendations">
        <h2>7. Targeted Recommendations</h2>
        
        <h3>Immediate Actions</h3>"""
        
        immediate_actions = recommendations.get("immediate", [])
        if immediate_actions:
            for i, action in enumerate(immediate_actions, 1):
                employee_info = action.get("employee", "Unknown")
                current_salary = action.get("current_salary", 0)
                proposed_uplift = action.get("proposed_uplift", 0)
                expected_impact = action.get("expected_impact", "Unknown")
                uplift_pct = (proposed_uplift / max(current_salary, 1) * 100) if current_salary > 0 else 0
                
                content += f"""
        <div class="recommendation">
            <h4>Action {i}: {action.get('action_type', 'Salary Adjustment')}</h4>
            <table>
                <tr><th>Parameter</th><th>Value</th></tr>
                <tr><td>Employee</td><td>{employee_info}</td></tr>
                <tr><td>Current Salary</td><td>£{current_salary:,.2f}</td></tr>
                <tr><td>Recommended Adjustment</td><td>£{proposed_uplift:,.2f} ({uplift_pct:+.1f}%)</td></tr>
                <tr><td>Expected Impact</td><td>{expected_impact}</td></tr>
            </table>
        </div>"""
        else:
            content += """
        <div class="alert alert-info">
            <p>No immediate actions identified within current budget constraints.</p>
        </div>"""
        
        # Medium-term strategies
        content += """
        <h3>Medium-Term Strategies (6-12 months)</h3>"""
        
        medium_term = recommendations.get("medium_term", [])
        if medium_term:
            content += "<ul>"
            for strategy in medium_term:
                content += f"""<li><strong>{strategy.get('title', 'Strategy')}:</strong> {strategy.get('description', 'No description')}"""
                if cost := strategy.get('estimated_cost'):
                    content += f" <em>(Estimated Cost: £{cost:,.2f})</em>"
                content += "</li>"
            content += "</ul>"
        else:
            content += """
        <div class="alert alert-info">
            <p>Medium-term strategies are being developed based on immediate action results.</p>
        </div>"""
        
        # Success metrics
        content += """
        <h3>Success Metrics</h3>
        <p>Track these metrics to measure intervention effectiveness:</p>"""
        
        metrics = recommendations.get("success_metrics", [])
        if metrics:
            content += """
        <table>
            <thead>
                <tr><th>Metric</th><th>Description</th><th>Target</th></tr>
            </thead>
            <tbody>"""
            
            for metric in metrics:
                name = metric.get('name', 'Metric')
                description = metric.get('description', 'No description')
                target = metric.get('target_value', 'TBD')
                content += f"""
                <tr>
                    <td>{name}</td>
                    <td>{description}</td>
                    <td>{target}</td>
                </tr>"""
            
            content += """
            </tbody>
        </table>"""
        
        content += """
    </div>"""
        
        return content
    
    def _generate_appendix_section(
        self, 
        manifest: Dict[str, Any], 
        analysis_payload: Dict[str, Any]
    ) -> str:
        """Generate appendix section."""
        config_hash = manifest.get("roles_config_sha256", "Unknown")
        
        content = f"""
    <div class="section" id="appendix">
        <h2>8. Appendix</h2>
        
        <h3>Assumptions</h3>
        <table>
            <tr><th>Assumption</th><th>Value</th></tr>
            <tr><td>Currency</td><td>{manifest.get("currency", "GBP")}</td></tr>
            <tr><td>Budget Period</td><td>Annual budget allocations</td></tr>
            <tr><td>Manager Constraints</td><td>Maximum {manifest.get("max_direct_reports", 6)} direct reports per manager</td></tr>
            <tr><td>Budget Constraint</td><td>{manifest.get("intervention_budget_pct", 0.5)}% of manager's team payroll for interventions</td></tr>
            <tr><td>Configuration Version</td><td>{manifest.get("config_version", 1)}</td></tr>
        </table>
        
        <h3>Reproducibility Information</h3>
        <div class="alert alert-info">
            <h4>To Reproduce This Analysis</h4>
            <p>Use the following command:</p>
            <pre><code>python employee_simulation_orchestrator.py \\
  --scenario GEL \\
  --org GEL \\
  --roles-config config/orgs/GEL/roles.yaml \\
  --report \\
  --random-seed {manifest.get("random_seed", 42)}</code></pre>
            
            <ul>
                <li><strong>Configuration Hash:</strong> <code>{config_hash}</code></li>
                <li><strong>Analysis Date:</strong> {manifest.get("timestamp_utc", "Unknown")}</li>
                <li><strong>Population Size:</strong> {manifest.get("population", 0):,} employees</li>
            </ul>
        </div>
        
        <h3>Role Configuration Summary</h3>
        <p><strong>Total Roles Configured:</strong> {len(analysis_payload.get("role_config", {}).get("roles", []))}</p>"""
        
        # Show sample roles
        roles = analysis_payload.get("role_config", {}).get("roles", [])
        if roles:
            content += """
        <table>
            <thead>
                <tr><th>Role Title</th><th>Minimum Salary</th><th>Notes</th></tr>
            </thead>
            <tbody>"""
            
            for role in roles[:10]:  # Show first 10 roles
                title = role.get("title", "Unknown")
                min_salary = min(role.get("min_salaries", [0]))
                notes = role.get("notes", "")
                content += f"""
                <tr>
                    <td>{title}</td>
                    <td>£{min_salary:,.2f}</td>
                    <td>{notes}</td>
                </tr>"""
            
            if len(roles) > 10:
                content += f"""
                <tr>
                    <td colspan="3"><em>... and {len(roles) - 10} more roles</em></td>
                </tr>"""
            
            content += """
            </tbody>
        </table>"""
        
        content += """
    </div>"""
        
        return content
    
    def _generate_footer(self) -> str:
        """Generate footer section."""
        return f"""
    <div class="footer">
        <p><em>Report generated by Employee Simulation Orchestrator - GEL Scenario</em></p>
        <p>Generated at: {datetime.utcnow().isoformat()}Z</p>
    </div>"""
    
    def _generate_charts(
        self, 
        analysis_payload: Dict[str, Any], 
        manifest: Dict[str, Any],
        assets_dir: Optional[Path]
    ) -> Dict[str, str]:
        """Generate embedded charts for the report.
        
        Returns dictionary with chart HTML content or references.
        """
        charts = {}
        
        # Generate sample population distribution chart
        try:
            stratification = analysis_payload.get("population_stratification", {})
            if "by_level" in stratification:
                levels = list(stratification["by_level"].keys())
                counts = [data.get("count", 0) for data in stratification["by_level"].values()]
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=levels,
                    y=counts,
                    marker_color='rgba(44, 90, 160, 0.8)',
                    name='Employee Count'
                ))
                
                fig.update_layout(
                    title="Employee Distribution by Level",
                    xaxis_title="Level",
                    yaxis_title="Count",
                    height=400,
                    margin=dict(l=50, r=50, t=50, b=50)
                )
                
                charts["population_chart"] = f'<div id="population-chart"></div>'
                charts["plotly_init"] = f"""
                Plotly.newPlot('population-chart', {fig.to_json()});
                """
        
        except Exception as e:
            self.logger.warning(f"Failed to generate population chart: {e}")
        
        return charts


if __name__ == "__main__":
    # Test the HTML report builder
    from report_builder_md import create_sample_analysis_payload
    
    builder = HTMLReportBuilder(output_dir="test_output")
    
    # Create sample data
    sample_manifest = {
        "scenario": "GEL",
        "org": "GEL", 
        "timestamp_utc": "2025-08-14T10:00:00Z",
        "population": 201,
        "median_salary": 71500,
        "below_median_pct": 42.3,
        "gender_gap_pct": 6.8,
        "intervention_budget_pct": 0.5,
        "max_direct_reports": 6,
        "roles_config_sha256": "8689a92285a3a305d8f4c87c2a54f3b7e1d29c6f8b7a4e5d3c2b1a9f8e7d6c5b4",
        "random_seed": 42,
        "currency": "GBP",
        "config_version": 1
    }
    
    sample_payload = create_sample_analysis_payload()
    
    # Generate report
    report_path = builder.build_gel_report(sample_payload, sample_manifest)
    print(f"Generated test HTML report: {report_path}")
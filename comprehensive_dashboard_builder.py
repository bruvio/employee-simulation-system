#!/usr/bin/env python3
"""
Comprehensive Dashboard Builder for Employee Simulation System.

Creates a complete dashboard with scenario overview, all generated files, images, detailed explanations, and proper data
source handling.
"""

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import quote

import pandas as pd

from smart_logging_manager import get_smart_logger


class ComprehensiveDashboardBuilder:
    """
    Builds comprehensive dashboard with all simulation results and explanations.
    """

    def __init__(self, config: Dict[str, Any], results_directory: str, scenario_name: str = "GEL"):
        """
        Initialize comprehensive dashboard builder.

        Args:
            config: Configuration settings
            results_directory: Path to results directory
            scenario_name: Name of the scenario being analyzed
        """
        self.config = config
        self.results_directory = Path(results_directory)
        self.scenario_name = scenario_name
        self.logger = get_smart_logger()
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Get configuration values with proper fallbacks
        self.default_gender_gap = config.get("defaults", {}).get("gender_pay_gap_percent", 15.8)
        scenario_config = config.get("scenarios", {}).get(scenario_name, {})
        self.scenario_gender_gap = scenario_config.get("gender_pay_gap_percent", self.default_gender_gap)
        self.target_gender_gap = scenario_config.get("target_gender_gap_percent", 5.0)
        self.population_size = scenario_config.get("population_size", 500)

        self.logger.log_info(f"Initialized ComprehensiveDashboardBuilder for {scenario_name} scenario")

    def build_comprehensive_dashboard(self, output_dir: str) -> str:
        """
        Build the complete comprehensive dashboard.

        Args:
            output_dir: Directory to save the dashboard

        Returns:
            Path to the generated dashboard HTML file
        """
        self.logger.log_info("🎯 Building comprehensive dashboard with all files and explanations")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Discover all generated files and images
        all_files = self._discover_all_files()

        # Load the latest simulation data
        simulation_data = self._load_simulation_data()

        # Calculate actual gender pay gap from data
        actual_gender_gap = self._calculate_actual_gender_gap(simulation_data)

        # Generate dashboard HTML
        dashboard_html = self._generate_comprehensive_html(all_files, simulation_data, actual_gender_gap)

        # Save dashboard
        dashboard_file = output_path / f"comprehensive_dashboard_{self.timestamp}.html"
        dashboard_file.write_text(dashboard_html, encoding="utf-8")

        self.logger.log_info(f"✅ Comprehensive dashboard saved to: {dashboard_file}")
        return str(dashboard_file)

    def _discover_all_files(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Discover all generated files and categorize them.

        Returns:
            Dictionary with categorized file listings
        """
        file_categories = {"images": [], "reports": [], "data_files": [], "dashboards": [], "stories": []}

        # Search in multiple locations
        search_paths = [
            self.results_directory,
            Path("/Users/brunoviola/WORK/employee-simulation-system/artifacts"),
            Path("/Users/brunoviola/WORK/employee-simulation-system/results"),
        ]

        for search_path in search_paths:
            if search_path.exists():
                self._scan_directory(search_path, file_categories)

        return file_categories

    def _scan_directory(self, directory: Path, file_categories: Dict[str, List]):
        """
        Recursively scan directory for files.
        """
        try:
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    file_info = {
                        "name": file_path.name,
                        "path": str(file_path),
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M"),
                    }

                    # Categorize by file extension
                    suffix = file_path.suffix.lower()
                    if suffix in [".png", ".jpg", ".jpeg", ".svg"]:
                        file_categories["images"].append(file_info)
                    elif suffix in [".md", ".pdf", ".txt"]:
                        file_categories["reports"].append(file_info)
                    elif suffix in [".csv", ".json", ".xlsx"]:
                        file_categories["data_files"].append(file_info)
                    elif suffix == ".html":
                        if "dashboard" in file_path.name.lower():
                            file_categories["dashboards"].append(file_info)
                        elif "story" in file_path.name.lower():
                            file_categories["stories"].append(file_info)
                        else:
                            file_categories["reports"].append(file_info)

        except Exception as e:
            self.logger.log_warning(f"Error scanning directory {directory}: {e}")

    def _load_simulation_data(self) -> Dict[str, Any]:
        """
        Load the latest simulation data.
        """
        # Try to find the most recent simulation results
        simulation_files = list(self.results_directory.rglob("*simulation_results*.json"))

        if not simulation_files:
            # Try broader search
            broader_search = Path("/Users/brunoviola/WORK/employee-simulation-system")
            simulation_files = list(broader_search.rglob("*simulation_results*.json"))

        if simulation_files:
            # Get the most recent file
            latest_file = max(simulation_files, key=lambda f: f.stat().st_mtime)
            try:
                with open(latest_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.log_warning(f"Error loading simulation data from {latest_file}: {e}")

        return {}

    def _calculate_actual_gender_gap(self, simulation_data: Dict[str, Any]) -> float:
        """
        Calculate actual gender pay gap from simulation data.

        Args:
            simulation_data: Loaded simulation results

        Returns:
            Actual calculated gender pay gap percentage
        """
        try:
            # Try to get population data
            population_data = simulation_data.get("population_data", [])
            if not population_data:
                # Try alternative keys
                population_data = simulation_data.get("employees", [])

            if population_data:
                df = pd.DataFrame(population_data)
                if "gender" in df.columns and "salary" in df.columns:
                    male_median = df[df["gender"] == "Male"]["salary"].median()
                    female_median = df[df["gender"] == "Female"]["salary"].median()

                    if pd.notna(male_median) and pd.notna(female_median) and male_median > 0:
                        gap_percent = ((male_median - female_median) / male_median) * 100
                        return round(gap_percent, 2)

        except Exception as e:
            self.logger.log_warning(f"Error calculating gender gap: {e}")

        return 0.0

    def _generate_comprehensive_html(
        self, all_files: Dict[str, List], simulation_data: Dict[str, Any], actual_gender_gap: float
    ) -> str:
        """
        Generate the comprehensive HTML dashboard.

        Args:
            all_files: Categorized file listings
            simulation_data: Simulation results data
            actual_gender_gap: Calculated gender pay gap

        Returns:
            Complete HTML content
        """
        # Count total files
        total_files = sum(len(category) for category in all_files.values())

        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Employee Simulation System - Comprehensive Results Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }}
        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
            font-size: 1.2em;
        }}
        .content {{
            padding: 40px;
        }}
        .section {{
            margin-bottom: 40px;
            padding: 30px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .section h2 {{
            margin-top: 0;
            color: #2c3e50;
            font-size: 1.8em;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #2c3e50;
        }}
        .metric-label {{
            color: #7f8c8d;
            margin-top: 5px;
        }}
        .config-comparison {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }}
        .config-comparison h3 {{
            margin-top: 0;
            color: #856404;
        }}
        .explanation {{
            background: #e8f4fd;
            border-left: 4px solid #1f77b4;
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }}
        .file-browser {{
            margin-top: 30px;
        }}
        .file-category {{
            margin-bottom: 30px;
        }}
        .file-category h3 {{
            color: #2c3e50;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .file-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }}
        .file-item {{
            background: white;
            border: 1px solid #dee2e6;
            border-radius: 6px;
            padding: 15px;
            transition: all 0.3s ease;
        }}
        .file-item:hover {{
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transform: translateY(-2px);
        }}
        .file-name {{
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        .file-meta {{
            font-size: 0.9em;
            color: #6c757d;
        }}
        .file-link {{
            color: #667eea;
            text-decoration: none;
        }}
        .file-link:hover {{
            text-decoration: underline;
        }}
        .alert {{
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .alert-warning {{
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
        }}
        .alert-info {{
            background-color: #d1ecf1;
            border: 1px solid #b8daff;
            color: #0c5460;
        }}
        .simulation-explanation {{
            background: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            padding: 25px;
            margin: 20px 0;
        }}
        .remediation-details {{
            background: #e8f5e8;
            border-left: 4px solid #28a745;
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 8px 8px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Employee Simulation System</h1>
            <p>Comprehensive Results Dashboard - {self.scenario_name} Scenario</p>
            <p style="font-size: 0.9em; opacity: 0.8;">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="content">
            <!-- Scenario Configuration Overview -->
            <div class="section">
                <h2>🎯 Scenario Configuration Overview</h2>
                <div class="config-comparison">
                    <h3>Gender Pay Gap Configuration Analysis</h3>
                    <div class="metrics-grid">
                        <div class="metric-card">
                            <div class="metric-value">{self.default_gender_gap}%</div>
                            <div class="metric-label">Default Config Setting</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{self.scenario_gender_gap}%</div>
                            <div class="metric-label">{self.scenario_name} Scenario Target</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{actual_gender_gap}%</div>
                            <div class="metric-label">Actual Calculated Gap</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{self.target_gender_gap}%</div>
                            <div class="metric-label">Final Target Goal</div>
                        </div>
                    </div>
                </div>
                
                <div class="explanation">
                    <h4>📋 Configuration Explanation</h4>
                    <p><strong>Default Configuration:</strong> The system's base configuration sets a {self.default_gender_gap}% gender pay gap as the starting point for all scenarios.</p>
                    <p><strong>{self.scenario_name} Scenario:</strong> This specific scenario targets a {self.scenario_gender_gap}% gender pay gap, representing the organization's current state or policy goal.</p>
                    <p><strong>Actual Results:</strong> The simulation calculated an actual gender pay gap of {actual_gender_gap}%, which may differ from the target due to:</p>
                    <ul>
                        <li>Random salary generation within defined ranges</li>
                        <li>Role distribution effects across levels</li>
                        <li>Population sampling variations</li>
                        <li>Salary constraint enforcement</li>
                    </ul>
                    <p><strong>Target Goal:</strong> The long-term organizational goal is to reduce the gap to {self.target_gender_gap}% through targeted interventions.</p>
                </div>
            </div>
            
            <!-- Key Performance Indicators -->
            <div class="section">
                <h2>📈 Key Performance Indicators</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-value">{self.population_size}</div>
                        <div class="metric-label">Total Employees</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{total_files}</div>
                        <div class="metric-label">Generated Files</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{len(all_files['images'])}</div>
                        <div class="metric-label">Visualization Images</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{len(all_files['reports'])}</div>
                        <div class="metric-label">Analysis Reports</div>
                    </div>
                </div>
            </div>
            
            <!-- Simulation Results Explanation -->
            <div class="section">
                <h2>🔍 Detailed Simulation Results Explanation</h2>
                <div class="simulation-explanation">
                    <h3>What the Simulation Models</h3>
                    <p>This employee simulation system models a realistic organizational salary structure with the following key components:</p>
                    
                    <h4>📊 Population Generation</h4>
                    <ul>
                        <li><strong>Size:</strong> {self.population_size} employees across 6 organizational levels</li>
                        <li><strong>Gender Distribution:</strong> Approximately balanced male/female distribution</li>
                        <li><strong>Salary Ranges:</strong> Level-specific salary constraints with realistic market ranges</li>
                        <li><strong>Performance Ratings:</strong> Distributed performance scores affecting promotion potential</li>
                    </ul>
                    
                    <h4>🎯 Gender Pay Gap Implementation</h4>
                    <p>The system implements gender pay disparities by:</p>
                    <ul>
                        <li>Applying systematic salary differences between genders within the same level</li>
                        <li>Modeling real-world promotion and advancement patterns</li>
                        <li>Considering the compound effect of small gaps over career progression</li>
                    </ul>
                    
                    <h4>🔄 Simulation Cycles</h4>
                    <p>The simulation runs multiple review cycles to model:</p>
                    <ul>
                        <li>Annual performance reviews and salary adjustments</li>
                        <li>Promotion opportunities based on performance and level capacity</li>
                        <li>Market-based salary corrections</li>
                        <li>Policy intervention effects over time</li>
                    </ul>
                </div>
                
                <div class="remediation-details">
                    <h3>💰 Remediation Cost Analysis</h3>
                    <p><strong>What Remediation Costs Represent:</strong></p>
                    <ul>
                        <li><strong>Annual Ongoing Investment:</strong> These are yearly salary increases, not one-time payments</li>
                        <li><strong>Compound Growth:</strong> Increases compound over time as employees advance</li>
                        <li><strong>Budget Constraints:</strong> Limited to 0.5% of total payroll per manager per year</li>
                        <li><strong>Targeted Approach:</strong> Prioritizes employees furthest below median for their level</li>
                        <li><strong>Sustainable Strategy:</strong> Designed to close gaps gradually without budget shock</li>
                    </ul>
                    
                    <p><strong>Implementation Timeline:</strong></p>
                    <ul>
                        <li><strong>Year 1-2:</strong> Address most severe disparities (>20% below median)</li>
                        <li><strong>Year 3-4:</strong> Reduce moderate gaps (10-20% below median)</li>
                        <li><strong>Year 5+:</strong> Fine-tune and maintain equity levels</li>
                    </ul>
                </div>
            </div>
            
            <!-- Generated Files Browser -->
            <div class="section">
                <h2>📁 Generated Files and Visualizations</h2>
                <p>All files generated during the simulation are organized below. Click any file name to view or download.</p>
                
                <div class="file-browser">
"""

        # Add file categories
        for category_name, files in all_files.items():
            if files:  # Only show categories that have files
                category_title = {
                    "images": "🖼️ Visualization Images",
                    "reports": "📄 Analysis Reports",
                    "data_files": "📊 Data Files",
                    "dashboards": "📈 Interactive Dashboards",
                    "stories": "📚 Employee Story Analysis",
                }.get(category_name, f"📁 {category_name.title()}")

                html_content += f"""
                    <div class="file-category">
                        <h3>{category_title} ({len(files)} files)</h3>
                        <div class="file-list">
"""

                for file_info in sorted(files, key=lambda x: x["modified"], reverse=True):
                    file_size = self._format_file_size(file_info["size"])
                    # Create file URL (using file:// protocol for local access)
                    file_url = f"file://{quote(file_info['path'])}"

                    html_content += f"""
                            <div class="file-item">
                                <div class="file-name">
                                    <a href="{file_url}" class="file-link" target="_blank">{file_info['name']}</a>
                                </div>
                                <div class="file-meta">
                                    📅 {file_info['modified']} | 📏 {file_size}
                                </div>
                            </div>
"""

                html_content += """
                        </div>
                    </div>
"""

        # Close HTML
        html_content += f"""
                </div>
            </div>
            
            <!-- Footer -->
            <div style="text-align: center; padding: 40px 0; border-top: 1px solid #dee2e6; margin-top: 40px;">
                <p style="color: #6c757d; margin: 0;">
                    🤖 Generated by Employee Simulation System Advanced Analytics<br>
                    📊 {total_files} files generated | 🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </div>
        </div>
    </div>
</body>
</html>
"""

        return html_content

    def _format_file_size(self, size_bytes: int) -> str:
        """
        Format file size in human readable format.
        """
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

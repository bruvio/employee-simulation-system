#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

import csv
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
import xml.etree.ElementTree as ET

import pandas as pd


class AdvancedStoryExportSystem:
    """Advanced story export and reporting system for employee simulation data.

    Implements Phase 4 PRP requirements for comprehensive story export functionality.

    Args:

    Returns:
    """

    def __init__(self, output_base_dir: str = "exports", smart_logger=None):
        self.output_base_dir = Path(output_base_dir)
        self.smart_logger = smart_logger
        self.export_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Ensure base directory exists
        self.output_base_dir.mkdir(parents=True, exist_ok=True)

    def _log(self, message: str, level: str = "info"):
        """Helper method for logging.

        Args:
          message: str:
          level: str:  (Default value = "info")

        Returns:
        """
        if self.smart_logger:
            getattr(self.smart_logger, f"log_{level}")(message)
        else:
            print(f"[{level.upper()}] {message}")

    def export_employee_stories_comprehensive(
        self,
        employee_stories: Dict[str, List],
        population_data: List[Dict],
        cycle_data: Optional[pd.DataFrame] = None,
        formats: List[str] = None,
    ) -> Dict[str, str]:
        """Export comprehensive employee stories in multiple formats.

        Args:
          employee_stories: Stories organized by category
          population_data: Full population data for context
          cycle_data: Optional cycle progression data
          formats: Export formats ['json', 'csv', 'excel', 'xml', 'markdown']
          employee_stories: Dict[str:
          List]:
          population_data: List[Dict]:
          cycle_data: Optional[pd.DataFrame]:  (Default value = None)
          formats: List[str]:  (Default value = None)

        Returns:
          : Dict of format -> file path mappings
        """
        if formats is None:
            formats = ["json", "csv", "excel", "markdown"]

        self._log(f"Exporting employee stories in {len(formats)} formats")

        export_files = {}

        # Create comprehensive story dataset
        comprehensive_data = self._prepare_comprehensive_story_data(employee_stories, population_data, cycle_data)

        try:
            # JSON Export - Detailed nested structure
            if "json" in formats:
                json_file = self._export_stories_json(comprehensive_data, employee_stories)
                export_files["json"] = str(json_file)

            # CSV Export - Flat structure for analysis
            if "csv" in formats:
                csv_file = self._export_stories_csv(comprehensive_data)
                export_files["csv"] = str(csv_file)

            # Excel Export - Multi-sheet workbook
            if "excel" in formats:
                excel_file = self._export_stories_excel(comprehensive_data, employee_stories)
                export_files["excel"] = str(excel_file)

            # XML Export - Structured markup
            if "xml" in formats:
                xml_file = self._export_stories_xml(comprehensive_data, employee_stories)
                export_files["xml"] = str(xml_file)

            # Markdown Export - Human-readable reports
            if "markdown" in formats:
                markdown_file = self._export_stories_markdown(comprehensive_data, employee_stories)
                export_files["markdown"] = str(markdown_file)

            self._log(f"Successfully exported stories in {len(export_files)} formats")
            return export_files

        except Exception as e:
            self._log(f"Failed to export employee stories: {e}", "error")
            raise

    def _prepare_comprehensive_story_data(
        self, employee_stories: Dict[str, List], population_data: List[Dict], cycle_data: Optional[pd.DataFrame] = None
    ) -> List[Dict]:
        """Prepare comprehensive story data for export.

        Args:
          employee_stories: Dict[str:
          List]:
          population_data: List[Dict]:
          cycle_data: Optional[pd.DataFrame]:  (Default value = None)

        Returns:
        """

        # Create lookup for population data
        pop_lookup = {emp["employee_id"]: emp for emp in population_data}

        comprehensive_stories = []

        for category, stories in employee_stories.items():
            for story in stories:
                # Extract story data
                if hasattr(story, "__dict__"):
                    story_data = story.__dict__.copy()
                else:
                    story_data = story.copy() if isinstance(story, dict) else {}

                emp_id = story_data.get("employee_id", "Unknown")

                # Add population context
                if emp_id in pop_lookup:
                    pop_data = pop_lookup[emp_id]
                    story_data.update(
                        {
                            "initial_level": pop_data.get("level"),
                            "initial_gender": pop_data.get("gender"),
                            "initial_performance_rating": pop_data.get("performance_rating"),
                            "department": pop_data.get("department", "Unknown"),
                        }
                    )

                # Add cycle progression if available
                if cycle_data is not None and not cycle_data.empty:
                    emp_cycles = cycle_data[cycle_data["employee_id"] == emp_id]
                    if not emp_cycles.empty:
                        # Ensure numeric columns are properly typed
                        emp_cycles = emp_cycles.copy()
                        emp_cycles["salary"] = pd.to_numeric(emp_cycles["salary"], errors="coerce")
                        emp_cycles["performance_rating"] = pd.to_numeric(
                            emp_cycles["performance_rating"], errors="coerce"
                        )
                        emp_cycles["level"] = pd.to_numeric(emp_cycles["level"], errors="coerce")

                        story_data.update(
                            {
                                "cycle_count": len(emp_cycles),
                                "salary_progression": emp_cycles["salary"].tolist(),
                                "level_progression": emp_cycles["level"].tolist(),
                                "performance_progression": emp_cycles["performance_rating"].tolist(),
                                "salary_growth_rate": self._calculate_growth_rate(emp_cycles["salary"].tolist()),
                                "level_changes": len(emp_cycles["level"].unique()) - 1,
                                "performance_improvement": (
                                    float(
                                        emp_cycles["performance_rating"].iloc[-1]
                                        - emp_cycles["performance_rating"].iloc[0]
                                    )
                                    if len(emp_cycles) > 1
                                    else 0
                                ),
                            }
                        )

                # Add metadata
                story_data.update(
                    {
                        "export_timestamp": self.export_timestamp,
                        "category": category,
                        "story_id": f"{category}_{emp_id}_{self.export_timestamp}",
                    }
                )

                comprehensive_stories.append(story_data)

        return comprehensive_stories

    def _calculate_growth_rate(self, values: List[float]) -> float:
        """Calculate compound growth rate.

        Args:
          values: List[float]:

        Returns:
        """
        if len(values) < 2:
            return 0.0

        initial_value = values[0]
        final_value = values[-1]
        periods = len(values) - 1

        if initial_value <= 0:
            return 0.0

        growth_rate = ((final_value / initial_value) ** (1 / periods)) - 1
        return round(growth_rate * 100, 2)  # Return as percentage

    def _export_stories_json(self, comprehensive_data: List[Dict], employee_stories: Dict[str, List]) -> Path:
        """Export stories as comprehensive JSON.

        Args:
          comprehensive_data: List[Dict]:
          employee_stories: Dict[str:
          List]:

        Returns:
        """

        json_export = {
            "metadata": {
                "export_timestamp": self.export_timestamp,
                "total_stories": len(comprehensive_data),
                "categories": list(employee_stories.keys()),
                "stories_per_category": {cat: len(stories) for cat, stories in employee_stories.items()},
                "export_version": "1.0",
            },
            "stories": comprehensive_data,
            "category_summaries": {},
        }

        # Add category summaries
        for category in employee_stories:
            if category_stories := [story for story in comprehensive_data if story.get("category") == category]:
                salaries = [story.get("current_salary", 0) for story in category_stories if story.get("current_salary")]
                growths = [
                    story.get("total_growth_percent", 0)
                    for story in category_stories
                    if story.get("total_growth_percent")
                ]

                json_export["category_summaries"][category] = {
                    "story_count": len(category_stories),
                    "avg_current_salary": sum(salaries) / len(salaries) if salaries else 0,
                    "avg_growth_percent": sum(growths) / len(growths) if growths else 0,
                    "salary_range": [min(salaries), max(salaries)] if salaries else [0, 0],
                }

        json_file = self.output_base_dir / f"employee_stories_comprehensive_{self.export_timestamp}.json"

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_export, f, indent=2, default=str, ensure_ascii=False)

        return json_file

    def _export_stories_csv(self, comprehensive_data: List[Dict]) -> Path:
        """Export stories as flat CSV for analysis.

        Args:
          comprehensive_data: List[Dict]:

        Returns:
        """

        if not comprehensive_data:
            # Create empty CSV with headers
            csv_file = self.output_base_dir / f"employee_stories_flat_{self.export_timestamp}.csv"
            with open(csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["No stories available"])
            return csv_file

        # Normalize data for CSV (flatten nested structures)
        flattened_data = []

        for story in comprehensive_data:
            flat_story = {}
            for key, value in story.items():
                if isinstance(value, list):
                    # Convert lists to comma-separated strings
                    flat_story[key] = ",".join(map(str, value)) if value else ""
                elif isinstance(value, dict):
                    # Flatten nested dicts with prefixed keys
                    for nested_key, nested_value in value.items():
                        flat_story[f"{key}_{nested_key}"] = nested_value
                else:
                    flat_story[key] = value

            flattened_data.append(flat_story)

        # Create CSV
        csv_file = self.output_base_dir / f"employee_stories_flat_{self.export_timestamp}.csv"

        if flattened_data:
            df = pd.DataFrame(flattened_data)
            df.to_csv(csv_file, index=False, encoding="utf-8")

        return csv_file

    def _export_stories_excel(self, comprehensive_data: List[Dict], employee_stories: Dict[str, List]) -> Path:
        """Export stories as multi-sheet Excel workbook.

        Args:
          comprehensive_data: List[Dict]:
          employee_stories: Dict[str:
          List]:

        Returns:
        """

        excel_file = self.output_base_dir / f"employee_stories_workbook_{self.export_timestamp}.xlsx"

        with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
            # Summary sheet
            summary_data = []
            for category in employee_stories:
                if category_stories := [s for s in comprehensive_data if s.get("category") == category]:
                    salaries = [s.get("current_salary", 0) for s in category_stories]
                    growths = [s.get("total_growth_percent", 0) for s in category_stories]

                    summary_data.append(
                        {
                            "Category": category.replace("_", " ").title(),
                            "Story Count": len(category_stories),
                            "Avg Current Salary": (sum(salaries) / len(salaries) if salaries else 0),
                            "Avg Growth %": (sum(growths) / len(growths) if growths else 0),
                            "Min Salary": min(salaries, default=0),
                            "Max Salary": max(salaries) if salaries else 0,
                        }
                    )

            if summary_data:
                pd.DataFrame(summary_data).to_excel(writer, sheet_name="Summary", index=False)

            # Individual category sheets
            for category in employee_stories:
                if category_stories := [s for s in comprehensive_data if s.get("category") == category]:
                    # Create DataFrame for category
                    df = pd.DataFrame(category_stories)

                    # Clean up column names
                    df.columns = [col.replace("_", " ").title() for col in df.columns]

                    # Write to sheet (truncate long sheet names)
                    sheet_name = category.replace("_", " ").title()[:30]
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

            # All stories sheet (flattened)
            if comprehensive_data:
                all_stories_df = pd.DataFrame(comprehensive_data)
                all_stories_df.columns = [col.replace("_", " ").title() for col in all_stories_df.columns]
                all_stories_df.to_excel(writer, sheet_name="All Stories", index=False)

        return excel_file

    def _export_stories_xml(self, comprehensive_data: List[Dict], employee_stories: Dict[str, List]) -> Path:
        """Export stories as structured XML.

        Args:
          comprehensive_data: List[Dict]:
          employee_stories: Dict[str:
          List]:

        Returns:
        """

        root = ET.Element("employee_stories")
        root.set("export_timestamp", self.export_timestamp)
        root.set("total_stories", str(len(comprehensive_data)))

        # Add metadata
        metadata = ET.SubElement(root, "metadata")
        ET.SubElement(metadata, "export_version").text = "1.0"
        ET.SubElement(metadata, "total_categories").text = str(len(employee_stories))

        categories_elem = ET.SubElement(metadata, "categories")
        for category in employee_stories:
            cat_elem = ET.SubElement(categories_elem, "category")
            cat_elem.set("name", category)
            cat_elem.set("story_count", str(len([s for s in comprehensive_data if s.get("category") == category])))

        # Add stories by category
        stories_elem = ET.SubElement(root, "stories")

        for category in employee_stories:
            category_elem = ET.SubElement(stories_elem, "category")
            category_elem.set("name", category)

            category_stories = [s for s in comprehensive_data if s.get("category") == category]
            for story in category_stories:
                story_elem = ET.SubElement(category_elem, "story")
                story_elem.set("id", str(story.get("story_id", "unknown")))

                for key, value in story.items():
                    if key != "story_id":  # Already used as attribute
                        elem = ET.SubElement(story_elem, key.replace(" ", "_").lower())
                        if isinstance(value, list):
                            elem.text = ",".join(map(str, value))
                        elif isinstance(value, dict):
                            elem.text = json.dumps(value)
                        else:
                            elem.text = str(value) if value is not None else ""

        # Write XML file
        xml_file = self.output_base_dir / f"employee_stories_{self.export_timestamp}.xml"

        # Pretty print XML
        from xml.dom import minidom

        rough_string = ET.tostring(root, encoding="unicode")
        reparsed = minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="  ")

        with open(xml_file, "w", encoding="utf-8") as f:
            f.write(pretty_xml)

        return xml_file

    def _export_stories_markdown(self, comprehensive_data: List[Dict], employee_stories: Dict[str, List]) -> Path:
        """Export stories as formatted Markdown report.

        Args:
          comprehensive_data: List[Dict]:
          employee_stories: Dict[str:
          List]:

        Returns:
        """

        markdown_file = self.output_base_dir / f"employee_stories_report_{self.export_timestamp}.md"

        lines = [
            "# Employee Story Analysis Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ]
        lines.append(f"**Total Stories:** {len(comprehensive_data)}")
        lines.extend((f"**Categories:** {len(employee_stories)}", ""))
        # Executive Summary
        lines.append("## Executive Summary")
        lines.append("")

        total_tracked = len(comprehensive_data)
        if total_tracked > 0:
            avg_growth = sum(s.get("total_growth_percent", 0) for s in comprehensive_data) / total_tracked
            avg_salary = sum(s.get("current_salary", 0) for s in comprehensive_data if s.get("current_salary", 0) > 0)
            salary_count = sum(bool(s.get("current_salary", 0) > 0) for s in comprehensive_data)
            avg_salary = avg_salary / salary_count if salary_count > 0 else 0

            lines.append(f"- **Average Salary Growth:** {avg_growth:.1f}%")
            lines.append(f"- **Average Current Salary:** £{avg_salary:,.0f}")
            lines.append("")

        # Category Analysis
        lines.append("## Category Analysis")
        lines.append("")

        for category, stories in employee_stories.items():
            if not stories:
                continue

            lines.append(f"### {category.replace('_', ' ').title()}")
            lines.append("")

            category_stories = [s for s in comprehensive_data if s.get("category") == category]
            lines.append(f"**Stories in Category:** {len(category_stories)}")

            if category_stories:
                salaries = [s.get("current_salary", 0) for s in category_stories if s.get("current_salary", 0) > 0]
                growths = [s.get("total_growth_percent", 0) for s in category_stories]

                if salaries:
                    lines.append(f"**Average Salary:** £{sum(salaries)/len(salaries):,.0f}")
                    lines.append(f"**Salary Range:** £{min(salaries):,.0f} - £{max(salaries):,.0f}")

                if growths:
                    lines.append(f"**Average Growth:** {sum(growths)/len(growths):.1f}%")

                lines.append("")
                lines.append("#### Individual Stories")
                lines.append("")

                for story in category_stories[:5]:  # Show first 5 stories
                    emp_id = story.get("employee_id", "Unknown")
                    current_salary = story.get("current_salary", 0)
                    growth = story.get("total_growth_percent", 0)
                    summary = story.get("story_summary", "No summary available")

                    lines.append(f"**Employee {emp_id}**")
                    lines.append(f"- Current Salary: £{current_salary:,.0f}")
                    lines.append(f"- Growth: {growth:+.1f}%")
                    lines.append(f"- Story: {summary}")
                    lines.append("")

                if len(category_stories) > 5:
                    lines.append(f"*... and {len(category_stories) - 5} more stories in this category*")
                    lines.append("")

        # Detailed Analysis
        lines.append("## Detailed Statistical Analysis")
        lines.append("")

        if comprehensive_data:
            # Growth distribution
            growths = [s.get("total_growth_percent", 0) for s in comprehensive_data]
            positive_growth = sum(bool(g > 0) for g in growths)
            negative_growth = sum(bool(g < 0) for g in growths)

            lines.append("### Growth Analysis")
            lines.append(
                f"- **Positive Growth:** {positive_growth} employees ({positive_growth/len(growths)*100:.1f}%)"
            )
            lines.append(
                f"- **Negative Growth:** {negative_growth} employees ({negative_growth/len(growths)*100:.1f}%)"
            )
            lines.append(f"- **Average Growth:** {sum(growths)/len(growths):.1f}%")
            lines.append("")

            if levels := [s.get("initial_level", 0) for s in comprehensive_data if s.get("initial_level", 0) > 0]:
                level_dist = {}
                for level in levels:
                    level_dist[level] = level_dist.get(level, 0) + 1

                lines.append("### Level Distribution")
                for level in sorted(level_dist.keys()):
                    count = level_dist[level]
                    percentage = count / len(levels) * 100
                    lines.append(f"- **Level {level}:** {count} employees ({percentage:.1f}%)")
                lines.append("")

        # Footer
        lines.append("---")
        lines.append("*Report generated by Advanced Story Export System v1.0*")
        lines.append(f"*Export ID: {self.export_timestamp}*")

        # Write markdown file
        with open(markdown_file, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return markdown_file

    def export_comparative_analysis(
        self, employee_stories: Dict[str, List], population_data: List[Dict], output_format: str = "json"
    ) -> str:
        """Export comparative analysis across employee categories.

        Args:
          employee_stories: Stories organized by category
          population_data: Full population data
          output_format: Output format ('json', 'csv', 'excel')
          employee_stories: Dict[str:
          List]:
          population_data: List[Dict]:
          output_format: str:  (Default value = "json")

        Returns:
          : Path to exported file
        """
        self._log(f"Generating comparative analysis in {output_format} format")

        # Create comparative analysis data
        analysis_data = {
            "metadata": {
                "analysis_timestamp": self.export_timestamp,
                "categories_analyzed": list(employee_stories.keys()),
                "total_population": len(population_data),
            },
            "category_comparisons": {},
            "cross_category_analysis": {},
            "population_benchmarks": {},
        }

        # Population benchmarks
        pop_df = pd.DataFrame(population_data)
        analysis_data["population_benchmarks"] = {
            "median_salary": float(pop_df["salary"].median()),
            "mean_salary": float(pop_df["salary"].mean()),
            "salary_std": float(pop_df["salary"].std()),
            "gender_distribution": pop_df["gender"].value_counts().to_dict(),
            "level_distribution": pop_df["level"].value_counts().to_dict(),
        }

        # Category comparisons
        all_story_data = []
        for category, stories in employee_stories.items():
            if not stories:
                continue

            category_metrics = {
                "story_count": len(stories),
                "employees": [],
                "salary_stats": {},
                "growth_stats": {},
                "level_distribution": {},
                "gender_distribution": {},
            }

            # Collect employee data for this category
            emp_data = []
            for story in stories:
                story_dict = story.__dict__ if hasattr(story, "__dict__") else story
                if emp_id := story_dict.get("employee_id"):
                    if pop_record := next(
                        (emp for emp in population_data if emp["employee_id"] == emp_id),
                        None,
                    ):
                        combined_data = {**pop_record, **story_dict}
                        emp_data.append(combined_data)
                        all_story_data.append({**combined_data, "category": category})

            if emp_data:
                emp_df = pd.DataFrame(emp_data)

                # Calculate statistics
                category_metrics["salary_stats"] = {
                    "mean": float(emp_df["salary"].mean()),
                    "median": float(emp_df["salary"].median()),
                    "std": float(emp_df["salary"].std()),
                    "min": float(emp_df["salary"].min()),
                    "max": float(emp_df["salary"].max()),
                }

                if "total_growth_percent" in emp_df.columns:
                    growth_col = emp_df["total_growth_percent"].dropna()
                    if not growth_col.empty:
                        category_metrics["growth_stats"] = {
                            "mean": float(growth_col.mean()),
                            "median": float(growth_col.median()),
                            "std": float(growth_col.std()),
                            "min": float(growth_col.min()),
                            "max": float(growth_col.max()),
                        }

                category_metrics["level_distribution"] = emp_df["level"].value_counts().to_dict()
                category_metrics["gender_distribution"] = emp_df["gender"].value_counts().to_dict()

            analysis_data["category_comparisons"][category] = category_metrics

        # Cross-category analysis
        if all_story_data:
            story_df = pd.DataFrame(all_story_data)

            # Find overlapping employees (if any)
            emp_category_counts = story_df["employee_id"].value_counts()
            overlapping_employees = emp_category_counts[emp_category_counts > 1].index.tolist()

            analysis_data["cross_category_analysis"] = {
                "overlapping_employees": overlapping_employees,
                "overlap_count": len(overlapping_employees),
                "category_correlations": {},
            }

            # Calculate category correlations if possible
            if len(employee_stories) > 1:
                categories = list(employee_stories.keys())
                for i, cat1 in enumerate(categories):
                    for cat2 in categories[i + 1 :]:
                        cat1_employees = set(story_df[story_df["category"] == cat1]["employee_id"])
                        cat2_employees = set(story_df[story_df["category"] == cat2]["employee_id"])

                        overlap = len(cat1_employees.intersection(cat2_employees))
                        union = len(cat1_employees.union(cat2_employees))
                        jaccard_similarity = overlap / union if union > 0 else 0

                        analysis_data["cross_category_analysis"]["category_correlations"][f"{cat1}_vs_{cat2}"] = {
                            "overlap_employees": overlap,
                            "jaccard_similarity": jaccard_similarity,
                            "cat1_unique": len(cat1_employees - cat2_employees),
                            "cat2_unique": len(cat2_employees - cat1_employees),
                        }

        # Export in requested format
        if output_format.lower() == "json":
            output_file = self.output_base_dir / f"comparative_analysis_{self.export_timestamp}.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(analysis_data, f, indent=2, default=str, ensure_ascii=False)

        elif output_format.lower() == "csv":
            # Flatten data for CSV
            flattened_rows = []
            for category, metrics in analysis_data["category_comparisons"].items():
                row = {"category": category}
                row |= metrics["salary_stats"]
                if metrics["growth_stats"]:
                    row.update({f"growth_{k}": v for k, v in metrics["growth_stats"].items()})
                flattened_rows.append(row)

            output_file = self.output_base_dir / f"comparative_analysis_{self.export_timestamp}.csv"
            if flattened_rows:
                pd.DataFrame(flattened_rows).to_csv(output_file, index=False)

        elif output_format.lower() == "excel":
            output_file = self.output_base_dir / f"comparative_analysis_{self.export_timestamp}.xlsx"

            with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
                # Summary sheet
                summary_rows = []
                for category, metrics in analysis_data["category_comparisons"].items():
                    row = {
                        "Category": category.replace("_", " ").title(),
                        "Story Count": metrics["story_count"],
                        "Mean Salary": metrics["salary_stats"].get("mean", 0),
                        "Median Salary": metrics["salary_stats"].get("median", 0),
                        "Salary Range": f"£{metrics['salary_stats'].get('min', 0):,.0f} - £{metrics['salary_stats'].get('max', 0):,.0f}",
                    }
                    if metrics["growth_stats"]:
                        row["Mean Growth %"] = metrics["growth_stats"].get("mean", 0)
                    summary_rows.append(row)

                if summary_rows:
                    pd.DataFrame(summary_rows).to_excel(writer, sheet_name="Summary", index=False)

                # Detailed analysis sheets
                for category, metrics in analysis_data["category_comparisons"].items():
                    if metrics.get("employees"):
                        df = pd.DataFrame(metrics["employees"])
                        sheet_name = category.replace("_", " ").title()[:30]
                        df.to_excel(writer, sheet_name=sheet_name, index=False)

        self._log(f"Comparative analysis exported: {output_file}")
        return str(output_file)

    def get_export_summary(self) -> Dict[str, Any]:
        """Get summary of export capabilities and recent exports."""

        # Count recent exports
        recent_exports = list(self.output_base_dir.glob(f"*{self.export_timestamp}*"))

        return {
            "export_capabilities": {
                "supported_formats": ["json", "csv", "excel", "xml", "markdown"],
                "features": [
                    "Comprehensive story data export",
                    "Multi-format support",
                    "Comparative analysis",
                    "Statistical summaries",
                    "Human-readable reports",
                ],
            },
            "recent_session": {
                "timestamp": self.export_timestamp,
                "files_generated": len(recent_exports),
                "export_directory": str(self.output_base_dir),
            },
            "version": "1.0",
        }

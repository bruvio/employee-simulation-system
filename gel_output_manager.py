#!/usr/bin/env python3

from datetime import datetime
import json
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional, Union

from logger import LOGGER


class GELOutputManager:
    """
    Clean deterministic output directory manager for GEL scenario reports.

    Creates structured output directories as specified in PRP:
    results/GEL/run_2025-08-14_09-00Z/
    ├─ index.html
    ├─ report.md
    ├─ manifest.json
    └─ assets/
       ├─ charts/*.png
       ├─ tables/*.csv
       └─ figures/*.svg
    """

    def __init__(self, base_results_dir: Union[str, Path] = "results"):
        self.base_results_dir = Path(base_results_dir)
        self.base_results_dir.mkdir(exist_ok=True)
        self.logger = LOGGER

    def create_gel_run_directory(
        self, org: str = "GEL", timestamp: Optional[datetime] = None, create_latest_link: bool = True
    ) -> Dict[str, Path]:
        """
        Create deterministic GEL run directory structure.

        Args:
            org: Organization identifier (default: GEL)
            timestamp: Optional timestamp (defaults to current UTC)
            create_latest_link: Create convenience 'latest' symlink

        Returns:
            Dictionary with all created directory paths
        """
        if timestamp is None:
            timestamp = datetime.utcnow()

        # Format: run_2025-08-14_09-00Z
        run_label = timestamp.strftime("run_%Y-%m-%d_%H-%MZ")

        # Create organization directory
        org_dir = self.base_results_dir / org
        org_dir.mkdir(exist_ok=True)

        # Create run-specific directory
        run_dir = org_dir / run_label
        if run_dir.exists():
            self.logger.warning(f"Run directory already exists: {run_dir}")
            # Add microseconds to avoid conflicts
            run_label = timestamp.strftime("run_%Y-%m-%d_%H-%M-%fZ")
            run_dir = org_dir / run_label

        # Create directory structure
        directories = {
            "run_root": run_dir,
            "assets": run_dir / "assets",
            "charts": run_dir / "assets" / "charts",
            "tables": run_dir / "assets" / "tables",
            "figures": run_dir / "assets" / "figures",
        }

        # Create all directories
        for dir_path in directories.values():
            dir_path.mkdir(parents=True, exist_ok=True)

        # Create convenience 'latest' symlink/reference
        if create_latest_link:
            self._create_latest_link(org_dir, run_dir)

        self.logger.info(f"Created GEL run directory: {run_dir}")
        return directories

    def _create_latest_link(self, org_dir: Path, run_dir: Path) -> None:
        """
        Create convenience 'latest' link to current run.

        Uses symlink on Unix/Mac, copies on Windows for compatibility.
        """
        latest_path = org_dir / "latest"

        try:
            # Remove existing latest link/directory
            if latest_path.exists():
                if latest_path.is_symlink():
                    latest_path.unlink()
                elif latest_path.is_dir():
                    shutil.rmtree(latest_path)
                else:
                    latest_path.unlink()

            # Create symlink (Unix/Mac) or copy (Windows fallback)
            try:
                latest_path.symlink_to(run_dir.name, target_is_directory=True)
                self.logger.debug(f"Created symlink: {latest_path} -> {run_dir.name}")
            except (OSError, NotImplementedError):
                # Fallback for Windows or systems without symlink support
                shutil.copytree(run_dir, latest_path)
                self.logger.debug(f"Created copy: {latest_path} (symlinks not supported)")

        except Exception as e:
            self.logger.warning(f"Failed to create latest link: {e}")

    def organize_gel_outputs(
        self,
        run_directories: Dict[str, Path],
        html_report: Optional[Path] = None,
        markdown_report: Optional[Path] = None,
        manifest_data: Optional[Dict[str, Any]] = None,
        chart_files: Optional[List[Path]] = None,
        table_files: Optional[List[Path]] = None,
        figure_files: Optional[List[Path]] = None,
        cleanup_temp: bool = True,
    ) -> Dict[str, Path]:
        """
        Organize and move GEL outputs to final directory structure.

        Args:
            run_directories: Directory structure from create_gel_run_directory
            html_report: Path to generated HTML report
            markdown_report: Path to generated Markdown report
            manifest_data: Manifest data to write as JSON
            chart_files: List of chart files to move to assets/charts/
            table_files: List of table files to move to assets/tables/
            figure_files: List of figure files to move to assets/figures/
            cleanup_temp: Remove temporary files after organizing

        Returns:
            Dictionary with final file paths
        """
        run_root = run_directories["run_root"]

        final_paths = {}

        # Move HTML report to index.html
        if html_report and html_report.exists():
            final_html = run_root / "index.html"
            shutil.copy2(html_report, final_html)
            final_paths["html_report"] = final_html
            self.logger.debug(f"Moved HTML report: {final_html}")

            if cleanup_temp and html_report.parent.name == "temp":
                html_report.unlink()

        # Move Markdown report to report.md
        if markdown_report and markdown_report.exists():
            final_md = run_root / "report.md"
            shutil.copy2(markdown_report, final_md)
            final_paths["markdown_report"] = final_md
            self.logger.debug(f"Moved Markdown report: {final_md}")

            if cleanup_temp and markdown_report.parent.name == "temp":
                markdown_report.unlink()

        # Create manifest.json
        if manifest_data:
            manifest_path = run_root / "manifest.json"
            with open(manifest_path, "w", encoding="utf-8") as f:
                json.dump(manifest_data, f, indent=2, default=str)
            final_paths["manifest"] = manifest_path
            self.logger.debug(f"Created manifest: {manifest_path}")

        # Organize asset files
        if chart_files:
            final_charts = self._organize_asset_files(chart_files, run_directories["charts"], "charts", cleanup_temp)
            final_paths["charts"] = final_charts

        if table_files:
            final_tables = self._organize_asset_files(table_files, run_directories["tables"], "tables", cleanup_temp)
            final_paths["tables"] = final_tables

        if figure_files:
            final_figures = self._organize_asset_files(
                figure_files, run_directories["figures"], "figures", cleanup_temp
            )
            final_paths["figures"] = final_figures

        self.logger.info(f"Organized GEL outputs in: {run_root}")
        return final_paths

    def _organize_asset_files(
        self, source_files: List[Path], target_dir: Path, asset_type: str, cleanup_temp: bool
    ) -> List[Path]:
        """
        Organize asset files into target directory.

        Args:
            source_files: List of source file paths
            target_dir: Target directory for assets
            asset_type: Type of assets (for logging)
            cleanup_temp: Remove source files if from temp directory

        Returns:
            List of final file paths
        """
        final_files = []

        for source_file in source_files:
            if not source_file.exists():
                self.logger.warning(f"Source {asset_type} file not found: {source_file}")
                continue

            # Use original filename or generate clean name
            final_file = target_dir / source_file.name

            # Handle name conflicts
            counter = 1
            while final_file.exists():
                stem = source_file.stem
                suffix = source_file.suffix
                final_file = target_dir / f"{stem}_{counter}{suffix}"
                counter += 1

            shutil.copy2(source_file, final_file)
            final_files.append(final_file)

            self.logger.debug(f"Moved {asset_type} file: {final_file}")

            # Clean up temporary files
            if cleanup_temp and source_file.parent.name in ["temp", "tmp", "temporary"]:
                source_file.unlink()

        return final_files

    def create_manifest_data(
        self,
        scenario: str,
        org: str,
        timestamp: datetime,
        config_hash: str,
        population: int,
        median_salary: float,
        below_median_pct: float,
        gender_gap_pct: float,
        intervention_budget_pct: float,
        recommended_uplifts_cost_pct: float,
        additional_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Create standardized manifest data for GEL scenarios.

        Args:
            scenario: Scenario name (e.g., "GEL")
            org: Organization identifier
            timestamp: Analysis timestamp
            config_hash: SHA256 hash of roles configuration
            population: Total population size
            median_salary: Overall median salary
            below_median_pct: Percentage below median
            gender_gap_pct: Gender pay gap percentage
            intervention_budget_pct: Budget percentage for interventions
            recommended_uplifts_cost_pct: Cost of recommendations as percentage
            additional_metadata: Optional additional metadata

        Returns:
            Dictionary with manifest data
        """
        manifest = {
            "scenario": scenario,
            "org": org,
            "timestamp_utc": timestamp.isoformat() + "Z",
            "roles_config_sha256": config_hash,
            "population": population,
            "median_salary": median_salary,
            "below_median_pct": below_median_pct,
            "gender_gap_pct": gender_gap_pct,
            "intervention_budget_pct": intervention_budget_pct,
            "recommended_uplifts_cost_pct": recommended_uplifts_cost_pct,
            "generated_files": {
                "html_report": "index.html",
                "markdown_report": "report.md",
                "manifest": "manifest.json",
                "assets_directory": "assets/",
            },
            "directory_structure": {
                "charts": "assets/charts/",
                "tables": "assets/tables/",
                "figures": "assets/figures/",
            },
        }

        # Add additional metadata if provided
        if additional_metadata:
            manifest.update(additional_metadata)

        return manifest

    def validate_gel_output(self, run_directory: Path) -> Dict[str, Any]:
        """
        Validate GEL output directory structure and contents.

        Args:
            run_directory: Path to GEL run directory

        Returns:
            Dictionary with validation results
        """
        validation_results = {"valid": True, "errors": [], "warnings": [], "files_found": {}, "directory_structure": {}}

        # Check required files
        required_files = {"index.html": "HTML report", "report.md": "Markdown report", "manifest.json": "Run manifest"}

        for filename, description in required_files.items():
            file_path = run_directory / filename
            if file_path.exists():
                validation_results["files_found"][filename] = {
                    "exists": True,
                    "size": file_path.stat().st_size,
                    "description": description,
                }
            else:
                validation_results["valid"] = False
                validation_results["errors"].append(f"Required file missing: {filename} ({description})")

        # Check assets directory structure
        assets_dir = run_directory / "assets"
        if assets_dir.exists():
            for subdir in ["charts", "tables", "figures"]:
                subdir_path = assets_dir / subdir
                if subdir_path.exists():
                    file_count = len(list(subdir_path.glob("*")))
                    validation_results["directory_structure"][f"assets/{subdir}"] = {
                        "exists": True,
                        "file_count": file_count,
                    }
                else:
                    validation_results["warnings"].append(f"Assets subdirectory missing: {subdir}")
                    validation_results["directory_structure"][f"assets/{subdir}"] = {"exists": False, "file_count": 0}
        else:
            validation_results["warnings"].append("Assets directory missing")

        # Check manifest content
        manifest_path = run_directory / "manifest.json"
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest_data = json.load(f)

                required_keys = [
                    "scenario",
                    "org",
                    "timestamp_utc",
                    "population",
                    "median_salary",
                    "below_median_pct",
                    "gender_gap_pct",
                ]

                for key in required_keys:
                    if key not in manifest_data:
                        validation_results["warnings"].append(f"Manifest missing key: {key}")

                validation_results["manifest_valid"] = True
            except json.JSONDecodeError as e:
                validation_results["errors"].append(f"Invalid manifest JSON: {e}")
                validation_results["manifest_valid"] = False

        return validation_results

    def cleanup_old_runs(self, org: str = "GEL", keep_recent: int = 5, dry_run: bool = False) -> List[Path]:
        """
        Clean up old GEL run directories, keeping only recent ones.

        Args:
            org: Organization identifier
            keep_recent: Number of recent runs to keep
            dry_run: If True, only report what would be deleted

        Returns:
            List of directories that were (or would be) deleted
        """
        org_dir = self.base_results_dir / org
        if not org_dir.exists():
            self.logger.info(f"No organization directory found: {org}")
            return []

        # Find all run directories
        run_dirs = []
        for item in org_dir.iterdir():
            if item.is_dir() and item.name.startswith("run_") and item.name != "latest":
                run_dirs.append(item)

        # Sort by modification time (newest first)
        run_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        # Identify directories to delete (keep only recent ones)
        to_delete = run_dirs[keep_recent:]

        if dry_run:
            self.logger.info(f"Would delete {len(to_delete)} old run directories (keeping {keep_recent})")
            for dir_path in to_delete:
                self.logger.info(f"  Would delete: {dir_path}")
        else:
            self.logger.info(f"Cleaning up {len(to_delete)} old run directories (keeping {keep_recent})")
            for dir_path in to_delete:
                try:
                    shutil.rmtree(dir_path)
                    self.logger.debug(f"Deleted old run: {dir_path}")
                except Exception as e:
                    self.logger.error(f"Failed to delete {dir_path}: {e}")

        return to_delete


if __name__ == "__main__":
    # Test the GEL output manager
    manager = GELOutputManager(base_results_dir="test_results")

    # Create sample run directory
    timestamp = datetime.utcnow()
    directories = manager.create_gel_run_directory(timestamp=timestamp)

    print("Created directories:")
    for name, path in directories.items():
        print(f"  {name}: {path}")

    # Create sample manifest
    manifest_data = manager.create_manifest_data(
        scenario="GEL",
        org="GEL",
        timestamp=timestamp,
        config_hash="abc123...",
        population=201,
        median_salary=71500,
        below_median_pct=42.3,
        gender_gap_pct=6.8,
        intervention_budget_pct=0.5,
        recommended_uplifts_cost_pct=0.49,
    )

    # Organize outputs (simulated)
    final_paths = manager.organize_gel_outputs(run_directories=directories, manifest_data=manifest_data)

    print(f"Final paths: {final_paths}")

    # Validate output
    validation = manager.validate_gel_output(directories["run_root"])
    print(f"Validation results: {validation}")

#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

from datetime import datetime
import json
from pathlib import Path
import shutil
from typing import Any, Dict, List, Optional

import pandas as pd


class FileOptimizationManager:
    """
    Enhanced file organization and optimization for employee simulation runs.

    Implements structured directories and consolidated outputs as per Phase 3 PRP requirements.

    Args:

    Returns:
    """

    def __init__(self, base_output_dir: str = "artifacts", base_images_dir: str = "images"):
        self.base_output_dir = Path(base_output_dir)
        self.base_images_dir = Path(base_images_dir)
        self.current_run_id = None
        self.run_structure = {}

        # Ensure base directories exist
        self.base_output_dir.mkdir(exist_ok=True)
        self.base_images_dir.mkdir(exist_ok=True)

    def create_run_directory(self, run_id: str, enable_story_tracking: bool = False) -> Dict[str, Path]:
        """
        Create structured directory hierarchy for a simulation run.

        Args:
          run_id: Unique identifier for the simulation run
          enable_story_tracking: Whether to create story-specific directories
          run_id: str:
          enable_story_tracking: bool:  (Default value = False)

        Returns:
          : Dict containing all created directory paths
        """
        self.current_run_id = run_id

        # Main run directory
        run_dir = self.base_output_dir / f"simulation_run_{run_id}"
        run_images_dir = self.base_images_dir / f"simulation_run_{run_id}"

        # Core directory structure
        directories = {
            "run_root": run_dir,
            "population_data": run_dir / "population_data",
            "simulation_results": run_dir / "simulation_results",
            "exports": run_dir / "exports",
            "logs": run_dir / "logs",
            "reports": run_dir / "reports",
            "images_root": run_images_dir,
            "charts": run_images_dir / "charts",
            "analysis_plots": run_images_dir / "analysis_plots",
        }

        # Story tracking directories (if enabled)
        if enable_story_tracking:
            directories |= {
                "employee_stories": run_dir / "employee_stories",
                "story_analysis": run_dir / "story_analysis",
                "story_visualizations": run_images_dir / "story_visualizations",
                "employee_progressions": run_images_dir / "employee_progressions",
                "salary_distributions_by_level": run_images_dir / "salary_distributions_by_level",
            }

        # Create all directories
        for dir_path in directories.values():
            dir_path.mkdir(parents=True, exist_ok=True)

        # Store structure for later use
        self.run_structure = directories

        # Create run metadata
        self._create_run_metadata(run_id, enable_story_tracking)

        return directories

    def _create_run_metadata(self, run_id: str, enable_story_tracking: bool):
        """
        Create metadata file for the run.

        Args:
          run_id: str:
          enable_story_tracking: bool:

        Returns:
        """
        metadata = {
            "run_id": run_id,
            "created_timestamp": datetime.now().isoformat(),
            "story_tracking_enabled": enable_story_tracking,
            "directory_structure": {k: str(v) for k, v in self.run_structure.items()},
            "file_organization_version": "1.0",
        }

        metadata_path = self.run_structure["run_root"] / "run_metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

    def organize_population_files(
        self, population_data: List[Dict], cycle_progressions: Optional[pd.DataFrame] = None
    ) -> Dict[str, str]:
        """
        Organize population-related files in structured format.

        Args:
          population_data: Initial employee population data
          cycle_progressions: DataFrame with cycle-by-cycle employee progressions
          population_data: List[Dict]:
          cycle_progressions: Optional[pd.DataFrame]:  (Default value = None)

        Returns:
          : Dict of generated file paths
        """
        if not self.run_structure:
            raise ValueError("Run directory not created. Call create_run_directory first.")

        pop_dir = self.run_structure["population_data"]

        # Save initial population
        population_path = pop_dir / "initial_population.json"
        with open(population_path, "w") as f:
            json.dump(population_data, f, indent=2, default=str)
        files_created = {"initial_population": str(population_path)}
        # Save population summary
        df = pd.DataFrame(population_data)
        summary = {
            "total_employees": len(population_data),
            "gender_distribution": df["gender"].value_counts().to_dict(),
            "level_distribution": df["level"].value_counts().sort_index().to_dict(),
            "salary_statistics": {
                "mean": float(df["salary"].mean()),
                "median": float(df["salary"].median()),
                "std": float(df["salary"].std()),
                "min": float(df["salary"].min()),
                "max": float(df["salary"].max()),
            },
        }

        summary_path = pop_dir / "population_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        files_created["population_summary"] = str(summary_path)

        # Save cycle progressions if provided
        if cycle_progressions is not None and not cycle_progressions.empty:
            progressions_path = pop_dir / "cycle_progressions.csv"
            cycle_progressions.to_csv(progressions_path, index=False)
            files_created["cycle_progressions"] = str(progressions_path)

            # Also save compressed version for large datasets
            if len(cycle_progressions) > 1000:
                compressed_path = pop_dir / "cycle_progressions.csv.gz"
                cycle_progressions.to_csv(compressed_path, index=False, compression="gzip")
                files_created["cycle_progressions_compressed"] = str(compressed_path)

        return files_created

    def organize_simulation_results(
        self, inequality_metrics: pd.DataFrame, convergence_info: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Organize simulation result files.

        Args:
          inequality_metrics: DataFrame with inequality progression across cycles
          convergence_info: Information about convergence
          inequality_metrics: pd.DataFrame:
          convergence_info: Dict[str:
          Any]:

        Returns:
          : Dict of generated file paths
        """
        if not self.run_structure:
            raise ValueError("Run directory not created. Call create_run_directory first.")

        sim_dir = self.run_structure["simulation_results"]

        # Save inequality metrics
        metrics_path = sim_dir / "inequality_progression.csv"
        inequality_metrics.to_csv(metrics_path, index=False)
        files_created = {"inequality_metrics": str(metrics_path)}
        # Save convergence analysis
        convergence_path = sim_dir / "convergence_analysis.json"
        with open(convergence_path, "w") as f:
            json.dump(convergence_info, f, indent=2, default=str)
        files_created["convergence_analysis"] = str(convergence_path)

        # Generate simulation summary
        summary = {
            "total_cycles": len(inequality_metrics) - 1,  # Subtract initial state
            "final_gini_coefficient": (
                None if inequality_metrics.empty else float(inequality_metrics.iloc[-1]["gini_coefficient"])
            ),
            "convergence_achieved": convergence_info.get("converged", False),
            "simulation_completed_at": datetime.now().isoformat(),
        }

        summary_path = sim_dir / "simulation_summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f, indent=2)
        files_created["simulation_summary"] = str(summary_path)

        return files_created

    def organize_story_files(
        self, employee_stories: Dict[str, List], story_timeline: Optional[pd.DataFrame] = None
    ) -> Dict[str, str]:
        """
        Organize employee story files by category.

        Args:
          employee_stories: Stories organized by category
          story_timeline: Timeline data for all tracked employees
          employee_stories: Dict[str:
          List]:
          story_timeline: Optional[pd.DataFrame]:  (Default value = None)

        Returns:
          : Dict of generated file paths
        """
        if not self.run_structure or "employee_stories" not in self.run_structure:
            raise ValueError(
                "Story tracking directories not available. Enable story tracking when creating run directory."
            )

        files_created = {}
        stories_dir = self.run_structure["employee_stories"]
        analysis_dir = self.run_structure["story_analysis"]

        # Save stories by category
        for category, stories in employee_stories.items():
            if stories:
                category_path = stories_dir / f"{category}_stories.json"
                # Convert story objects to dictionaries for JSON serialization
                serializable_stories = []
                for story in stories:
                    if hasattr(story, "__dict__"):
                        serializable_stories.append(story.__dict__)
                    else:
                        serializable_stories.append(story)

                with open(category_path, "w") as f:
                    json.dump(serializable_stories, f, indent=2, default=str)
                files_created[f"{category}_stories"] = str(category_path)

        # Save story timeline if provided
        if story_timeline is not None and not story_timeline.empty:
            timeline_path = analysis_dir / "story_timeline.csv"
            story_timeline.to_csv(timeline_path, index=False)
            files_created["story_timeline"] = str(timeline_path)

        # Generate story analysis summary
        total_tracked = sum(len(stories) for stories in employee_stories.values())
        story_summary = {
            "total_tracked_employees": total_tracked,
            "categories_tracked": list(employee_stories.keys()),
            "stories_by_category": {cat: len(stories) for cat, stories in employee_stories.items()},
            "analysis_generated_at": datetime.now().isoformat(),
        }

        summary_path = analysis_dir / "story_analysis_summary.json"
        with open(summary_path, "w") as f:
            json.dump(story_summary, f, indent=2)
        files_created["story_analysis_summary"] = str(summary_path)

        return files_created

    def organize_export_files(self, export_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Organize exported data files (CSV, Excel, JSON)

        Args:
          export_data: Dictionary containing various export formats
          export_data: Dict[str:
          Any]:

        Returns:
          : Dict of organized file paths
        """
        if not self.run_structure:
            raise ValueError("Run directory not created. Call create_run_directory first.")

        files_created = {}
        exports_dir = self.run_structure["exports"]

        # Organize by export type and format
        for export_type, formats in export_data.items():
            if isinstance(formats, dict):
                type_dir = exports_dir / export_type
                type_dir.mkdir(exist_ok=True)

                for format_name, file_path in formats.items():
                    if file_path and Path(file_path).exists():
                        target_path = type_dir / Path(file_path).name
                        shutil.copy2(file_path, target_path)
                        files_created[f"{export_type}_{format_name}"] = str(target_path)

        return files_created

    def organize_visualization_files(self, viz_files: List[str]) -> Dict[str, str]:
        """
        Organize visualization files into appropriate subdirectories.

        Args:
          viz_files: List of visualization file paths
          viz_files: List[str]:

        Returns:
          : Dict of organized file paths
        """
        if not self.run_structure:
            raise ValueError("Run directory not created. Call create_run_directory first.")

        files_created = {}

        for viz_file in viz_files:
            if not viz_file or not Path(viz_file).exists():
                continue

            source_path = Path(viz_file)
            filename = source_path.name.lower()

            # Determine target directory based on filename patterns
            if "story" in filename or "employee" in filename:
                target_dir = self.run_structure.get("story_visualizations", self.run_structure["charts"])
            elif "salary" in filename or "distribution" in filename:
                target_dir = self.run_structure.get("salary_distributions_by_level", self.run_structure["charts"])
            elif "progression" in filename or "timeline" in filename:
                target_dir = self.run_structure.get("employee_progressions", self.run_structure["charts"])
            else:
                target_dir = self.run_structure["charts"]

            # Copy file to organized location
            target_path = target_dir / source_path.name
            shutil.copy2(source_path, target_path)
            files_created[source_path.stem] = str(target_path)

        return files_created

    def generate_run_index(self) -> str:
        """
        Generate comprehensive index file for the simulation run.

        Args:

        Returns:
          : Path to the generated index file
        """
        if not self.run_structure:
            raise ValueError("Run directory not created. Call create_run_directory first.")

        # Collect all files in the run directory
        run_root = self.run_structure["run_root"]
        images_root = self.run_structure["images_root"]

        file_inventory = {}

        # Scan artifacts directory
        for item in run_root.rglob("*"):
            if item.is_file() and item.name != "run_index.json":
                rel_path = item.relative_to(run_root)
                category = str(rel_path.parent) if rel_path.parent != Path(".") else "root"
                if category not in file_inventory:
                    file_inventory[category] = []
                file_inventory[category].append(
                    {
                        "filename": item.name,
                        "path": str(item),
                        "size_bytes": item.stat().st_size,
                        "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                    }
                )

        # Scan images directory
        if images_root.exists():
            for item in images_root.rglob("*"):
                if item.is_file():
                    rel_path = item.relative_to(images_root)
                    category = f"images/{rel_path.parent}" if rel_path.parent != Path(".") else "images/root"
                    if category not in file_inventory:
                        file_inventory[category] = []
                    file_inventory[category].append(
                        {
                            "filename": item.name,
                            "path": str(item),
                            "size_bytes": item.stat().st_size,
                            "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                        }
                    )

        # Generate index
        run_index = {
            "run_id": self.current_run_id,
            "index_generated_at": datetime.now().isoformat(),
            "directory_structure": {k: str(v) for k, v in self.run_structure.items()},
            "file_inventory": file_inventory,
            "total_files": sum(len(files) for files in file_inventory.values()),
            "total_size_bytes": sum(sum(f["size_bytes"] for f in files) for files in file_inventory.values()),
        }

        # Save index
        index_path = run_root / "run_index.json"
        with open(index_path, "w") as f:
            json.dump(run_index, f, indent=2)

        return str(index_path)

    def cleanup_temporary_files(self, temp_patterns: List[str] = None) -> int:
        """
        Clean up temporary files and optimize storage.

        Args:
          temp_patterns: List of glob patterns for temporary files to remove
          temp_patterns: List[str]:  (Default value = None)

        Returns:
          : Number of files cleaned up
        """
        if temp_patterns is None:
            temp_patterns = ["*.tmp", "*.temp", "*~", ".DS_Store"]

        cleaned_count = 0

        # Clean from base directories
        for base_dir in [self.base_output_dir, self.base_images_dir]:
            for pattern in temp_patterns:
                for temp_file in base_dir.rglob(pattern):
                    if temp_file.is_file():
                        temp_file.unlink()
                        cleaned_count += 1

        return cleaned_count

    def get_run_summary(self) -> Dict[str, Any]:
        """
        Get summary information about the current run organization.

        Args:

        Returns:
          : Dictionary with run organization summary
        """
        if not self.run_structure:
            return {"error": "No run directory created"}

        summary = {
            "run_id": self.current_run_id,
            "directories_created": len(self.run_structure),
            "directory_paths": {k: str(v) for k, v in self.run_structure.items()},
        }

        # Add file counts if directories exist
        for dir_name, dir_path in self.run_structure.items():
            if dir_path.exists():
                file_count = len([f for f in dir_path.rglob("*") if f.is_file()])
                summary[f"{dir_name}_file_count"] = file_count

        return summary

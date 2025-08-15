"""
Centralized path authority for the Employee Simulation System.

This module provides a single source of truth for all output paths,
ensuring consistent and deterministic run directories.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Optional


def repo_root(p: Optional[Path] = None) -> Path:
    """Find the repository root directory.
    
    Args:
        p: Starting path (defaults to this file's location)
        
    Returns:
        Path to repository root
    """
    p = (p or Path(__file__)).resolve()
    for parent in [p] + list(p.parents):
        if (
            (parent / ".git").exists() 
            or (parent / "pyproject.toml").exists() 
            or (parent / "requirements.txt").exists()
        ):
            return parent
    return Path.cwd().resolve()


# Global path constants
REPO_ROOT = repo_root()
BASE_OUTPUT = Path(os.environ.get("SIM_OUTPUT_DIR") or (REPO_ROOT / "results")).resolve()
RUN_STAMP = os.environ.get("SIM_RUN_STAMP") or datetime.utcnow().strftime("%Y%m%d_%H%M%S")
RUN_DIR = BASE_OUTPUT / f"run_{RUN_STAMP}"
ARTIFACTS_DIR = RUN_DIR / "artifacts"
CHARTS_DIR = RUN_DIR / "assets" / "charts"
TABLES_DIR = RUN_DIR / "assets" / "tables"


def get_population_size(cfg: dict, cli_value: Optional[int] = None) -> tuple[int, str]:
    """Get population size with strict enforcement and source tracking.
    
    Args:
        cfg: Configuration dictionary
        cli_value: CLI override value
        
    Returns:
        Tuple of (population_size, source_description)
        
    Raises:
        KeyError: If no population size is configured
        ValueError: If conflicting sizes are found
    """
    if cli_value is not None:
        return int(cli_value), "--population-size"
    
    keys = [k for k in ("population_size", "n_employees") if k in cfg]
    if not keys:
        raise KeyError(
            "Population size not configured. Set 'population_size' (preferred) or 'n_employees' in config"
        )
    
    if len(keys) == 2 and int(cfg["population_size"]) != int(cfg["n_employees"]):
        raise ValueError(
            f"Conflicting population sizes: population_size={cfg['population_size']} "
            f"!= n_employees={cfg['n_employees']}"
        )
    
    key = keys[0]
    return int(cfg[key]), f"config.{key}"


def ensure_dirs() -> None:
    """Create all required output directories."""
    for d in (ARTIFACTS_DIR, CHARTS_DIR, TABLES_DIR):
        d.mkdir(parents=True, exist_ok=True)


def get_artifact_path(filename: str) -> Path:
    """Get path for artifact files (JSON, etc.).
    
    Args:
        filename: Name of the artifact file
        
    Returns:
        Full path to artifact file
    """
    return ARTIFACTS_DIR / filename


def get_chart_path(filename: str) -> Path:
    """Get path for chart files (PNG, SVG, etc.).
    
    Args:
        filename: Name of the chart file
        
    Returns:
        Full path to chart file
    """
    return CHARTS_DIR / filename


def get_table_path(filename: str) -> Path:
    """Get path for table files (CSV, Excel, etc.).
    
    Args:
        filename: Name of the table file
        
    Returns:
        Full path to table file
    """
    return TABLES_DIR / filename


def validate_output_path(path: Path) -> None:
    """Validate that output path is writable.
    
    Args:
        path: Path to validate
        
    Raises:
        PermissionError: If path is not writable
        OSError: If path cannot be created or accessed
    """
    try:
        # Try to create the directory if it doesn't exist
        path.mkdir(parents=True, exist_ok=True)
        
        # Test if we can write to it by creating a temporary file
        test_file = path / ".write_test"
        test_file.write_text("test")
        test_file.unlink()
        
    except PermissionError:
        raise PermissionError(f"Output directory is not writable: {path}")
    except OSError as e:
        raise OSError(f"Cannot access output directory {path}: {e}")


def override_output_base(new_base: str) -> None:
    """Override the base output directory (for CLI --out flag).
    
    This function handles CLI --out flag integration with precedence over
    SIM_OUTPUT_DIR environment variable. CLI arguments take highest precedence,
    followed by environment variables, then defaults.
    
    Args:
        new_base: New base output directory path
        
    Raises:
        PermissionError: If the directory is not writable
        OSError: If the directory cannot be created or accessed
    """
    global BASE_OUTPUT, RUN_DIR, ARTIFACTS_DIR, CHARTS_DIR, TABLES_DIR
    
    BASE_OUTPUT = Path(new_base).resolve()
    validate_output_path(BASE_OUTPUT)
    
    RUN_DIR = BASE_OUTPUT / f"run_{RUN_STAMP}"
    ARTIFACTS_DIR = RUN_DIR / "artifacts"
    CHARTS_DIR = RUN_DIR / "assets" / "charts"
    TABLES_DIR = RUN_DIR / "assets" / "tables"


def check_migration_needed() -> dict:
    """Check for existing data that may need migration.
    
    Returns:
        dict: Information about existing data directories and recommendations
    """
    migration_info = {
        "legacy_artifacts": Path("artifacts").exists(),
        "legacy_results": Path("results").exists(),
        "recommendations": []
    }
    
    if migration_info["legacy_artifacts"]:
        artifacts_files = list(Path("artifacts").glob("*"))
        if artifacts_files:
            migration_info["recommendations"].append(
                "Legacy artifacts/ directory contains files. Consider archiving them before deletion."
            )
            migration_info["artifacts_files"] = len(artifacts_files)
    
    if migration_info["legacy_results"]:
        results_dirs = [d for d in Path("results").iterdir() if d.is_dir()]
        if results_dirs:
            migration_info["recommendations"].append(
                "Legacy results/ contains subdirectories. Review and archive important data."
            )
            migration_info["results_dirs"] = len(results_dirs)
    
    return migration_info
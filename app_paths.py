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
        if (parent / ".git").exists() or (parent / "pyproject.toml").exists() or (parent / "requirements.txt").exists():
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
        raise KeyError("Population size not configured. Set 'population_size' (preferred) or 'n_employees' in config")

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
    """Validate that output path is writable with comprehensive checks.

    Performs multiple validation steps:
    1. Checks if path exists and is accessible
    2. Attempts to create directory structure if needed
    3. Tests write permissions with temporary file creation
    4. Provides specific error messages for different failure scenarios

    Args:
        path: Path to validate

    Raises:
        PermissionError: If path is not writable with specific reason
        OSError: If path cannot be created or accessed with specific reason
        ValueError: If path is invalid (e.g., points to a file instead of directory)
    """
    try:
        # Check if path exists and is a file (not directory)
        if path.exists() and path.is_file():
            raise ValueError(f"Output path points to an existing file, not a directory: {path}")

        # Try to create the directory if it doesn't exist
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)

        # Test write permissions by creating a temporary file
        test_file = path / ".sim_write_test"
        try:
            test_file.write_text("write_test")
            test_file.unlink()
        except PermissionError:
            raise PermissionError(
                f"Output directory exists but is not writable: {path}\n"
                f"Check permissions and ensure you have write access to this location."
            )

    except PermissionError:
        # Re-raise permission errors with our detailed message
        raise
    except FileNotFoundError as e:
        raise OSError(f"Cannot create output directory (parent directory may not exist): {path}\n" f"Error: {e}")
    except OSError as e:
        if "No space left" in str(e).lower():
            raise OSError(f"Insufficient disk space to create output directory: {path}")
        elif "read-only" in str(e).lower():
            raise OSError(f"Cannot create directory on read-only filesystem: {path}")
        else:
            raise OSError(
                f"Cannot access or create output directory: {path}\n"
                f"Error: {e}\n"
                f"This may be due to insufficient permissions, invalid path, or filesystem issues."
            )


def override_output_base(new_base: str) -> None:
    """Override the base output directory (for CLI --out flag).

    PRECEDENCE RULES (highest to lowest):
    1. CLI --out flag (this function) - overrides everything
    2. SIM_OUTPUT_DIR environment variable
    3. Default: {repo_root}/results

    When called, this function:
    1. Validates the provided path for writability
    2. Updates all global path constants
    3. Ensures the new run directory structure is created

    Integration with orchestrator:
    - Called from run_employee_simulation.py before orchestrator initialization
    - Orchestrator reads updated global constants (RUN_DIR, ARTIFACTS_DIR, etc.)
    - All writers automatically use the new paths

    Args:
        new_base: New base output directory path

    Raises:
        PermissionError: If the directory is not writable
        OSError: If the directory cannot be created or accessed
        ValueError: If the path is invalid or empty
    """
    global BASE_OUTPUT, RUN_DIR, ARTIFACTS_DIR, CHARTS_DIR, TABLES_DIR

    if not new_base or not new_base.strip():
        raise ValueError("Output base path cannot be empty")

    try:
        BASE_OUTPUT = Path(new_base).resolve()
    except (OSError, ValueError) as e:
        raise ValueError(f"Invalid path '{new_base}': {e}")

    validate_output_path(BASE_OUTPUT)

    RUN_DIR = BASE_OUTPUT / f"run_{RUN_STAMP}"
    ARTIFACTS_DIR = RUN_DIR / "artifacts"
    CHARTS_DIR = RUN_DIR / "assets" / "charts"
    TABLES_DIR = RUN_DIR / "assets" / "tables"


def check_migration_needed() -> dict:
    """Check for existing data that may need migration and provide archival strategy.

    MIGRATION STRATEGY:
    1. ASSESSMENT: Scan for legacy directories with data
    2. BACKUP: Create timestamped archives of non-empty directories
    3. CLEANUP: Remove empty directories after confirmation
    4. MIGRATION: Move important data to new structure if needed

    Recommended workflow:
    ```python
    migration_info = check_migration_needed()
    if migration_info['needs_attention']:
        print("Migration needed - see recommendations")
        if migration_info['has_data']:
            # Archive existing data first
            create_migration_backup(migration_info)
        # Then proceed with cleanup
    ```

    Returns:
        dict: Comprehensive migration information including:
            - legacy_artifacts: bool - artifacts/ directory exists
            - legacy_results: bool - results/ directory exists
            - has_data: bool - any directories contain files
            - needs_attention: bool - any action required
            - recommendations: list - specific actions to take
            - file_counts: dict - detailed file counts per directory
            - suggested_commands: list - shell commands for manual migration
    """
    migration_info = {
        "legacy_artifacts": Path("artifacts").exists(),
        "legacy_results": Path("results").exists(),
        "has_data": False,
        "needs_attention": False,
        "recommendations": [],
        "file_counts": {},
        "suggested_commands": [],
    }

    # Check legacy artifacts directory
    if migration_info["legacy_artifacts"]:
        artifacts_path = Path("artifacts")
        artifacts_files = list(artifacts_path.glob("**/*"))
        artifacts_data_files = [f for f in artifacts_files if f.is_file()]

        if artifacts_data_files:
            migration_info["has_data"] = True
            migration_info["needs_attention"] = True
            migration_info["file_counts"]["artifacts"] = len(artifacts_data_files)
            migration_info["recommendations"].append(
                f"⚠️  IMPORTANT: Legacy artifacts/ directory contains {len(artifacts_data_files)} files.\n"
                f"   → Archive before deletion: tar -czf artifacts_backup_$(date +%Y%m%d_%H%M%S).tar.gz artifacts/\n"
                f"   → Review files and move important data to new structure if needed."
            )
            migration_info["suggested_commands"].append(
                "tar -czf artifacts_backup_$(date +%Y%m%d_%H%M%S).tar.gz artifacts/"
            )
        else:
            migration_info["recommendations"].append(
                "✅ Legacy artifacts/ directory is empty and can be safely removed."
            )
            migration_info["suggested_commands"].append("rmdir artifacts/")

    # Check legacy results directory
    if migration_info["legacy_results"]:
        results_path = Path("results")
        if results_path.exists():
            # Check for non-run directories (legacy structure)
            all_items = list(results_path.iterdir())
            legacy_dirs = [d for d in all_items if d.is_dir() and not d.name.startswith("run_")]
            legacy_files = [f for f in all_items if f.is_file()]

            if legacy_dirs or legacy_files:
                total_items = len(legacy_dirs) + len(legacy_files)
                migration_info["has_data"] = True
                migration_info["needs_attention"] = True
                migration_info["file_counts"]["results_legacy"] = total_items
                migration_info["recommendations"].append(
                    f"⚠️  IMPORTANT: Legacy results/ structure detected ({total_items} items).\n"
                    f"   → Archive before cleanup: tar -czf results_legacy_backup_$(date +%Y%m%d_%H%M%S).tar.gz results/\n"
                    f"   → Review and migrate important data to new run_YYYYMMDD_HHMMSS/ structure."
                )
                migration_info["suggested_commands"].extend(
                    [
                        "tar -czf results_legacy_backup_$(date +%Y%m%d_%H%M%S).tar.gz results/",
                        "# Review contents before cleanup:",
                        "find results/ -type f -name '*.json' -o -name '*.csv' -o -name '*.png' | head -20",
                    ]
                )
            else:
                migration_info["recommendations"].append(
                    "✅ Results/ directory only contains new run_* structure - no migration needed."
                )

    # Add general recommendations if migration needed
    if migration_info["needs_attention"]:
        migration_info["recommendations"].insert(
            0,
            "🚨 DATA MIGRATION REQUIRED\n"
            "The new path structure centralizes all outputs under results/run_YYYYMMDD_HHMMSS/.\n"
            "Follow the recommendations below to safely migrate existing data.",
        )

    return migration_info


def create_migration_backup(migration_info: dict) -> bool:
    """Create backup archives of existing data before migration.

    Args:
        migration_info: Information from check_migration_needed()

    Returns:
        bool: True if backup was successful, False otherwise
    """
    import subprocess
    from datetime import datetime

    if not migration_info.get("has_data"):
        return True  # No data to backup

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_success = True

    try:
        # Backup artifacts if it has data
        if migration_info.get("file_counts", {}).get("artifacts", 0) > 0:
            backup_name = f"artifacts_backup_{timestamp}.tar.gz"
            subprocess.run(["tar", "-czf", backup_name, "artifacts/"], check=True)
            print(f"✅ Created backup: {backup_name}")

        # Backup legacy results if it has data
        if migration_info.get("file_counts", {}).get("results_legacy", 0) > 0:
            backup_name = f"results_legacy_backup_{timestamp}.tar.gz"
            subprocess.run(["tar", "-czf", backup_name, "results/"], check=True)
            print(f"✅ Created backup: {backup_name}")

    except subprocess.CalledProcessError as e:
        print(f"❌ Backup failed: {e}")
        backup_success = False
    except Exception as e:
        print(f"❌ Backup error: {e}")
        backup_success = False

    return backup_success


def print_migration_summary(migration_info: dict) -> None:
    """Print a user-friendly migration summary.

    Args:
        migration_info: Information from check_migration_needed()
    """
    print("\n" + "=" * 60)
    print("📦 MIGRATION ASSESSMENT SUMMARY")
    print("=" * 60)

    if not migration_info["needs_attention"]:
        print("✅ No migration needed - directory structure is up to date.")
        return

    print("⚠️  Migration attention required\n")

    for i, recommendation in enumerate(migration_info["recommendations"], 1):
        print(f"{i}. {recommendation}\n")

    if migration_info["suggested_commands"]:
        print("🔧 SUGGESTED COMMANDS:")
        for cmd in migration_info["suggested_commands"]:
            if cmd.startswith("#"):
                print(f"   {cmd}")
            else:
                print(f"   $ {cmd}")
        print()

    print("📋 CHECKLIST:")
    print("   [ ] Review existing data and identify what to keep")
    print("   [ ] Create backups using suggested commands above")
    print("   [ ] Test that backups are valid (tar -tzf backup.tar.gz)")
    print("   [ ] Remove legacy directories after confirming backup")
    print("   [ ] Run simulation to verify new structure works")
    print("=" * 60)

#!/usr/bin/env python3
"""
Migration Helper for Employee Simulation System Path Consolidation

This utility helps users migrate from the old scattered output paths 
to the new centralized results/run_YYYYMMDD_HHMMSS/ structure.

Usage:
    python migration_helper.py --check           # Assessment only
    python migration_helper.py --migrate         # Full migration with backup
    python migration_helper.py --clean-empty     # Remove empty legacy directories
"""

import argparse
import sys
from pathlib import Path

# Import our migration functions
from app_paths import check_migration_needed, create_migration_backup, print_migration_summary


def main():
    """Main migration helper interface."""
    parser = argparse.ArgumentParser(
        description="Migration Helper for Employee Simulation Path Consolidation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check what migration is needed
  python migration_helper.py --check
  
  # Full migration: assess, backup, and provide cleanup instructions
  python migration_helper.py --migrate
  
  # Just remove empty legacy directories
  python migration_helper.py --clean-empty
  
  # Show detailed migration strategy
  python migration_helper.py --strategy
        """
    )
    
    parser.add_argument("--check", action="store_true", 
                       help="Check for migration needs and show assessment")
    parser.add_argument("--migrate", action="store_true",
                       help="Perform full migration with backup creation")
    parser.add_argument("--clean-empty", action="store_true", 
                       help="Remove empty legacy directories only")
    parser.add_argument("--strategy", action="store_true",
                       help="Show detailed migration strategy documentation")
    parser.add_argument("--quiet", action="store_true",
                       help="Reduce output verbosity")
    
    # If no arguments, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    if args.strategy:
        show_migration_strategy()
        return
    
    # Get migration assessment
    migration_info = check_migration_needed()
    
    if args.check:
        print_migration_summary(migration_info)
        return
    
    if args.migrate:
        if not args.quiet:
            print("🔄 Starting full migration process...")
            print_migration_summary(migration_info)
        
        if migration_info["needs_attention"]:
            if migration_info["has_data"]:
                print("\n📦 Creating backups...")
                if create_migration_backup(migration_info):
                    print("✅ Backups created successfully")
                    print("\n🧹 Next steps:")
                    print("1. Verify backup files were created")
                    print("2. Test backups: tar -tzf backup_file.tar.gz")
                    print("3. Remove legacy directories when ready")
                    print("4. Run simulation to test new structure")
                else:
                    print("❌ Backup creation failed - migration aborted")
                    sys.exit(1)
            else:
                print("✅ No data to backup - directories are empty")
        else:
            print("✅ No migration needed - system is up to date")
    
    if args.clean_empty:
        clean_empty_directories(migration_info, quiet=args.quiet)


def show_migration_strategy():
    """Show detailed migration strategy documentation."""
    print("""
📋 EMPLOYEE SIMULATION MIGRATION STRATEGY
==========================================

OVERVIEW:
The new path structure centralizes all simulation outputs under:
  results/run_YYYYMMDD_HHMMSS/
    ├── artifacts/     (JSON data, simulation state)
    ├── assets/
    │   ├── charts/    (PNG, SVG visualizations)  
    │   └── tables/    (CSV, Excel exports)

OLD STRUCTURE ISSUES:
❌ ~/bruvio-tools/images/     (outside project)
❌ ./artifacts/               (mixed with source code)
❌ ./results/ (unstructured)  (no run separation)

NEW STRUCTURE BENEFITS:
✅ All outputs in project directory
✅ Run-specific isolation prevents conflicts
✅ Clear separation of artifacts vs visualizations
✅ Easy cleanup and archival per run

MIGRATION PROCESS:
1. ASSESSMENT: Scan for legacy directories
2. BACKUP: Create timestamped archives
3. MIGRATION: Move important data if needed
4. CLEANUP: Remove empty legacy directories
5. VALIDATION: Test new structure works

PATH PRECEDENCE RULES:
1. CLI --out flag          (highest priority)
2. SIM_OUTPUT_DIR env var  (medium priority) 
3. Default: ./results      (lowest priority)

INTEGRATION POINTS:
- run_employee_simulation.py: CLI entry point
- app_paths.py: Centralized path authority
- employee_simulation_orchestrator.py: Uses paths
- All writers: Use get_*_path() functions

SAFETY MEASURES:
✅ Comprehensive validation before any changes
✅ Timestamped backups of existing data
✅ Clear error messages with specific solutions
✅ Dry-run capabilities for verification
✅ Rollback strategy documentation
""")


def clean_empty_directories(migration_info: dict, quiet: bool = False):
    """Clean up empty legacy directories."""
    if not migration_info["needs_attention"]:
        if not quiet:
            print("✅ No empty directories to clean")
        return
    
    cleaned = []
    
    # Clean empty artifacts directory
    if migration_info["legacy_artifacts"]:
        artifacts_path = Path("artifacts")
        if artifacts_path.exists():
            artifacts_files = list(artifacts_path.glob("**/*"))
            if not any(f.is_file() for f in artifacts_files):
                try:
                    artifacts_path.rmdir()
                    cleaned.append("artifacts/")
                    if not quiet:
                        print("🗑️  Removed empty artifacts/ directory")
                except OSError as e:
                    if not quiet:
                        print(f"⚠️  Could not remove artifacts/: {e}")
            elif not quiet:
                print("⚠️  artifacts/ contains files - skipping (use --migrate to backup first)")
    
    # Clean empty results subdirectories (but keep results/ itself for new structure)
    if migration_info["legacy_results"]:
        results_path = Path("results")
        if results_path.exists():
            for item in results_path.iterdir():
                if item.is_dir() and not item.name.startswith("run_"):
                    try:
                        if not any(item.rglob("*")):
                            item.rmdir()
                            cleaned.append(f"results/{item.name}/")
                            if not quiet:
                                print(f"🗑️  Removed empty results/{item.name}/ directory")
                    except OSError as e:
                        if not quiet:
                            print(f"⚠️  Could not remove results/{item.name}/: {e}")
    
    if cleaned and not quiet:
        print(f"✅ Cleaned {len(cleaned)} empty directories: {', '.join(cleaned)}")
    elif not cleaned and not quiet:
        print("ℹ️  No empty directories found to clean")


if __name__ == "__main__":
    main()
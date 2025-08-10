#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

"""
Test file optimization and structured directory creation
"""

import json
import sys
from pathlib import Path


def test_file_optimization():
    """Test that FileOptimizationManager integration works"""

    try:
        # Import the orchestrator with FileOptimizationManager
        from employee_simulation_orchestrator import EmployeeSimulationOrchestrator

        # Create minimal config for testing
        test_config = {
            "population_size": 10,
            "random_seed": 42,
            "max_cycles": 1,
            "export_formats": ["json"],
            "generate_visualizations": False,
            "export_individual_files": False,
            "export_comprehensive_report": False,
            "enable_story_tracking": True,
            "log_level": "WARNING",  # Reduce log noise
            "enable_progress_bar": False,
            "generate_summary_report": False,
        }

        print("🧪 Testing File Optimization Integration")
        print("=" * 50)

        # Initialize orchestrator (should create structured directories)
        orchestrator = EmployeeSimulationOrchestrator(config=test_config)

        # Verify file manager was initialized
        if hasattr(orchestrator, "file_manager") and orchestrator.file_manager:
            print("✅ FileOptimizationManager successfully initialized")
        else:
            print("❌ FileOptimizationManager not found in orchestrator")
            return False

        # Verify structured directories were created
        if hasattr(orchestrator, "run_directories") and orchestrator.run_directories:
            run_dirs = orchestrator.run_directories
            print("✅ Structured directories created:")

            required_dirs = ["run_root", "population_data", "simulation_results", "logs", "reports"]
            story_dirs = ["employee_stories", "story_analysis"] if test_config["enable_story_tracking"] else []

            missing_dirs = []
            for dir_name in required_dirs + story_dirs:
                if dir_name in run_dirs and run_dirs[dir_name].exists():
                    print(f"   ✓ {dir_name}: {run_dirs[dir_name]}")
                else:
                    missing_dirs.append(dir_name)
                    print(f"   ✗ {dir_name}: Missing or not created")

            if missing_dirs:
                print(f"❌ Missing directories: {missing_dirs}")
                return False

        else:
            print("❌ Structured directories not created")
            return False

        # Test file organization summary
        file_summary = orchestrator.file_manager.get_run_summary()
        if file_summary and "run_id" in file_summary:
            print("✅ File organization summary works")
            print(f"   Run ID: {file_summary['run_id']}")
            print(f"   Directories created: {file_summary['directories_created']}")
        else:
            print("❌ File organization summary failed")
            return False

        # Test metadata file creation
        metadata_file = run_dirs["run_root"] / "run_metadata.json"
        if metadata_file.exists():
            print("✅ Run metadata file created")
            with open(metadata_file, "r") as f:
                metadata = json.load(f)
                print(f"   Story tracking enabled: {metadata['story_tracking_enabled']}")
        else:
            print("❌ Run metadata file not created")
            return False

        print("✅ File optimization integration test completed successfully")
        return True

    except Exception as e:
        print(f"❌ File optimization integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_file_optimization()
    sys.exit(0 if success else 1)

#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

"""
Phase 3 Validation Test: Smart Logging & File Management
Tests concise logging, structured file organization, and progress indicators
"""

import json
import sys
from pathlib import Path


def test_phase3_validation():
    """Comprehensive test for Phase 3: Smart Logging & File Management"""

    print("🚀 Phase 3 Validation: Smart Logging & File Management")
    print("=" * 60)

    try:
        from employee_simulation_orchestrator import EmployeeSimulationOrchestrator

        # Test configuration with Phase 3 features enabled
        test_config = {
            "population_size": 50,
            "random_seed": 42,
            "max_cycles": 3,
            "export_formats": ["json"],
            "generate_visualizations": False,
            "export_individual_files": False,
            "export_comprehensive_report": True,
            "enable_story_tracking": True,
            "tracked_employee_count": 5,
            # Phase 3 specific settings
            "log_level": "INFO",
            "enable_progress_bar": True,
            "enable_file_logging": True,
            "generate_summary_report": True,
        }

        print("📊 Test Configuration:")
        print(f"   Population size: {test_config['population_size']}")
        print(f"   Max cycles: {test_config['max_cycles']}")
        print(f"   Story tracking: {test_config['enable_story_tracking']}")
        print(f"   Log level: {test_config['log_level']}")
        print("")

        # Initialize orchestrator
        print("🔧 Initializing orchestrator with Phase 3 enhancements...")
        orchestrator = EmployeeSimulationOrchestrator(config=test_config)

        # Validate smart logging integration
        phase3_checks = {
            "smart_logger_initialized": hasattr(orchestrator, "smart_logger"),
            "file_manager_initialized": hasattr(orchestrator, "file_manager"),
            "structured_directories_created": hasattr(orchestrator, "run_directories"),
            "progress_indicators_enabled": (
                orchestrator.smart_logger.enable_progress if hasattr(orchestrator, "smart_logger") else False
            ),
        }

        print("✅ Phase 3 Component Check:")
        for check, passed in phase3_checks.items():
            status = "✓" if passed else "✗"
            print(f"   {status} {check.replace('_', ' ').title()}: {passed}")

        if not all(phase3_checks.values()):
            print("❌ Phase 3 component initialization failed")
            return False

        print("")

        # Test structured directory creation
        print("📁 Testing Structured Directory Organization:")
        run_dirs = orchestrator.run_directories
        expected_dirs = [
            "run_root",
            "population_data",
            "simulation_results",
            "reports",
            "logs",
            "employee_stories",
            "story_analysis",
        ]

        directory_checks = {}
        for dir_name in expected_dirs:
            if dir_name in run_dirs and run_dirs[dir_name].exists():
                directory_checks[dir_name] = True
                print(f"   ✓ {dir_name}: {run_dirs[dir_name]}")
            else:
                directory_checks[dir_name] = False
                print(f"   ✗ {dir_name}: Missing")

        if not all(directory_checks.values()):
            print("❌ Structured directory creation failed")
            return False

        print("")

        # Test run metadata creation
        print("📋 Testing Run Metadata:")
        metadata_file = run_dirs["run_root"] / "run_metadata.json"
        if metadata_file.exists():
            with open(metadata_file, "r") as f:
                metadata = json.load(f)

            metadata_checks = {
                "run_id_present": "run_id" in metadata,
                "timestamp_present": "created_timestamp" in metadata,
                "story_tracking_flag": metadata.get("story_tracking_enabled", False),
                "directory_structure_documented": "directory_structure" in metadata,
            }

            for check, passed in metadata_checks.items():
                status = "✓" if passed else "✗"
                print(f"   {status} {check.replace('_', ' ').title()}: {passed}")

            if not all(metadata_checks.values()):
                print("❌ Run metadata validation failed")
                return False
        else:
            print("❌ Run metadata file not created")
            return False

        print("")

        # Test smart logging functionality
        print("📝 Testing Smart Logging Features:")

        # Test progress tracking
        orchestrator.smart_logger.start_phase("Phase 3 Validation Test", 3)
        orchestrator.smart_logger.update_progress("Component validation")
        orchestrator.smart_logger.update_progress("Directory structure check")
        orchestrator.smart_logger.update_progress("Metadata validation")
        orchestrator.smart_logger.complete_phase("Phase 3 Validation Test")

        # Test summary generation
        summary = orchestrator.smart_logger.generate_execution_summary()
        summary_checks = {
            "execution_summary_generated": "execution_summary" in summary,
            "phase_details_present": "phase_details" in summary,
            "configuration_documented": "configuration" in summary,
            "operations_tracked": summary.get("execution_summary", {}).get("total_operations", 0) > 0,
        }

        for check, passed in summary_checks.items():
            status = "✓" if passed else "✗"
            print(f"   {status} {check.replace('_', ' ').title()}: {passed}")

        if not all(summary_checks.values()):
            print("❌ Smart logging validation failed")
            return False

        print("")

        # Test file organization capabilities
        print("🗂️ Testing File Organization:")
        file_summary = orchestrator.file_manager.get_run_summary()

        org_checks = {
            "run_summary_available": bool(file_summary),
            "run_id_tracked": "run_id" in file_summary,
            "directory_count_tracked": "directories_created" in file_summary,
            "file_paths_documented": "directory_paths" in file_summary,
        }

        for check, passed in org_checks.items():
            status = "✓" if passed else "✗"
            print(f"   {status} {check.replace('_', ' ').title()}: {passed}")

        if not all(org_checks.values()):
            print("❌ File organization validation failed")
            return False

        print("")

        # Final validation summary
        total_checks = (
            len(phase3_checks) + len(directory_checks) + len(metadata_checks) + len(summary_checks) + len(org_checks)
        )
        passed_checks = sum(
            [
                sum(phase3_checks.values()),
                sum(directory_checks.values()),
                sum(metadata_checks.values()),
                sum(summary_checks.values()),
                sum(org_checks.values()),
            ]
        )

        success_rate = (passed_checks / total_checks) * 100

        print("📊 Phase 3 Validation Summary:")
        print(f"   Total checks performed: {total_checks}")
        print(f"   Checks passed: {passed_checks}")
        print(f"   Success rate: {success_rate:.1f}%")

        if success_rate >= 95.0:
            print("✅ Phase 3 validation PASSED - Smart logging and file management working correctly")
            return True
        else:
            print(f"❌ Phase 3 validation FAILED - Success rate {success_rate:.1f}% below threshold (95%)")
            return False

    except Exception as e:
        print(f"❌ Phase 3 validation failed with exception: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_phase3_validation()
    sys.exit(0 if success else 1)

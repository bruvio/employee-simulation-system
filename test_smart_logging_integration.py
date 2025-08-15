#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

"""
Quick test to verify SmartLoggingManager integration works.
"""

import sys


def test_smart_logging_integration():
    """
    Test that SmartLoggingManager integration works in orchestrator.
    """

    try:
        # Import the orchestrator with SmartLoggingManager
        from employee_simulation_orchestrator import EmployeeSimulationOrchestrator

        # Create minimal config for testing
        test_config = {
            "population_size": 50,
            "random_seed": 42,
            "max_cycles": 2,
            "export_formats": ["csv"],
            "generate_visualizations": False,
            "export_individual_files": False,
            "export_comprehensive_report": False,
            "log_level": "INFO",
            "enable_progress_bar": True,
            "enable_file_logging": False,
            "generate_summary_report": True,
        }

        print("🧪 Testing SmartLoggingManager Integration")
        print("=" * 50)

        # Initialize orchestrator (should use SmartLoggingManager)
        orchestrator = EmployeeSimulationOrchestrator(config=test_config)

        # Verify smart logger was initialized
        if hasattr(orchestrator, "smart_logger") and orchestrator.smart_logger:
            print("✅ SmartLoggingManager successfully initialized")

            # Test logging functionality
            orchestrator.smart_logger.log_info("Testing smart logging integration")
            orchestrator.smart_logger.start_phase("Test Phase", 3)
            orchestrator.smart_logger.update_progress("Test operation 1")
            orchestrator.smart_logger.update_progress("Test operation 2")
            orchestrator.smart_logger.update_progress("Test operation 3")
            orchestrator.smart_logger.complete_phase("Test Phase")

            # Test summary generation
            summary = orchestrator.smart_logger.generate_execution_summary()
            if summary and "execution_summary" in summary:
                print("✅ Execution summary generation works")
                print(f"   Phases completed: {len(summary['execution_summary']['phases_completed'])}")
                print(f"   Operations completed: {summary['execution_summary']['total_operations']}")
            else:
                print("❌ Execution summary generation failed")
                return False

            print("✅ SmartLoggingManager integration test completed successfully")
            return True

        else:
            print("❌ SmartLoggingManager not found in orchestrator")
            return False

    except Exception as e:
        print(f"❌ SmartLoggingManager integration test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_smart_logging_integration()
    sys.exit(0 if success else 1)

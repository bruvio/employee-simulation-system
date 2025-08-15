#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

"""
Test Interactive Dashboard Generation.
"""

from pathlib import Path
import sys

import pandas as pd


def test_interactive_dashboard():
    """
    Test interactive dashboard generation functionality.
    """

    print("🚀 Testing Interactive Dashboard Generation")
    print("=" * 50)

    try:
        from employee_simulation_orchestrator import EmployeeSimulationOrchestrator
        from interactive_dashboard_generator import InteractiveDashboardGenerator

        # Test configuration with interactive dashboard enabled
        test_config = {
            "population_size": 100,
            "random_seed": 42,
            "max_cycles": 3,
            "export_formats": ["json"],
            "generate_visualizations": True,
            "export_individual_files": False,
            "export_comprehensive_report": False,
            # Enable story tracking and interactive dashboard
            "enable_story_tracking": True,
            "tracked_employee_count": 8,
            "generate_interactive_dashboard": True,
            "create_individual_story_charts": True,
            # Phase 4 specific settings
            "log_level": "INFO",
            "enable_progress_bar": True,
            "enable_file_logging": False,
            "generate_summary_report": True,
        }

        print("📊 Test Configuration:")
        print(f"   Population size: {test_config['population_size']}")
        print(f"   Story tracking: {test_config['enable_story_tracking']}")
        print(f"   Interactive dashboard: {test_config['generate_interactive_dashboard']}")
        print(f"   Individual story charts: {test_config['create_individual_story_charts']}")
        print("")

        # Initialize orchestrator
        print("🔧 Initializing orchestrator with interactive dashboard support...")
        orchestrator = EmployeeSimulationOrchestrator(config=test_config)

        # Validate Phase 4 components
        phase4_checks = {
            "interactive_dashboard_generator_available": True,
            "dashboard_config_enabled": test_config["generate_interactive_dashboard"],
            "story_charts_enabled": test_config["create_individual_story_charts"],
            "story_tracker_available": hasattr(orchestrator, "story_tracker")
            and orchestrator.story_tracker is not None,
        }

        print("✅ Phase 4 Component Check:")
        for check, passed in phase4_checks.items():
            status = "✓" if passed else "✗"
            print(f"   {status} {check.replace('_', ' ').title()}: {passed}")

        if not all(phase4_checks.values()):
            print("❌ Phase 4 component initialization failed")
            return False

        print("")

        # Test standalone dashboard generator
        print("🎨 Testing Standalone Dashboard Generator:")

        sample_population = [
            {
                "employee_id": f"EMP{i+1:03d}",
                "level": (i % 6) + 1,
                "gender": "Female" if i % 2 == 0 else "Male",
                "salary": 40000 + (i * 2000) + ((i % 6) * 5000),
                "performance_rating": 2.5 + (i % 3) * 0.5,
            }
            for i in range(20)
        ]
        # Create sample tracked employees
        sample_tracked = {
            "gender_gap": [
                type("Employee", (), {"employee_id": "EMP001", "category": "gender_gap"}),
                type("Employee", (), {"employee_id": "EMP003", "category": "gender_gap"}),
            ],
            "high_performer": [
                type("Employee", (), {"employee_id": "EMP010", "category": "high_performer"}),
                type("Employee", (), {"employee_id": "EMP015", "category": "high_performer"}),
            ],
        }

        dashboard_generator = InteractiveDashboardGenerator()

        # Test individual dashboard components
        component_tests = {}

        # Test salary distribution explorer
        salary_explorer = dashboard_generator.create_salary_distribution_explorer(sample_population)
        component_tests["salary_explorer"] = {
            "created": salary_explorer is not None,
            "has_figure": "figure" in salary_explorer,
            "data_points": salary_explorer.get("data_points", 0),
        }

        # Test employee story timeline
        story_timeline = dashboard_generator.create_employee_story_timeline(sample_tracked)
        component_tests["story_timeline"] = {
            "created": story_timeline is not None,
            "has_figure": "figure" in story_timeline,
            "total_stories": story_timeline.get("total_stories", 0),
        }

        # Test comparative analysis dashboard
        comparative_dashboard = dashboard_generator.create_comparative_analysis_dashboard(
            sample_population, sample_tracked
        )
        component_tests["comparative_dashboard"] = {
            "created": comparative_dashboard is not None,
            "has_figure": "figure" in comparative_dashboard,
            "categories_analyzed": comparative_dashboard.get("categories_analyzed", 0),
        }

        print("   Component Tests:")
        all_components_passed = True
        for component, tests in component_tests.items():
            component_passed = all(tests.values())
            all_components_passed = all_components_passed and component_passed
            status = "✓" if component_passed else "✗"
            print(f"   {status} {component.replace('_', ' ').title()}: {tests}")

        if not all_components_passed:
            print("❌ Dashboard component tests failed")
            return False

        print("")

        # Test comprehensive dashboard generation
        print("📈 Testing Comprehensive Dashboard Generation:")

        # Create cycle data for timeline
        cycle_data = pd.DataFrame(
            [
                {"employee_id": "EMP001", "cycle": 0, "salary": 45000, "level": 2, "performance_rating": 3.0},
                {"employee_id": "EMP001", "cycle": 1, "salary": 47000, "level": 2, "performance_rating": 3.2},
                {"employee_id": "EMP010", "cycle": 0, "salary": 60000, "level": 4, "performance_rating": 4.5},
                {"employee_id": "EMP010", "cycle": 1, "salary": 65000, "level": 5, "performance_rating": 4.7},
            ]
        )

        # Generate comprehensive dashboard
        dashboard_path = dashboard_generator.generate_comprehensive_dashboard(
            population_data=sample_population,
            tracked_employees=sample_tracked,
            cycle_data=cycle_data,
            output_path="test_dashboard.html",
        )

        dashboard_tests = {
            "dashboard_file_created": Path(dashboard_path).exists(),
            "dashboard_path_returned": dashboard_path is not None,
            "html_file_extension": dashboard_path.endswith(".html"),
        }

        for test, passed in dashboard_tests.items():
            status = "✓" if passed else "✗"
            print(f"   {status} {test.replace('_', ' ').title()}: {passed}")

        if not all(dashboard_tests.values()):
            print("❌ Comprehensive dashboard generation failed")
            return False

        # Check dashboard file size (should be substantial if properly generated)
        dashboard_file = Path(dashboard_path)
        if dashboard_file.exists():
            file_size = dashboard_file.stat().st_size
            print(f"   ✓ Dashboard File Size: {file_size:,} bytes")

            if file_size < 10000:  # Less than 10KB suggests incomplete generation
                print("   ⚠️ Warning: Dashboard file seems small, may be incomplete")

        print("")

        # Test dashboard metadata
        print("📋 Testing Dashboard Metadata:")

        metadata = dashboard_generator.get_dashboard_metadata()
        metadata_tests = {
            "metadata_available": metadata is not None,
            "layout_config_present": "layout_config" in metadata,
            "generation_timestamp_present": "generation_timestamp" in metadata,
            "version_present": "version" in metadata,
        }

        for test, passed in metadata_tests.items():
            status = "✓" if passed else "✗"
            print(f"   {status} {test.replace('_', ' ').title()}: {passed}")

        if not all(metadata_tests.values()):
            print("❌ Dashboard metadata tests failed")
            return False

        print("")

        # Final validation summary
        all_test_groups = [
            phase4_checks.values(),
            component_tests.values(),
            dashboard_tests.values(),
            metadata_tests.values(),
        ]

        total_checks = sum(
            (
                len(list(group))
                if hasattr(group, "__len__")
                else (
                    sum(len(list(comp.values())) for comp in group)
                    if all(isinstance(comp, dict) for comp in group)
                    else len(list(group))
                )
            )
            for group in all_test_groups
        )

        passed_checks = (
            sum(phase4_checks.values())
            + sum(sum(comp.values()) for comp in component_tests.values())
            + sum(dashboard_tests.values())
            + sum(metadata_tests.values())
        )

        success_rate = (passed_checks / total_checks) * 100

        print("📊 Interactive Dashboard Test Summary:")
        print(f"   Total checks performed: {total_checks}")
        print(f"   Checks passed: {passed_checks}")
        print(f"   Success rate: {success_rate:.1f}%")

        if dashboard_file.exists():
            print(f"   Dashboard generated: {dashboard_path}")
            print("   🎉 You can open the dashboard file in a web browser to explore!")

        if success_rate >= 95.0:
            print("✅ Interactive dashboard test PASSED - All components working correctly")
            return True
        else:
            print(f"❌ Interactive dashboard test FAILED - Success rate {success_rate:.1f}% below threshold (95%)")
            return False

    except Exception as e:
        print(f"❌ Interactive dashboard test failed with exception: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Clean up test files
        test_files = ["test_dashboard.html"]
        for test_file in test_files:
            test_path = Path(test_file)
            if test_path.exists():
                print(f"🧹 Cleaned up test file: {test_file}")
                test_path.unlink()


if __name__ == "__main__":
    success = test_interactive_dashboard()
    sys.exit(0 if success else 1)

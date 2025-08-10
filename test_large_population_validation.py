#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

"""
Final Validation Test: Large Population (5000 employees) with Comprehensive Dashboard Export
This test validates the complete system with performance optimizations for large-scale simulations.
"""

import json
import sys
import time
import psutil
from pathlib import Path


def get_memory_usage():
    """Get current memory usage in MB"""
    try:
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    except Exception:
        return 0.0


def test_large_population_validation():
    """Final validation test with 5000 employees and comprehensive features"""

    print("🚀 FINAL VALIDATION: Large Population Test (5000 Employees)")
    print("=" * 70)

    start_time = time.time()
    initial_memory = get_memory_usage()

    try:
        from employee_simulation_orchestrator import EmployeeSimulationOrchestrator

        # Configuration for large-scale test with all features enabled
        large_scale_config = {
            "population_size": 5000,
            "random_seed": 42,
            "max_cycles": 10,  # Reduced for performance
            "export_formats": ["json", "csv"],  # Reduced formats for speed
            "generate_visualizations": True,
            "export_individual_files": False,  # Disabled for performance
            "export_comprehensive_report": True,
            # Enable all advanced features
            "enable_story_tracking": True,
            "tracked_employee_count": 50,  # Increased for large population
            "story_categories": ["gender_gap", "above_range", "high_performer"],
            "story_export_formats": ["json", "csv", "markdown"],
            "export_story_data": True,
            "generate_interactive_dashboard": True,
            "create_individual_story_charts": False,  # Disabled for performance
            # Performance optimizations
            "log_level": "INFO",
            "enable_progress_bar": True,
            "enable_file_logging": False,  # Disabled for performance
            "generate_summary_report": True,
        }

        print("📊 Large Scale Test Configuration:")
        print(f"   Population size: {large_scale_config['population_size']:,}")
        print(f"   Max cycles: {large_scale_config['max_cycles']}")
        print(f"   Story tracking: {large_scale_config['enable_story_tracking']}")
        print(f"   Tracked employees: {large_scale_config['tracked_employee_count']}")
        print(f"   Interactive dashboard: {large_scale_config['generate_interactive_dashboard']}")
        print(f"   Export formats: {large_scale_config['story_export_formats']}")
        print("")

        # Memory checkpoint
        print(f"🧠 Initial Memory Usage: {initial_memory:.1f} MB")
        print("")

        # Initialize orchestrator
        print("🔧 Initializing orchestrator with large-scale optimizations...")
        init_start = time.time()

        orchestrator = EmployeeSimulationOrchestrator(config=large_scale_config)

        init_time = time.time() - init_start
        init_memory = get_memory_usage()
        memory_increase = init_memory - initial_memory

        print(f"✅ Orchestrator initialized in {init_time:.2f}s (Memory: +{memory_increase:.1f}MB)")

        # Validate performance optimizations
        perf_optimizations = orchestrator.performance_optimizations
        print(f"🚀 Performance optimizations applied: {perf_optimizations['optimization_level']}")
        print(f"   Chunk size: {perf_optimizations['chunk_size']}")
        print(f"   Memory threshold: {perf_optimizations['memory_threshold_mb']}MB")
        print(f"   Optimizations active: {len(perf_optimizations['optimizations_applied'])}")
        print("")

        # Run simulation with story tracking
        print("⚡ Running large-scale simulation with story tracking...")
        simulation_start = time.time()

        results = orchestrator.run_with_story_tracking()

        simulation_time = time.time() - simulation_start
        simulation_memory = get_memory_usage()

        print(f"✅ Simulation completed in {simulation_time:.2f}s")
        print(f"🧠 Peak Memory Usage: {simulation_memory:.1f} MB")
        print("")

        # Validate results
        validation_tests = {
            "simulation_completed": "error" not in results,
            "population_generated": results.get("summary_metrics", {}).get("population_size", 0) == 5000,
            "cycles_completed": results.get("summary_metrics", {}).get("cycles_completed", 0) > 0,
            "stories_tracked": results.get("summary_metrics", {}).get("total_tracked_employees", 0) > 0,
            "files_generated": len(results.get("files_generated", {})) > 0,
        }

        print("✅ Simulation Validation:")
        for test, passed in validation_tests.items():
            status = "✓" if passed else "✗"
            print(f"   {status} {test.replace('_', ' ').title()}: {passed}")

        if not all(validation_tests.values()):
            print("❌ Basic simulation validation failed")
            return False

        print("")

        # Validate specific metrics
        metrics = results.get("summary_metrics", {})
        stories = results.get("employee_stories", {})
        files = results.get("files_generated", {})

        print("📊 Simulation Metrics:")
        print(f"   Population Size: {metrics.get('population_size', 0):,}")
        print(f"   Cycles Completed: {metrics.get('cycles_completed', 0)}")
        print(f"   Final Gini Coefficient: {metrics.get('final_gini_coefficient', 'N/A')}")
        print(f"   Convergence Achieved: {metrics.get('convergence_achieved', 'N/A')}")
        print(f"   Total Tracked Employees: {metrics.get('total_tracked_employees', 0)}")
        print("")

        print("📚 Story Tracking Results:")
        for category, category_stories in stories.items():
            print(f"   {category.replace('_', ' ').title()}: {len(category_stories)} employees")
        print("")

        # Validate file generation
        print("📁 File Generation Validation:")

        file_validation = {
            "execution_summary": "execution_summary" in files,
            "run_index": "run_index" in files,
            "performance_analysis": "performance_analysis" in files,
            "story_exports": "story_exports" in files,
            "comparative_analysis": "comparative_analysis" in files,
            "interactive_dashboard": "interactive_dashboard" in files,
        }

        for file_type, exists in file_validation.items():
            status = "✓" if exists else "✗"
            print(f"   {status} {file_type.replace('_', ' ').title()}: {exists}")

        if not all(file_validation.values()):
            print("❌ File generation validation failed")
            return False

        print("")

        # Validate dashboard generation
        if "interactive_dashboard" in files:
            dashboard_path = Path(files["interactive_dashboard"])
            if dashboard_path.exists():
                dashboard_size = dashboard_path.stat().st_size
                print(f"🎨 Interactive Dashboard: {dashboard_size:,} bytes")
                print(f"   Path: {dashboard_path}")

                if dashboard_size < 10000:
                    print("⚠️ Warning: Dashboard file seems small")
            else:
                print("❌ Dashboard file not found")
                return False

        print("")

        # Performance analysis
        if "performance_analysis" in files:
            perf_path = Path(files["performance_analysis"])
            if perf_path.exists():
                with open(perf_path, "r") as f:
                    perf_data = json.load(f)

                perf_metrics = perf_data.get("performance_metrics", {})
                optimizations = perf_data.get("optimizations", {})
                recommendations = perf_data.get("recommendations", [])

                print("⚡ Performance Analysis:")
                print(f"   Total Execution Time: {perf_metrics.get('total_execution_time_seconds', 0):.2f}s")
                print(f"   Peak Memory Usage: {perf_metrics.get('peak_memory_usage_mb', 0):.1f}MB")
                print(f"   Operations Tracked: {perf_metrics.get('operations_tracked', 0)}")
                print(f"   Optimizations Applied: {optimizations.get('total_applied', 0)}")

                if recommendations:
                    print(f"   Performance Recommendations:")
                    for rec in recommendations[:3]:  # Show first 3
                        print(f"     • {rec}")
                print("")

        # Memory efficiency validation
        memory_efficiency_tests = {
            "memory_under_control": simulation_memory < 2000,  # Under 2GB
            "reasonable_memory_growth": memory_increase < 1000,  # Under 1GB increase
            "performance_acceptable": simulation_time < 300,  # Under 5 minutes
        }

        print("🧠 Performance Efficiency Validation:")
        for test, passed in memory_efficiency_tests.items():
            status = "✓" if passed else "⚠️"
            print(f"   {status} {test.replace('_', ' ').title()}: {passed}")

        print("")

        # Final calculation
        total_time = time.time() - start_time
        final_memory = get_memory_usage()

        all_tests = [validation_tests.values(), file_validation.values(), memory_efficiency_tests.values()]

        total_checks = sum(len(list(group)) for group in all_tests)
        passed_checks = sum(sum(group) for group in all_tests)

        # Adjust for warnings as partial passes
        warning_count = sum(1 for passed in memory_efficiency_tests.values() if not passed)
        adjusted_passed = passed_checks - (warning_count * 0.5)

        success_rate = (adjusted_passed / total_checks) * 100

        print("📊 FINAL VALIDATION SUMMARY:")
        print("=" * 50)
        print(f"Population Size: {large_scale_config['population_size']:,} employees")
        print(f"Total Execution Time: {total_time:.2f} seconds")
        print(f"Peak Memory Usage: {final_memory:.1f} MB")
        print(f"Files Generated: {len(files)} file types")
        print(f"Stories Tracked: {metrics.get('total_tracked_employees', 0)} employees")
        print(f"Interactive Dashboard: {'✓' if dashboard_path.exists() else '✗'}")
        print("")
        print(f"Total Checks: {total_checks}")
        print(f"Checks Passed: {int(adjusted_passed)}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("")

        if success_rate >= 90.0:
            print("🎉 FINAL VALIDATION PASSED!")
            print("✅ Large population simulation with comprehensive features working correctly")
            print(f"🚀 System successfully handles {large_scale_config['population_size']:,} employees")
            print("🎨 Interactive dashboard and advanced story export operational")
            print("⚡ Performance optimizations effective for large-scale workloads")
            return True
        else:
            print(f"❌ FINAL VALIDATION FAILED")
            print(f"Success rate {success_rate:.1f}% below threshold (90%)")
            return False

    except Exception as e:
        print(f"❌ Large population validation failed with exception: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_large_population_validation()
    sys.exit(0 if success else 1)

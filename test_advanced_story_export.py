#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

"""Test Advanced Story Export System."""

import json
from pathlib import Path
import shutil
import sys
import tempfile

import pandas as pd


def test_advanced_story_export():
    """Test advanced story export functionality."""

    print("🚀 Testing Advanced Story Export System")
    print("=" * 50)

    # Create temporary directory for testing
    test_dir = Path(tempfile.mkdtemp())

    try:
        from advanced_story_export_system import AdvancedStoryExportSystem

        # Initialize export system
        export_system = AdvancedStoryExportSystem(output_base_dir=str(test_dir))

        print("📊 Test Configuration:")
        print(f"   Test directory: {test_dir}")
        print("   Export formats: json, csv, excel, xml, markdown")
        print("")

        # Create sample data
        print("🔧 Creating sample data...")

        sample_population = [
            {
                "employee_id": f"EMP{i+1:03d}",
                "level": (i % 6) + 1,
                "gender": "Female" if i % 2 == 0 else "Male",
                "salary": 35000 + (i * 1500) + ((i % 6) * 4000),
                "performance_rating": 2.0 + (i % 4) * 0.75,
                "department": ["Engineering", "Marketing", "Sales", "HR"][i % 4],
            }
            for i in range(30)
        ]
        # Sample employee stories
        sample_stories = {
            "gender_gap": [
                type(
                    "Story",
                    (),
                    {
                        "employee_id": "EMP001",
                        "category": "gender_gap",
                        "initial_salary": 40000,
                        "current_salary": 45000,
                        "total_growth_percent": 12.5,
                        "story_summary": "Employee experiencing gender-based salary gap despite strong performance",
                        "key_events": ["Promotion to Level 2", "Salary adjustment"],
                        "recommendations": ["Regular salary reviews", "Gender pay audit"],
                    },
                ),
                type(
                    "Story",
                    (),
                    {
                        "employee_id": "EMP003",
                        "category": "gender_gap",
                        "initial_salary": 38000,
                        "current_salary": 42000,
                        "total_growth_percent": 10.5,
                        "story_summary": "Consistent performer with below-market salary progression",
                        "key_events": ["Performance review improvement"],
                        "recommendations": ["Market rate analysis", "Accelerated review cycle"],
                    },
                ),
            ],
            "high_performer": [
                type(
                    "Story",
                    (),
                    {
                        "employee_id": "EMP010",
                        "category": "high_performer",
                        "initial_salary": 65000,
                        "current_salary": 78000,
                        "total_growth_percent": 20.0,
                        "story_summary": "Top performer with rapid advancement and salary growth",
                        "key_events": ["Promotion to Level 4", "Leadership role assignment"],
                        "recommendations": ["Leadership development program", "Stock options consideration"],
                    },
                ),
                type(
                    "Story",
                    (),
                    {
                        "employee_id": "EMP015",
                        "category": "high_performer",
                        "initial_salary": 58000,
                        "current_salary": 71000,
                        "total_growth_percent": 22.4,
                        "story_summary": "Exceptional contributor with cross-functional impact",
                        "key_events": ["Project leadership success", "Mentorship role"],
                        "recommendations": ["Senior level promotion consideration", "Retention bonus"],
                    },
                ),
            ],
            "above_range": [
                type(
                    "Story",
                    (),
                    {
                        "employee_id": "EMP020",
                        "category": "above_range",
                        "initial_salary": 95000,
                        "current_salary": 98000,
                        "total_growth_percent": 3.2,
                        "story_summary": "Senior employee with salary above market range",
                        "key_events": ["Cost-of-living adjustment"],
                        "recommendations": ["Performance improvement plan", "Role expansion consideration"],
                    },
                )
            ],
        }

        # Sample cycle data
        cycle_data = pd.DataFrame(
            [
                {"employee_id": "EMP001", "cycle": 0, "salary": 40000, "level": 2, "performance_rating": 3.5},
                {"employee_id": "EMP001", "cycle": 1, "salary": 42000, "level": 2, "performance_rating": 3.7},
                {"employee_id": "EMP001", "cycle": 2, "salary": 45000, "level": 3, "performance_rating": 3.8},
                {"employee_id": "EMP010", "cycle": 0, "salary": 65000, "level": 4, "performance_rating": 4.5},
                {"employee_id": "EMP010", "cycle": 1, "salary": 72000, "level": 4, "performance_rating": 4.7},
                {"employee_id": "EMP010", "cycle": 2, "salary": 78000, "level": 5, "performance_rating": 4.9},
            ]
        )

        print("✅ Sample data created successfully")
        print(f"   Population: {len(sample_population)} employees")
        print(
            f"   Stories: {sum(len(stories) for stories in sample_stories.values())} across {len(sample_stories)} categories"
        )
        print(f"   Cycle data: {len(cycle_data)} records")
        print("")

        # Test comprehensive export
        print("📤 Testing Comprehensive Story Export:")

        export_formats = ["json", "csv", "excel", "xml", "markdown"]
        export_files = export_system.export_employee_stories_comprehensive(
            employee_stories=sample_stories,
            population_data=sample_population,
            cycle_data=cycle_data,
            formats=export_formats,
        )

        export_tests = {}
        for format_name, file_path in export_files.items():
            file_exists = Path(file_path).exists()
            file_size = Path(file_path).stat().st_size if file_exists else 0

            export_tests[format_name] = {"file_exists": file_exists, "file_size": file_size, "file_path": file_path}

            status = "✓" if file_exists and file_size > 100 else "✗"
            print(f"   {status} {format_name.upper()} Export: {file_size:,} bytes")

        all_exports_passed = all(test["file_exists"] and test["file_size"] > 100 for test in export_tests.values())

        if not all_exports_passed:
            print("❌ Comprehensive export test failed")
            return False

        print("")

        # Test comparative analysis export
        print("📊 Testing Comparative Analysis Export:")

        comparative_formats = ["json", "csv", "excel"]
        comparative_tests = {}

        for format_name in comparative_formats:
            comparative_file = export_system.export_comparative_analysis(
                employee_stories=sample_stories, population_data=sample_population, output_format=format_name
            )

            file_exists = Path(comparative_file).exists()
            file_size = Path(comparative_file).stat().st_size if file_exists else 0

            comparative_tests[format_name] = {
                "file_exists": file_exists,
                "file_size": file_size,
                "file_path": comparative_file,
            }

            status = "✓" if file_exists and file_size > 50 else "✗"
            print(f"   {status} {format_name.upper()} Comparative Analysis: {file_size:,} bytes")

        all_comparative_passed = all(
            test["file_exists"] and test["file_size"] > 50 for test in comparative_tests.values()
        )

        if not all_comparative_passed:
            print("❌ Comparative analysis export test failed")
            return False

        print("")

        # Test export system capabilities
        print("🔍 Testing Export System Capabilities:")

        export_summary = export_system.get_export_summary()

        capability_tests = {
            "summary_available": export_summary is not None,
            "supported_formats_documented": "export_capabilities" in export_summary
            and "supported_formats" in export_summary["export_capabilities"],
            "features_documented": "export_capabilities" in export_summary
            and "features" in export_summary["export_capabilities"],
            "session_tracking": "recent_session" in export_summary,
            "version_info": "version" in export_summary,
        }

        for test, passed in capability_tests.items():
            status = "✓" if passed else "✗"
            print(f"   {status} {test.replace('_', ' ').title()}: {passed}")

        if not all(capability_tests.values()):
            print("❌ Export system capabilities test failed")
            return False

        print(f"   ✓ Supported Formats: {export_summary['export_capabilities']['supported_formats']}")
        print(f"   ✓ Features Count: {len(export_summary['export_capabilities']['features'])}")
        print("")

        # Test file content validation (sample checks)
        print("📄 Testing Export File Content:")

        content_tests = {}

        # Test JSON content
        if "json" in export_files:
            json_path = Path(export_files["json"])
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    json_data = json.load(f)

                content_tests["json_valid"] = True
                content_tests["json_has_metadata"] = "metadata" in json_data
                content_tests["json_has_stories"] = "stories" in json_data and len(json_data["stories"]) > 0
                content_tests["json_has_summaries"] = "category_summaries" in json_data
            except Exception:
                content_tests["json_valid"] = False

        # Test CSV content
        if "csv" in export_files:
            csv_path = Path(export_files["csv"])
            try:
                df = pd.read_csv(csv_path)
                content_tests["csv_readable"] = True
                content_tests["csv_has_data"] = len(df) > 0
                content_tests["csv_has_employee_ids"] = "employee_id" in df.columns
            except Exception:
                content_tests["csv_readable"] = False

        # Test Markdown content
        if "markdown" in export_files:
            md_path = Path(export_files["markdown"])
            try:
                with open(md_path, "r", encoding="utf-8") as f:
                    md_content = f.read()

                content_tests["markdown_readable"] = True
                content_tests["markdown_has_title"] = "# Employee Story Analysis Report" in md_content
                content_tests["markdown_has_categories"] = any(
                    cat.replace("_", " ").title() in md_content for cat in sample_stories
                )
            except Exception:
                content_tests["markdown_readable"] = False

        for test, passed in content_tests.items():
            status = "✓" if passed else "✗"
            print(f"   {status} {test.replace('_', ' ').title()}: {passed}")

        if not all(content_tests.values()):
            print("❌ Export content validation failed")
            return False

        print("")

        # Final validation summary
        all_test_groups = [
            export_tests.values(),
            comparative_tests.values(),
            capability_tests.values(),
            content_tests.values(),
        ]

        total_checks = sum(len(list(group)) for group in all_test_groups)
        passed_checks = (
            sum(bool(test["file_exists"] and test["file_size"] > 100) for test in export_tests.values())
            + sum(bool(test["file_exists"] and test["file_size"] > 50) for test in comparative_tests.values())
            + sum(capability_tests.values())
            + sum(content_tests.values())
        )

        success_rate = (passed_checks / total_checks) * 100

        print("📊 Advanced Story Export Test Summary:")
        print(f"   Total checks performed: {total_checks}")
        print(f"   Checks passed: {passed_checks}")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   Files generated: {len(export_files) + len(comparative_formats)}")
        print(
            f"   Total file size: {sum(test['file_size'] for test in export_tests.values()) + sum(test['file_size'] for test in comparative_tests.values()):,} bytes"
        )

        if success_rate >= 95.0:
            print("✅ Advanced story export test PASSED - All export formats working correctly")
            print(f"   📁 Test files created in: {test_dir}")
            return True
        else:
            print(f"❌ Advanced story export test FAILED - Success rate {success_rate:.1f}% below threshold (95%)")
            return False

    except Exception as e:
        print(f"❌ Advanced story export test failed with exception: {e}")
        import traceback

        traceback.print_exc()
        return False
    finally:
        # Clean up test directory
        if test_dir.exists():
            try:
                shutil.rmtree(test_dir)
                print(f"🧹 Cleaned up test directory: {test_dir}")
            except Exception as e:
                print(f"⚠️ Could not clean up test directory: {e}")


if __name__ == "__main__":
    success = test_advanced_story_export()
    sys.exit(0 if success else 1)

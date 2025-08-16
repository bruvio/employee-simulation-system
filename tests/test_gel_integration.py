#!/usr/bin/env python3

from datetime import datetime
from pathlib import Path
import shutil
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from gel_output_manager import GELOutputManager
from report_builder_html import HTMLReportBuilder
from report_builder_md import MarkdownReportBuilder, create_sample_analysis_payload
from roles_config import InterventionPolicy, Role, RolesConfig, RolesConfigLoader


class TestGELIntegration:
    """
    Integration tests for complete GEL workflow.
    """

    def setup_method(self):
        """
        Set up test fixtures.
        """
        self.temp_dir = Path(tempfile.mkdtemp())
        self.sample_manifest = {
            "scenario": "GEL",
            "org": "TestOrg",
            "timestamp_utc": "2025-08-14T10:00:00Z",
            "population": 201,
            "median_salary": 71500,
            "below_median_pct": 42.3,
            "gender_gap_pct": 6.8,
            "intervention_budget_pct": 0.5,
            "roles_config_sha256": "abc123...",
            "random_seed": 42,
            "currency": "GBP",
            "config_version": 1,
            "max_direct_reports": 6,
        }
        self.sample_payload = create_sample_analysis_payload()

    def teardown_method(self):
        """
        Clean up test fixtures.
        """
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_complete_gel_workflow(self):
        """
        Test complete GEL reporting workflow.
        """
        # Initialize components
        output_manager = GELOutputManager(base_results_dir=self.temp_dir)
        md_builder = MarkdownReportBuilder(output_dir=self.temp_dir / "temp")
        html_builder = HTMLReportBuilder(output_dir=self.temp_dir / "temp")

        # Create run directory
        timestamp = datetime.utcnow()
        run_dirs = output_manager.create_gel_run_directory(org="TestOrg", timestamp=timestamp)

        # Verify directory structure
        assert run_dirs["run_root"].exists()
        assert run_dirs["assets"].exists()
        assert run_dirs["charts"].exists()
        assert run_dirs["tables"].exists()
        assert run_dirs["figures"].exists()

        # Generate reports
        md_report = md_builder.build_gel_report(self.sample_payload, self.sample_manifest, "test_report.md")

        html_report = html_builder.build_gel_report(
            self.sample_payload, self.sample_manifest, run_dirs["assets"], "test_index.html"
        )

        # Verify reports were created
        assert md_report.exists()
        assert html_report.exists()

        # Check report contents
        md_content = md_report.read_text()
        assert "# TestOrg Employee Analysis Report" in md_content
        assert "```mermaid" in md_content
        assert "## 1. Overview & Inputs" in md_content

        html_content = html_report.read_text()
        assert "<title>TestOrg Employee Analysis Report" in html_content
        assert "<!DOCTYPE html>" in html_content
        assert "mermaid" in html_content.lower()

        # Organize outputs
        final_paths = output_manager.organize_gel_outputs(
            run_directories=run_dirs,
            html_report=html_report,
            markdown_report=md_report,
            manifest_data=self.sample_manifest,
        )

        # Verify final structure
        assert "html_report" in final_paths
        assert "markdown_report" in final_paths
        assert "manifest" in final_paths

        final_html = Path(final_paths["html_report"])
        final_md = Path(final_paths["markdown_report"])
        final_manifest = Path(final_paths["manifest"])

        assert final_html.exists()
        assert final_md.exists()
        assert final_manifest.exists()

        # Verify final files are in correct locations
        assert final_html.name == "index.html"
        assert final_md.name == "report.md"
        assert final_manifest.name == "manifest.json"

        # Validate complete output
        validation = output_manager.validate_gel_output(run_dirs["run_root"])
        assert validation["valid"] is True
        assert len(validation["errors"]) == 0

    def test_gel_with_roles_config(self):
        """
        Test GEL workflow with roles configuration.
        """
        # Create sample roles config
        roles_config = RolesConfig(
            org="TestOrg",
            currency="GBP",
            version=1,
            intervention_policy=InterventionPolicy(max_direct_reports=6, inequality_budget_percent=0.5),
            roles=[
                Role(title="Data Engineer", min_salaries=[73000], headcount_hint=4),
                Role(title="Platform Engineer", min_salaries=[71500]),
                Role(title="Senior Designer", min_salaries=[63300, 71300]),
            ],
        )

        # Create temporary roles config file
        roles_file = self.temp_dir / "test_roles.yaml"
        import yaml

        with open(roles_file, "w") as f:
            yaml.dump(roles_config.model_dump(), f)

        # Load roles config
        loader = RolesConfigLoader()
        loaded_config = loader.load_config(roles_file)

        # Verify config loaded correctly
        assert loaded_config.org == "TestOrg"
        assert len(loaded_config.roles) == 3

        # Test role lookup functionality
        data_engineer_min = loader.get_minimum_for_role(loaded_config, "Data Engineer")
        assert data_engineer_min == 73000

        senior_designer_mins = [
            loader.get_minimum_for_role(loaded_config, "Senior Designer", 0),
            loader.get_minimum_for_role(loaded_config, "Senior Designer", 1),
        ]
        assert 63300 in senior_designer_mins
        assert 71300 in senior_designer_mins

    def test_gel_output_validation(self):
        """
        Test GEL output validation functionality.
        """
        output_manager = GELOutputManager(base_results_dir=self.temp_dir)

        # Create run directory
        run_dirs = output_manager.create_gel_run_directory()

        # Test validation with missing files
        validation = output_manager.validate_gel_output(run_dirs["run_root"])
        assert validation["valid"] is False
        assert len(validation["errors"]) > 0

        # Create required files
        (run_dirs["run_root"] / "index.html").write_text("<html><body>Test HTML</body></html>")
        (run_dirs["run_root"] / "report.md").write_text("# Test Report\n\nTest content")
        (run_dirs["run_root"] / "manifest.json").write_text('{"test": "manifest"}')

        # Test validation with files present
        validation = output_manager.validate_gel_output(run_dirs["run_root"])
        assert validation["valid"] is True
        assert len(validation["errors"]) == 0
        assert validation["files_found"]["index.html"]["exists"] is True

    def test_gel_output_cleanup(self):
        """
        Test GEL output cleanup functionality.
        """
        output_manager = GELOutputManager(base_results_dir=self.temp_dir)

        # Create multiple run directories
        old_runs = []
        for i in range(7):  # Create 7 runs
            timestamp = datetime(2025, 8, 14, 10, i, 0)  # Different minutes
            run_dirs = output_manager.create_gel_run_directory(
                org="TestOrg", timestamp=timestamp, create_latest_link=False  # Don't create latest link for test
            )
            old_runs.append(run_dirs["run_root"])

        # Test dry run cleanup (keep 3)
        to_delete = output_manager.cleanup_old_runs(org="TestOrg", keep_recent=3, dry_run=True)

        # Should identify 4 runs for deletion (7 - 3)
        assert len(to_delete) == 4

        # All directories should still exist (dry run)
        for run_dir in old_runs:
            assert run_dir.exists()

        # Test actual cleanup
        deleted = output_manager.cleanup_old_runs(org="TestOrg", keep_recent=3, dry_run=False)

        # Should have deleted 4 directories
        assert len(deleted) == 4

        # Check that 3 most recent still exist
        existing_count = sum(1 for run_dir in old_runs if run_dir.exists())
        assert existing_count == 3

    def test_manifest_data_creation(self):
        """
        Test manifest data creation and structure.
        """
        output_manager = GELOutputManager()

        timestamp = datetime.utcnow()
        manifest = output_manager.create_manifest_data(
            scenario="GEL",
            org="TestOrg",
            timestamp=timestamp,
            config_hash="abc123def456",
            population=1000,
            median_salary=72000,
            below_median_pct=38.5,
            gender_gap_pct=7.2,
            intervention_budget_pct=0.5,
            recommended_uplifts_cost_pct=0.42,
            additional_metadata={"test_field": "test_value", "random_seed": 42},
        )

        # Verify manifest structure
        assert manifest["scenario"] == "GEL"
        assert manifest["org"] == "TestOrg"
        assert manifest["population"] == 1000
        assert manifest["median_salary"] == 72000
        assert manifest["gender_gap_pct"] == 7.2
        assert manifest["test_field"] == "test_value"
        assert manifest["random_seed"] == 42

        # Verify file structure metadata
        assert manifest["generated_files"]["html_report"] == "index.html"
        assert manifest["generated_files"]["markdown_report"] == "report.md"
        assert manifest["directory_structure"]["charts"] == "assets/charts/"

    def test_report_content_consistency(self):
        """
        Test that HTML and Markdown reports contain consistent information.
        """
        md_builder = MarkdownReportBuilder(output_dir=self.temp_dir)
        html_builder = HTMLReportBuilder(output_dir=self.temp_dir)

        # Generate both reports
        md_report = md_builder.build_gel_report(self.sample_payload, self.sample_manifest, "consistency_test.md")

        html_report = html_builder.build_gel_report(
            self.sample_payload, self.sample_manifest, None, "consistency_test.html"  # No assets dir
        )

        # Read content
        md_content = md_report.read_text()
        html_content = html_report.read_text()

        # Check for common key information
        key_info = [
            "TestOrg",
            "2025-08-14T10:00:00Z",
            "201 employees"
            if "201" in str(self.sample_manifest["population"])
            else str(self.sample_manifest["population"]),
            "£71,500"
            if "71500" in str(self.sample_manifest["median_salary"])
            else str(self.sample_manifest["median_salary"]),
            "42.3%"
            if "42.3" in str(self.sample_manifest["below_median_pct"])
            else str(self.sample_manifest["below_median_pct"]),
            "6.8%"
            if "6.8" in str(self.sample_manifest["gender_gap_pct"])
            else str(self.sample_manifest["gender_gap_pct"]),
        ]

        for info in key_info:
            # Both reports should contain the key information (allowing for formatting differences)
            assert info in md_content or info.replace(",", "") in md_content.replace(",", "")
            assert info in html_content or info.replace(",", "") in html_content.replace(",", "")

    def test_error_handling_and_recovery(self):
        """
        Test error handling and recovery in GEL workflow.
        """
        output_manager = GELOutputManager(base_results_dir=self.temp_dir)

        # Test with invalid manifest data
        invalid_manifest = {"invalid": "data"}

        run_dirs = output_manager.create_gel_run_directory()

        # Should handle invalid manifest gracefully
        final_paths = output_manager.organize_gel_outputs(run_directories=run_dirs, manifest_data=invalid_manifest)

        # Should still create manifest file
        assert "manifest" in final_paths
        manifest_file = Path(final_paths["manifest"])
        assert manifest_file.exists()

        # Test with non-existent files
        non_existent_html = self.temp_dir / "nonexistent.html"
        non_existent_md = self.temp_dir / "nonexistent.md"

        # Should handle missing files gracefully
        final_paths = output_manager.organize_gel_outputs(
            run_directories=run_dirs,
            html_report=non_existent_html,
            markdown_report=non_existent_md,
            manifest_data=self.sample_manifest,
        )

        # Should not crash, just not include missing files
        assert isinstance(final_paths, dict)

    def test_concurrent_run_handling(self):
        """
        Test handling of concurrent GEL runs.
        """
        output_manager = GELOutputManager(base_results_dir=self.temp_dir)

        # Try to create runs with same timestamp
        timestamp = datetime(2025, 8, 14, 10, 30, 0)

        run_dirs_1 = output_manager.create_gel_run_directory(org="TestOrg", timestamp=timestamp)

        run_dirs_2 = output_manager.create_gel_run_directory(org="TestOrg", timestamp=timestamp)

        # Should create different directories
        assert run_dirs_1["run_root"] != run_dirs_2["run_root"]
        assert run_dirs_1["run_root"].exists()
        assert run_dirs_2["run_root"].exists()

    def test_symlink_fallback(self):
        """
        Test symlink creation and fallback behavior.
        """
        output_manager = GELOutputManager(base_results_dir=self.temp_dir)

        # Create run directory with latest link
        run_dirs = output_manager.create_gel_run_directory(org="TestOrg", create_latest_link=True)

        # Check if latest link was created (or copy on systems without symlink support)
        latest_path = self.temp_dir / "TestOrg" / "latest"

        # Should exist as either symlink or directory copy
        if latest_path.is_symlink():
            # If symlink is supported, verify it points to correct location
            target = latest_path.resolve()
            assert target == run_dirs["run_root"].resolve()
        elif latest_path.is_dir():
            # If copy was used (e.g., Windows), verify structure exists
            assert (latest_path / "assets").exists()

        # Test creating second run (should update latest)
        run_dirs_2 = output_manager.create_gel_run_directory(org="TestOrg", create_latest_link=True)

        # Latest should now point to second run
        if latest_path.is_symlink():
            target = latest_path.resolve()
            assert target == run_dirs_2["run_root"].resolve()


class TestGELCLIIntegration:
    """
    Test GEL CLI integration (mocked orchestrator calls).
    """

    def setup_method(self):
        """
        Set up test fixtures.
        """
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """
        Clean up test fixtures.
        """
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @patch("employee_simulation_orchestrator.HTMLReportBuilder")
    @patch("employee_simulation_orchestrator.MarkdownReportBuilder")
    @patch("employee_simulation_orchestrator.GELPolicyConstraints")
    @patch("employee_simulation_orchestrator.GELOutputManager")
    @patch("employee_simulation_orchestrator.RolesConfigLoader")
    def test_cli_workflow_simulation(self, mock_loader, mock_output_manager, mock_policy, mock_md_builder, mock_html_builder):
        """
        Test simulated CLI workflow with mocked components.
        """
        # Setup mocks
        mock_config = MagicMock()
        mock_config.org = "GEL"
        mock_config.currency = "GBP"
        mock_config.roles = []
        mock_config.intervention_policy.max_direct_reports = 6
        mock_config.intervention_policy.inequality_budget_percent = 0.5

        mock_loader_instance = MagicMock()
        mock_loader_instance.load_config.return_value = mock_config
        mock_loader_instance.calculate_config_hash.return_value = "abc123..."
        mock_loader.return_value = mock_loader_instance

        mock_output_instance = MagicMock()
        mock_run_dirs = {
            "run_root": self.temp_dir / "GEL" / "run_2025-08-14_10-00Z",
            "assets": self.temp_dir / "GEL" / "run_2025-08-14_10-00Z" / "assets",
        }
        # Create the directories for the test
        mock_run_dirs["run_root"].mkdir(parents=True, exist_ok=True)
        mock_run_dirs["assets"].mkdir(parents=True, exist_ok=True)
        
        mock_output_instance.create_gel_run_directory.return_value = mock_run_dirs
        mock_output_instance.create_manifest_data.return_value = {"test": "manifest"}
        mock_output_instance.organize_gel_outputs.return_value = {
            "html_report": str(mock_run_dirs["run_root"] / "index.html"),
            "markdown_report": str(mock_run_dirs["run_root"] / "report.md"),
        }
        mock_output_manager.return_value = mock_output_instance

        # Setup report builder mocks
        mock_md_instance = MagicMock()
        mock_md_instance.build_gel_report.return_value = str(mock_run_dirs["run_root"] / "report.md")
        mock_md_builder.return_value = mock_md_instance

        mock_html_instance = MagicMock()
        mock_html_instance.build_gel_report.return_value = str(mock_run_dirs["run_root"] / "index.html")
        mock_html_builder.return_value = mock_html_instance

        # Setup policy constraints mock
        mock_policy_instance = MagicMock()
        mock_policy_instance.identify_managers_and_teams.return_value = {}
        mock_policy_instance.prioritize_interventions.return_value = {}
        mock_policy_instance.optimize_budget_allocation.return_value = {}
        mock_policy_instance.generate_policy_summary.return_value = {}
        mock_policy.return_value = mock_policy_instance

        # Simulate CLI arguments
        config = {"enable_gel_reporting": True, "gel_org": "GEL", "gel_roles_config_path": "config/orgs/GEL/roles.yaml"}

        simulation_results = {
            "population_data": [],
            "summary_metrics": {"median_salary": 71500, "gender_pay_gap_percent": 6.8},
            "advanced_analysis": {"median_convergence": {}, "intervention_strategies": {}},
        }

        # Import and call the function (would normally be part of orchestrator)
        from employee_simulation_orchestrator import run_gel_reporting

        # Mock orchestrator
        mock_orchestrator = MagicMock()

        result = run_gel_reporting(mock_orchestrator, simulation_results, config)

        # Verify mocks were called
        mock_loader_instance.load_config.assert_called_once()
        mock_output_instance.create_gel_run_directory.assert_called_once()

        # Verify result structure
        assert result["success"] is True
        assert "html_report" in result
        assert "markdown_report" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

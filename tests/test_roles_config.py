#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import yaml

from roles_config import (
    RolesConfig, 
    RolesConfigLoader, 
    Role, 
    InterventionPolicy,
    create_example_config
)


class TestRole:
    """Test Role model validation."""
    
    def test_valid_role(self):
        """Test creating valid role."""
        role = Role(
            title="Software Engineer",
            min_salaries=[65000],
            headcount_hint=5,
            notes="Entry level position"
        )
        
        assert role.title == "Software Engineer"
        assert role.min_salaries == [65000]
        assert role.headcount_hint == 5
        assert role.notes == "Entry level position"
    
    def test_role_multiple_salaries(self):
        """Test role with multiple salary bands."""
        role = Role(
            title="Senior Engineer",
            min_salaries=[85000, 95000, 105000]
        )
        
        # Should be sorted automatically
        assert role.min_salaries == [85000, 95000, 105000]
    
    def test_role_sorts_salaries(self):
        """Test that salaries are sorted automatically."""
        role = Role(
            title="Engineer",
            min_salaries=[95000, 85000, 105000]
        )
        
        assert role.min_salaries == [85000, 95000, 105000]
    
    def test_role_validation_empty_salaries(self):
        """Test validation fails with empty salaries."""
        with pytest.raises(ValueError, match="min_salaries cannot be empty"):
            Role(title="Engineer", min_salaries=[])
    
    def test_role_validation_negative_salary(self):
        """Test validation fails with negative salary."""
        with pytest.raises(ValueError, match="must be positive"):
            Role(title="Engineer", min_salaries=[-1000])
    
    def test_role_validation_unreasonable_salary(self):
        """Test validation fails with unreasonably high salary."""
        with pytest.raises(ValueError, match="unreasonably high"):
            Role(title="Engineer", min_salaries=[2000000])


class TestInterventionPolicy:
    """Test InterventionPolicy model."""
    
    def test_default_policy(self):
        """Test default intervention policy."""
        policy = InterventionPolicy()
        
        assert policy.max_direct_reports == 6
        assert policy.inequality_budget_percent == 0.5
    
    def test_custom_policy(self):
        """Test custom intervention policy."""
        policy = InterventionPolicy(
            max_direct_reports=8,
            inequality_budget_percent=1.0
        )
        
        assert policy.max_direct_reports == 8
        assert policy.inequality_budget_percent == 1.0
    
    def test_policy_validation_negative_reports(self):
        """Test validation fails with invalid max reports."""
        with pytest.raises(ValueError):
            InterventionPolicy(max_direct_reports=0)
    
    def test_policy_validation_excessive_budget(self):
        """Test validation fails with excessive budget percent."""
        with pytest.raises(ValueError):
            InterventionPolicy(inequality_budget_percent=10.0)


class TestRolesConfig:
    """Test complete roles configuration."""
    
    def test_valid_config(self):
        """Test creating valid roles config."""
        roles = [
            Role(title="Engineer", min_salaries=[65000]),
            Role(title="Senior Engineer", min_salaries=[85000])
        ]
        
        config = RolesConfig(
            org="TestOrg",
            currency="USD",
            version=1,
            roles=roles
        )
        
        assert config.org == "TestOrg"
        assert config.currency == "USD"
        assert len(config.roles) == 2
    
    def test_config_duplicate_roles(self):
        """Test validation fails with duplicate role titles."""
        roles = [
            Role(title="Engineer", min_salaries=[65000]),
            Role(title="Engineer", min_salaries=[70000])  # Duplicate
        ]
        
        with pytest.raises(ValueError, match="Duplicate role titles"):
            RolesConfig(org="TestOrg", roles=roles)
    
    def test_config_empty_roles(self):
        """Test validation fails with empty roles list."""
        with pytest.raises(ValueError, match="roles list cannot be empty"):
            RolesConfig(org="TestOrg", roles=[])
    
    def test_config_invalid_currency(self):
        """Test validation fails with invalid currency code."""
        roles = [Role(title="Engineer", min_salaries=[65000])]
        
        with pytest.raises(ValueError):
            RolesConfig(org="TestOrg", currency="INVALID", roles=roles)


class TestRolesConfigLoader:
    """Test roles configuration loader."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.loader = RolesConfigLoader()
        self.sample_config = {
            "org": "TestOrg",
            "currency": "GBP",
            "version": 1,
            "intervention_policy": {
                "max_direct_reports": 6,
                "inequality_budget_percent": 0.5
            },
            "roles": [
                {
                    "title": "Software Engineer",
                    "min_salaries": [65000],
                    "headcount_hint": 5
                },
                {
                    "title": "Senior Software Engineer", 
                    "min_salaries": [85000, 95000],
                    "notes": "Multiple bands"
                }
            ]
        }
    
    def test_load_yaml_config(self):
        """Test loading YAML configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.sample_config, f)
            temp_path = Path(f.name)
        
        try:
            config = self.loader.load_config(temp_path)
            
            assert config.org == "TestOrg"
            assert config.currency == "GBP"
            assert len(config.roles) == 2
            assert config.roles[0].title == "Software Engineer"
            assert config.intervention_policy.max_direct_reports == 6
        finally:
            temp_path.unlink()
    
    def test_load_json_config(self):
        """Test loading JSON configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.sample_config, f)
            temp_path = Path(f.name)
        
        try:
            config = self.loader.load_config(temp_path)
            
            assert config.org == "TestOrg"
            assert len(config.roles) == 2
        finally:
            temp_path.unlink()
    
    def test_load_nonexistent_file(self):
        """Test loading non-existent file fails."""
        with pytest.raises(FileNotFoundError):
            self.loader.load_config("nonexistent.yaml")
    
    def test_load_invalid_yaml(self):
        """Test loading invalid YAML fails."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content:")
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="Invalid YAML format"):
                self.loader.load_config(temp_path)
        finally:
            temp_path.unlink()
    
    def test_load_unsupported_format(self):
        """Test loading unsupported format fails."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("some text")
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(ValueError, match="Unsupported config format"):
                self.loader.load_config(temp_path)
        finally:
            temp_path.unlink()
    
    def test_get_minimum_for_role(self):
        """Test getting minimum salary for role."""
        config = RolesConfig(
            org="TestOrg",
            roles=[
                Role(title="Engineer", min_salaries=[65000, 75000]),
                Role(title="Manager", min_salaries=[95000])
            ]
        )
        
        # Test getting first band (default)
        assert self.loader.get_minimum_for_role(config, "Engineer") == 65000
        
        # Test getting specific band
        assert self.loader.get_minimum_for_role(config, "Engineer", 1) == 75000
        
        # Test getting band beyond available (should return highest)
        assert self.loader.get_minimum_for_role(config, "Engineer", 5) == 75000
        
        # Test non-existent role
        assert self.loader.get_minimum_for_role(config, "NonExistent") is None
    
    def test_get_all_roles(self):
        """Test getting all role titles."""
        config = RolesConfig(
            org="TestOrg",
            roles=[
                Role(title="Engineer", min_salaries=[65000]),
                Role(title="Manager", min_salaries=[95000]),
                Role(title="Director", min_salaries=[120000])
            ]
        )
        
        roles = self.loader.get_all_roles(config)
        
        assert len(roles) == 3
        assert "Engineer" in roles
        assert "Manager" in roles
        assert "Director" in roles
    
    def test_calculate_config_hash(self):
        """Test configuration hash calculation."""
        config1 = RolesConfig(
            org="TestOrg",
            roles=[Role(title="Engineer", min_salaries=[65000])]
        )
        
        config2 = RolesConfig(
            org="TestOrg", 
            roles=[Role(title="Engineer", min_salaries=[65000])]
        )
        
        # Same configs should have same hash
        hash1 = self.loader.calculate_config_hash(config1)
        hash2 = self.loader.calculate_config_hash(config2)
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex length
    
    def test_validate_config_file_success(self):
        """Test successful config file validation."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(self.sample_config, f)
            temp_path = Path(f.name)
        
        try:
            result = self.loader.validate_config_file(temp_path)
            
            assert result["valid"] is True
            assert "config" in result
            assert "hash" in result
            assert result["summary"]["org"] == "TestOrg"
            assert result["summary"]["total_roles"] == 2
            assert result["summary"]["roles_with_multiple_bands"] == 1
        finally:
            temp_path.unlink()
    
    def test_validate_config_file_failure(self):
        """Test config file validation failure."""
        invalid_config = {"invalid": "config"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(invalid_config, f)
            temp_path = Path(f.name)
        
        try:
            result = self.loader.validate_config_file(temp_path)
            
            assert result["valid"] is False
            assert "error" in result
        finally:
            temp_path.unlink()


class TestCreateExampleConfig:
    """Test example config creation."""
    
    def test_create_example_config(self):
        """Test creating example configuration."""
        config = create_example_config()
        
        assert config.org == "ExampleOrg"
        assert config.currency == "USD"
        assert len(config.roles) == 3
        
        # Check specific roles
        role_titles = [role.title for role in config.roles]
        assert "Software Engineer" in role_titles
        assert "Senior Software Engineer" in role_titles
        assert "Product Manager" in role_titles


# Integration test for the full workflow
class TestFullWorkflow:
    """Test complete workflow with real files."""
    
    def test_gel_config_workflow(self):
        """Test complete workflow using GEL configuration."""
        # Use the actual GEL config file
        config_path = Path("config/orgs/GEL/roles.yaml")
        
        if config_path.exists():
            loader = RolesConfigLoader()
            
            # Load and validate
            config = loader.load_config(config_path)
            
            # Verify basic structure
            assert config.org == "GEL"
            assert config.currency == "GBP"
            assert len(config.roles) > 0
            
            # Test role lookup
            data_engineer_min = loader.get_minimum_for_role(config, "Data Engineer")
            assert data_engineer_min == 73000
            
            # Test hash calculation
            config_hash = loader.calculate_config_hash(config)
            assert len(config_hash) == 64
            
            # Test validation
            validation = loader.validate_config_file(config_path)
            assert validation["valid"] is True


if __name__ == "__main__":
    # Run tests manually if needed
    pytest.main([__file__, "-v"])
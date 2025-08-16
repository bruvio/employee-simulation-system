#!/usr/bin/env python3

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, ValidationError, field_validator
import yaml

from logger import LOGGER


class InterventionPolicy(BaseModel):
    """
    Policy constraints for management interventions.

    Args:
        max_direct_reports: Maximum number of direct reports per manager
        inequality_budget_percent: Budget percentage for inequality remediation
    """

    max_direct_reports: int = Field(default=6, ge=1, description="Maximum direct reports per manager")
    inequality_budget_percent: float = Field(
        default=0.5, ge=0.0, le=5.0, description="Budget percentage (0.5 = 0.5%) for inequality remediation"
    )


class Role(BaseModel):
    """
    Individual role configuration with salary minimums.

    Args:
        title: Job title/role name
        min_salaries: List of minimum salaries (supports multiple bands)
        headcount_hint: Optional expected headcount for planning
        notes: Optional descriptive notes (e.g., contract type, team)
    """

    title: str = Field(description="Job title or role name")
    min_salaries: List[float] = Field(description="List of minimum salaries (supports multiple bands)", min_length=1)
    headcount_hint: Optional[int] = Field(default=None, ge=0, description="Optional expected headcount for planning")
    notes: Optional[str] = Field(default=None, description="Optional descriptive notes")

    @field_validator("min_salaries")
    @classmethod
    def validate_salaries(cls, v):
        """
        Validate salary values are positive and reasonable.
        """
        if not v:
            raise ValueError("min_salaries cannot be empty")

        for salary in v:
            if salary <= 0:
                raise ValueError(f"Salary {salary} must be positive")
            if salary > 1_000_000:  # Reasonable upper bound
                raise ValueError(f"Salary {salary} seems unreasonably high")

        # Sort salaries for consistency
        return sorted(v)


class RolesConfig(BaseModel):
    """
    Complete role configuration for an organization.

    Args:
        org: Organization identifier
        currency: Currency code (e.g., 'GBP', 'USD')
        version: Configuration version number
        intervention_policy: Manager intervention constraints
        roles: List of role configurations
    """

    org: str = Field(description="Organization identifier")
    currency: str = Field(default="GBP", pattern=r"^[A-Z]{3}$", description="3-letter currency code")
    version: int = Field(default=1, ge=1, description="Configuration version")
    intervention_policy: InterventionPolicy = Field(
        default_factory=InterventionPolicy, description="Manager intervention constraints"
    )
    roles: List[Role] = Field(description="List of role configurations")

    @field_validator("roles")
    @classmethod
    def validate_roles(cls, v):
        """
        Validate role list has no duplicate titles.
        """
        if not v:
            raise ValueError("roles list cannot be empty")

        titles = [role.title for role in v]
        if len(titles) != len(set(titles)):
            duplicates = [title for title in titles if titles.count(title) > 1]
            raise ValueError(f"Duplicate role titles found: {duplicates}")

        return v


class RolesConfigLoader:
    """
    Loader and validator for role configuration files.

    Supports YAML and JSON formats with comprehensive validation.
    """

    def __init__(self):
        self.logger = LOGGER

    def load_config(self, config_path: Union[str, Path]) -> RolesConfig:
        """
        Load and validate role configuration from file.

        Args:
            config_path: Path to YAML or JSON configuration file

        Returns:
            Validated RolesConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValidationError: If config is invalid
            ValueError: If file format is unsupported
        """
        config_path = Path(config_path)

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        self.logger.info(f"Loading roles config from {config_path}")

        try:
            # Load based on file extension
            with open(config_path, "r", encoding="utf-8") as f:
                if config_path.suffix.lower() in [".yaml", ".yml"]:
                    data = yaml.safe_load(f)
                elif config_path.suffix.lower() == ".json":
                    data = json.load(f)
                else:
                    raise ValueError(f"Unsupported config format: {config_path.suffix}")

            # Validate and create config
            config = RolesConfig(**data)

            self.logger.info(
                f"Successfully loaded config for {config.org}: "
                f"{len(config.roles)} roles, {config.currency} currency"
            )

            return config

        except yaml.YAMLError as e:
            raise ValidationError(f"Invalid YAML format: {e}")
        except json.JSONDecodeError as e:
            raise ValidationError(f"Invalid JSON format: {e}")
        except ValidationError as e:
            self.logger.error(f"Config validation failed: {e}")
            raise
        except Exception as e:
            raise ValidationError(f"Failed to load config: {e}")

    def get_minimum_for_role(self, config: RolesConfig, title: str, band_index: int = 0) -> Optional[float]:
        """
        Get minimum salary for a specific role.

        Args:
            config: Loaded roles configuration
            title: Job title to lookup
            band_index: Index for multiple salary bands (default: 0 for lowest)

        Returns:
            Minimum salary or None if role not found
        """
        for role in config.roles:
            if role.title == title:
                if band_index < len(role.min_salaries):
                    return role.min_salaries[band_index]
                else:
                    # Return highest band if index exceeds available bands
                    return role.min_salaries[-1]

        self.logger.warning(f"Role '{title}' not found in config")
        return None

    def get_all_roles(self, config: RolesConfig) -> List[str]:
        """
        Get list of all role titles in config.

        Args:
            config: Loaded roles configuration

        Returns:
            List of role titles
        """
        return [role.title for role in config.roles]

    def calculate_config_hash(self, config: RolesConfig) -> str:
        """
        Calculate SHA256 hash of configuration for tracking changes.

        Args:
            config: Roles configuration

        Returns:
            SHA256 hash string
        """
        # Create deterministic string representation
        config_dict = config.model_dump(mode="json")
        config_str = json.dumps(config_dict, sort_keys=True, separators=(",", ":"))

        # Calculate hash
        return hashlib.sha256(config_str.encode("utf-8")).hexdigest()

    def validate_config_file(self, config_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Validate configuration file and return summary.

        Args:
            config_path: Path to configuration file

        Returns:
            Dictionary with validation results and summary statistics
        """
        try:
            config = self.load_config(config_path)

            # Calculate summary statistics
            total_roles = len(config.roles)
            roles_with_multiple_bands = sum(1 for role in config.roles if len(role.min_salaries) > 1)
            min_salary = min(min(role.min_salaries) for role in config.roles)
            max_salary = max(max(role.min_salaries) for role in config.roles)
            roles_with_hints = sum(1 for role in config.roles if role.headcount_hint)

            return {
                "valid": True,
                "config": config,
                "hash": self.calculate_config_hash(config),
                "summary": {
                    "org": config.org,
                    "currency": config.currency,
                    "version": config.version,
                    "total_roles": total_roles,
                    "roles_with_multiple_bands": roles_with_multiple_bands,
                    "salary_range": {"min": min_salary, "max": max_salary},
                    "roles_with_headcount_hints": roles_with_hints,
                    "intervention_policy": {
                        "max_direct_reports": config.intervention_policy.max_direct_reports,
                        "budget_percent": config.intervention_policy.inequality_budget_percent,
                    },
                },
            }

        except Exception as e:
            return {"valid": False, "error": str(e), "summary": None}


def create_example_config() -> RolesConfig:
    """
    Create example configuration for testing.

    Returns:
        Example RolesConfig instance
    """
    return RolesConfig(
        org="ExampleOrg",
        currency="USD",
        version=1,
        intervention_policy=InterventionPolicy(max_direct_reports=6, inequality_budget_percent=0.5),
        roles=[
            Role(title="Software Engineer", min_salaries=[65000], headcount_hint=5),
            Role(
                title="Senior Software Engineer",
                min_salaries=[85000, 95000],
                notes="Two bands for different specializations",
            ),
            Role(title="Product Manager", min_salaries=[90000], headcount_hint=2),
        ],
    )


if __name__ == "__main__":
    # Example usage and validation
    loader = RolesConfigLoader()

    # Create and validate example config
    example_config = create_example_config()
    print("Example config created successfully")
    print(f"Config hash: {loader.calculate_config_hash(example_config)}")

    # Test role lookup
    salary = loader.get_minimum_for_role(example_config, "Senior Software Engineer", 1)
    print(f"Senior Software Engineer (band 1): ${salary:,.2f}")

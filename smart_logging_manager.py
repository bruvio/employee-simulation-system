#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

from datetime import datetime
from enum import Enum
import json
import logging
from pathlib import Path
import sys
from typing import Any, Dict, Optional


class LogLevel(Enum):
    """Enhanced log levels with smart filtering."""

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"
    DEBUG = "DEBUG"


class SmartLoggingManager:
    """Smart logging manager with configurable levels and reduced noise.

    Addresses the excessive DEBUG-level logging noted in the PRP requirements.

    Args:

    Returns:
    """

    def __init__(
        self,
        log_level: str = "INFO",
        enable_progress_indicators: bool = True,
        log_file_path: Optional[str] = None,
        suppress_noisy_libraries: bool = True,
    ):
        """Initialize smart logging manager.

        Args:
            log_level: Logging level (ERROR/WARNING/INFO/DEBUG)
            enable_progress_indicators: Show progress bars and indicators
            log_file_path: Optional path to log file
            suppress_noisy_libraries: Suppress matplotlib/boto3 debug logs
        """
        self.log_level = LogLevel(log_level.upper())
        self.enable_progress = enable_progress_indicators
        self.log_file_path = log_file_path
        self.suppress_noisy = suppress_noisy_libraries

        # Progress tracking
        self.current_phase = ""
        self.phase_progress = {}
        self.execution_stats = {
            "start_time": datetime.now(),
            "phases_completed": [],
            "total_operations": 0,
            "warnings_count": 0,
            "errors_count": 0,
        }

        # Create logger instance first (needed in _setup_logging)
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize logging configuration
        self._setup_logging()

        self.logger.info(f"SmartLoggingManager initialized with level: {self.log_level.value}")

    def _setup_logging(self):
        """Configure logging with smart filtering."""
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        # Set root level based on configuration
        level_mapping = {
            LogLevel.ERROR: logging.ERROR,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.INFO: logging.INFO,
            LogLevel.DEBUG: logging.DEBUG,
        }
        root_level = level_mapping[self.log_level]
        root_logger.setLevel(root_level)

        # Create formatter with enhanced format
        if self.log_level == LogLevel.DEBUG:
            # Detailed format for debugging
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
            )
        else:
            # Clean format for production
            formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # Console handler with intelligent filtering
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(root_level)
        root_logger.addHandler(console_handler)

        # Optional file handler
        if self.log_file_path:
            try:
                log_path = Path(self.log_file_path)
                log_path.parent.mkdir(parents=True, exist_ok=True)

                file_handler = logging.FileHandler(self.log_file_path)
                file_handler.setFormatter(formatter)
                file_handler.setLevel(logging.DEBUG)  # File gets all logs
                root_logger.addHandler(file_handler)

                self.logger.info(f"File logging enabled: {self.log_file_path}")
            except Exception as e:
                print(f"Warning: Could not setup file logging: {e}")

        # Suppress noisy third-party libraries
        if self.suppress_noisy:
            self._suppress_noisy_loggers()

    def _suppress_noisy_loggers(self):
        """Suppress debug logs from noisy third-party libraries."""
        noisy_loggers = [
            "matplotlib",
            "matplotlib.pyplot",
            "matplotlib.font_manager",
            "PIL",
            "PIL.PngImagePlugin",
            "urllib3",
            "urllib3.connectionpool",
            "boto3",
            "botocore",
            "boto3.resources.action",
            "boto3.resources.factory",
            "s3transfer",
            "botocore.hooks",
            "botocore.auth",
            "botocore.endpoint",
            "plotly",
            "plotly.graph_objects",
            "pandas",
            "numpy",
        ]

        suppress_level = logging.WARNING if self.log_level != LogLevel.DEBUG else logging.INFO

        for logger_name in noisy_loggers:
            noisy_logger = logging.getLogger(logger_name)
            noisy_logger.setLevel(suppress_level)

        if self.log_level != LogLevel.DEBUG:
            self.logger.debug(f"Suppressed {len(noisy_loggers)} noisy loggers to {suppress_level}")

    def start_phase(self, phase_name: str, total_operations: int = 0):
        """Start a new execution phase with progress tracking.

        Args:
          phase_name: str:
          total_operations: int:  (Default value = 0)

        Returns:
        """
        self.current_phase = phase_name
        self.phase_progress[phase_name] = {
            "start_time": datetime.now(),
            "total_operations": total_operations,
            "completed_operations": 0,
            "status": "in_progress",
        }

        if self.enable_progress:
            print(f"\n🚀 Starting {phase_name}")
            if total_operations > 0:
                print(f"   Operations to complete: {total_operations}")

        self.logger.info(f"Phase started: {phase_name}")

    def update_progress(self, operation_name: str, completed_count: int = 1):
        """Update progress for the current phase.

        Args:
          operation_name: str:
          completed_count: int:  (Default value = 1)

        Returns:
        """
        if not self.current_phase or self.current_phase not in self.phase_progress:
            return

        phase_data = self.phase_progress[self.current_phase]
        phase_data["completed_operations"] += completed_count
        self.execution_stats["total_operations"] += completed_count

        if self.enable_progress:
            if phase_data["total_operations"] > 0:
                progress_pct = (phase_data["completed_operations"] / phase_data["total_operations"]) * 100
                print(f"   ✓ {operation_name} ({progress_pct:.1f}%)")
            else:
                print(f"   ✓ {operation_name}")

    def complete_phase(self, phase_name: str = None):
        """Complete the current phase.

        Args:
          phase_name: str:  (Default value = None)

        Returns:
        """
        phase_name = phase_name or self.current_phase
        if phase_name not in self.phase_progress:
            return

        phase_data = self.phase_progress[phase_name]
        phase_data["status"] = "completed"
        phase_data["end_time"] = datetime.now()
        phase_data["duration"] = phase_data["end_time"] - phase_data["start_time"]

        self.execution_stats["phases_completed"].append(phase_name)

        duration = phase_data["duration"].total_seconds()
        if self.enable_progress:
            print(f"✅ {phase_name} completed ({duration:.1f}s)")

        self.logger.info(f"Phase completed: {phase_name} ({duration:.1f}s)")

        # Clear current phase if it matches
        if self.current_phase == phase_name:
            self.current_phase = ""

    def log_warning(self, message: str, **kwargs):
        """Log warning with enhanced tracking.

        Args:
          message: str:
          **kwargs:

        Returns:
        """
        self.execution_stats["warnings_count"] += 1
        self.logger.warning(message, **kwargs)

        if self.enable_progress:
            print(f"⚠️  {message}")

    def log_error(self, message: str, exception: Exception = None, **kwargs):
        """Log error with enhanced tracking.

        Args:
          message: str:
          exception: Exception:  (Default value = None)
          **kwargs:

        Returns:
        """
        self.execution_stats["errors_count"] += 1

        if exception:
            self.logger.error(f"{message}: {str(exception)}", **kwargs)
            if self.log_level == LogLevel.DEBUG:
                self.logger.exception("Exception details:")
        else:
            self.logger.error(message, **kwargs)

        if self.enable_progress:
            print(f"❌ {message}")

    def log_info(self, message: str, **kwargs):
        """Log info message.

        Args:
          message: str:
          **kwargs:

        Returns:
        """
        self.logger.info(message, **kwargs)

    def log_debug(self, message: str, **kwargs):
        """Log debug message (only in DEBUG mode)

        Args:
          message: str:
          **kwargs:

        Returns:
        """
        if self.log_level == LogLevel.DEBUG:
            self.logger.debug(message, **kwargs)

    def log_success(self, message: str, **kwargs):
        """Log success message with visual indicator.

        Args:
          message: str:
          **kwargs:

        Returns:
        """
        self.logger.info(message, **kwargs)

        if self.enable_progress:
            print(f"✅ {message}")

    def generate_execution_summary(self) -> Dict[str, Any]:
        """Generate comprehensive execution summary."""
        end_time = datetime.now()
        total_duration = end_time - self.execution_stats["start_time"]

        summary = {
            "execution_summary": {
                "start_time": self.execution_stats["start_time"].isoformat(),
                "end_time": end_time.isoformat(),
                "total_duration_seconds": total_duration.total_seconds(),
                "phases_completed": self.execution_stats["phases_completed"],
                "total_operations": self.execution_stats["total_operations"],
                "warnings_count": self.execution_stats["warnings_count"],
                "errors_count": self.execution_stats["errors_count"],
                "success_rate": self._calculate_success_rate(),
            },
            "phase_details": {},
            "configuration": {
                "log_level": self.log_level.value,
                "progress_indicators_enabled": self.enable_progress,
                "file_logging": bool(self.log_file_path),
                "noisy_libraries_suppressed": self.suppress_noisy,
            },
        }

        # Add phase-specific details
        for phase_name, phase_data in self.phase_progress.items():
            duration = None
            if "end_time" in phase_data and "start_time" in phase_data:
                duration = (phase_data["end_time"] - phase_data["start_time"]).total_seconds()

            summary["phase_details"][phase_name] = {
                "status": phase_data["status"],
                "operations_completed": phase_data["completed_operations"],
                "total_operations": phase_data["total_operations"],
                "duration_seconds": duration,
                "start_time": phase_data["start_time"].isoformat(),
            }

            if "end_time" in phase_data:
                summary["phase_details"][phase_name]["end_time"] = phase_data["end_time"].isoformat()

        return summary

    def _calculate_success_rate(self) -> float:
        """Calculate overall success rate based on errors vs operations."""
        if self.execution_stats["total_operations"] == 0:
            return 1.0

        error_rate = self.execution_stats["errors_count"] / self.execution_stats["total_operations"]
        return max(0.0, 1.0 - error_rate)

    def print_execution_summary(self):
        """Print formatted execution summary."""
        summary = self.generate_execution_summary()
        exec_summary = summary["execution_summary"]

        print("\n" + "=" * 60)
        print("📊 EXECUTION SUMMARY")
        print("=" * 60)

        duration_str = f"{exec_summary['total_duration_seconds']:.1f}s"
        print(f"⏱️  Total Duration: {duration_str}")
        print(f"🔧 Operations Completed: {exec_summary['total_operations']}")
        print(f"✅ Phases Completed: {len(exec_summary['phases_completed'])}")

        if exec_summary["warnings_count"] > 0:
            print(f"⚠️  Warnings: {exec_summary['warnings_count']}")

        if exec_summary["errors_count"] > 0:
            print(f"❌ Errors: {exec_summary['errors_count']}")

        success_rate = exec_summary["success_rate"] * 100
        print(f"📈 Success Rate: {success_rate:.1f}%")

        # Phase breakdown
        if summary["phase_details"]:
            print("\n📋 Phase Breakdown:")
            for phase_name, phase_info in summary["phase_details"].items():
                status_icon = "✅" if phase_info["status"] == "completed" else "🔄"
                duration = f"{phase_info['duration_seconds']:.1f}s" if phase_info["duration_seconds"] else "ongoing"
                print(f"   {status_icon} {phase_name}: {duration}")

        print("=" * 60)

    def export_summary(self, output_path: str):
        """Export execution summary to JSON file.

        Args:
          output_path: str:

        Returns:
        """
        try:
            summary = self.generate_execution_summary()

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w") as f:
                json.dump(summary, f, indent=2, default=str)

            self.log_success(f"Execution summary exported: {output_path}")
            return True

        except Exception as e:
            self.log_error("Failed to export execution summary", e)
            return False

    def get_logger(self, name: str = None) -> logging.Logger:
        """Get a configured logger instance.

        Args:
          name: str:  (Default value = None)

        Returns:
        """
        logger_name = name or f"{self.__class__.__name__}.client"
        return logging.getLogger(logger_name)


# Singleton instance for easy access
_smart_logger_instance = None


def get_smart_logger(log_level: str = "INFO", **kwargs) -> SmartLoggingManager:
    """Get or create global SmartLoggingManager instance.

    Args:
      log_level: str:  (Default value = "INFO")
      **kwargs:

    Returns:
    """
    global _smart_logger_instance

    if _smart_logger_instance is None:
        _smart_logger_instance = SmartLoggingManager(log_level=log_level, **kwargs)

    return _smart_logger_instance


def configure_smart_logging(log_level: str = "INFO", **kwargs):
    """Configure global smart logging.

    Args:
      log_level: str:  (Default value = "INFO")
      **kwargs:

    Returns:
    """
    global _smart_logger_instance
    _smart_logger_instance = SmartLoggingManager(log_level=log_level, **kwargs)
    return _smart_logger_instance

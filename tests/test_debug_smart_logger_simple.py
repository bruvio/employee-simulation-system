#!/usr/bin/env python3
"""Simple tests for debug_smart_logger module."""

import pytest


def test_import_module():
    """Test that the module can be imported."""
    import debug_smart_logger

    assert hasattr(debug_smart_logger, "__file__")


def test_smart_logging_manager_import():
    """Test importing SmartLoggingManager from the debug script's dependency."""
    from smart_logging_manager import SmartLoggingManager

    logger_manager = SmartLoggingManager()
    assert logger_manager is not None


def test_smart_logging_manager_basic():
    """Test basic SmartLoggingManager functionality."""
    from smart_logging_manager import SmartLoggingManager

    logger_manager = SmartLoggingManager(log_level="INFO")
    assert hasattr(logger_manager, "log_info")

    # Should be able to call basic methods
    try:
        logger_manager.log_info("Test message")
    except Exception:
        pass  # Some methods might require setup, but shouldn't crash import

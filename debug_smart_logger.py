#!/usr/bin/env python3

"""Debug SmartLoggingManager."""

from smart_logging_manager import SmartLoggingManager

# Test basic functionality
try:
    print("Testing SmartLoggingManager basic functionality...")
    smart_logger = SmartLoggingManager(log_level="INFO", enable_progress_indicators=True)
    print(f"SmartLoggingManager created: {smart_logger}")
    print(f"Has logger attribute: {hasattr(smart_logger, 'logger')}")
    print(f"Has get_logger method: {hasattr(smart_logger, 'get_logger')}")

    if hasattr(smart_logger, "logger"):
        print("✅ SmartLoggingManager has logger attribute")
    else:
        print("❌ SmartLoggingManager missing logger attribute")

    if hasattr(smart_logger, "get_logger"):
        client_logger = smart_logger.get_logger("TestClient")
        print("✅ get_logger method works")
    else:
        print("❌ get_logger method missing")

    smart_logger.log_info("Test message")
    print("✅ SmartLoggingManager basic test passed")

except Exception as e:
    print(f"❌ SmartLoggingManager basic test failed: {e}")
    import traceback

    traceback.print_exc()

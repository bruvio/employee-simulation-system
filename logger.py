# logging_config.py
import logging
import os

log_level = os.getenv("LOG_LEVEL", "DEBUG").upper()  # Default to 'DEBUG' if not set
level = logging.getLevelName(log_level)
LOGGER = logging.getLogger(__name__)

# Custom formatter to exclude request ID
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Configure the root logger
root_logger = logging.getLogger()
root_logger.setLevel(level)

# Remove existing handlers (if any)
if root_logger.hasHandlers():
    root_logger.handlers.clear()

# Add custom handler
handler = logging.StreamHandler()
handler.setFormatter(formatter)
root_logger.addHandler(handler)

# Set level for the specific logger
LOGGER.setLevel(level)

# Suppress logs from noisy libraries
for name in logging.Logger.manager.loggerDict.keys():
    if (
        ("boto" in name)
        or ("urllib3" in name)
        or ("s3transfer" in name)
        or ("boto3" in name)
        or ("botocore" in name)
        or ("nose" in name)
    ):
        logging.getLogger(name).setLevel(logging.CRITICAL)

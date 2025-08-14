"""Centralized constants for the employee simulation system."""

# Population Configuration
DEFAULT_POPULATION_SIZE = 1000
MIN_POPULATION_SIZE = 1
MAX_POPULATION_SIZE = 10000
DEFAULT_RANDOM_SEED = 42

# Level Distribution (6 levels)
DEFAULT_LEVEL_DISTRIBUTION = [0.25, 0.25, 0.20, 0.15, 0.10, 0.05]

# Performance Ratings
PERFORMANCE_RATINGS = ["Not met", "Partially met", "Achieving", "High Performing", "Exceeding"]

# Gender Configuration
DEFAULT_GENDER_DISTRIBUTION = {"Male": 0.65, "Female": 0.35}
DEFAULT_GENDER_PAY_GAP_PERCENT = 15.0

# Salary Constraints by Level
DEFAULT_SALARY_CONSTRAINTS = {
    1: {"min": 28000, "max": 35000, "median_target": 30000},
    2: {"min": 45000, "max": 72000, "median_target": 60000},
    3: {"min": 72000, "max": 95000, "median_target": 83939},
    4: {"min": 76592, "max": 103624, "median_target": 90108},
    5: {"min": 76592, "max": 103624, "median_target": 90108},
    6: {"min": 76592, "max": 103624, "median_target": 90108},
}

# Analysis Configuration
DEFAULT_ANALYSIS_YEARS = 5
DEFAULT_CONFIDENCE_LEVEL = 0.95
DEFAULT_MARKET_INFLATION_RATE = 0.025

# Convergence Analysis
DEFAULT_MIN_GAP_PERCENT = 5.0
DEFAULT_TARGET_GAP_PERCENT = 0.05
DEFAULT_MAX_YEARS = 3
DEFAULT_BUDGET_LIMIT_PERCENT = 0.5

# File Configuration
DEFAULT_OUTPUT_FORMAT = "text"
DEFAULT_OUTPUT_DIR = "simulation_results"
DEFAULT_REPORTS_DIR = "reports"

# Visualization Configuration
DEFAULT_CHART_WIDTH = 800
DEFAULT_CHART_HEIGHT = 600
DEFAULT_DPI = 300

# Complexity Thresholds
MAX_FUNCTION_LINES = 50
MAX_FILE_LINES = 500
MAX_METHOD_COUNT_PER_CLASS = 20

# Currency and Formatting
CURRENCY_SYMBOL = "£"
PERCENTAGE_DECIMAL_PLACES = 1
CURRENCY_DECIMAL_PLACES = 2

# Validation Limits
MIN_SALARY = 20000
MAX_SALARY = 200000
MIN_LEVEL = 1
MAX_LEVEL = 6
MIN_YEARS_EXPERIENCE = 0
MAX_YEARS_EXPERIENCE = 50

# Test Configuration
TEST_POPULATION_SIZE = 100
TEST_RANDOM_SEED = 42
TEST_COVERAGE_THRESHOLD = 0.90

# Export Configuration
EXPORT_FORMATS = ["json", "csv", "xlsx", "text"]
DEFAULT_EXPORT_FORMAT = "json"

# Logging Configuration
DEFAULT_LOG_LEVEL = "INFO"
MAX_LOG_MESSAGE_LENGTH = 1000

# Performance Configuration
DEFAULT_CHUNK_SIZE = 1000
MAX_CONCURRENT_WORKERS = 4

# Employee Simulation System - Development Docker Environment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt requirements-test.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir -r requirements-test.txt

# Copy source code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app
ENV SIMULATION_DEFAULT_POPULATION_SIZE=1000
ENV SIMULATION_DEFAULT_RANDOM_SEED=42
ENV GENDER_PAY_GAP_DEFAULT_PERCENT=15.8
ENV MAX_PROJECTION_YEARS=10
ENV BUDGET_CONSTRAINT_PERCENT=0.005

# Create directories for outputs
RUN mkdir -p artifacts logs images

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command
CMD ["python", "-m", "pytest", "-v"]
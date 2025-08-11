"""Employee Simulation System - Advanced salary progression modeling and simulation."""

__version__ = "1.0.0"
__author__ = "Bruno Viola"
__email__ = "bruno.viola@example.com"

# Import main components for convenience
try:
    from .employee_simulation_orchestrator import EmployeeSimulationOrchestrator
    from .salary_forecasting_engine import SalaryForecastingEngine
    from .performance_review_system import PerformanceReviewSystem
    from .analyze_individual_progression import analyze_progression
    from .model_interventions import model_interventions
    
    __all__ = [
        'EmployeeSimulationOrchestrator',
        'SalaryForecastingEngine', 
        'PerformanceReviewSystem',
        'analyze_progression',
        'model_interventions',
        '__version__',
    ]
except ImportError as e:
    # Handle import errors gracefully during package installation
    import warnings
    warnings.warn(f"Some modules could not be imported: {e}")
    __all__ = ['__version__']
#!/Users/brunoviola/bruvio-tools/.venv/bin/python3

from datetime import datetime
from functools import wraps
import gc
import time
from typing import Any, Callable, Dict, List, Optional
import warnings

import numpy as np
import pandas as pd
import psutil


class PerformanceOptimizationManager:
    """Performance optimization manager for large-scale employee simulations.

    Implements Phase 4 PRP requirements for handling 10K+ employee populations.
    """

    def __init__(self, smart_logger=None):
        self.smart_logger = smart_logger
        self.performance_metrics = {}
        self.memory_checkpoints = {}
        self.optimization_config = {
            "chunk_size": 1000,  # Process employees in chunks
            "memory_threshold_mb": 500,  # Memory usage threshold
            "gc_frequency": 100,  # Garbage collection frequency
            "use_vectorized_ops": True,  # Use pandas/numpy vectorization
            "batch_export_size": 500,  # Batch size for exports
            "enable_progress_tracking": True,
            "memory_monitoring": True,
        }

        # Performance tracking
        self.operation_times = {}
        self.memory_usage = {}
        self.optimization_applied = []

    def _log(self, message: str, level: str = "info"):
        """Helper method for logging."""
        if self.smart_logger:
            getattr(self.smart_logger, f"log_{level}")(message)
        else:
            print(f"[{level.upper()}] {message}")

    def performance_monitor(self, operation_name: str):
        """Decorator to monitor performance of operations."""

        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Start monitoring
                start_time = time.time()
                start_memory = self._get_memory_usage()

                try:
                    # Execute function
                    result = func(*args, **kwargs)

                    # Record performance metrics
                    end_time = time.time()
                    end_memory = self._get_memory_usage()

                    duration = end_time - start_time
                    memory_delta = end_memory - start_memory

                    self.operation_times[operation_name] = {
                        "duration_seconds": duration,
                        "start_memory_mb": start_memory,
                        "end_memory_mb": end_memory,
                        "memory_delta_mb": memory_delta,
                        "timestamp": datetime.now().isoformat(),
                    }

                    if self.optimization_config["enable_progress_tracking"]:
                        self._log(
                            f"Operation {operation_name} completed in {duration:.2f}s (Memory: {memory_delta:+.1f}MB)"
                        )

                    return result

                except Exception as e:
                    self._log(f"Operation {operation_name} failed: {e}", "error")
                    raise

            return wrapper

        return decorator

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except Exception:
            return 0.0

    def optimize_population_generation(self, population_size: int) -> Dict[str, Any]:
        """Optimize population generation for large sizes.

        Args:
            population_size: Target population size

        Returns:
            Optimization configuration and recommendations
        """
        self._log(f"Optimizing population generation for {population_size:,} employees")

        optimization_plan = {
            "population_size": population_size,
            "optimization_strategy": "standard",
            "chunk_size": self.optimization_config["chunk_size"],
            "memory_management": {},
            "vectorization": {},
            "recommendations": [],
        }

        # Adjust chunk size based on population
        if population_size > 10000:
            optimization_plan["chunk_size"] = max(500, population_size // 20)
            optimization_plan["optimization_strategy"] = "large_population"
            optimization_plan["recommendations"].append("Use chunked processing")
            self.optimization_applied.append("chunked_processing")

        if population_size > 50000:
            optimization_plan["chunk_size"] = max(200, population_size // 50)
            optimization_plan["optimization_strategy"] = "massive_population"
            optimization_plan["recommendations"].extend(
                [
                    "Enable aggressive garbage collection",
                    "Use memory-mapped files for data storage",
                    "Consider distributed processing",
                ]
            )
            self.optimization_applied.extend(["aggressive_gc", "memory_mapping"])

        # Memory management strategies
        optimization_plan["memory_management"] = {
            "enable_gc": population_size > 5000,
            "gc_frequency": max(50, self.optimization_config["gc_frequency"] // max(1, population_size // 1000)),
            "memory_monitoring": population_size > 1000,
            "data_types_optimization": population_size > 10000,
        }

        # Vectorization strategies
        optimization_plan["vectorization"] = {
            "use_numpy_arrays": population_size > 1000,
            "batch_operations": population_size > 5000,
            "vectorized_calculations": population_size > 500,
        }

        self._log(f"Optimization strategy: {optimization_plan['optimization_strategy']}")
        return optimization_plan

    def optimize_story_identification(
        self, population_data: List[Dict], max_per_category: int, chunk_size: Optional[int] = None
    ) -> Dict[str, List]:
        """Optimize employee story identification for large populations.

        Args:
            population_data: Full employee population
            max_per_category: Maximum employees per category
            chunk_size: Optional chunk size override

        Returns:
            Optimized tracked employees by category
        """
        if chunk_size is None:
            chunk_size = self.optimization_config["chunk_size"]

        population_size = len(population_data)
        self._log(f"Optimizing story identification for {population_size:,} employees")

        # Manual performance monitoring
        start_time = time.time()
        start_memory = self._get_memory_usage()

        # Convert to DataFrame for vectorized operations
        df = pd.DataFrame(population_data)

        # Optimize data types to reduce memory usage
        if population_size > 10000:
            df = self._optimize_dataframe_dtypes(df)
            self.optimization_applied.append("dtype_optimization")

        tracked_employees = {}

        # Gender gap identification (vectorized)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            # Vectorized gender gap analysis
            gender_salary_stats = df.groupby(["level", "gender"])["salary"].agg(["mean", "median"]).reset_index()

            for level in df["level"].unique():
                level_stats = gender_salary_stats[gender_salary_stats["level"] == level]
                if len(level_stats) >= 2:  # Need at least 2 gender groups
                    max_median = level_stats["median"].max()
                    min_median = level_stats["median"].min()
                    gap_threshold = (max_median - min_median) / max_median

                    if gap_threshold > 0.05:  # 5% gap threshold
                        # Find employees in the lower-paid gender group
                        lower_gender = level_stats.loc[level_stats["median"].idxmin(), "gender"]
                        candidates = df[(df["level"] == level) & (df["gender"] == lower_gender)]

                        if len(candidates) > 0:
                            # Select top performers in the affected group
                            top_candidates = candidates.nlargest(
                                min(max_per_category, len(candidates)), "performance_rating"
                            )

                            if "gender_gap" not in tracked_employees:
                                tracked_employees["gender_gap"] = []
                            tracked_employees["gender_gap"].extend(top_candidates["employee_id"].tolist())

        # High performer identification (vectorized)
        # Ensure performance_rating is numeric
        df["performance_rating"] = pd.to_numeric(df["performance_rating"], errors="coerce")
        df["salary"] = pd.to_numeric(df["salary"], errors="coerce")

        performance_threshold = df["performance_rating"].quantile(0.9)  # Top 10%
        salary_threshold = df["salary"].quantile(0.8)  # Top 20% salary

        high_performers = df[
            (df["performance_rating"] >= performance_threshold) | (df["salary"] >= salary_threshold)
        ].nlargest(max_per_category, "performance_rating")

        if len(high_performers) > 0:
            tracked_employees["high_performer"] = high_performers["employee_id"].tolist()

        # Above range identification (vectorized)
        level_salary_stats = df.groupby("level")["salary"].agg(["mean", "std"]).reset_index()
        above_range_employees = []

        for _, level_stat in level_salary_stats.iterrows():
            level = level_stat["level"]
            mean_salary = level_stat["mean"]
            std_salary = level_stat["std"]
            upper_bound = mean_salary + (2 * std_salary)  # 2 standard deviations above mean

            level_employees = df[df["level"] == level]
            above_range_level = level_employees[level_employees["salary"] > upper_bound]

            if len(above_range_level) > 0:
                selected = above_range_level.nlargest(min(max_per_category // 2, len(above_range_level)), "salary")
                above_range_employees.extend(selected["employee_id"].tolist())

        if above_range_employees:
            tracked_employees["above_range"] = above_range_employees[:max_per_category]

        # Memory cleanup
        if population_size > 10000:
            del df, gender_salary_stats, level_salary_stats
            gc.collect()
            self.optimization_applied.append("memory_cleanup")

        total_tracked = sum(len(employees) for employees in tracked_employees.values())

        # Record performance metrics
        end_time = time.time()
        end_memory = self._get_memory_usage()
        duration = end_time - start_time
        memory_delta = end_memory - start_memory

        self.operation_times["chunked_story_identification"] = {
            "duration_seconds": duration,
            "start_memory_mb": start_memory,
            "end_memory_mb": end_memory,
            "memory_delta_mb": memory_delta,
            "timestamp": datetime.now().isoformat(),
        }

        self._log(
            f"Story identification completed: {total_tracked} employees tracked across {len(tracked_employees)} categories in {duration:.2f}s"
        )

        return tracked_employees

    def _optimize_dataframe_dtypes(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize DataFrame data types to reduce memory usage."""
        original_memory = df.memory_usage(deep=True).sum() / 1024 / 1024  # MB

        # Optimize numeric columns
        for col in df.select_dtypes(include=["int64"]).columns:
            df[col] = pd.to_numeric(df[col], downcast="integer")

        for col in df.select_dtypes(include=["float64"]).columns:
            df[col] = pd.to_numeric(df[col], downcast="float")

        # Optimize string columns to categorical if they have few unique values
        # But preserve numeric columns that might be stored as objects
        for col in df.select_dtypes(include=["object"]).columns:
            # Skip if column contains numeric data
            if col in ["performance_rating", "salary", "level", "employee_id"]:
                continue

            unique_ratio = len(df[col].unique()) / len(df)
            if unique_ratio < 0.5:  # Less than 50% unique values
                df[col] = df[col].astype("category")

        optimized_memory = df.memory_usage(deep=True).sum() / 1024 / 1024  # MB
        memory_reduction = ((original_memory - optimized_memory) / original_memory) * 100

        self._log(
            f"DataFrame memory optimized: {memory_reduction:.1f}% reduction ({original_memory:.1f}MB → {optimized_memory:.1f}MB)"
        )

        return df

    def optimize_visualization_generation(self, population_size: int, story_count: int) -> Dict[str, Any]:
        """Optimize visualization generation for large datasets.

        Args:
            population_size: Size of population dataset
            story_count: Number of tracked employee stories

        Returns:
            Visualization optimization configuration
        """
        self._log(f"Optimizing visualization generation for {population_size:,} employees, {story_count} stories")

        viz_config = {
            "sampling_strategy": "none",
            "max_points": population_size,
            "use_aggregation": False,
            "enable_interactivity": True,
            "memory_efficient": False,
        }

        # Apply sampling for very large populations
        if population_size > 10000:
            viz_config["sampling_strategy"] = "stratified"
            viz_config["max_points"] = 5000
            viz_config["use_aggregation"] = True
            self.optimization_applied.append("visualization_sampling")

        if population_size > 50000:
            viz_config["sampling_strategy"] = "random"
            viz_config["max_points"] = 2000
            viz_config["enable_interactivity"] = False
            viz_config["memory_efficient"] = True
            self.optimization_applied.append("aggressive_viz_optimization")

        # Story-specific optimizations
        if story_count > 1000:
            viz_config["story_sampling"] = True
            viz_config["max_story_points"] = 500
            self.optimization_applied.append("story_sampling")

        return viz_config

    def optimize_export_operations(self, data_size: int, export_formats: List[str]) -> Dict[str, Any]:
        """Optimize export operations for large datasets.

        Args:
            data_size: Size of data to export
            export_formats: List of export formats

        Returns:
            Export optimization configuration
        """
        self._log(f"Optimizing export operations for {data_size:,} records in {len(export_formats)} formats")

        export_config = {
            "batch_size": self.optimization_config["batch_export_size"],
            "use_compression": False,
            "parallel_exports": False,
            "memory_efficient_writing": False,
            "format_priorities": export_formats,
        }

        # Optimize batch size based on data size
        if data_size > 10000:
            export_config["batch_size"] = max(100, data_size // 100)
            export_config["use_compression"] = True
            export_config["memory_efficient_writing"] = True
            self.optimization_applied.append("batch_export")

        if data_size > 100000:
            export_config["parallel_exports"] = True
            export_config["format_priorities"] = ["csv", "json"]  # Prioritize faster formats
            self.optimization_applied.append("parallel_export")

        return export_config

    def monitor_memory_usage(self, checkpoint_name: str):
        """Create memory usage checkpoint."""
        if self.optimization_config["memory_monitoring"]:
            memory_mb = self._get_memory_usage()
            self.memory_checkpoints[checkpoint_name] = {"memory_mb": memory_mb, "timestamp": datetime.now().isoformat()}

            # Check for memory threshold breach
            if memory_mb > self.optimization_config["memory_threshold_mb"]:
                self._log(f"Memory usage high at {checkpoint_name}: {memory_mb:.1f}MB", "warning")

                # Trigger garbage collection
                collected = gc.collect()
                new_memory = self._get_memory_usage()
                memory_freed = memory_mb - new_memory

                if memory_freed > 10:  # Significant memory freed
                    self._log(f"Garbage collection freed {memory_freed:.1f}MB ({collected} objects)")

    def apply_performance_optimizations(self, population_size: int, enable_story_tracking: bool) -> Dict[str, Any]:
        """Apply comprehensive performance optimizations based on population size.

        Args:
            population_size: Size of employee population
            enable_story_tracking: Whether story tracking is enabled

        Returns:
            Applied optimization summary
        """
        self._log(f"Applying performance optimizations for {population_size:,} employees")

        # Create optimization plan
        optimization_plan = self.optimize_population_generation(population_size)

        # Update configuration based on optimizations
        if population_size > 5000:
            self.optimization_config.update(
                {
                    "chunk_size": optimization_plan["chunk_size"],
                    "gc_frequency": max(50, 100 - max(1, population_size // 1000)),
                    "memory_threshold_mb": min(1000, 500 + max(1, population_size // 100)),
                }
            )

        if population_size > 10000:
            self.optimization_config.update(
                {
                    "batch_export_size": max(100, max(1, population_size // 100)),
                    "enable_progress_tracking": True,
                    "memory_monitoring": True,
                }
            )

            # Enable numpy/pandas optimizations
            pd.options.mode.chained_assignment = None
            np.seterr(all="ignore")  # Ignore numpy warnings for performance

        applied_optimizations = {
            "population_size": population_size,
            "optimization_level": optimization_plan["optimization_strategy"],
            "chunk_size": self.optimization_config["chunk_size"],
            "memory_threshold_mb": self.optimization_config["memory_threshold_mb"],
            "optimizations_applied": self.optimization_applied.copy(),
            "performance_config": self.optimization_config.copy(),
        }

        self._log(f"Performance optimizations applied: {len(self.optimization_applied)} optimizations active")

        return applied_optimizations

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance analysis summary."""

        # Calculate total execution time
        total_time = sum(metric["duration_seconds"] for metric in self.operation_times.values())

        # Memory usage analysis
        memory_usage = [checkpoint["memory_mb"] for checkpoint in self.memory_checkpoints.values()]

        peak_memory = max(memory_usage, default=0)
        avg_memory = sum(memory_usage) / len(memory_usage) if memory_usage else 0

        return {
            "performance_metrics": {
                "total_execution_time_seconds": total_time,
                "operations_tracked": len(self.operation_times),
                "memory_checkpoints": len(self.memory_checkpoints),
                "peak_memory_usage_mb": peak_memory,
                "average_memory_usage_mb": avg_memory,
            },
            "optimizations": {
                "total_applied": len(self.optimization_applied),
                "optimization_list": list(set(self.optimization_applied)),
                "current_config": self.optimization_config,
            },
            "operation_breakdown": self.operation_times,
            "memory_timeline": self.memory_checkpoints,
            "recommendations": self._generate_performance_recommendations(),
        }

    def _generate_performance_recommendations(self) -> List[str]:
        """Generate performance improvement recommendations."""
        recommendations = []

        if memory_usage := [checkpoint["memory_mb"] for checkpoint in self.memory_checkpoints.values()]:
            peak_memory = max(memory_usage)

            if peak_memory > 1000:
                recommendations.append("Consider implementing data streaming for very large populations")

            if peak_memory > 2000:
                recommendations.append("Use distributed processing or reduce batch sizes")

        if slow_operations := [
            name for name, metrics in self.operation_times.items() if metrics["duration_seconds"] > 60
        ]:
            recommendations.append(f"Optimize slow operations: {', '.join(slow_operations)}")

        # Optimization coverage recommendations
        if "chunked_processing" not in self.optimization_applied:
            recommendations.append("Enable chunked processing for better memory management")

        if "dtype_optimization" not in self.optimization_applied:
            recommendations.append("Apply data type optimizations to reduce memory usage")

        if not recommendations:
            recommendations.append("Performance is well optimized for current workload")

        return recommendations

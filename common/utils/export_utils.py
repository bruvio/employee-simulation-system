"""Centralized export utilities for data export and file operations."""

import csv
from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd

from ..config.constants import DEFAULT_EXPORT_FORMAT, DEFAULT_OUTPUT_DIR, EXPORT_FORMATS


class ExportError(Exception):
    """Custom exception for export operations."""


def ensure_directory_exists(file_path: Union[str, Path]) -> None:
    """Ensure the directory for a file path exists.

    Args:
        file_path: Path to file or directory
    """
    path = Path(file_path)
    directory = path.parent if path.is_file() or "." in path.name else path
    directory.mkdir(parents=True, exist_ok=True)


def generate_output_filename(
    base_name: str,
    output_format: str = DEFAULT_EXPORT_FORMAT,
    timestamp: bool = True,
    output_dir: str = DEFAULT_OUTPUT_DIR,
) -> str:
    """Generate standardized output filename.

    Args:
        base_name: Base filename without extension
        output_format: File format (json, csv, xlsx, txt)
        timestamp: Whether to include timestamp
        output_dir: Output directory

    Returns:
        Full file path
    """
    if timestamp:
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{base_name}_{timestamp_str}.{output_format}"
    else:
        filename = f"{base_name}.{output_format}"

    return str(Path(output_dir) / filename)


def export_to_json(data: Any, file_path: str, indent: int = 2, ensure_ascii: bool = False) -> None:
    """Export data to JSON file.

    Args:
        data: Data to export
        file_path: Output file path
        indent: JSON indentation
        ensure_ascii: Whether to escape non-ASCII characters
    """
    ensure_directory_exists(file_path)

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii, default=str)
    except (TypeError, ValueError) as e:
        raise ExportError(f"Failed to export JSON to {file_path}: {e}")


def export_to_csv(data: List[Dict], file_path: str, fieldnames: Optional[List[str]] = None) -> None:
    """Export data to CSV file.

    Args:
        data: List of dictionaries to export
        file_path: Output file path
        fieldnames: Column names (auto-detected if None)
    """
    if not data:
        raise ExportError("Cannot export empty data to CSV")

    ensure_directory_exists(file_path)

    if fieldnames is None:
        fieldnames = list(data[0].keys())

    try:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
    except Exception as e:
        raise ExportError(f"Failed to export CSV to {file_path}: {e}")


def export_to_excel(data: Union[List[Dict], Dict[str, List[Dict]]], file_path: str, sheet_name: str = "Sheet1") -> None:
    """Export data to Excel file.

    Args:
        data: Data to export (single sheet or multi-sheet dict)
        file_path: Output file path
        sheet_name: Sheet name for single sheet export
    """
    ensure_directory_exists(file_path)

    try:
        if isinstance(data, dict):
            # Multi-sheet export
            with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
                for sheet, sheet_data in data.items():
                    df = pd.DataFrame(sheet_data)
                    df.to_excel(writer, sheet_name=sheet, index=False)
        else:
            # Single sheet export
            df = pd.DataFrame(data)
            df.to_excel(file_path, sheet_name=sheet_name, index=False)
    except Exception as e:
        raise ExportError(f"Failed to export Excel to {file_path}: {e}")


def export_to_text(content: str, file_path: str, encoding: str = "utf-8") -> None:
    """Export text content to file.

    Args:
        content: Text content to write
        file_path: Output file path
        encoding: File encoding
    """
    ensure_directory_exists(file_path)

    try:
        with open(file_path, "w", encoding=encoding) as f:
            f.write(content)
    except Exception as e:
        raise ExportError(f"Failed to export text to {file_path}: {e}")


def export_data(data: Any, file_path: str, export_format: Optional[str] = None, **kwargs) -> None:
    """Universal data export function.

    Args:
        data: Data to export
        file_path: Output file path
        export_format: Format to export (auto-detected from extension if None)
        **kwargs: Additional arguments for specific exporters
    """
    if export_format is None:
        export_format = Path(file_path).suffix.lstrip(".")

    if export_format not in EXPORT_FORMATS:
        raise ExportError(f"Unsupported export format: {export_format}")

    if export_format == "json":
        export_to_json(data, file_path, **kwargs)
    elif export_format == "csv":
        if not isinstance(data, list):
            raise ExportError("CSV export requires list of dictionaries")
        export_to_csv(data, file_path, **kwargs)
    elif export_format in ["xlsx", "xls"]:
        export_to_excel(data, file_path, **kwargs)
    elif export_format in ["txt", "text"]:
        if not isinstance(data, str):
            data = str(data)
        export_to_text(data, file_path, **kwargs)
    else:
        raise ExportError(f"Export format {export_format} not implemented")


def load_from_json(file_path: str) -> Any:
    """Load data from JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        Loaded data
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise ExportError(f"Failed to load JSON from {file_path}: {e}")


def load_from_csv(file_path: str) -> List[Dict]:
    """Load data from CSV file.

    Args:
        file_path: Path to CSV file

    Returns:
        List of dictionaries
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        raise ExportError(f"Failed to load CSV from {file_path}: {e}")


def load_from_excel(file_path: str, sheet_name: Optional[str] = None) -> Union[Dict[str, List[Dict]], List[Dict]]:
    """Load data from Excel file.

    Args:
        file_path: Path to Excel file
        sheet_name: Specific sheet to load (all sheets if None)

    Returns:
        Data from Excel file
    """
    try:
        if sheet_name:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            return df.to_dict("records")
        else:
            # Load all sheets
            excel_data = pd.read_excel(file_path, sheet_name=None)
            return {sheet: df.to_dict("records") for sheet, df in excel_data.items()}
    except Exception as e:
        raise ExportError(f"Failed to load Excel from {file_path}: {e}")


def load_population_data(data_source: str) -> List[Dict]:
    """Load population data from various sources.

    Args:
        data_source: Path to data file or 'generate' for test data

    Returns:
        List of employee dictionaries
    """
    if data_source == "generate":
        # Import here to avoid circular imports
        from ...employee_population_simulator import EmployeePopulationGenerator
        from ..config.constants import DEFAULT_POPULATION_SIZE, DEFAULT_RANDOM_SEED

        generator = EmployeePopulationGenerator(
            population_size=DEFAULT_POPULATION_SIZE, random_seed=DEFAULT_RANDOM_SEED
        )
        return generator.generate_population()

    file_path = Path(data_source)
    if not file_path.exists():
        raise ExportError(f"Data source not found: {data_source}")

    extension = file_path.suffix.lower()

    if extension == ".json":
        return load_from_json(str(file_path))
    elif extension == ".csv":
        return load_from_csv(str(file_path))
    elif extension in [".xlsx", ".xls"]:
        result = load_from_excel(str(file_path))
        if isinstance(result, dict):
            # Return first sheet if multiple sheets
            return list(result.values())[0]
        return result
    else:
        raise ExportError(f"Unsupported data source format: {extension}")


def create_export_summary(
    export_path: str, data_count: int, export_format: str, additional_info: Optional[Dict] = None
) -> Dict[str, Any]:
    """Create summary information about an export operation.

    Args:
        export_path: Path where data was exported
        data_count: Number of records exported
        export_format: Format used for export
        additional_info: Additional metadata

    Returns:
        Export summary dictionary
    """
    summary = {
        "export_path": export_path,
        "export_format": export_format,
        "record_count": data_count,
        "export_timestamp": datetime.now().isoformat(),
        "file_size_bytes": Path(export_path).stat().st_size if Path(export_path).exists() else 0,
    }

    if additional_info:
        summary.update(additional_info)

    return summary


def batch_export(
    data_sets: Dict[str, Any], base_output_dir: str, export_format: str = DEFAULT_EXPORT_FORMAT, timestamp: bool = True
) -> List[Dict[str, Any]]:
    """Export multiple datasets in batch.

    Args:
        data_sets: Dictionary of dataset_name -> data
        base_output_dir: Base directory for exports
        export_format: Export format to use
        timestamp: Whether to include timestamps in filenames

    Returns:
        List of export summaries
    """
    summaries = []

    for dataset_name, data in data_sets.items():
        file_path = generate_output_filename(dataset_name, export_format, timestamp, base_output_dir)

        export_data(data, file_path, export_format)

        summary = create_export_summary(
            file_path, len(data) if isinstance(data, (list, dict)) else 1, export_format, {"dataset_name": dataset_name}
        )
        summaries.append(summary)

    return summaries

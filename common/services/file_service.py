"""
File management service for centralized file operations.
"""

from datetime import datetime
import json
from pathlib import Path
import shutil
import tempfile
from typing import Any, Dict, List, Optional, Union

from ..config.constants import DEFAULT_OUTPUT_DIR, DEFAULT_REPORTS_DIR


class FileServiceError(Exception):
    """
    Custom exception for file service operations.
    """


class FileService:
    """
    Centralized file management service.
    """

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize file service.

        Args:
            base_dir: Base directory for file operations (current dir if None)
        """
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.output_dir = self.base_dir / DEFAULT_OUTPUT_DIR
        self.reports_dir = self.base_dir / DEFAULT_REPORTS_DIR

    def ensure_directory(self, path: Union[str, Path]) -> Path:
        """
        Ensure directory exists, creating if necessary.

        Args:
            path: Directory path

        Returns:
            Path object for the directory
        """
        dir_path = Path(path)
        if not dir_path.is_absolute():
            dir_path = self.base_dir / dir_path

        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            return dir_path
        except OSError as e:
            raise FileServiceError(f"Failed to create directory {dir_path}: {e}")

    def get_output_path(self, filename: str, subdirectory: str = "") -> Path:
        """
        Get full path for output file.

        Args:
            filename: Name of the file
            subdirectory: Optional subdirectory within output dir

        Returns:
            Full path for the output file
        """
        if subdirectory:
            output_path = self.output_dir / subdirectory
        else:
            output_path = self.output_dir

        self.ensure_directory(output_path)
        return output_path / filename

    def get_reports_path(self, filename: str, subdirectory: str = "") -> Path:
        """
        Get full path for report file.

        Args:
            filename: Name of the file
            subdirectory: Optional subdirectory within reports dir

        Returns:
            Full path for the report file
        """
        if subdirectory:
            reports_path = self.reports_dir / subdirectory
        else:
            reports_path = self.reports_dir

        self.ensure_directory(reports_path)
        return reports_path / filename

    def save_text_file(self, content: str, file_path: Union[str, Path], encoding: str = "utf-8") -> Path:
        """
        Save text content to file.

        Args:
            content: Text content to save
            file_path: Path to save file
            encoding: File encoding

        Returns:
            Path where file was saved
        """
        full_path = self._resolve_path(file_path)
        self.ensure_directory(full_path.parent)

        try:
            with open(full_path, "w", encoding=encoding) as f:
                f.write(content)
            return full_path
        except IOError as e:
            raise FileServiceError(f"Failed to save text file {full_path}: {e}")

    def load_text_file(self, file_path: Union[str, Path], encoding: str = "utf-8") -> str:
        """
        Load text content from file.

        Args:
            file_path: Path to load file
            encoding: File encoding

        Returns:
            File content as string
        """
        full_path = self._resolve_path(file_path)

        if not full_path.exists():
            raise FileServiceError(f"File not found: {full_path}")

        try:
            with open(full_path, "r", encoding=encoding) as f:
                return f.read()
        except IOError as e:
            raise FileServiceError(f"Failed to load text file {full_path}: {e}")

    def save_json_file(
        self, data: Any, file_path: Union[str, Path], indent: int = 2, ensure_ascii: bool = False
    ) -> Path:
        """
        Save data as JSON file.

        Args:
            data: Data to save
            file_path: Path to save file
            indent: JSON indentation
            ensure_ascii: Whether to escape non-ASCII characters

        Returns:
            Path where file was saved
        """
        full_path = self._resolve_path(file_path)
        self.ensure_directory(full_path.parent)

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii, default=str)
            return full_path
        except (TypeError, ValueError, IOError) as e:
            raise FileServiceError(f"Failed to save JSON file {full_path}: {e}")

    def load_json_file(self, file_path: Union[str, Path]) -> Any:
        """
        Load data from JSON file.

        Args:
            file_path: Path to load file

        Returns:
            Loaded data
        """
        full_path = self._resolve_path(file_path)

        if not full_path.exists():
            raise FileServiceError(f"File not found: {full_path}")

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise FileServiceError(f"Failed to load JSON file {full_path}: {e}")

    def copy_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Path:
        """
        Copy file from source to destination.

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            Path where file was copied
        """
        src_path = self._resolve_path(source)
        dest_path = self._resolve_path(destination)

        if not src_path.exists():
            raise FileServiceError(f"Source file not found: {src_path}")

        self.ensure_directory(dest_path.parent)

        try:
            shutil.copy2(src_path, dest_path)
            return dest_path
        except (shutil.Error, OSError) as e:
            raise FileServiceError(f"Failed to copy file {src_path} to {dest_path}: {e}")

    def move_file(self, source: Union[str, Path], destination: Union[str, Path]) -> Path:
        """
        Move file from source to destination.

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            Path where file was moved
        """
        src_path = self._resolve_path(source)
        dest_path = self._resolve_path(destination)

        if not src_path.exists():
            raise FileServiceError(f"Source file not found: {src_path}")

        self.ensure_directory(dest_path.parent)

        try:
            shutil.move(str(src_path), str(dest_path))
            return dest_path
        except (shutil.Error, OSError) as e:
            raise FileServiceError(f"Failed to move file {src_path} to {dest_path}: {e}")

    def delete_file(self, file_path: Union[str, Path]) -> bool:
        """
        Delete a file if it exists.

        Args:
            file_path: Path to file to delete

        Returns:
            True if file was deleted, False if it didn't exist
        """
        full_path = self._resolve_path(file_path)

        if not full_path.exists():
            return False

        try:
            full_path.unlink()
            return True
        except OSError as e:
            raise FileServiceError(f"Failed to delete file {full_path}: {e}")

    def list_files(self, directory: Union[str, Path], pattern: str = "*", recursive: bool = False) -> List[Path]:
        """
        List files in directory matching pattern.

        Args:
            directory: Directory to search
            pattern: Glob pattern to match
            recursive: Whether to search recursively

        Returns:
            List of matching file paths
        """
        dir_path = self._resolve_path(directory)

        if not dir_path.exists():
            raise FileServiceError(f"Directory not found: {dir_path}")

        if not dir_path.is_dir():
            raise FileServiceError(f"Path is not a directory: {dir_path}")

        try:
            if recursive:
                return list(dir_path.rglob(pattern))
            else:
                return list(dir_path.glob(pattern))
        except OSError as e:
            raise FileServiceError(f"Failed to list files in {dir_path}: {e}")

    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Get information about a file.

        Args:
            file_path: Path to file

        Returns:
            Dictionary with file information
        """
        full_path = self._resolve_path(file_path)

        if not full_path.exists():
            raise FileServiceError(f"File not found: {full_path}")

        try:
            stat = full_path.stat()
            return {
                "path": str(full_path),
                "name": full_path.name,
                "size_bytes": stat.st_size,
                "modified_time": datetime.fromtimestamp(stat.st_mtime),
                "created_time": datetime.fromtimestamp(stat.st_ctime),
                "is_file": full_path.is_file(),
                "is_directory": full_path.is_dir(),
                "extension": full_path.suffix,
            }
        except OSError as e:
            raise FileServiceError(f"Failed to get file info for {full_path}: {e}")

    def create_temp_file(self, suffix: str = "", prefix: str = "temp_", content: Optional[str] = None) -> Path:
        """
        Create a temporary file.

        Args:
            suffix: File suffix/extension
            prefix: File prefix
            content: Optional content to write to file

        Returns:
            Path to temporary file
        """
        try:
            with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, prefix=prefix, delete=False) as f:
                if content:
                    f.write(content)
                temp_path = Path(f.name)

            return temp_path
        except OSError as e:
            raise FileServiceError(f"Failed to create temporary file: {e}")

    def cleanup_temp_files(self, temp_paths: List[Path]) -> int:
        """
        Clean up temporary files.

        Args:
            temp_paths: List of temporary file paths to clean up

        Returns:
            Number of files successfully deleted
        """
        deleted_count = 0
        for temp_path in temp_paths:
            try:
                if temp_path.exists():
                    temp_path.unlink()
                    deleted_count += 1
            except OSError:
                # Ignore errors during cleanup
                pass
        return deleted_count

    def organize_files_by_date(
        self, source_dir: Union[str, Path], target_dir: Union[str, Path], date_format: str = "%Y/%m"
    ) -> Dict[str, List[Path]]:
        """
        Organize files by date into subdirectories.

        Args:
            source_dir: Source directory with files to organize
            target_dir: Target directory for organized files
            date_format: Date format for subdirectory structure

        Returns:
            Dictionary mapping date strings to lists of moved files
        """
        src_path = self._resolve_path(source_dir)
        tgt_path = self._resolve_path(target_dir)

        if not src_path.exists() or not src_path.is_dir():
            raise FileServiceError(f"Source directory not found: {src_path}")

        organized_files = {}

        for file_path in src_path.iterdir():
            if file_path.is_file():
                # Get file modification time
                mod_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                date_str = mod_time.strftime(date_format)

                # Create target subdirectory
                target_subdir = tgt_path / date_str
                self.ensure_directory(target_subdir)

                # Move file
                new_path = self.move_file(file_path, target_subdir / file_path.name)

                if date_str not in organized_files:
                    organized_files[date_str] = []
                organized_files[date_str].append(new_path)

        return organized_files

    def _resolve_path(self, path: Union[str, Path]) -> Path:
        """
        Resolve path relative to base directory.

        Args:
            path: Path to resolve

        Returns:
            Resolved absolute path
        """
        path_obj = Path(path)
        if path_obj.is_absolute():
            return path_obj
        else:
            return self.base_dir / path_obj


# Global file service instance
_file_service = None


def get_file_service(base_dir: Optional[str] = None) -> FileService:
    """
    Get global file service instance.

    Args:
        base_dir: Base directory (uses current if None and not already initialized)

    Returns:
        FileService instance
    """
    global _file_service
    if _file_service is None:
        _file_service = FileService(base_dir)
    return _file_service

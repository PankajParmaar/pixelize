import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class Snapshot:
    """Structured representation of a previously exported snapshot."""

    device: Dict[str, Any]
    installed_packages: List[str]
    system_packages: List[str]
    user_packages: List[str]
    package_paths: Dict[str, str]


class SnapshotValidationError(ValueError):
    """Raised when a snapshot file is missing required structure."""


def _require_mapping(value, field_name):
    if not isinstance(value, dict):
        raise SnapshotValidationError(f"{field_name} must be an object")
    return value


def _require_list(value, field_name):
    if not isinstance(value, list):
        raise SnapshotValidationError(f"{field_name} must be a list")
    return value


def _require_string_map(value, field_name):
    if not isinstance(value, dict):
        raise SnapshotValidationError(f"{field_name} must be an object")

    for key, item in value.items():
        if not isinstance(key, str) or not isinstance(item, str):
            raise SnapshotValidationError(f"{field_name} must map strings to strings")

    return value


def load_snapshot(snapshot_path):
    """Load and validate a snapshot JSON file into a typed Snapshot object."""

    path = Path(snapshot_path)
    if not path.exists():
        raise FileNotFoundError(f"Snapshot not found: {snapshot_path}")

    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)

    if not isinstance(data, dict):
        raise SnapshotValidationError("Snapshot root must be an object")

    if "snapshot_version" not in data:
        raise SnapshotValidationError("snapshot_version is required")

    device = _require_mapping(data.get("device"), "device")
    packages = _require_mapping(data.get("packages"), "packages")

    if "installed" not in packages or "system" not in packages or "user" not in packages or "paths" not in packages:
        raise SnapshotValidationError("packages must contain installed, system, user, and paths")

    installed_packages = _require_list(packages.get("installed"), "packages.installed")
    system_packages = _require_list(packages.get("system"), "packages.system")
    user_packages = _require_list(packages.get("user"), "packages.user")
    package_paths = _require_string_map(packages.get("paths"), "packages.paths")

    for entry in installed_packages:
        if not isinstance(entry, str):
            raise SnapshotValidationError("packages.installed must contain only strings")

    for entry in system_packages:
        if not isinstance(entry, str):
            raise SnapshotValidationError("packages.system must contain only strings")

    for entry in user_packages:
        if not isinstance(entry, str):
            raise SnapshotValidationError("packages.user must contain only strings")

    return Snapshot(
        device=device,
        installed_packages=installed_packages,
        system_packages=system_packages,
        user_packages=user_packages,
        package_paths=package_paths,
    )

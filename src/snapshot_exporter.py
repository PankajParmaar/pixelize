import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from adb import adb
from scanner import get_device_info


def _parse_package_list(output):
    """Parse raw adb package-list output into a sorted list of package names."""

    packages = []
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("package:"):
            packages.append(line[len("package:"):])

    return sorted(packages)


def _run_adb_command(command):
    """Run an adb command and return stdout when available, otherwise an empty string."""

    output = adb(command)
    if output:
        return output

    result = subprocess.run(["adb"] + command, capture_output=True, text=True)
    if result.returncode != 0:
        return ""

    return result.stdout.strip()


def _get_package_paths(packages):
    """Return a mapping of package names to their APK paths."""

    paths = {}
    for package in packages:
        output = _run_adb_command(["shell", "pm", "path", package])
        for line in output.splitlines():
            line = line.strip()
            if line.startswith("package:"):
                paths[package] = line[len("package:"):]
                break

    return paths


def export_snapshot(output_path):
    """Export a device/package snapshot as a single JSON file."""

    installed_output = _run_adb_command(["shell", "pm", "list", "packages", "--user", "0"])
    system_output = _run_adb_command(["shell", "pm", "list", "packages", "-s"])
    user_output = _run_adb_command(["shell", "pm", "list", "packages", "-3"])

    installed_packages = _parse_package_list(installed_output)
    system_packages = _parse_package_list(system_output)
    user_packages = _parse_package_list(user_output)
    package_paths = _get_package_paths(installed_packages)

    snapshot = {
        "snapshot_version": 1,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "device": get_device_info(),
        "packages": {
            "installed": installed_packages,
            "system": system_packages,
            "user": user_packages,
            "paths": package_paths,
        },
    }

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(snapshot, handle, indent=2)
        handle.write("\n")

    return str(path)

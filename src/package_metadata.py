from functools import lru_cache

try:
    from adb import adb
except ImportError:  # pragma: no cover - fallback when imported as part of the package
    from src.adb import adb


def _parse_package_list(output):
    """Convert adb package-list output into a set of package names."""

    return {
        line[len("package:"):]
        for line in output.splitlines()
        if line.startswith("package:")
    }


@lru_cache(maxsize=1)
def _get_package_cache():
    """Load system and user package lists once per process."""

    system_output = adb(["shell", "pm", "list", "packages", "-s"])
    user_output = adb(["shell", "pm", "list", "packages", "-3"])
    return _parse_package_list(system_output), _parse_package_list(user_output)


def get_package_metadata(package_name):
    """Return whether a package appears to be system-installed or user-installed."""

    package = (package_name or "").strip()
    if not package:
        return {
            "package": "",
            "system_app": False,
            "user_app": False,
        }

    system_packages, user_packages = _get_package_cache()

    return {
        "package": package,
        "system_app": package in system_packages,
        "user_app": package in user_packages,
    }

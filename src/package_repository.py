from typing import Dict, List, Optional


class PackageRepository:
    """Read-only repository over a loaded snapshot."""

    def __init__(self, snapshot):
        self._snapshot = snapshot
        self._installed_set = set(snapshot.installed_packages)
        self._system_set = set(snapshot.system_packages)
        self._user_set = set(snapshot.user_packages)
        self._package_paths = dict(snapshot.package_paths)
        self._package_index = {
            package: {
                "package": package,
                "installed": package in self._installed_set,
                "system": package in self._system_set,
                "user": package in self._user_set,
                "path": self._package_paths.get(package),
            }
            for package in self._installed_set
        }

    def get_package(self, package_name):
        """Return a package record if present, otherwise None."""

        return self._package_index.get(package_name)

    def package_exists(self, package_name):
        """Return True if the package exists in the snapshot."""

        return package_name in self._package_index

    def get_installed_packages(self):
        """Return installed packages as a sorted list."""

        return sorted(self._installed_set)

    def get_system_packages(self):
        """Return system packages as a sorted list."""

        return sorted(self._system_set)

    def get_user_packages(self):
        """Return user packages as a sorted list."""

        return sorted(self._user_set)

    def get_package_path(self, package_name):
        """Return the package APK path if available, otherwise None."""

        package = self.get_package(package_name)
        if not package:
            return None
        return package.get("path")

    def search(self, query):
        """Return matching package names for a case-insensitive query."""

        if not query:
            return []

        normalized_query = query.lower()
        return sorted(
            package
            for package in self._installed_set
            if normalized_query in package.lower()
        )

    def is_system_package(self, package_name):
        """Return True if the package is present in the system package list."""

        return package_name in self._system_set

    def is_user_package(self, package_name):
        """Return True if the package is present in the user package list."""

        return package_name in self._user_set

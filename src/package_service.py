from typing import List, Optional

from package_repository import PackageRepository


class PackageService:
    """Read-only service layer over package repository operations."""

    def __init__(self, repository: PackageRepository):
        self._repository = repository

    def get_package(self, package_name: str) -> Optional[dict]:
        """Return package details for the given package name if present."""

        return self._repository.get_package(package_name)

    def package_exists(self, package_name: str) -> bool:
        """Return True when the package exists in the repository snapshot."""

        return self._repository.package_exists(package_name)

    def get_installed_packages(self) -> List[str]:
        """Return installed package names from the repository."""

        return self._repository.get_installed_packages()

    def get_system_packages(self) -> List[str]:
        """Return system package names from the repository."""

        return self._repository.get_system_packages()

    def get_user_packages(self) -> List[str]:
        """Return user package names from the repository."""

        return self._repository.get_user_packages()

    def get_package_path(self, package_name: str) -> Optional[str]:
        """Return the package APK path when available."""

        return self._repository.get_package_path(package_name)

    def search(self, query: str) -> List[str]:
        """Search package names using the repository's case-insensitive search."""

        return self._repository.search(query)

    def is_system_package(self, package_name: str) -> bool:
        """Return True when the package is marked as a system package."""

        return self._repository.is_system_package(package_name)

    def is_user_package(self, package_name: str) -> bool:
        """Return True when the package is marked as a user package."""

        return self._repository.is_user_package(package_name)

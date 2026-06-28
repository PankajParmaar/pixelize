from package_service import PackageService


def search_packages(service: PackageService, keyword: str):
    """Return package names containing the keyword, case-insensitively."""

    if hasattr(service, "search"):
        return service.search(keyword)

    if hasattr(service, "get_installed_packages"):
        packages = service.get_installed_packages()
    else:
        packages = service

    normalized_keyword = keyword.lower()
    matches = [
        package for package in packages
        if normalized_keyword in package.lower()
    ]
    return sorted(matches)

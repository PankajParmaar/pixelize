def search_packages(packages, keyword):
    """Return package names containing the keyword, case-insensitively."""

    normalized_keyword = keyword.lower()
    matches = [
        package for package in packages
        if normalized_keyword in package.lower()
    ]
    return sorted(matches)

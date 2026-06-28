from classifier import classify_package


def analyze_packages(packages):
    """Return a count of packages by classification category."""

    counts = {}

    for package in packages:
        category = classify_package(package)
        counts[category] = counts.get(category, 0) + 1

    return counts

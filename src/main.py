from pathlib import Path

from advisor import get_debloat_recommendations
from analyzer import analyze_packages
from classifier import classify_package
from executor import execute_action_plan
from package_repository import PackageRepository
from package_service import PackageService
from planner import create_action_plan
from search import search_packages
from snapshot_loader import SnapshotValidationError, load_snapshot


def _format_recommendation_label(recommendation):
    """Return a user-friendly label for a recommendation bucket."""

    return recommendation.capitalize() if recommendation else "Unknown"


def _print_recommendation(recommendation):
    """Print a recommendation object returned by the advisor."""

    print(recommendation["package"])
    print(f"  Recommendation : {_format_recommendation_label(recommendation.get('recommendation', 'unknown'))}")
    print(f"  Confidence     : {recommendation.get('confidence', 'unknown').capitalize()}")
    print(f"  Reason         : {recommendation.get('reason', 'No reason provided')}")


def print_device_info(info):
    print("=" * 35)
    print(" Pixelize")
    print("=" * 35)

    print(f"Manufacturer   : {info.get('manufacturer', 'Unknown')}")
    print(f"Model          : {info.get('model', 'Unknown')}")
    print(f"Android        : {info.get('android', 'Unknown')}")
    print(f"SDK            : {info.get('sdk', 'Unknown')}")
    print(f"Security Patch : {info.get('security_patch', 'Unknown')}")
    print(f"Build ID       : {info.get('build_id', 'Unknown')}")
    print(f"CPU ABI        : {info.get('cpu', 'Unknown')}")


def print_package_analysis(packages):
    print("Package Analysis")
    print("-" * 16)
    analysis = analyze_packages(packages)
    for category in sorted(analysis):
        print(f"{category}: {analysis[category]}")


def print_grouped_packages(packages):
    grouped_packages = {}
    for package in packages:
        category = classify_package(package)
        grouped_packages.setdefault(category, []).append(package)

    print("Installed Package List")
    print("-" * 22)
    for category in sorted(grouped_packages):
        print(category)
        for package in grouped_packages[category]:
            print(f"  {package}")


def print_search_results(package_service):
    keyword = input("Search keyword: ").strip()
    if not keyword:
        return

    print()
    print("Search Results")
    print("-" * 14)
    for package in search_packages(package_service, keyword):
        print(package)


def print_debloat_advisor(packages):
    recommendations = get_debloat_recommendations(packages)

    print()
    print("Debloat Advisor")
    print("-" * 15)

    for section in ("Safe", "Review", "Critical"):
        lower_section = section.lower()
        items = recommendations[lower_section]
        print()
        print(section)
        print("-" * len(section))
        print(len(items))
        for recommendation in items[:20]:
            _print_recommendation(recommendation)

    unknown_items = recommendations.get("unknown", [])
    print()
    print("Unknown Packages")
    print("-" * 16)
    print(len(unknown_items))
    print("These packages have no knowledge entry yet and should be reviewed before recommendations are made.")
    for item in unknown_items[:20]:
        print(item["package"])
        print(f"  Reason : {item.get('reason', 'No reason provided')}")


def _prompt_package_selection(package_service):
    keyword = input("Search term: ").strip()
    if not keyword:
        print("Search term cannot be empty.")
        return None

    matches = search_packages(package_service, keyword)
    if not matches:
        print("No installed packages matched your search.")
        return None

    if len(matches) == 1:
        print(f"One match found: {matches[0]}")
        return matches[0]

    print()
    print("Matches")
    print("-" * 7)
    for index, package in enumerate(matches, 1):
        print(f"{index}. {package}")

    while True:
        selection = input("Select a package number: ").strip()
        if not selection.isdigit():
            print("Please enter a number from the list.")
            continue

        selection_index = int(selection)
        if 1 <= selection_index <= len(matches):
            return matches[selection_index - 1]

        print("Selection is out of range. Please choose a listed number.")


def _get_recommendation_value(package_name, packages):
    recommendations = get_debloat_recommendations(packages)
    for bucket in ("safe", "review", "critical", "unknown"):
        for recommendation in recommendations.get(bucket, []):
            if recommendation.get("package") == package_name:
                return recommendation.get("recommendation", "unknown")

    return "unknown"


def _print_action_plan(plan):
    print()
    print("Action Plan Preview")
    print("-" * 20)
    print(f"Package                : {plan.package}")
    print(f"Recommendation         : {_format_recommendation_label(plan.recommendation)}")
    print(f"Confidence             : {plan.confidence.capitalize()}")
    print(f"Action                 : {plan.action}")
    print(f"ADB Command            : {plan.adb_command}")
    print(f"Restore Command        : {plan.restore_command}")
    print(f"Warnings               : {', '.join(plan.warnings) if plan.warnings else 'None'}")
    print(f"Evidence               : {', '.join(plan.evidence) if plan.evidence else 'None'}")
    print(f"Preconditions          : {', '.join(plan.preconditions) if plan.preconditions else 'None'}")
    print(f"Estimated Impact       : {plan.estimated_impact}")
    print(f"Requires Confirmation  : {'Yes' if plan.requires_confirmation else 'No'}")
    print(f"Execution ID           : {plan.execution_id}")
    print()
    print("This is a dry-run preview only. No changes were made.")


def _print_action_result(result):
    print()
    print("Action Result")
    print("-" * 13)
    print(f"Package        : {result.package}")
    print(f"Action         : {result.action}")
    print(f"Success        : {'Yes' if result.success else 'No'}")
    print(f"Exit Code      : {result.exit_code}")
    print(f"Timestamp      : {result.timestamp}")
    print(f"Stdout         : {result.stdout.strip() if result.stdout else '(empty)'}")
    print(f"Stderr         : {result.stderr.strip() if result.stderr else '(empty)'}")


def print_action_plan_preview(package_service, packages):
    package_name = _prompt_package_selection(package_service)
    if not package_name:
        return

    recommendation_value = _get_recommendation_value(package_name, packages)
    plan = create_action_plan(package_name, recommendation_value)
    _print_action_plan(plan)


def print_action_execution(package_service, packages):
    package_name = _prompt_package_selection(package_service)
    if not package_name:
        return

    recommendation_value = _get_recommendation_value(package_name, packages)
    plan = create_action_plan(package_name, recommendation_value)
    _print_action_plan(plan)

    confirmation = input("Execute this action? (y/N): ").strip().lower()
    if confirmation != "y":
        print("Action execution cancelled.")
        return

    result = execute_action_plan(plan)
    _print_action_result(result)


def main():
    snapshot_path = Path(__file__).resolve().parent.parent / "snapshots" / "iqoo13_2026-06-28.json"

    try:
        snapshot = load_snapshot(snapshot_path)
    except (FileNotFoundError, SnapshotValidationError) as exc:
        print(f"Failed to load snapshot: {exc}")
        return

    print_device_info(snapshot.device)

    repository = PackageRepository(snapshot)
    package_service = PackageService(repository)
    packages = package_service.get_installed_packages()

    while True:
        print()
        print("=" * 35)
        print(" Pixelize")
        print("=" * 35)
        print("1. Package Analysis")
        print("2. List Packages")
        print("3. Search Packages")
        print("4. Debloat Advisor")
        print("5. Preview Action Plan")
        print("6. Execute Action")
        print("7. Exit")
        print()

        choice = input("Choice: ").strip()

        if choice == "1":
            print_package_analysis(packages)
        elif choice == "2":
            print_grouped_packages(packages)
        elif choice == "3":
            print_search_results(package_service)
        elif choice == "4":
            print_debloat_advisor(packages)
        elif choice == "5":
            print_action_plan_preview(package_service, packages)
        elif choice == "6":
            print_action_execution(package_service, packages)
        elif choice == "7":
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()
   
from analyzer import analyze_packages
from classifier import classify_package
from packages import get_installed_packages
from scanner import get_device_info


def main():

    info = get_device_info()

    print("=" * 35)
    print(" Pixelize v0.2.0")
    print("=" * 35)

    print(f"Manufacturer   : {info['manufacturer']}")
    print(f"Model          : {info['model']}")
    print(f"Android        : {info['android']}")
    print(f"SDK            : {info['sdk']}")
    print(f"Security Patch : {info['security_patch']}")
    print(f"Build ID       : {info['build_id']}")
    print(f"CPU ABI        : {info['cpu']}")

    packages = get_installed_packages()
    print(f"Installed Packages : {len(packages)}")
    print()
    print("Package Analysis")
    print("-" * 16)
    analysis = analyze_packages(packages)
    for category in sorted(analysis):
        print(f"{category}: {analysis[category]}")
    print()
    print("Installed Package List")
    print("-" * 22)
    grouped_packages = {}
    for package in packages:
        category = classify_package(package)
        if category not in grouped_packages:
            grouped_packages[category] = []
        grouped_packages[category].append(package)

    for category in sorted(grouped_packages):
        print(category)
        for package in grouped_packages[category]:
            print(f"  {package}")


if __name__ == "__main__":
    main()
   
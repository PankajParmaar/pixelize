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


if __name__ == "__main__":
    main()
   
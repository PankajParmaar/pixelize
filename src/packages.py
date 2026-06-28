from adb import adb


def get_installed_packages():
    """Return a sorted list of installed package names for user 0."""

    output = adb(["shell", "pm", "list", "packages", "--user", "0"])
    packages = []

    for line in output.splitlines():
        line = line.strip()
        if line.startswith("package:"):
            packages.append(line[len("package:"):])

    return sorted(packages)
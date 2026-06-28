import subprocess


def adb(command):
    """Execute an adb command and return its output."""

    result = subprocess.run(
        ["adb"] + command,
        capture_output=True,
        text=True
    )

    return result.stdout.strip()
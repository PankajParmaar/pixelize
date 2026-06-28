def classify_package(package_name):
    """Classify a package name into a high-level category."""

    if package_name.startswith(("com.android", "android.")):
        return "Android"
    if package_name.startswith("com.google"):
        return "Google"
    if package_name.startswith(("com.vivo", "com.bbk", "vivo.")):
        return "vivo"
    if package_name.startswith(("com.qualcomm", "com.qti", "org.codeaurora", "vendor.qti")):
        return "Qualcomm"
    return "Other"

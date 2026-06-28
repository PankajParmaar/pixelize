from adb import adb


def get_device_info():

    return {
        "manufacturer": adb(["shell", "getprop", "ro.product.manufacturer"]),
        "model": adb(["shell", "getprop", "ro.product.model"]),
        "android": adb(["shell", "getprop", "ro.build.version.release"]),
        "sdk": adb(["shell", "getprop", "ro.build.version.sdk"]),
        "security_patch": adb(
            ["shell", "getprop", "ro.build.version.security_patch"]
        ),
        "build_id": adb(["shell", "getprop", "ro.build.display.id"]),
        "fingerprint": adb(["shell", "getprop", "ro.build.fingerprint"]),
        "cpu": adb(["shell", "getprop", "ro.product.cpu.abi"]),
    }
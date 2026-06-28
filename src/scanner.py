from adb import adb


def get_device_info():

    return {
        "manufacturer": adb(["shell", "getprop", "ro.product.manufacturer"]),
        "model": adb(["shell", "getprop", "ro.product.model"]),
        "android": adb(["shell", "getprop", "ro.build.version.release"])
    }
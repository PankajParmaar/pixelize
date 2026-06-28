from scanner import get_device_info


def main():

    info = get_device_info()

    print("=" * 35)
    print(" Pixelize v0.1")
    print("=" * 35)

    print(f"Manufacturer : {info['manufacturer']}")
    print(f"Model        : {info['model']}")
    print(f"Android      : {info['android']}")


if __name__ == "__main__":
    main()
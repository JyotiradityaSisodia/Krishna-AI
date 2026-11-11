DEVICES = {}


def register_device(device_id: str, info: dict):
    DEVICES[device_id] = info


def get_device(device_id: str):
    return DEVICES.get(device_id)


def list_devices():
    return DEVICES


def update_device_status(device_id: str, status: str):
    if device_id in DEVICES:
        DEVICES[device_id]["status"] = status
import requests
import socket
import uuid

CLOUD_URL = "http://127.0.0.1:9000"

DEVICE_ID = f"desktop-{uuid.getnode()}"
DEVICE_NAME = socket.gethostname()
DEVICE_TYPE = "desktop"


def register_this_device():
    try:
        res = requests.post(
            f"{CLOUD_URL}/register",
            json={
                "device_id": DEVICE_ID,
                "device_name": DEVICE_NAME,
                "device_type": DEVICE_TYPE,
                "status": "online",
            },
            timeout=10,
        )
        return res.json()
    except Exception as e:
        return {"success": False, "message": str(e)}


def fetch_commands():
    try:
        res = requests.get(f"{CLOUD_URL}/fetch_commands/{DEVICE_ID}", timeout=10)
        return res.json().get("commands", [])
    except Exception:
        return []


def fetch_results():
    try:
        res = requests.get(f"{CLOUD_URL}/fetch_results/{DEVICE_ID}", timeout=10)
        return res.json().get("results", [])
    except Exception:
        return []


def send_command(target_device_id: str, command_type: str, payload: dict):
    try:
        res = requests.post(
            f"{CLOUD_URL}/send_command",
            json={
                "source_device_id": DEVICE_ID,
                "target_device_id": target_device_id,
                "command_type": command_type,
                "payload": payload,
            },
            timeout=10,
        )
        return res.json()
    except Exception as e:
        return {"success": False, "message": str(e)}
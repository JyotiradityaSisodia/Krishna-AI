import requests
import json
import sys

BASE_URL = "http://127.0.0.1:9000/unified/create_task"


def send_task(skill_name, params, target_device="android-main"):
    payload = {
        "source_device": "desktop-main",
        "target_device": target_device,
        "skill_name": skill_name,
        "intent": skill_name,
        "params": params
    }

    try:
        response = requests.post(BASE_URL, json=payload, timeout=10)
        print("Status Code:", response.status_code)

        try:
            print("Response:", json.dumps(response.json(), indent=2))
        except Exception:
            print("Raw Response:", response.text)

    except Exception as e:
        print("Error:", str(e))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
Usage:

1. Order food:
python desktop\\unified_sender.py order_food "veg biryani" "Sagar Gaire"

2. Open app:
python desktop\\unified_sender.py open_app "zomato"

3. Tap text:
python desktop\\unified_sender.py tap_text "Search"

4. Read screen:
python desktop\\unified_sender.py read_screen
""")
        sys.exit(0)

    command = sys.argv[1]

    if command == "order_food":
        item = sys.argv[2] if len(sys.argv) > 2 else "veg biryani"
        restaurant = sys.argv[3] if len(sys.argv) > 3 else "Sagar Gaire"

        send_task("order_food", {
            "item_or_cuisine": item,
            "restaurant": restaurant,
            "platform": "zomato"
        })

    elif command == "open_app":
        app_name = sys.argv[2] if len(sys.argv) > 2 else "zomato"

        send_task("open_app", {
            "app_name": app_name
        })

    elif command == "tap_text":
        text = sys.argv[2] if len(sys.argv) > 2 else "Search"

        send_task("tap_text", {
            "text": text
        })

    elif command == "read_screen":
        send_task("read_screen", {})

    else:
        print("Unknown command")

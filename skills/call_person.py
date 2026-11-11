import json
import os
import time
import webbrowser

from pywinauto import Application
from pywinauto.findwindows import ElementNotFoundError
from skills.base import BaseSkill


CONTACTS_PATH = r"D:\krishna\data\contacts.json"


def load_contacts():
    if not os.path.exists(CONTACTS_PATH):
        return {}

    try:
        with open(CONTACTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


class CallPersonSkill(BaseSkill):
    name = "call_person"
    required_fields = ["person"]

    def run(self, params: dict, session: dict) -> dict:
        missing = self.get_missing_fields(params)

        if missing:
            return {
                "status": "need_input",
                "missing_fields": missing,
                "message": "I need to know who you want to call."
            }

        contacts = load_contacts()
        person_key = params.get("person", "").strip().lower()

        if person_key not in contacts:
            return {
                "status": "need_input",
                "missing_fields": ["person"],
                "message": f"I could not find '{params.get('person')}' in your contacts."
            }

        return {
            "status": "awaiting_approval",
            "summary": {
                "skill": self.name,
                "person": params.get("person"),
                "phone": contacts[person_key]
            },
            "message": f"I am ready to call {params.get('person')} at {contacts[person_key]}."
        }

    def execute(self, params: dict, session: dict) -> dict:
        contacts = load_contacts()
        person_key = params.get("person", "").strip().lower()

        if person_key not in contacts:
            return {
                "status": "failed",
                "message": f"I could not find '{params.get('person')}' in your contacts."
            }

        phone_number = contacts[person_key]

        try:
            # Open default calling handler (Phone Link)
            webbrowser.open(f"tel:{phone_number}")

            # Give Windows + Phone Link time to open
            time.sleep(6)

            app = Application(backend="uia").connect(
                title_re=".*Phone Link.*|.*Link to Windows.*",
                timeout=20
            )

            win = app.top_window()

            # Bring the window to front in case it opened behind something
            try:
                win.restore()
            except Exception:
                pass

            try:
                win.set_focus()
            except Exception:
                pass

            time.sleep(2)

            # 1) Exact direct lookup
            try:
                call_button = win.child_window(title="Call", control_type="Button")
                if call_button.exists(timeout=5):
                    call_button.wait("visible enabled", timeout=5)
                    call_button.click_input()
                    return {
                        "status": "success",
                        "message": f"Automatically started call to {params.get('person')} at {phone_number}."
                    }
            except Exception:
                pass

            # 2) Search all buttons for exact text 'Call'
            try:
                for child in win.descendants(control_type="Button"):
                    try:
                        text = (child.window_text() or "").strip()
                        if text.lower() == "call":
                            child.wait("visible enabled", timeout=3)
                            child.click_input()
                            return {
                                "status": "success",
                                "message": f"Automatically started call to {params.get('person')} at {phone_number}."
                            }
                    except Exception:
                        pass
            except Exception:
                pass

            # 3) Fallback: any visible button containing 'call'
            try:
                for child in win.descendants():
                    try:
                        text = (child.window_text() or "").strip()
                        ctype = child.element_info.control_type
                        if ctype == "Button" and "call" in text.lower():
                            child.click_input()
                            return {
                                "status": "success",
                                "message": f"Automatically started call to {params.get('person')} at {phone_number}."
                            }
                    except Exception:
                        pass
            except Exception:
                pass

            # 4) Debug fallback
            try:
                available_buttons = []
                for child in win.descendants(control_type="Button"):
                    try:
                        txt = (child.window_text() or "").strip()
                        if txt:
                            available_buttons.append(txt)
                    except Exception:
                        pass

                return {
                    "status": "failed",
                    "message": "Phone Link opened, but I could not click the Call button automatically. "
                               f"Visible buttons found: {available_buttons}"
                }
            except Exception:
                return {
                    "status": "failed",
                    "message": "Phone Link opened, but I could not find the Call button."
                }

        except ElementNotFoundError:
            return {
                "status": "failed",
                "message": "Phone Link window was not found after opening the call."
            }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"Failed to start call for {params.get('person')}: {str(e)}"
            }
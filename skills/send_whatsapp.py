import json
import os

from skills.base import BaseSkill
from tools.whatsapp_sender import send_whatsapp_message


CONTACTS_PATH = r"D:\krishna\data\contacts.json"


def load_contacts():
    if not os.path.exists(CONTACTS_PATH):
        return {}

    try:
        with open(CONTACTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


class SendWhatsAppSkill(BaseSkill):
    name = "send_whatsapp"
    required_fields = ["person", "message"]

    def run(self, params: dict, session: dict) -> dict:
        missing = self.get_missing_fields(params)

        if missing:
            return {
                "status": "need_input",
                "missing_fields": missing,
                "message": f"I need these details for WhatsApp: {', '.join(missing)}."
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
                "phone": contacts[person_key],
                "message": params.get("message")
            },
            "message": f"I am ready to send a WhatsApp message to {params.get('person')}."
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
        message = params.get("message", "").strip()

        if not message:
            return {
                "status": "failed",
                "message": "No message text was provided."
            }

        return send_whatsapp_message(phone_number, message)
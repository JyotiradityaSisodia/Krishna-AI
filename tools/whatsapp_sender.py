import os
from pathlib import Path
from playwright.sync_api import sync_playwright


PROFILE_DIR = Path(r"D:\krishna\data\playwright_whatsapp")


def send_whatsapp_message(phone_number: str, message: str) -> dict:
    clean_phone = phone_number.replace("+", "").replace(" ", "").replace("-", "")

    if not clean_phone or not message.strip():
        return {
            "status": "failed",
            "message": "Phone number or message is missing."
        }

    url = f"https://web.whatsapp.com/send?phone={clean_phone}&text={message}"

    try:
        PROFILE_DIR.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=str(PROFILE_DIR),
                headless=False
            )

            page = context.pages[0] if context.pages else context.new_page()
            page.goto(url, wait_until="domcontentloaded")

            # If not logged in, user must scan QR once.
            # On later runs, the same profile should stay logged in.
            try:
                page.wait_for_selector("div[contenteditable='true'][role='textbox']", timeout=30000)
            except Exception:
                context.close()
                return {
                    "status": "failed",
                    "message": "WhatsApp Web is not ready. If this is the first run, open it once and scan the QR code."
                }

            # Give WhatsApp a moment to fully place the prefilled text in the compose box
            page.wait_for_timeout(1500)

            # Press Enter in the compose box to send the message
            box = page.locator("div[contenteditable='true'][role='textbox']").last
            box.click()
            box.press("Enter")

            page.wait_for_timeout(1500)
            context.close()

            return {
                "status": "success",
                "message": f"WhatsApp message sent to {phone_number}."
            }

    except Exception as e:
        return {
            "status": "failed",
            "message": f"Failed to send WhatsApp message: {str(e)}"
        }
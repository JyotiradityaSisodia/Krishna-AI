def interpret_upgrade_intent(user_input: str):
    text = user_input.lower()

    if "maximize your speed" in text or "be faster" in text:
        return {
            "action": "upgrade",
            "target_file": "app/config.py",
            "reason": "User requested faster performance",
            "content": '''APP_NAME = "Krishna"
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "phi3"
DATABASE_PATH = "data/krishna.db"
# speed optimized settings
TIMEOUT = 30
'''
        }

    if "improve your ui" in text:
        return {
            "action": "upgrade",
            "target_file": "desktop/main_window.py",
            "reason": "User requested UI improvement",
            "content": "# Krishna UI improvement placeholder\n"
        }

    return None
import subprocess
import webbrowser
import os


def execute_device_command(command: dict) -> str:
    command_type = command.get("command_type")
    payload = command.get("payload", {})

    if command_type == "open_website":
        url = payload.get("url", "")
        if not url:
            return "No URL provided."
        webbrowser.open(url)
        return f"Opened website: {url}"

    if command_type == "open_app":
        app_name = payload.get("app_name", "").lower()

        app_map = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "notepad": "notepad.exe",
            "vscode": r"C:\Users\Public\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        }

        path = app_map.get(app_name)
        if not path:
            return f"Unknown app: {app_name}"

        try:
            subprocess.Popen(path)
            return f"Opened app: {app_name}"
        except Exception as e:
            return f"Failed to open app {app_name}: {str(e)}"

    if command_type == "say_text":
        text = payload.get("text", "")
        return f"Desktop received text to say: {text}"

    return f"Unknown command type: {command_type}"
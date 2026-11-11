from __future__ import annotations

import os
import subprocess
import webbrowser
from datetime import datetime
from typing import Any


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


APP_MAP = {
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "paint": "mspaint.exe",
    "cmd": "cmd.exe",
    "command prompt": "cmd.exe",
    "explorer": "explorer.exe",
    "file explorer": "explorer.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
}


WEBSITE_MAP = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "github": "https://www.github.com",
    "chatgpt": "https://chatgpt.com",
    "gmail": "https://mail.google.com",
    "whatsapp": "https://web.whatsapp.com",
    "instagram": "https://www.instagram.com",
}


def detect_tool_intent(user_input: str) -> dict[str, Any]:
    text = normalize(user_input)

    if text.startswith("open "):
        target = text[len("open "):].strip()

        if target in WEBSITE_MAP:
            return {"tool": "open_website", "target": target}

        if target in APP_MAP:
            return {"tool": "open_app", "target": target}

        if target.startswith("http://") or target.startswith("https://"):
            return {"tool": "open_direct_url", "target": target}

        return {"tool": "open_unknown", "target": target}

    if text.startswith("search "):
        query = user_input[len("search "):].strip()
        return {"tool": "web_search", "target": query}

    if text.startswith("google "):
        query = user_input[len("google "):].strip()
        return {"tool": "web_search", "target": query}

    if "what time" in text or text == "time":
        return {"tool": "tell_time", "target": ""}

    if "what date" in text or "what day" in text or text == "date":
        return {"tool": "tell_date", "target": ""}

    return {"tool": None, "target": ""}


def open_app(app_name: str) -> str:
    app_name = normalize(app_name)
    exe = APP_MAP.get(app_name)

    if not exe:
        return f"I do not know how to open {app_name} yet, sir."

    try:
        if os.path.exists(exe) or exe.endswith(".exe"):
            subprocess.Popen([exe], shell=False)
            return f"Opening {app_name}, sir."
    except Exception as e:
        return f"I could not open {app_name}, sir. {e}"

    return f"I could not open {app_name}, sir."


def open_website(site_name: str) -> str:
    site_name = normalize(site_name)
    url = WEBSITE_MAP.get(site_name)

    if not url:
        return f"I do not know that website yet, sir."

    try:
        webbrowser.open(url)
        return f"Opening {site_name}, sir."
    except Exception as e:
        return f"I could not open {site_name}, sir. {e}"


def open_direct_url(url: str) -> str:
    try:
        webbrowser.open(url)
        return "Opening it now, sir."
    except Exception as e:
        return f"I could not open that link, sir. {e}"


def web_search(query: str) -> str:
    query = query.strip()
    if not query:
        return "Tell me what to search for, sir."

    try:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searching for {query}, sir."
    except Exception as e:
        return f"I could not search for that, sir. {e}"


def tell_time() -> str:
    now = datetime.now().strftime("%I:%M %p")
    return f"The time is {now}, sir."


def tell_date() -> str:
    today = datetime.now().strftime("%A, %d %B %Y")
    return f"Today is {today}, sir."


def execute_tool(user_input: str) -> str | None:
    intent = detect_tool_intent(user_input)
    tool = intent["tool"]
    target = intent["target"]

    if tool == "open_app":
        return open_app(target)

    if tool == "open_website":
        return open_website(target)

    if tool == "open_direct_url":
        return open_direct_url(target)

    if tool == "web_search":
        return web_search(target)

    if tool == "tell_time":
        return tell_time()

    if tool == "tell_date":
        return tell_date()

    return None
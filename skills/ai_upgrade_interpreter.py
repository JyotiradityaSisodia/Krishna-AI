import json
import requests


OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2:1b"


def interpret_upgrade_intent_ai(user_input: str):
    text = user_input.lower().strip()

    ui_keywords = [
        "interface", "ui", "look", "theme", "dark", "cool",
        "modern", "layout", "design", "appearance"
    ]
    speed_keywords = [
        "faster", "speed", "quicker", "responsive", "lightweight"
    ]
    memory_keywords = [
        "memory", "remember", "recall", "preferences"
    ]
    personality_keywords = [
        "warm", "friendly", "helpful", "personality", "tone"
    ]

    if any(word in text for word in ui_keywords):
        theme = "modern_dark"
        if "blue" in text:
            theme = "modern_blue"
        elif "minimal" in text:
            theme = "minimal_dark"
        elif "cool" in text or "dark" in text or "modern" in text:
            theme = "modern_dark"

        return {
            "action": "upgrade",
            "category": "ui",
            "target_file": "desktop/main_window.py",
            "reason": f"User requested a UI/interface improvement: {user_input}",
            "theme": theme
        }

    if any(word in text for word in speed_keywords):
        return {
            "action": "upgrade",
            "category": "speed",
            "target_file": "app/config.py",
            "reason": f"User requested a speed/performance improvement: {user_input}"
        }

    if any(word in text for word in memory_keywords):
        return {
            "action": "upgrade",
            "category": "memory",
            "target_file": "app/orchestrator.py",
            "reason": f"User requested a memory improvement: {user_input}"
        }

    if any(word in text for word in personality_keywords):
        return {
            "action": "upgrade",
            "category": "personality",
            "target_file": "app/orchestrator.py",
            "reason": f"User requested a personality/tone improvement: {user_input}"
        }

    system_prompt = """
You are an AI upgrade interpreter for Krishna.

Your job:
- Decide if the user's request is asking Krishna to upgrade or change itself.
- If yes, return a JSON object only.
- If no, return {"action":"none"}.

Allowed upgrade categories:
- ui
- speed
- memory
- personality

Allowed target files:
- desktop/main_window.py
- app/config.py
- app/orchestrator.py

Rules:
- Return JSON only
- Do not explain
- Do not include markdown
"""

    user_prompt = f"""
User request: {user_input}

Return one JSON object in this format:

{{
  "action": "upgrade" or "none",
  "category": "ui" or "speed" or "memory" or "personality",
  "target_file": "desktop/main_window.py" or "app/config.py" or "app/orchestrator.py",
  "reason": "short reason"
}}
"""

    try:
        res = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "stream": False
            }
        )

        if not res.ok:
            return {"action": "none", "error": f"Ollama returned {res.status_code}: {res.text}"}

        raw = res.text.strip()

        try:
            data = json.loads(raw)
            if "message" in data and "content" in data["message"]:
                return json.loads(data["message"]["content"].strip())
            return data
        except Exception:
            lines = [line.strip() for line in raw.splitlines() if line.strip()]
            for line in lines:
                try:
                    obj = json.loads(line)
                    if "message" in obj and "content" in obj["message"]:
                        return json.loads(obj["message"]["content"].strip())
                except Exception:
                    pass

        return {"action": "none", "error": "Could not parse upgrade interpreter output."}

    except Exception as e:
        return {"action": "none", "error": str(e)}


def build_upgrade_content(plan: dict):
    category = plan.get("category")
    target_file = plan.get("target_file")

    if category == "speed" and target_file == "app/config.py":
        return '''APP_NAME = "Krishna"
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "llama3.2:1b"
DATABASE_PATH = "data/krishna.db"
BACKEND_TIMEOUT = 10
DESKTOP_TIMEOUT = 30
'''

    if category == "memory" and target_file == "app/orchestrator.py":
        return None

    if category == "personality" and target_file == "app/orchestrator.py":
        return None

    if category == "ui" and target_file == "desktop/main_window.py":
        theme = plan.get("theme", "modern_dark")
        return build_ui_theme_file(theme)

    return None


def build_ui_theme_file(theme: str):
    if theme == "modern_blue":
        accent = "#3b82f6"
        hover = "#2563eb"
        bg = "#0b1220"
        panel = "#111827"
        border = "#334155"
        subtitle = "#93c5fd"
    elif theme == "minimal_dark":
        accent = "#475569"
        hover = "#334155"
        bg = "#111111"
        panel = "#1a1a1a"
        border = "#2a2a2a"
        subtitle = "#a3a3a3"
    else:
        accent = "#2563eb"
        hover = "#1d4ed8"
        bg = "#020617"
        panel = "#0f172a"
        border = "#334155"
        subtitle = "#7dd3fc"

    return f'''from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel,
    QHBoxLayout, QListWidget, QListWidgetItem, QFrame, QMessageBox
)
import requests


class ChatWorker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, message: str, timeout: int = 30):
        super().__init__()
        self.message = message
        self.timeout = timeout

    def run(self):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/chat",
                json={{"message": self.message}},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            reply = data.get("reply", "No reply received.")
            self.finished.emit(reply)
        except Exception as e:
            self.error.emit(str(e))


class KrishnaWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Krishna")
        self.resize(1100, 720)

        self.chat_thread = None
        self.chat_worker = None

        root = QHBoxLayout()
        self.setLayout(root)

        sidebar = QVBoxLayout()
        sidebar_frame = QFrame()
        sidebar_frame.setLayout(sidebar)
        sidebar_frame.setFixedWidth(250)

        self.logo = QLabel("Krishna")
        self.logo.setStyleSheet("font-size: 32px; font-weight: bold;")

        self.subtitle = QLabel("Modern Krishna UI")
        self.subtitle.setStyleSheet("font-size: 14px; color: {subtitle};")

        self.quick_actions = QListWidget()
        for item in [
            "Research Problem",
            "Write Code",
            "Order Food",
            "Book Ride",
            "Book Show",
            "Send Email",
            "Send WhatsApp",
            "Call Person"
        ]:
            QListWidgetItem(item, self.quick_actions)

        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("font-size: 13px; color: {subtitle};")

        sidebar.addWidget(self.logo)
        sidebar.addWidget(self.subtitle)
        sidebar.addSpacing(12)
        sidebar.addWidget(QLabel("Quick Actions"))
        sidebar.addWidget(self.quick_actions)
        sidebar.addSpacing(12)
        sidebar.addWidget(self.status_label)

        main_layout = QVBoxLayout()

        self.chat_title = QLabel("Conversation")
        self.chat_title.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("Krishna conversations will appear here...")

        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("Talk to Krishna...")
        self.input_box.setFixedHeight(110)

        button_row = QHBoxLayout()

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_chat)

        button_row.addWidget(self.send_button)
        button_row.addWidget(self.clear_button)

        main_layout.addWidget(self.chat_title)
        main_layout.addWidget(self.chat_history)
        main_layout.addWidget(self.input_box)
        main_layout.addLayout(button_row)

        root.addWidget(sidebar_frame)
        root.addLayout(main_layout)

        self.quick_actions.itemClicked.connect(self.handle_quick_action)

        self.setStyleSheet("""
            QWidget {{
                background-color: {bg};
                color: #f8fafc;
                font-family: Segoe UI;
                font-size: 14px;
            }}
            QFrame {{
                background-color: {panel};
                border: 1px solid {border};
                border-radius: 18px;
                padding: 10px;
            }}
            QTextEdit {{
                background-color: {panel};
                color: #f8fafc;
                border: 1px solid {border};
                border-radius: 14px;
                padding: 10px;
            }}
            QPushButton {{
                background-color: {accent};
                color: white;
                border: none;
                border-radius: 12px;
                padding: 10px 16px;
                min-width: 100px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:disabled {{
                background-color: #475569;
                color: #cbd5e1;
            }}
            QListWidget {{
                background-color: {panel};
                border: 1px solid {border};
                border-radius: 14px;
                padding: 6px;
            }}
            QListWidget::item {{
                padding: 10px;
                border-radius: 10px;
            }}
            QListWidget::item:selected {{
                background-color: {hover};
            }}
            QLabel {{
                color: #f8fafc;
            }}
        """)

    def send_message(self):
        message = self.input_box.toPlainText().strip()
        if not message:
            return

        self.chat_history.append(f"You:\\n{{message}}\\n")
        self.input_box.clear()
        self.chat_history.append("Krishna:\\n...\\n")
        self.status_label.setText("Status: Thinking...")
        self.send_button.setEnabled(False)

        self.chat_thread = QThread()
        self.chat_worker = ChatWorker(message, timeout=30)
        self.chat_worker.moveToThread(self.chat_thread)

        self.chat_thread.started.connect(self.chat_worker.run)
        self.chat_worker.finished.connect(self.on_chat_finished)
        self.chat_worker.error.connect(self.on_chat_error)
        self.chat_worker.finished.connect(self.chat_thread.quit)
        self.chat_worker.error.connect(self.chat_thread.quit)
        self.chat_worker.finished.connect(self.chat_worker.deleteLater)
        self.chat_worker.error.connect(self.chat_worker.deleteLater)
        self.chat_thread.finished.connect(self.chat_thread.deleteLater)

        self.chat_thread.start()

    def on_chat_finished(self, reply: str):
        text = self.chat_history.toPlainText()
        text = text.rsplit("Krishna:\\n...\\n", 1)[0]
        self.chat_history.setPlainText(text)
        self.chat_history.append(f"Krishna:\\n{{reply}}\\n")
        self.status_label.setText("Status: Ready")
        self.send_button.setEnabled(True)

    def on_chat_error(self, error: str):
        text = self.chat_history.toPlainText()
        text = text.rsplit("Krishna:\\n...\\n", 1)[0]
        self.chat_history.setPlainText(text)
        self.chat_history.append(f"Krishna:\\nError: {{error}}\\n")
        self.status_label.setText("Status: Error")
        self.send_button.setEnabled(True)

    def clear_chat(self):
        self.chat_history.clear()
        self.status_label.setText("Status: Ready")

    def handle_quick_action(self, item):
        action = item.text()
        prompts = {{
            "Research Problem": "Research this problem step by step:",
            "Write Code": "Write code for this task:",
            "Order Food": "Help me order food:",
            "Book Ride": "Help me book a ride:",
            "Book Show": "Help me book a show:",
            "Send Email": "Draft an email for:",
            "Send WhatsApp": "Draft a WhatsApp message for:",
            "Call Person": "Help me call:"
        }}
        self.input_box.setPlainText(prompts.get(action, ""))
        self.input_box.setFocus()
'''
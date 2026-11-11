from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel,
    QHBoxLayout, QListWidget, QListWidgetItem, QFrame, QMessageBox
)
import requests
from pathlib import Path

from widgets import ApprovalDialog
from self_upgrade.manager import prepare_self_upgrade, apply_approved_upgrade
from skills.ai_upgrade_interpreter import interpret_upgrade_intent_ai, build_upgrade_content
from ai_voice import speak
from voice_input import listen_once


class ChatWorker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, message: str, timeout: int = 45):
        super().__init__()
        self.message = message
        self.timeout = timeout

    def run(self):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/chat",
                json={"message": self.message},
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            reply = data.get("reply", "No reply received.")
            self.finished.emit(reply)
        except Exception as e:
            self.error.emit(str(e))


class UpgradeInterpreterWorker(QObject):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, message: str):
        super().__init__()
        self.message = message

    def run(self):
        try:
            plan = interpret_upgrade_intent_ai(self.message)
            self.finished.emit(plan)
        except Exception as e:
            self.error.emit(str(e))


class VoiceWorker(QObject):
    finished = Signal()
    error = Signal(str)

    def __init__(self, text: str, mode: str = "short"):
        super().__init__()
        self.text = text
        self.mode = mode

    def run(self):
        try:
            speak(self.text, self.mode)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class ListenWorker(QObject):
    finished = Signal(str)
    error = Signal(str)

    def run(self):
        try:
            text = listen_once(seconds=5)
            self.finished.emit(text)
        except Exception as e:
            self.error.emit(str(e))


class KrishnaWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Krishna")
        self.resize(1100, 720)

        self.chat_thread = None
        self.chat_worker = None
        self.upgrade_thread = None
        self.upgrade_worker = None
        self.voice_thread = None
        self.voice_worker = None
        self.listen_thread = None
        self.listen_worker = None
        self.last_user_message = ""

        root = QHBoxLayout()
        self.setLayout(root)

        # Sidebar
        sidebar = QVBoxLayout()
        sidebar_frame = QFrame()
        sidebar_frame.setLayout(sidebar)
        sidebar_frame.setFixedWidth(250)

        self.logo = QLabel("Krishna")
        self.logo.setStyleSheet("font-size: 30px; font-weight: bold;")

        self.subtitle = QLabel("Fast Chat + Voice Input")
        self.subtitle.setStyleSheet("font-size: 14px; color: #9ca3af;")

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
        self.status_label.setStyleSheet("font-size: 13px; color: #93c5fd;")

        sidebar.addWidget(self.logo)
        sidebar.addWidget(self.subtitle)
        sidebar.addSpacing(12)
        sidebar.addWidget(QLabel("Quick Actions"))
        sidebar.addWidget(self.quick_actions)
        sidebar.addSpacing(12)
        sidebar.addWidget(self.status_label)

        # Main area
        main_layout = QVBoxLayout()

        self.chat_title = QLabel("Conversation")
        self.chat_title.setStyleSheet("font-size: 22px; font-weight: bold;")

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setPlaceholderText("Krishna conversations will appear here...")

        self.input_box = QTextEdit()
        self.input_box.setPlaceholderText("Talk to Krishna...")
        self.input_box.setFixedHeight(110)

        button_row = QHBoxLayout()

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_message)

        self.speak_button = QPushButton("Speak")
        self.speak_button.clicked.connect(self.start_listening)

        self.upgrade_button = QPushButton("Interpret Upgrade")
        self.upgrade_button.clicked.connect(self.interpret_upgrade_request)

        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_chat)

        button_row.addWidget(self.send_button)
        button_row.addWidget(self.speak_button)
        button_row.addWidget(self.upgrade_button)
        button_row.addWidget(self.clear_button)

        main_layout.addWidget(self.chat_title)
        main_layout.addWidget(self.chat_history)
        main_layout.addWidget(self.input_box)
        main_layout.addLayout(button_row)

        root.addWidget(sidebar_frame)
        root.addLayout(main_layout)

        self.quick_actions.itemClicked.connect(self.handle_quick_action)

        self.setStyleSheet("""
            QWidget {
                background-color: #0f172a;
                color: #f8fafc;
                font-family: Segoe UI;
                font-size: 14px;
            }
            QFrame {
                background-color: #111827;
                border: 1px solid #1f2937;
                border-radius: 14px;
                padding: 10px;
            }
            QTextEdit {
                background-color: #111827;
                color: #f8fafc;
                border: 1px solid #374151;
                border-radius: 12px;
                padding: 10px;
            }
            QPushButton {
                background-color: #2563eb;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 10px 16px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #475569;
                color: #cbd5e1;
            }
            QListWidget {
                background-color: #111827;
                border: 1px solid #374151;
                border-radius: 12px;
                padding: 6px;
            }
            QListWidget::item {
                padding: 10px;
                border-radius: 8px;
            }
            QListWidget::item:selected {
                background-color: #1d4ed8;
            }
            QLabel {
                color: #f8fafc;
            }
        """)

    def send_message(self):
        message = self.input_box.toPlainText().strip()
        if not message:
            return

        self.last_user_message = message

        self.chat_history.append(f"You:\n{message}\n")
        self.input_box.clear()
        self.chat_history.append("Krishna:\n...\n")
        self.status_label.setText("Status: Thinking...")
        self.send_button.setEnabled(False)
        self.speak_button.setEnabled(False)
        self.upgrade_button.setEnabled(False)

        self.chat_thread = QThread()
        self.chat_worker = ChatWorker(message, timeout=45)
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

    def start_listening(self):
        self.status_label.setText("Status: Listening...")
        self.send_button.setEnabled(False)
        self.speak_button.setEnabled(False)
        self.upgrade_button.setEnabled(False)

        self.listen_thread = QThread()
        self.listen_worker = ListenWorker()
        self.listen_worker.moveToThread(self.listen_thread)

        self.listen_thread.started.connect(self.listen_worker.run)
        self.listen_worker.finished.connect(self.on_listen_finished)
        self.listen_worker.error.connect(self.on_listen_error)
        self.listen_worker.finished.connect(self.listen_thread.quit)
        self.listen_worker.error.connect(self.listen_thread.quit)
        self.listen_worker.finished.connect(self.listen_worker.deleteLater)
        self.listen_worker.error.connect(self.listen_worker.deleteLater)
        self.listen_thread.finished.connect(self.listen_thread.deleteLater)

        self.listen_thread.start()

    def on_listen_finished(self, text: str):
        self.send_button.setEnabled(True)
        self.speak_button.setEnabled(True)
        self.upgrade_button.setEnabled(True)

        if not text.strip():
            self.status_label.setText("Status: Ready")
            self.chat_history.append("Krishna:\nI did not hear anything clearly.\n")
            return

        self.input_box.setPlainText(text)
        self.status_label.setText("Status: Heard voice input")
        self.send_message()

    def on_listen_error(self, error: str):
        self.send_button.setEnabled(True)
        self.speak_button.setEnabled(True)
        self.upgrade_button.setEnabled(True)
        self.status_label.setText("Status: Voice input error")
        self.chat_history.append(f"Krishna:\nVoice input error: {error}\n")

    def interpret_upgrade_request(self):
        message = self.input_box.toPlainText().strip()
        if not message:
            QMessageBox.information(self, "No Input", "Type an upgrade request first.")
            return

        self.chat_history.append(f"You (upgrade request):\n{message}\n")
        self.input_box.clear()
        self.chat_history.append("Krishna:\nInterpreting upgrade request...\n")
        self.status_label.setText("Status: Interpreting upgrade...")
        self.send_button.setEnabled(False)
        self.speak_button.setEnabled(False)
        self.upgrade_button.setEnabled(False)

        self.upgrade_thread = QThread()
        self.upgrade_worker = UpgradeInterpreterWorker(message)
        self.upgrade_worker.moveToThread(self.upgrade_thread)

        self.upgrade_thread.started.connect(self.upgrade_worker.run)
        self.upgrade_worker.finished.connect(self.on_upgrade_interpreted)
        self.upgrade_worker.error.connect(self.on_upgrade_error)
        self.upgrade_worker.finished.connect(self.upgrade_thread.quit)
        self.upgrade_worker.error.connect(self.upgrade_thread.quit)
        self.upgrade_worker.finished.connect(self.upgrade_worker.deleteLater)
        self.upgrade_worker.error.connect(self.upgrade_worker.deleteLater)
        self.upgrade_thread.finished.connect(self.upgrade_thread.deleteLater)

        self.upgrade_thread.start()

    def on_chat_finished(self, reply: str):
        text = self.chat_history.toPlainText()
        text = text.rsplit("Krishna:\n...\n", 1)[0]
        self.chat_history.setPlainText(text)
        self.chat_history.append(f"Krishna:\n{reply}\n")
        self.status_label.setText("Status: Ready")
        self.send_button.setEnabled(True)
        self.speak_button.setEnabled(True)
        self.upgrade_button.setEnabled(True)

        research_keywords = [
            "research", "analyze", "analysis", "explain in detail",
            "step by step", "plan", "compare", "study", "investigate",
            "deeply", "full detail", "detailed"
        ]

        voice_mode = "short"
        user_text = self.last_user_message.lower().strip()

        if any(keyword in user_text for keyword in research_keywords):
            voice_mode = "full"

        self.start_voice(reply, voice_mode)

    def on_chat_error(self, error: str):
        text = self.chat_history.toPlainText()
        text = text.rsplit("Krishna:\n...\n", 1)[0]
        self.chat_history.setPlainText(text)
        self.chat_history.append(f"Krishna:\nError: {error}\n")
        self.status_label.setText("Status: Error")
        self.send_button.setEnabled(True)
        self.speak_button.setEnabled(True)
        self.upgrade_button.setEnabled(True)

    def on_upgrade_interpreted(self, plan: dict):
        self.send_button.setEnabled(True)
        self.speak_button.setEnabled(True)
        self.upgrade_button.setEnabled(True)

        text = self.chat_history.toPlainText()
        text = text.rsplit("Krishna:\nInterpreting upgrade request...\n", 1)[0]
        self.chat_history.setPlainText(text)

        if not plan:
            self.chat_history.append("Krishna:\nI could not interpret that upgrade request.\n")
            self.status_label.setText("Status: Ready")
            return

        if plan.get("error"):
            self.chat_history.append(f"Krishna:\nUpgrade interpreter note: {plan['error']}\n")

        if plan.get("action") != "upgrade":
            self.chat_history.append("Krishna:\nI did not detect a safe self-upgrade request from that message.\n")
            self.status_label.setText("Status: Ready")
            return

        target_file = plan.get("target_file", "")
        reason = plan.get("reason", "User requested an upgrade")
        category = plan.get("category", "")

        new_content = build_upgrade_content(plan)

        if category == "ui" and target_file == "desktop/main_window.py":
            path = Path(target_file)
            current_content = path.read_text(encoding="utf-8") if path.exists() else ""
            note = f'\n# Krishna UI upgrade request noted: {reason}\n'
            new_content = current_content + note

        if not new_content:
            self.chat_history.append(
                f"Krishna:\nI understood the request, but I do not yet have a safe code template for category '{category}'.\n"
            )
            self.status_label.setText("Status: Ready")
            return

        self.process_upgrade(target_file, new_content, reason)

    def on_upgrade_error(self, error: str):
        text = self.chat_history.toPlainText()
        text = text.rsplit("Krishna:\nInterpreting upgrade request...\n", 1)[0]
        self.chat_history.setPlainText(text)
        self.chat_history.append(f"Krishna:\nUpgrade interpreter error: {error}\n")
        self.status_label.setText("Status: Error")
        self.send_button.setEnabled(True)
        self.speak_button.setEnabled(True)
        self.upgrade_button.setEnabled(True)

    def start_voice(self, text: str, mode: str = "short"):
        if not text or not text.strip():
            return

        self.voice_thread = QThread()
        self.voice_worker = VoiceWorker(text, mode)
        self.voice_worker.moveToThread(self.voice_thread)

        self.voice_thread.started.connect(self.voice_worker.run)
        self.voice_worker.finished.connect(self.on_voice_finished)
        self.voice_worker.finished.connect(self.voice_thread.quit)
        self.voice_worker.error.connect(self.on_voice_error)
        self.voice_worker.error.connect(self.voice_thread.quit)
        self.voice_worker.finished.connect(self.voice_worker.deleteLater)
        self.voice_worker.error.connect(self.voice_worker.deleteLater)
        self.voice_thread.finished.connect(self.voice_thread.deleteLater)

        self.voice_thread.start()

    def on_voice_finished(self):
        self.status_label.setText("Status: Ready")

    def on_voice_error(self, error: str):
        self.chat_history.append(f"Krishna:\nVoice error: {error}\n")
        self.status_label.setText("Status: Ready")

    def clear_chat(self):
        self.chat_history.clear()
        self.status_label.setText("Status: Ready")

    def handle_quick_action(self, item):
        action = item.text()
        prompts = {
            "Research Problem": "Research this problem step by step:",
            "Write Code": "Write code for this task:",
            "Order Food": "Help me order food:",
            "Book Ride": "Help me book a ride:",
            "Book Show": "Help me book a show:",
            "Send Email": "Draft an email for:",
            "Send WhatsApp": "Draft a WhatsApp message for:",
            "Call Person": "Help me call:"
        }
        self.input_box.setPlainText(prompts.get(action, ""))
        self.input_box.setFocus()

    def process_upgrade(self, target_file: str, new_content: str, reason: str):
        try:
            proposal = prepare_self_upgrade(target_file, new_content, reason)

            if proposal["status"] != "awaiting_approval":
                QMessageBox.warning(self, "Upgrade Rejected", proposal.get("message", "Unknown error"))
                self.status_label.setText("Status: Upgrade rejected")
                return

            dialog = ApprovalDialog(
                proposal["summary"],
                proposal["proposed_content"],
                self
            )
            result = dialog.exec()

            if result and dialog.approved:
                applied = apply_approved_upgrade(target_file, proposal["proposed_content"])
                QMessageBox.information(self, "Upgrade Applied", applied["message"])
                self.chat_history.append(
                    f"Krishna:\nApplied self-upgrade to {target_file}\nBackup saved at {proposal['summary']['backup_path']}\n"
                )
                self.status_label.setText("Status: Upgrade applied")
            else:
                QMessageBox.information(self, "Upgrade Cancelled", "You rejected the proposed self-upgrade.")
                self.chat_history.append("Krishna:\nSelf-upgrade proposal rejected by user.\n")
                self.status_label.setText("Status: Upgrade cancelled")

        except Exception as e:
            QMessageBox.critical(self, "Upgrade Error", str(e))
            self.status_label.setText("Status: Upgrade error")
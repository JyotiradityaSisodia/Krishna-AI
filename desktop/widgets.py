from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QTextEdit,
    QPushButton, QHBoxLayout, QTabWidget, QWidget
)


class ApprovalDialog(QDialog):
    def __init__(self, summary: dict, proposed_content: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Krishna Approval Required")
        self.resize(950, 700)
        self.approved = False

        layout = QVBoxLayout()

        title = QLabel("Krishna wants to apply a self-upgrade")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")

        target = QLabel(f"Target file: {summary.get('target_file', 'Unknown')}")
        reason = QLabel(f"Reason: {summary.get('reason', 'No reason provided')}")
        backup = QLabel(f"Backup path: {summary.get('backup_path', 'No backup created')}")

        tabs = QTabWidget()

        content_tab = QWidget()
        content_layout = QVBoxLayout()
        self.preview = QTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setPlainText(proposed_content)
        content_layout.addWidget(self.preview)
        content_tab.setLayout(content_layout)

        diff_tab = QWidget()
        diff_layout = QVBoxLayout()
        self.diff_view = QTextEdit()
        self.diff_view.setReadOnly(True)
        self.diff_view.setPlainText(summary.get("diff_text", "No diff available"))
        diff_layout.addWidget(self.diff_view)
        diff_tab.setLayout(diff_layout)

        tabs.addTab(content_tab, "Proposed Content")
        tabs.addTab(diff_tab, "Diff")

        buttons = QHBoxLayout()
        self.approve_button = QPushButton("Approve")
        self.reject_button = QPushButton("Reject")

        self.approve_button.clicked.connect(self.on_approve)
        self.reject_button.clicked.connect(self.on_reject)

        buttons.addWidget(self.approve_button)
        buttons.addWidget(self.reject_button)

        layout.addWidget(title)
        layout.addWidget(target)
        layout.addWidget(reason)
        layout.addWidget(backup)
        layout.addWidget(tabs)
        layout.addLayout(buttons)

        self.setLayout(layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #0f172a;
                color: #f8fafc;
                font-family: Segoe UI;
            }
            QLabel {
                color: #f8fafc;
                margin-bottom: 4px;
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
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QTabWidget::pane {
                border: 1px solid #374151;
                border-radius: 8px;
            }
        """)

    def on_approve(self):
        self.approved = True
        self.accept()

    def on_reject(self):
        self.approved = False
        self.reject()
from pywinauto import Application

app = Application(backend="uia").connect(title_re=".*Phone Link.*|.*Link to Windows.*", timeout=15)
win = app.top_window()

print("WINDOW:", win.window_text())
print("=" * 50)

for child in win.descendants():
    try:
        print(
            "TEXT:", repr(child.window_text()),
            "| TYPE:", child.element_info.control_type
        )
    except Exception:
        pass
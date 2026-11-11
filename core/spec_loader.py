import os

SPEC_PATH = os.path.join("docs", "krishna_spec.md")

def load_krishna_spec() -> str:
    try:
        with open(SPEC_PATH, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""
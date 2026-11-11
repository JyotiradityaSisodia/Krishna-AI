from pathlib import Path


def apply_patch(file_path: str, new_content: str):
    target = Path(file_path)
    target.write_text(new_content, encoding="utf-8")
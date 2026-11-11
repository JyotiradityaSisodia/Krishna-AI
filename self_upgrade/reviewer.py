import difflib
from pathlib import Path


def build_diff(target_file: str, new_content: str) -> str:
    path = Path(target_file)

    old_content = ""
    if path.exists():
        old_content = path.read_text(encoding="utf-8")

    diff = difflib.unified_diff(
        old_content.splitlines(),
        new_content.splitlines(),
        fromfile=f"old/{target_file}",
        tofile=f"new/{target_file}",
        lineterm=""
    )
    return "\n".join(diff)


def build_change_summary(target_file: str, reason: str, backup_path: str, diff_text: str) -> dict:
    return {
        "target_file": target_file,
        "reason": reason,
        "backup_path": backup_path,
        "approval_required": True,
        "status": "waiting_for_approval",
        "diff_text": diff_text
    }
from self_upgrade.backup import backup_file
from self_upgrade.patcher import apply_patch
from self_upgrade.reviewer import build_change_summary, build_diff
from self_upgrade.sandbox_runner import run_basic_validation


def prepare_self_upgrade(target_file: str, new_content: str, reason: str):
    validation = run_basic_validation(new_content)
    if not validation["ok"]:
        return {
            "status": "rejected",
            "message": validation["message"]
        }

    backup_path = backup_file(target_file)
    diff_text = build_diff(target_file, new_content)
    summary = build_change_summary(target_file, reason, backup_path, diff_text)

    return {
        "status": "awaiting_approval",
        "summary": summary,
        "proposed_content": new_content
    }


def apply_approved_upgrade(target_file: str, new_content: str):
    apply_patch(target_file, new_content)
    return {
        "status": "applied",
        "message": f"Upgrade applied to {target_file}"
    }
def run_basic_validation(new_content: str) -> dict:
    if not new_content or not new_content.strip():
        return {"ok": False, "message": "Generated content is empty."}

    return {"ok": True, "message": "Basic validation passed."}
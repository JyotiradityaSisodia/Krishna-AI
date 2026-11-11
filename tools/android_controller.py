import subprocess
import time
import re
import xml.etree.ElementTree as ET

ADB_PATH = r"D:\krishna\android\platform-tools\adb.exe"


def run_adb_command(args: list[str]) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            [ADB_PATH] + args,
            capture_output=True,
            text=True,
            timeout=20
        )
        if result.returncode != 0:
            return False, result.stderr.strip() or result.stdout.strip()
        return True, result.stdout.strip()
    except Exception as e:
        return False, str(e)


def is_device_connected() -> bool:
    ok, output = run_adb_command(["devices"])
    if not ok:
        return False

    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for line in lines[1:]:
        if "\tdevice" in line:
            return True
    return False


def tap(x: int, y: int) -> tuple[bool, str]:
    return run_adb_command(["shell", "input", "tap", str(x), str(y)])


def type_text(text: str) -> tuple[bool, str]:
    safe = text.replace(" ", "%s")
    return run_adb_command(["shell", "input", "text", safe])


def keyevent(code: int) -> tuple[bool, str]:
    return run_adb_command(["shell", "input", "keyevent", str(code)])


def swipe(x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300) -> tuple[bool, str]:
    return run_adb_command([
        "shell", "input", "swipe",
        str(x1), str(y1), str(x2), str(y2), str(duration_ms)
    ])


def open_app(package_name: str) -> tuple[bool, str]:
    return run_adb_command([
        "shell", "monkey",
        "-p", package_name,
        "-c", "android.intent.category.LAUNCHER",
        "1"
    ])


def sleep(seconds: float):
    time.sleep(seconds)


def dump_ui() -> str:
    run_adb_command(["shell", "uiautomator", "dump", "/sdcard/window_dump.xml"])
    ok, xml_text = run_adb_command(["shell", "cat", "/sdcard/window_dump.xml"])
    return xml_text if ok else ""


def _center_from_bounds(bounds: str):
    m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
    if not m:
        return None
    x1, y1, x2, y2 = map(int, m.groups())
    return (x1 + x2) // 2, (y1 + y2) // 2


def find_element_center(
    text_contains: str | None = None,
    resource_id_contains: str | None = None,
    content_desc_contains: str | None = None,
    class_name_contains: str | None = None,
):
    xml_text = dump_ui()
    if not xml_text:
        return None

    try:
        root = ET.fromstring(xml_text)
    except Exception:
        return None

    for node in root.iter("node"):
        text = node.attrib.get("text", "") or ""
        resource_id = node.attrib.get("resource-id", "") or ""
        content_desc = node.attrib.get("content-desc", "") or ""
        class_name = node.attrib.get("class", "") or ""
        bounds = node.attrib.get("bounds", "")

        if text_contains and text_contains.lower() not in text.lower():
            continue
        if resource_id_contains and resource_id_contains.lower() not in resource_id.lower():
            continue
        if content_desc_contains and content_desc_contains.lower() not in content_desc.lower():
            continue
        if class_name_contains and class_name_contains.lower() not in class_name.lower():
            continue

        center = _center_from_bounds(bounds)
        if center:
            return center

    return None


def tap_element(
    text_contains: str | None = None,
    resource_id_contains: str | None = None,
    content_desc_contains: str | None = None,
    class_name_contains: str | None = None,
):
    center = find_element_center(
        text_contains=text_contains,
        resource_id_contains=resource_id_contains,
        content_desc_contains=content_desc_contains,
        class_name_contains=class_name_contains,
    )
    if not center:
        return False, "Element not found"

    return tap(center[0], center[1])
import xml.etree.ElementTree as ET
from tools.android_controller import dump_ui

xml_text = dump_ui()

try:
    root = ET.fromstring(xml_text)
except Exception as e:
    print("XML parse error:", e)
    raise

for node in root.iter("node"):
    text = (node.attrib.get("text", "") or "").strip()
    desc = (node.attrib.get("content-desc", "") or "").strip()
    rid = (node.attrib.get("resource-id", "") or "").strip()
    cls = (node.attrib.get("class", "") or "").strip()
    bounds = (node.attrib.get("bounds", "") or "").strip()

    if text or desc:
        print(f"TEXT={text!r} DESC={desc!r} ID={rid!r} CLASS={cls!r} BOUNDS={bounds!r}")
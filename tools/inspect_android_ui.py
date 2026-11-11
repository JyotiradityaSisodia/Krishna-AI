from tools.android_controller import dump_ui

xml_text = dump_ui()
print(xml_text[:20000])  # first 20k chars
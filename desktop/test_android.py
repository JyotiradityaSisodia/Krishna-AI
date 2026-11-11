from tools.android_controller import is_device_connected, open_app

print("Device connected:", is_device_connected())
print(open_app("com.application.zomato"))
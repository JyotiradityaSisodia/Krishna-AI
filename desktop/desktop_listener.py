import time
from desktop.cloud_client import register_this_device, fetch_commands
from desktop.device_actions import execute_device_command

print(register_this_device())
print("Desktop listener started...")

while True:
    commands = fetch_commands()
    for command in commands:
        print("Received command:", command)
        result = execute_device_command(command)
        print("Result:", result)
    time.sleep(3)
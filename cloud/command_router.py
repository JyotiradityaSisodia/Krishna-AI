COMMAND_QUEUE = {}
COMMAND_RESULTS = {}


def push_command(target_device_id: str, command: dict):
    if target_device_id not in COMMAND_QUEUE:
        COMMAND_QUEUE[target_device_id] = []
    COMMAND_QUEUE[target_device_id].append(command)


def pop_commands(target_device_id: str):
    cmds = COMMAND_QUEUE.get(target_device_id, [])
    COMMAND_QUEUE[target_device_id] = []
    return cmds


def push_result(device_id: str, result: dict):
    if device_id not in COMMAND_RESULTS:
        COMMAND_RESULTS[device_id] = []
    COMMAND_RESULTS[device_id].append(result)


def pop_results(device_id: str):
    results = COMMAND_RESULTS.get(device_id, [])
    COMMAND_RESULTS[device_id] = []
    return results
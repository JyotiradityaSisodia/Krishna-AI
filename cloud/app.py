from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional

from cloud.models import DeviceRegisterRequest, CommandRequest, CommandResultRequest
from cloud.device_registry import register_device, list_devices
from cloud.command_router import push_command, pop_commands, push_result, pop_results

from core.unified_orchestrator import create_unified_task
from core.task_store import (
    list_tasks,
    get_task,
    update_task_status,
    complete_task,
    tasks_for_target_device,
)

app = FastAPI(title="Krishna Cloud")


class UnifiedTaskCreateRequest(BaseModel):
    source_device: str
    skill_name: str
    intent: str
    params: Dict[str, Any]
    target_device: Optional[str] = None


class UnifiedTaskResultRequest(BaseModel):
    task_id: str
    success: bool
    message: str
    data: Dict[str, Any] = {}


@app.get("/")
def root():
    return {"message": "Krishna Cloud is running"}


@app.post("/register")
def register(req: DeviceRegisterRequest):
    register_device(req.device_id, {
        "device_name": req.device_name,
        "device_type": req.device_type,
        "status": req.status,
    })
    return {"success": True, "message": f"Registered {req.device_name}"}


@app.get("/devices")
def devices():
    return {"devices": list_devices()}


@app.post("/send_command")
def send_command(req: CommandRequest):
    push_command(req.target_device_id, {
        "source_device_id": req.source_device_id,
        "command_type": req.command_type,
        "payload": req.payload,
    })
    return {"success": True, "message": "Command queued"}


@app.get("/fetch_commands/{device_id}")
def fetch_commands(device_id: str):
    cmds = pop_commands(device_id)
    return {"commands": cmds}


@app.post("/push_result")
def push_command_result(req: CommandResultRequest):
    push_result(req.target_device_id, {
        "source_device_id": req.source_device_id,
        "command_type": req.command_type,
        "success": req.success,
        "message": req.message,
        "data": req.data or {},
    })
    return {"success": True, "message": "Result stored"}


@app.get("/fetch_results/{device_id}")
def fetch_results(device_id: str):
    results = pop_results(device_id)
    return {"results": results}


# ----------------------------
# Unified task system
# ----------------------------

@app.post("/unified/create_task")
def unified_create_task(req: UnifiedTaskCreateRequest):
    result = create_unified_task(
        source_device=req.source_device,
        skill_name=req.skill_name,
        intent=req.intent,
        params=req.params,
        target_device=req.target_device,
    )
    return result


@app.get("/unified/tasks")
def unified_list_tasks():
    return {"tasks": list_tasks()}


@app.get("/unified/tasks/{task_id}")
def unified_get_task(task_id: str):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"task": task}


@app.get("/unified/tasks_for_device/{device_id}")
def unified_tasks_for_device(device_id: str):
    return {"tasks": tasks_for_target_device(device_id)}


@app.post("/unified/tasks/{task_id}/status/{status}")
def unified_update_status(task_id: str, status: str):
    task = update_task_status(task_id, status)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True, "task": task}


@app.post("/unified/tasks/complete")
def unified_complete_task(req: UnifiedTaskResultRequest):
    task = complete_task(
        task_id=req.task_id,
        success=req.success,
        message=req.message,
        data=req.data,
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True, "task": task}

from pydantic import BaseModel
from typing import Optional, Dict, Any


class DeviceRegisterRequest(BaseModel):
    device_id: str
    device_name: str
    device_type: str
    status: str = "online"


class CommandRequest(BaseModel):
    source_device_id: str
    target_device_id: str
    command_type: str
    payload: Dict[str, Any]


class CommandResultRequest(BaseModel):
    source_device_id: str
    target_device_id: str
    command_type: str
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None


class CommandResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
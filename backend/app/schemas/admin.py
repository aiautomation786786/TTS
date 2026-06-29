from pydantic import BaseModel
from typing import Optional, List

class AdminDashboardStats(BaseModel):
    total_users: int
    total_generations: int
    total_characters: int
    total_clones: int
    total_voices: int
    active_users: int
    recent_generations: list
    recent_users: list

class EngineStatus(BaseModel):
    name: str
    available: bool
    version: Optional[str] = None
    details: dict

class SystemStatusResponse(BaseModel):
    engines: List[EngineStatus]
    gpu_available: bool
    gpu_info: Optional[str] = None
    storage_used: str
    database_size: str
    uptime: str

class SystemSettingUpdate(BaseModel):
    key: str
    value: str

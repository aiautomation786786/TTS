from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class TTSRequest(BaseModel):
    text: str = Field(..., max_length=50000)
    voice_id: int
    speed: float = Field(default=1.0, ge=0.5, le=2.0)
    pitch: str = Field(default="+0Hz")
    project_id: Optional[int] = None
    auto_translate: bool = Field(default=False)

class GenerationResponse(BaseModel):
    id: int
    user_id: int
    text: str
    voice_id: Optional[int] = None
    voice_name: Optional[str] = None
    voice_engine: Optional[str] = None
    audio_path: Optional[str] = None
    audio_url: Optional[str] = None
    audio_duration: Optional[float] = None
    char_count: int
    speed: float
    pitch: str
    file_size: Optional[int] = None
    file_format: str
    status: str
    mode: str = "short_form"
    total_chunks: int = 1
    completed_chunks: int = 0
    progress: float = 100.0
    error_message: Optional[str] = None
    failed_chunk_index: Optional[int] = None
    failed_chunk_text_preview: Optional[str] = None
    failed_engine_error: Optional[str] = None
    generation_time_seconds: Optional[float] = None
    project_id: Optional[int] = None
    batch_id: Optional[int] = None
    is_favorite: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class GenerationListResponse(BaseModel):
    generations: List[GenerationResponse]
    total: int
    page: int
    per_page: int

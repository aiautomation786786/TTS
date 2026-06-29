import os
from uuid import uuid4
from fastapi import UploadFile

def get_audio_duration(file_path: str) -> float | None:
    try:
        from mutagen import File
        audio = File(file_path)
        if audio is not None and audio.info is not None:
            return audio.info.length
        return None
    except Exception:
        return None

def get_file_size(file_path: str) -> int:
    try:
        return os.path.getsize(file_path)
    except OSError:
        return 0

def format_duration(seconds: float) -> str:
    if seconds is None:
        return "Unknown"
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes:02d}:{remaining_seconds:02d}"

def format_file_size(size_bytes: int) -> str:
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def validate_audio_file(file: UploadFile, settings) -> tuple[bool, str]:
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_AUDIO_EXTENSIONS:
        return False, f"Unsupported audio format: {ext}"
    return True, ""

def generate_output_filename(user_id: int, format: str = "mp3") -> str:
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{user_id}_{uuid4().hex[:8]}_{timestamp}.{format}"

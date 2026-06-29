import os
import shutil
import aiohttp
import asyncio
import tempfile
from uuid import uuid4
from fastapi import UploadFile
from sqlalchemy.orm import Session
from ..models.user import User
from ..models.voice import Voice
from ..config import get_settings

WORKER_URL = "http://127.0.0.1:8001"

class CloneService:
    def __init__(self):
        self._coqui_available = None
    
    async def check_availability(self) -> dict:
        result = {
            "coqui_installed": False,
            "model_available": False,
            "gpu_available": False,
            "gpu_info": None,
            "message": "",
            "diagnostics": {
                "package_status": "Worker Offline",
                "setup_instructions": "1. Run setup_coqui_env.bat\n2. Run run_coqui_worker.bat",
                "last_error": ""
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{WORKER_URL}/health", timeout=0.5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        result["coqui_installed"] = data.get("tts_installed", False)
                        result["model_available"] = data.get("model_loaded", False)
                        result["gpu_available"] = data.get("cuda_available", False)
                        result["diagnostics"]["package_status"] = "Worker Online"
                        result["diagnostics"]["python_version"] = data.get("python_version", "")
                        result["diagnostics"]["last_error"] = data.get("last_error", "")
                        
                        if result["model_available"]:
                            result["message"] = "Coqui XTTS Worker is operational."
                        else:
                            result["message"] = "Worker is online, but model failed to load."
                    else:
                        result["message"] = "Worker returned error status."
                        result["diagnostics"]["last_error"] = f"Status: {resp.status}"
        except Exception as e:
            result["message"] = "Coqui XTTS Worker is unreachable."
            result["diagnostics"]["last_error"] = str(e)
            
        return result
        
    async def clone_voice(self, db: Session, user: User, file: UploadFile, voice_name: str, description: str = "", language: str = "English", category: str = "cloned") -> Voice:
        settings = get_settings()
        ext = os.path.splitext(file.filename)[1].lower()
        
        if ext not in settings.ALLOWED_AUDIO_EXTENSIONS:
            raise ValueError(f"Unsupported audio format: {ext}")
            
        user_upload_dir = os.path.join(settings.UPLOAD_DIR, str(user.id))
        os.makedirs(user_upload_dir, exist_ok=True)
        sample_filename = f"clone_sample_{uuid4().hex[:8]}{ext}"
        sample_path = os.path.join(user_upload_dir, sample_filename)
        
        content = await file.read()
        if len(content) > settings.MAX_UPLOAD_SIZE:
            raise ValueError(f"File too large. Maximum: {settings.MAX_UPLOAD_SIZE // 1048576}MB")
            
        with open(sample_path, "wb") as f:
            f.write(content)
            
        try:
            from mutagen import File as MutagenFile
            audio_info = MutagenFile(sample_path)
            if audio_info and audio_info.info and audio_info.info.length < 3:
                os.remove(sample_path)
                raise ValueError("Audio sample too short. Minimum 3 seconds required.")
        except Exception as e:
            if "too short" in str(e):
                raise
                
        clone_id = f"clone_{user.id}_{uuid4().hex[:8]}"
        clone_dir = os.path.join(settings.CLONE_DIR, clone_id)
        os.makedirs(clone_dir, exist_ok=True)
        shutil.copy2(sample_path, os.path.join(clone_dir, f"reference{ext}"))
        
        from ..models.voice import Voice
        voice = Voice(
            name=voice_name,
            voice_id=clone_id,
            engine="coqui",
            language=language,
            locale=language[:2].lower() + "-" + language[:2].upper() if len(language) > 2 else "en-US",
            gender="unknown",
            style="cloned",
            category=category,
            quality_label="Cloned",
            is_builtin=False,
            is_active=True,
            is_cloned=True,
            sample_path=sample_path,
            user_id=user.id,
            description=description,
            tags='["Cloned", "Custom"]',
            use_case_tags='["Custom Voice"]',
            tone_tags='[]',
            recommended_for='[]',
            preview_status="working",
            generation_status="working"
        )
        db.add(voice)
        user.clone_count += 1
        db.commit()
        db.refresh(voice)
        return voice
        
    async def generate_with_clone(self, text: str, clone_voice_id: str, output_path: str, speed: float = 1.0, language: str = "en") -> str:
        settings = get_settings()
        clone_dir = os.path.join(settings.CLONE_DIR, clone_voice_id)
        
        reference_file = None
        for ext in settings.ALLOWED_AUDIO_EXTENSIONS:
            candidate = os.path.join(clone_dir, f"reference{ext}")
            if os.path.exists(candidate):
                reference_file = candidate
                break
                
        if not reference_file:
            raise FileNotFoundError("Reference audio not found for cloned voice.")
            
        # Send to worker
        try:
            with open(reference_file, "rb") as f:
                file_data = f.read()
                
            form_data = aiohttp.FormData()
            form_data.add_field("text", text)
            form_data.add_field("language", language)
            form_data.add_field("file", file_data, filename=os.path.basename(reference_file))

            # Set a very long timeout for CPU generation and initial model download
            timeout = aiohttp.ClientTimeout(total=900) 
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(f"{WORKER_URL}/clone", data=form_data) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        remote_output = data.get("output_path")
                        
                        # Fetch the resulting audio from worker
                        filename = os.path.basename(remote_output)
                        async with session.get(f"{WORKER_URL}/download/{filename}") as audio_resp:
                            if audio_resp.status == 200:
                                audio_content = await audio_resp.read()
                                with open(output_path, "wb") as out_f:
                                    out_f.write(audio_content)
                                return output_path
                            else:
                                raise RuntimeError("Worker succeeded but failed to serve audio file.")
                    else:
                        error_text = await resp.text()
                        raise RuntimeError(f"Clone worker returned error: {error_text}")
        except aiohttp.ClientConnectorError:
            raise RuntimeError("Clone Worker is offline. Please start the worker.")
        except asyncio.TimeoutError:
            raise RuntimeError("Clone Worker timed out during generation (CPU generation can be very slow).")
        except Exception as e:
            raise RuntimeError(f"Voice cloning generation failed: {str(e)}")
            
    async def delete_clone(self, db, voice_id: int, user_id: int) -> bool:
        from ..models.voice import Voice
        from ..models.user import User
        voice = db.query(Voice).filter(Voice.id == voice_id, Voice.user_id == user_id, Voice.is_cloned == True).first()
        if not voice:
            return False
            
        settings = get_settings()
        clone_dir = os.path.join(settings.CLONE_DIR, voice.voice_id)
        if os.path.exists(clone_dir):
            shutil.rmtree(clone_dir)
            
        if voice.sample_path and os.path.exists(voice.sample_path):
            os.remove(voice.sample_path)
            
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.clone_count > 0:
            user.clone_count -= 1
            
        db.delete(voice)
        db.commit()
        return True

clone_service = CloneService()

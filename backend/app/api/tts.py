import os
from fastapi import APIRouter, Depends, Query, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..core.dependencies import get_db, get_current_user
from ..schemas.generation import TTSRequest, GenerationResponse
from ..schemas.voice import VoiceListResponse
from ..services.tts_service import generate_speech, get_available_voices, get_supported_languages
from ..services.long_form_service import start_long_form_job, get_job, retry_failed_job

router = APIRouter(prefix="/api/tts", tags=["Text-to-Speech"])

@router.post("/generate", response_model=GenerationResponse)
async def generate(request: TTSRequest, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    generation = await generate_speech(db, current_user, request.text, request.voice_id, request.speed, request.pitch, request.project_id, request.auto_translate)
    # Add url
    gen_dict = generation.__dict__.copy()
    gen_dict["audio_url"] = f"/api/audio/outputs/{os.path.basename(generation.audio_path)}"
    return gen_dict

@router.get("/voices", response_model=VoiceListResponse)
async def list_tts_voices(engine: str = Query(None), db: Session = Depends(get_db)):
    voices = get_available_voices(db, engine)
    return {"voices": voices, "total": len(voices)}

@router.get("/languages")
async def list_languages(db: Session = Depends(get_db)):
    return get_supported_languages(db)

# --- Long Form Routes ---

@router.post("/long-form/start", response_model=GenerationResponse)
async def start_long_form(request: TTSRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    try:
        job = await start_long_form_job(background_tasks, db, current_user, request.text, request.voice_id, request.speed, request.pitch, request.project_id, request.auto_translate)
        return job
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/long-form/{job_id}/status", response_model=GenerationResponse)
async def get_long_form_status(job_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    job = get_job(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    # We serialize audio_url if completed
    gen_dict = job.__dict__.copy()
    if job.status == "completed" and job.audio_path:
        gen_dict["audio_url"] = f"/api/audio/outputs/long_form/{os.path.basename(job.audio_path)}"
        
    return gen_dict

@router.post("/long-form/{job_id}/retry")
async def retry_long_form(job_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    job = get_job(db, job_id, current_user.id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    try:
        success = await retry_failed_job(background_tasks, db, job)
        return {"success": success}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

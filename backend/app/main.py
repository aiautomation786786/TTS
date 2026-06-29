from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import get_settings
from .database import init_db
from .api import auth, tts, voices, history, users, admin, presets, notifications

settings = get_settings()

app = FastAPI(
    title="VoxForge API",
    description="Premium Text-to-Speech SaaS API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(tts.router)
app.include_router(voices.router)
app.include_router(history.router)
app.include_router(admin.router)

app.include_router(presets.router)
app.include_router(notifications.router)

@app.on_event("startup")
async def startup_event():
    init_db()

# Ensure directories exist before mounting
import os
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PREVIEW_DIR, exist_ok=True)

app.mount("/api/audio/outputs", StaticFiles(directory=settings.OUTPUT_DIR), name="outputs")
app.mount("/api/audio/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.mount("/api/audio/previews", StaticFiles(directory=settings.PREVIEW_DIR), name="previews")

@app.get("/")
def read_root():
    return {"app": "VoxForge", "status": "running"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

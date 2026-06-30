import os
import sys
import subprocess
import json
from sqlalchemy.orm import Session
from app.models.voice import Voice
from app.services.tts_engines import engine_manager

CODE_TO_LANGUAGE = {
    "en": "English", "ar": "Arabic", "es": "Spanish", "fr": "French",
    "de": "German", "it": "Italian", "pt": "Portuguese", "ru": "Russian",
    "zh": "Chinese", "ja": "Japanese", "ko": "Korean", "hi": "Hindi",
    "tr": "Turkish", "pl": "Polish", "nl": "Dutch", "sv": "Swedish",
    "ur": "Urdu", "id": "Indonesian", "th": "Thai", "vi": "Vietnamese",
    "ta": "Tamil", "te": "Telugu", "bn": "Bengali", "ml": "Malayalam",
    "mr": "Marathi", "gu": "Gujarati", "kn": "Kannada", "fa": "Persian",
    "he": "Hebrew", "el": "Greek", "fi": "Finnish", "da": "Danish",
    "no": "Norwegian", "cs": "Czech", "hu": "Hungarian", "ro": "Romanian",
    "sk": "Slovak", "uk": "Ukrainian", "bg": "Bulgarian", "sr": "Serbian",
    "hr": "Croatian", "ms": "Malay", "sw": "Swahili", "am": "Amharic",
    "af": "Afrikaans", "zu": "Zulu", "sl": "Slovenian", "lt": "Lithuanian",
    "lv": "Latvian", "et": "Estonian", "is": "Icelandic", "cy": "Welsh",
    "ga": "Irish", "mt": "Maltese", "sq": "Albanian", "mk": "Macedonian",
    "ka": "Georgian", "hy": "Armenian", "az": "Azerbaijani", "kk": "Kazakh",
    "uz": "Uzbek", "mn": "Mongolian", "ne": "Nepali", "si": "Sinhala",
    "km": "Khmer", "lo": "Lao", "my": "Burmese", "tl": "Filipino"
}

LANGUAGE_TO_CODE = {v: k for k, v in CODE_TO_LANGUAGE.items()}

# Comprehensive Professional Tag Map
VOICE_METADATA_MAP = {
    # English
    "en-US-AriaNeural": {
        "use_cases": ["YouTube", "Social Media", "Explainer", "Commercial"],
        "tones": ["Energetic", "Warm", "Engaging", "Professional"],
        "recommended": ["YouTube", "Commercial"]
    },
    "en-US-GuyNeural": {
        "use_cases": ["Documentary", "News", "Professional Corporate", "Audiobook"],
        "tones": ["Deep", "Serious", "Professional", "Neutral"],
        "recommended": ["Documentary", "News"]
    },
    "en-US-JennyNeural": {
        "use_cases": ["Storytelling", "Podcast", "Audiobook", "Meditation"],
        "tones": ["Warm", "Calm", "Emotional", "Clear"],
        "recommended": ["Storytelling", "Audiobook"]
    },
    "en-US-ChristopherNeural": {
        "use_cases": ["Trailer", "Cinematic", "Horror", "Drama"],
        "tones": ["Deep", "Suspense", "Dramatic", "Dark"],
        "recommended": ["Trailer", "Horror"]
    },
    "en-US-EricNeural": {
        "use_cases": ["Gaming", "Trailer", "Motivation", "YouTube"],
        "tones": ["Energetic", "Deep", "Dramatic", "Engaging"],
        "recommended": ["Gaming", "Motivation"]
    },
    "en-US-MichelleNeural": {
        "use_cases": ["Education", "Explainer", "Professional Corporate"],
        "tones": ["Clear", "Professional", "Warm", "Formal"],
        "recommended": ["Education", "Professional Corporate"]
    },
    "en-US-AnaNeural": {
        "use_cases": ["Kids", "Storytelling", "Meditation"],
        "tones": ["Soft", "Warm", "Peaceful", "Calm"],
        "recommended": ["Kids", "Meditation"]
    },
    "en-US-RogerNeural": {
        "use_cases": ["News", "Documentary", "Professional Corporate"],
        "tones": ["Neutral", "Professional", "Clear", "Serious"],
        "recommended": ["News", "Documentary"]
    },
    "en-US-SteffanNeural": {
        "use_cases": ["Horror", "Drama", "Suspense"],
        "tones": ["Deep", "Dark", "Mystery"],
        "recommended": ["Horror", "Drama"]
    },
    "en-US-BrianNeural": {
        "use_cases": ["YouTube", "Gaming", "Explainer"],
        "tones": ["Energetic", "Engaging", "Clear"],
        "recommended": ["YouTube"]
    },
    
    # Arabic
    "ar-SA-HamedNeural": {
        "use_cases": ["News", "Documentary", "Professional Corporate"],
        "tones": ["Serious", "Professional", "Deep", "Clear"],
        "recommended": ["News", "Documentary"]
    },
    "ar-SA-ZariyahNeural": {
        "use_cases": ["Storytelling", "Audiobook", "Commercial"],
        "tones": ["Warm", "Expressive", "Professional"],
        "recommended": ["Storytelling", "Commercial"]
    },
    "ar-AE-FatimaNeural": {
        "use_cases": ["Education", "News", "Professional Corporate"],
        "tones": ["Clear", "Neutral", "Formal"],
        "recommended": ["News", "Education"]
    },
    "ar-AE-HamdanNeural": {
        "use_cases": ["Documentary", "Trailer", "Cinematic"],
        "tones": ["Deep", "Serious", "Dramatic"],
        "recommended": ["Documentary", "Cinematic"]
    },

    # Spanish
    "es-ES-AlvaroNeural": {
        "use_cases": ["Documentary", "News", "Professional Corporate"],
        "tones": ["Deep", "Professional", "Clear"],
        "recommended": ["Documentary", "News"]
    },
    "es-ES-ElviraNeural": {
        "use_cases": ["Storytelling", "Audiobook", "Meditation"],
        "tones": ["Warm", "Calm", "Expressive"],
        "recommended": ["Storytelling", "Audiobook"]
    },
    "es-MX-DaliaNeural": {
        "use_cases": ["YouTube", "Commercial", "Social Media"],
        "tones": ["Energetic", "Engaging", "Bright"],
        "recommended": ["YouTube", "Commercial"]
    },
    "es-MX-JorgeNeural": {
        "use_cases": ["Gaming", "Trailer", "Horror"],
        "tones": ["Deep", "Dramatic", "Suspense"],
        "recommended": ["Gaming", "Horror"]
    },
    
    # French
    "fr-FR-HenriNeural": {
        "use_cases": ["Documentary", "Professional Corporate"],
        "tones": ["Deep", "Formal", "Serious"],
        "recommended": ["Documentary"]
    },
    "fr-FR-DeniseNeural": {
        "use_cases": ["Audiobook", "Storytelling", "Commercial"],
        "tones": ["Warm", "Expressive", "Professional"],
        "recommended": ["Audiobook"]
    },
    
    # German
    "de-DE-ConradNeural": {
        "use_cases": ["Documentary", "News", "Professional Corporate"],
        "tones": ["Deep", "Serious", "Clear"],
        "recommended": ["Documentary"]
    },
    "de-DE-KatjaNeural": {
        "use_cases": ["YouTube", "Commercial", "Explainer"],
        "tones": ["Energetic", "Engaging", "Professional"],
        "recommended": ["YouTube"]
    }
}

def generate_fallback_tags(gender: str):
    if gender == "Male":
        return {
            "use_cases": ["Professional Corporate", "Documentary", "News"],
            "tones": ["Deep", "Professional", "Clear"],
            "recommended": ["Professional Corporate"]
        }
    else:
        return {
            "use_cases": ["Audiobook", "Storytelling", "Education"],
            "tones": ["Warm", "Professional", "Clear"],
            "recommended": ["Audiobook"]
        }

def get_real_edge_voices():
    voices = []
    try:
        out = subprocess.check_output([sys.executable, '-m', 'edge_tts', '--list-voices']).decode('utf-8', 'ignore')
        for line in out.splitlines():
            if not line.strip(): continue
            parts = line.split()
            if not parts: continue
            voice_id = parts[0]
            if voice_id == "Name" or voice_id.startswith("---"): continue
            gender = "Male" if "Male" in line else "Female" if "Female" in line else "Unknown"
            
            locale = voice_id.split('-')[0] + "-" + voice_id.split('-')[1] if '-' in voice_id else voice_id
            lang_prefix = voice_id.split('-')[0].lower() if '-' in voice_id else ""
            
            language = CODE_TO_LANGUAGE.get(lang_prefix, lang_prefix.upper())
                
            name_part = voice_id.split('-')[-1].replace('Neural', '')
            if name_part != 'Multilingual':
                name_part = name_part.replace('Multilingual', '')
            if not name_part or name_part.lower() == "unknown":
                name_part = f"{language} Voice"
            
            if 'Multilingual' in voice_id and any(v['name'] == name_part for v in voices):
                continue
                
            metadata = VOICE_METADATA_MAP.get(voice_id, generate_fallback_tags(gender))
                
            voices.append({
                "name": name_part,
                "voice_id": voice_id,
                "engine": "edge-tts",
                "language": language,
                "locale": locale,
                "gender": gender,
                "style": "professional",
                "category": "neural",
                "quality_label": "Premium",
                "accent": locale,
                "use_case_tags": json.dumps(metadata["use_cases"]),
                "tone_tags": json.dumps(metadata["tones"]),
                "recommended_for": json.dumps(metadata["recommended"]),
                "preview_status": "pending",
                "generation_status": "pending",
                "tags": json.dumps(["Premium", language, "Professional", gender]),
                "description": f"Premium {gender.lower()} {language} voice."
            })
    except Exception as e:
        print("Failed to run edge-tts:", str(e))
        
    # Group by language and limit to 30 premium voices
    grouped = {}
    for v in voices:
        grouped.setdefault(v["language"], []).append(v)
        
    final_voices = []
    for lang, lang_voices in grouped.items():
        final_voices.extend(lang_voices)
        
    return final_voices

def get_real_piper_voices():
    # We need to run this async or directly load from disk since PiperTTSEngine get_voices is async
    # A simple way without async context is to manually read the models folder like get_voices does.
    voices = []
    model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'piper'))
    if not os.path.exists(model_dir):
        return voices
        
    for file in os.listdir(model_dir):
        if file.endswith(".onnx"):
            voice_id = file[:-5]
            json_file = os.path.join(model_dir, f"{voice_id}.onnx.json")
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        lang = data.get("language", {}).get("name_english", "English")
                        locale = f"{data.get('language', {}).get('code', 'en')}-{data.get('language', {}).get('region', 'US')}"
                        quality = data.get("quality", "standard")
                        
                        quality_label = "Premium" if quality == "high" else "Standard"
                        if quality == "medium":
                            quality_label = "High"
                        
                        parts = voice_id.split("-")
                        name = parts[1].capitalize() if len(parts) > 1 else voice_id.capitalize()
                        
                        voices.append({
                            "name": f"{name} ({quality_label})",
                            "voice_id": voice_id,
                            "engine": "piper",
                            "language": lang,
                            "locale": locale,
                            "gender": "Unknown",
                            "style": "local",
                            "category": "offline",
                            "quality_label": quality_label,
                            "accent": locale,
                            "use_case_tags": json.dumps(["Offline", "Fast"]),
                            "tone_tags": json.dumps([]),
                            "recommended_for": json.dumps([]),
                            "preview_status": "working",
                            "generation_status": "working",
                            "tags": json.dumps(["Local", "Offline", lang]),
                            "description": f"Local Piper TTS voice ({quality} quality)."
                        })
                except Exception:
                    pass
    return voices

def get_coqui_voices():
    voices = []
    json_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'coqui_speakers.json'))
    if os.path.exists(json_path):
        try:
            import json
            with open(json_path, 'r', encoding='utf-8') as f:
                spks = json.load(f)
            for spk in spks:
                voices.append({
                    "name": spk.replace("_", " ").title(),
                    "voice_id": spk,
                    "engine": "coqui",
                    "language": "English",
                    "locale": "en-US",
                    "gender": "Unknown",
                    "style": "professional",
                    "category": "neural",
                    "quality_label": "Premium",
                    "accent": "en-US",
                    "use_case_tags": json.dumps(["Cloning", "Expressive"]),
                    "tone_tags": json.dumps(["Natural"]),
                    "recommended_for": json.dumps(["Voice Cloning"]),
                    "preview_status": "pending",
                    "generation_status": "pending",
                    "tags": json.dumps(["Premium", "Cloning"]),
                    "description": "Premium built-in XTTS voice."
                })
        except Exception:
            pass
    return voices

def seed_or_repair_voices(db: Session):
    print("Running dynamic voice validation and tagging system...")
    
    curated_voices = get_real_edge_voices()
    piper_voices = get_real_piper_voices()
    coqui_voices = get_coqui_voices()
    
    all_voices = curated_voices + piper_voices + coqui_voices
    valid_ids = set([v["voice_id"] for v in all_voices])
    
    inserted = 0
    updated = 0
    
    existing_voices = db.query(Voice).filter(Voice.is_builtin == True).all()
    existing_map = {v.voice_id: v for v in existing_voices}
    
    for curated in all_voices:
        if curated["voice_id"] in existing_map:
            v = existing_map[curated["voice_id"]]
            needs_update = False
            for k, val in curated.items():
                if getattr(v, k) != val:
                    setattr(v, k, val)
                    needs_update = True
                    
            if not v.is_active:
                v.is_active = True
                needs_update = True
                
            if needs_update:
                updated += 1
        else:
            new_voice = Voice(
                **curated,
                is_builtin=True,
                is_active=True,
                is_cloned=False
            )
            db.add(new_voice)
            inserted += 1
            
    # Delete if engine removed it
    for v in existing_voices:
        if v.voice_id not in valid_ids:
            print(f"[WARN] Deleting {v.name}: engine missing {v.voice_id}")
            db.delete(v)
            updated += 1
            
    db.commit()
    print(f"Voice Sync: Inserted {inserted}, Updated {updated} voices. Total active: {len(all_voices)}")

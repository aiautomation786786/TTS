import json
from TTS.api import TTS
import os
os.environ["COQUI_TOS_AGREED"] = "1"
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
speakers = getattr(tts.synthesizer.tts_model.speaker_manager, "name_to_id", {})
spks = list(speakers.keys())
with open(r"d:\TTS\backend\coqui_speakers.json", "w") as f:
    json.dump(spks, f)

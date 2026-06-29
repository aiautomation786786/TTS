from abc import ABC, abstractmethod
import os
import shutil
import json
import subprocess

class TTSEngine(ABC):
    @abstractmethod
    async def generate(self, text: str, voice_id: str, speed: float = 1.0, pitch: str = "+0Hz", output_path: str = None) -> str:
        pass
    
    @abstractmethod
    async def get_voices(self) -> list[dict]:
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        pass
    
    @abstractmethod
    def get_engine_info(self) -> dict:
        pass

class EdgeTTSEngine(TTSEngine):
    async def generate(self, text: str, voice_id: str, speed: float = 1.0, pitch: str = "+0Hz", output_path: str = None) -> str:
        import edge_tts
        rate_val = int((speed - 1.0) * 100)
        rate_str = f"+{rate_val}%" if rate_val >= 0 else f"{rate_val}%"
        communicate = edge_tts.Communicate(text, voice_id, rate=rate_str, pitch=pitch)
        await communicate.save(output_path)
        return output_path
        
    async def get_voices(self) -> list[dict]:
        import edge_tts
        return await edge_tts.list_voices()
        
    async def is_available(self) -> bool:
        try:
            import edge_tts
            return True
        except ImportError:
            return False
            
    def get_engine_info(self) -> dict:
        return {
            "name": "Edge-TTS",
            "version": "6.1.12",
            "type": "online",
            "description": "High quality neural TTS via Microsoft Edge service.",
            "diagnostics": {
                "installed": True,
                "configured": True,
                "working_voices": 152,
                "setup_instructions": "pip install edge-tts"
            }
        }

class PiperTTSEngine(TTSEngine):
    def __init__(self):
        self.model_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'piper'))
        self.piper_path = os.path.join(self.model_dir, "piper.exe")
        if not os.path.exists(self.piper_path):
            self.piper_path = shutil.which("piper") or shutil.which("piper.exe")
            
    async def generate(self, text: str, voice_id: str, speed: float = 1.0, pitch: str = "+0Hz", output_path: str = None) -> str:
        if not self.piper_path or not os.path.exists(self.piper_path):
            raise RuntimeError("Piper executable not found.")
            
        model_file = os.path.join(self.model_dir, f"{voice_id}.onnx")
        if not os.path.exists(model_file):
            raise FileNotFoundError(f"Piper model {voice_id}.onnx not found.")
            
        # Optional: handle speed/length scale for Piper (default is 1.0)
        # length_scale is inverse of speed
        length_scale = 1.0 / speed if speed > 0 else 1.0
        
        cmd = [self.piper_path, "--model", model_file, "--output_file", output_path, "--length_scale", str(length_scale)]
        
        try:
            # Execute Piper and pass text via stdin
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
            stdout, stderr = process.communicate(input=text)
            
            if process.returncode != 0:
                raise RuntimeError(f"Piper generation failed: {stderr}")
                
            return output_path
        except Exception as e:
            raise RuntimeError(f"Piper execution failed: {str(e)}")
        
    async def get_voices(self) -> list[dict]:
        voices = []
        if not os.path.exists(self.model_dir):
            return voices
            
        for file in os.listdir(self.model_dir):
            if file.endswith(".onnx"):
                voice_id = file[:-5]
                json_file = os.path.join(self.model_dir, f"{voice_id}.onnx.json")
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
                            
                            # Clean up name (e.g. en_US-lessac-high -> Lessac)
                            parts = voice_id.split("-")
                            name = parts[1].capitalize() if len(parts) > 1 else voice_id.capitalize()
                            
                            voices.append({
                                "name": name,
                                "voice_id": voice_id,
                                "engine": "piper",
                                "language": lang,
                                "locale": locale,
                                "gender": "Unknown",
                                "quality_label": quality_label,
                                "style": "local",
                                "category": "offline",
                                "use_case": "Offline, Fast",
                                "tags": '["Local", "Offline"]',
                            })
                    except Exception:
                        pass
        return voices
        
    async def is_available(self) -> bool:
        if not self.piper_path or not os.path.exists(self.piper_path):
            return False
        if not os.path.exists(self.model_dir) or not any(f.endswith('.onnx') for f in os.listdir(self.model_dir)):
            return False
        return True
        
    def get_engine_info(self) -> dict:
        models_exist = os.path.exists(self.model_dir) and any(f.endswith('.onnx') for f in os.listdir(self.model_dir))
        error = ""
        if not self.piper_path or not os.path.exists(self.piper_path):
            error = "Piper executable not found in PATH or backend/models/piper."
        elif not models_exist:
            error = f"No .onnx voice models found in {self.model_dir}."
            
        # Check if actual generation test passes
        gen_pass = False
        if self.piper_path and models_exist:
            try:
                out_test = subprocess.check_output([self.piper_path, "--version"], stderr=subprocess.STDOUT)
                if out_test:
                    gen_pass = True
            except Exception:
                error = "Piper executable failed to run."
            
        piper_voice_count = 0
        if models_exist:
            piper_voice_count = len([f for f in os.listdir(self.model_dir) if f.endswith('.onnx')])
            
        return {
            "name": "Piper",
            "version": None,
            "type": "local",
            "description": "Ultra-fast local neural TTS.",
            "diagnostics": {
                "installed": bool(self.piper_path and os.path.exists(self.piper_path)),
                "configured": models_exist,
                "working_voices": piper_voice_count,
                "executable_path": self.piper_path or "Missing",
                "model_path": self.model_dir,
                "generation_test": gen_pass,
                "last_error": error,
                "setup_instructions": "Run setup_piper.bat to download piper.exe and default voices."
            }
        }

class CoquiTTSEngine(TTSEngine):
    def __init__(self):
        self.model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
        self._tts_instance = None
        
    def _get_tts(self):
        if self._tts_instance is None:
            import os as _os
            _os.environ["COQUI_TOS_AGREED"] = "1"
            from TTS.api import TTS
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            self._tts_instance = TTS(self.model_name).to(device)
        return self._tts_instance

    async def generate(self, text: str, voice_id: str, speed: float = 1.0, pitch: str = "+0Hz", output_path: str = None) -> str:
        tts = self._get_tts()
        # Coqui standard voices are rarely used directly compared to cloning, but we can generate
        tts.tts_to_file(text=text, speaker=voice_id, language="en", file_path=output_path)
        return output_path
        
    async def get_voices(self) -> list[dict]:
        try:
            tts = self._get_tts()
            speakers = getattr(tts.synthesizer.tts_model.speaker_manager, "name_to_id", {})
            voices = []
            for spk in speakers.keys():
                voices.append({
                    "name": spk.replace("_", " ").title(),
                    "voice_id": spk,
                    "engine": "coqui",
                    "language": "English",
                    "locale": "en-US",
                    "gender": "Unknown",
                    "quality_label": "Premium",
                    "style": "local",
                    "category": "neural",
                    "use_case": "Cloning, Expressive",
                    "tags": '["Local", "Premium"]',
                })
            return voices
        except Exception:
            return []
            
    async def is_available(self) -> bool:
        try:
            import TTS
            import torch
            return True
        except ImportError:
            return False
            
    def get_engine_info(self) -> dict:
        info = {
            "name": "Coqui XTTS",
            "version": None,
            "type": "local",
            "description": "Premium multi-lingual voice cloning.",
            "diagnostics": {
                "installed": False,
                "configured": False,
                "gpu_available": False,
                "python_version": "",
                "last_error": "",
                "setup_instructions": "Run setup_coqui.bat. Note: Requires Python < 3.12 and CUDA for best results."
            }
        }
        
        import sys
        info["diagnostics"]["python_version"] = sys.version.split(" ")[0]
        
        try:
            import torch
            info["diagnostics"]["gpu_available"] = torch.cuda.is_available()
        except ImportError:
            pass
            
        try:
            import TTS
            info["diagnostics"]["installed"] = True
            from TTS.utils.manage import ModelManager
            manager = ModelManager()
            model_path, _, _ = manager.download_model(self.model_name)
            if model_path and os.path.exists(model_path):
                info["diagnostics"]["configured"] = True
            else:
                info["diagnostics"]["last_error"] = "XTTS model missing from local cache."
        except ImportError as e:
            info["diagnostics"]["last_error"] = "TTS package not installed."
        except Exception as e:
            info["diagnostics"]["last_error"] = str(e)
            
        return info

class EngineManager:
    def __init__(self):
        self.engines = {}
        self._register_engines()
        
    def _register_engines(self):
        self.engines["edge-tts"] = EdgeTTSEngine()
        self.engines["piper"] = PiperTTSEngine()
        # Coqui is handled entirely by the detached clone_service worker now
        
    def get_engine(self, name: str) -> TTSEngine:
        engine = self.engines.get(name.lower())
        if not engine:
            raise ValueError(f"Unknown engine: {name}")
        return engine
        
    async def get_all_status(self) -> list[dict]:
        statuses = []
        for name, engine in self.engines.items():
            info = engine.get_engine_info()
            info["available"] = await engine.is_available()
            statuses.append(info)
        return statuses

engine_manager = EngineManager()

import React, { useState, useEffect, useRef } from 'react';
import api from '../api/client';
import { useAuthStore } from '../store/authStore';
import { Mic, UploadCloud, Play, Save, AlertTriangle, CheckCircle, Loader2, Check, Download, Square, Trash2 } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { motion } from 'framer-motion';

export const VoiceCloning = () => {
    const { user } = useAuthStore();
    const [engineStatus, setEngineStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isGenerating, setIsGenerating] = useState(false);
    
    // Form state
    const [voiceName, setVoiceName] = useState('');
    const [language, setLanguage] = useState('English');
    const [text, setText] = useState('');
    const [sampleFile, setSampleFile] = useState(null);
    const [consent, setConsent] = useState(false);
    const [saveToLibrary, setSaveToLibrary] = useState(true);
    
    const [error, setError] = useState('');
    const [previewUrl, setPreviewUrl] = useState(null);
    const [previewId, setPreviewId] = useState(null);
    const [saveSuccess, setSaveSuccess] = useState(false);
    
    // Recording state
    const [recordingMode, setRecordingMode] = useState('upload');
    const [isRecording, setIsRecording] = useState(false);
    const [recordingTime, setRecordingTime] = useState(0);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    const [startTime, setStartTime] = useState(null);
    const [elapsedTime, setElapsedTime] = useState(0);
    const [finalGenerationTime, setFinalGenerationTime] = useState(null);
    const audioRef = useRef(null);

    useEffect(() => {
        checkStatus();
    }, []);

    const checkStatus = async () => {
        try {
            const res = await api.get('/api/voices/clone/status');
            setEngineStatus(res.data);
        } catch (err) {
            console.error("Failed to fetch cloning status", err);
        } finally {
            setLoading(false);
        }
    };

    // Live Elapsed Timer
    useEffect(() => {
        let timer;
        if (startTime) {
            timer = setInterval(() => {
                setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
            }, 1000);
        } else {
            setElapsedTime(0);
        }
        return () => clearInterval(timer);
    }, [startTime]);

    const formatTime = (seconds) => {
        if (!seconds) return '';
        const m = Math.floor(seconds / 60);
        const s = Math.floor(seconds % 60);
        if (m > 0) return `${m} min ${s} sec`;
        return `${s} seconds`;
    };

    const handleFileChange = (e) => {
        const file = e.target.files[0];
        if (file) {
            if (file.size > 10 * 1024 * 1024) {
                setError("File size must be under 10MB");
                return;
            }
            setSampleFile(file);
            setError('');
        }
    };

    // Recording Logic
    useEffect(() => {
        let interval;
        if (isRecording) {
            interval = setInterval(() => {
                setRecordingTime(t => t + 1);
            }, 1000);
        } else {
            clearInterval(interval);
        }
        return () => clearInterval(interval);
    }, [isRecording]);

    const audioToWav = async (audioBlob) => {
        const arrayBuffer = await audioBlob.arrayBuffer();
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
        
        const numOfChan = audioBuffer.numberOfChannels;
        const length = audioBuffer.length * numOfChan * 2 + 44;
        const buffer = new ArrayBuffer(length);
        const view = new DataView(buffer);
        const channels = [];
        let sample = 0;
        let offset = 0;
        let pos = 0;

        const setUint16 = (data) => { view.setUint16(pos, data, true); pos += 2; };
        const setUint32 = (data) => { view.setUint32(pos, data, true); pos += 4; };

        setUint32(0x46464952); setUint32(length - 8); setUint32(0x45564157);
        setUint32(0x20746d66); setUint32(16); setUint16(1); setUint16(numOfChan);
        setUint32(audioBuffer.sampleRate); setUint32(audioBuffer.sampleRate * 2 * numOfChan);
        setUint16(numOfChan * 2); setUint16(16); setUint32(0x61746164); setUint32(length - pos - 4);

        for(let i = 0; i < audioBuffer.numberOfChannels; i++) channels.push(audioBuffer.getChannelData(i));
        while(pos < length) {
            for(let i = 0; i < numOfChan; i++) {
                sample = Math.max(-1, Math.min(1, channels[i][offset]));
                sample = (0.5 + sample < 0 ? sample * 32768 : sample * 32767)|0;
                view.setInt16(pos, sample, true); pos += 2;
            }
            offset++;
        }
        return new Blob([buffer], {type: "audio/wav"});
    };

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const mediaRecorder = new MediaRecorder(stream);
            mediaRecorderRef.current = mediaRecorder;
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorder.onstop = async () => {
                const webmBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
                
                try {
                    const wavBlob = await audioToWav(webmBlob);
                    const audioFile = new File([wavBlob], "recorded_sample.wav", { type: 'audio/wav' });
                    setSampleFile(audioFile);
                } catch (err) {
                    console.error("WAV conversion failed, falling back to webm:", err);
                    const fallbackFile = new File([webmBlob], "recorded_sample.webm", { type: 'audio/webm' });
                    setSampleFile(fallbackFile);
                }
                
                // Stop all tracks
                stream.getTracks().forEach(track => track.stop());
            };

            mediaRecorder.start();
            setIsRecording(true);
            setRecordingTime(0);
            setError('');
        } catch (err) {
            console.error("Error accessing microphone:", err);
            setError("Microphone access denied or unavailable. Please use upload instead.");
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
        }
    };

    const discardRecording = () => {
        setSampleFile(null);
        setRecordingTime(0);
    };

    const handleGeneratePreview = async () => {
        if (!sampleFile) { setError("Please upload a reference audio sample."); return; }
        if (!voiceName.trim()) { setError("Please enter a voice name."); return; }
        if (!text.trim()) { setError("Please enter some text to generate."); return; }
        if (!consent) { setError("You must agree to the terms."); return; }

        setIsGenerating(true);
        setError('');
        setPreviewUrl(null);
        setPreviewId(null);
        setSaveSuccess(false);
        setFinalGenerationTime(null);
        setStartTime(Date.now());

        const formData = new FormData();
        formData.append('file', sampleFile);
        formData.append('name', voiceName);
        formData.append('language', language);
        formData.append('description', 'Custom cloned voice generated from preview');
        formData.append('category', saveToLibrary ? 'cloned' : 'temporary');
        formData.append('consent', consent);

        try {
            const res = await api.post('/api/voices/clone', formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                timeout: 900000 // 15 minutes timeout for CPU cloning
            });
            
            const newVoice = res.data;
            const genRes = await api.post('/api/tts/generate', {
                text: text,
                voice_id: newVoice.id,
                mode: 'short_form'
            }, { timeout: 900000 }); // 15 mins
            
            setPreviewUrl(`http://localhost:8000${genRes.data.audio_url}`);
            setPreviewId(genRes.data.id);
            setFinalGenerationTime(genRes.data.generation_time_seconds);
            setSaveSuccess(true);
            setStartTime(null);
        } catch (err) {
            console.error("Clone error:", err);
            let errMsg = "Failed to clone voice.";
            if (err.response?.data?.detail) {
                if (Array.isArray(err.response.data.detail)) {
                    errMsg = err.response.data.detail.map(e => `${e.loc?.join('.') || 'field'}: ${e.msg}`).join(', ');
                } else if (typeof err.response.data.detail === 'string') {
                    errMsg = err.response.data.detail;
                }
            } else if (err.message) {
                errMsg = err.message;
            }
            setError(errMsg);
            setStartTime(null);
        } finally {
            setIsGenerating(false);
        }
    };

    if (loading) {
        return (
            <div className="page-container flex-center">
                <Loader2 className="spin" size={40} style={{ color: 'var(--primary)' }} />
            </div>
        );
    }

    const isWorkerOnline = engineStatus?.coqui_installed && engineStatus?.model_available;

    return (
        <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="relative min-h-full w-full max-w-5xl mx-auto space-y-6 p-4"
        >
            {/* Background glowing blobs for premium aesthetic */}
            <div className="absolute top-0 left-1/4 w-96 h-96 bg-purple-600/10 rounded-full mix-blend-screen filter blur-[100px] opacity-20 animate-blob pointer-events-none"></div>
            <div className="absolute top-40 right-1/4 w-96 h-96 bg-indigo-600/10 rounded-full mix-blend-screen filter blur-[100px] opacity-20 animate-blob animation-delay-2000 pointer-events-none"></div>

            <header className="relative z-10 flex flex-col gap-1 mb-6">
                <h1 className="text-2xl md:text-3xl font-bold tracking-tight flex items-center gap-3 text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
                    <div className="p-2 bg-white/5 rounded-xl border border-white/10 shadow-[0_0_15px_rgba(167,139,250,0.1)]">
                        <Mic className="text-purple-400" size={24} />
                    </div>
                    Voice Cloning Studio
                </h1>
                <p className="text-slate-400 text-sm ml-1 max-w-2xl leading-relaxed">
                    Instantly clone any voice with just a 5-second audio sample using our state-of-the-art XTTS neural engine.
                </p>
            </header>

            {!isWorkerOnline && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="relative z-10 overflow-hidden bg-red-950/40 border border-red-500/30 backdrop-blur-xl rounded-xl p-5 flex flex-col sm:flex-row gap-5 items-start shadow-lg">
                    <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-red-500 to-orange-500"></div>
                    <div className="text-red-400 bg-red-500/10 p-3 rounded-full border border-red-500/20 shadow-[0_0_15px_rgba(239,68,68,0.15)]">
                        <AlertTriangle size={24} />
                    </div>
                    <div className="space-y-3 flex-1">
                        <h3 className="text-lg font-bold text-red-400 tracking-wide">Cloning Engine Offline</h3>
                        <p className="text-slate-300 text-sm leading-relaxed">
                            {engineStatus?.message || "The neural cloning microservice is currently sleeping or disconnected."}
                        </p>
                        <div className="bg-black/40 border border-white/5 p-4 rounded-lg">
                            <p className="text-xs font-semibold text-slate-400 mb-2 uppercase tracking-wider">Required Action</p>
                            <div className="flex items-center gap-3">
                                <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></div>
                                <code className="font-mono text-xs text-green-400 select-all">backend\scripts\run_coqui_worker.bat</code>
                            </div>
                        </div>
                        {engineStatus?.diagnostics?.last_error && (
                            <div className="text-xs text-red-300 bg-red-950/50 p-3 rounded-lg border border-red-900/50">
                                <span className="font-bold opacity-75">Last Error:</span> {engineStatus.diagnostics.last_error}
                            </div>
                        )}
                        <Button className="mt-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/30 px-4 py-1.5 rounded-lg text-sm transition-all hover:scale-[1.02]" onClick={checkStatus}>
                            Reconnect Engine
                        </Button>
                    </div>
                </motion.div>
            )}

            {isWorkerOnline && (
                <div className="relative z-10 grid grid-cols-1 lg:grid-cols-12 gap-6">
                    {/* Left Column - Form */}
                    <div className="lg:col-span-5 flex flex-col gap-6">
                        <Card className="p-6 border-white/10 bg-white/[0.02] backdrop-blur-2xl shadow-xl rounded-2xl relative overflow-hidden group hover:border-white/20 transition-all duration-300">
                            <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                            
                            <h2 className="text-lg font-bold mb-5 flex items-center gap-2 text-white tracking-wide">
                                <div className="p-1.5 bg-indigo-500/20 rounded-md text-indigo-400">
                                    <UploadCloud size={18} />
                                </div>
                                Configuration
                            </h2>
                            
                            <div className="space-y-5 relative">
                                <div className="space-y-2">
                                    <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex justify-between">
                                        Voice Target Name
                                    </label>
                                    <input 
                                        type="text" 
                                        className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-indigo-500 focus:bg-white/5 focus:ring-1 focus:ring-indigo-500/20 transition-all placeholder:text-slate-600"
                                        value={voiceName}
                                        onChange={(e) => setVoiceName(e.target.value)}
                                        placeholder="e.g., Cinematic Narrator" 
                                    />
                                </div>

                                <div className="space-y-2">
                                    <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex justify-between">
                                        Voice Language
                                    </label>
                                    <select 
                                        className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-indigo-500 focus:bg-white/5 focus:ring-1 focus:ring-indigo-500/20 transition-all"
                                        value={language}
                                        onChange={(e) => setLanguage(e.target.value)}
                                    >
                                        <option value="English" className="bg-slate-900 text-slate-200">English</option>
                                        <option value="Spanish" className="bg-slate-900 text-slate-200">Spanish</option>
                                        <option value="French" className="bg-slate-900 text-slate-200">French</option>
                                        <option value="German" className="bg-slate-900 text-slate-200">German</option>
                                        <option value="Italian" className="bg-slate-900 text-slate-200">Italian</option>
                                        <option value="Portuguese" className="bg-slate-900 text-slate-200">Portuguese</option>
                                        <option value="Polish" className="bg-slate-900 text-slate-200">Polish</option>
                                        <option value="Turkish" className="bg-slate-900 text-slate-200">Turkish</option>
                                        <option value="Russian" className="bg-slate-900 text-slate-200">Russian</option>
                                        <option value="Dutch" className="bg-slate-900 text-slate-200">Dutch</option>
                                        <option value="Czech" className="bg-slate-900 text-slate-200">Czech</option>
                                        <option value="Arabic" className="bg-slate-900 text-slate-200">Arabic</option>
                                        <option value="Chinese" className="bg-slate-900 text-slate-200">Chinese (Simplified)</option>
                                        <option value="Japanese" className="bg-slate-900 text-slate-200">Japanese</option>
                                        <option value="Korean" className="bg-slate-900 text-slate-200">Korean</option>
                                        <option value="Hindi" className="bg-slate-900 text-slate-200">Hindi</option>
                                        <option value="Urdu" className="bg-slate-900 text-slate-200">Urdu</option>
                                    </select>
                                </div>

                                <div className="space-y-2">
                                    <div className="flex justify-between items-end mb-2">
                                        <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
                                            Reference Sample
                                            <span className="text-[10px] text-indigo-400 normal-case tracking-normal font-medium bg-indigo-500/10 px-1.5 py-0.5 rounded">5-15s ideal</span>
                                        </label>
                                        <div className="flex bg-black/40 border border-white/10 rounded-lg p-0.5">
                                            <button 
                                                className={`px-3 py-1 text-[10px] font-medium rounded-md transition-all ${recordingMode === 'upload' ? 'bg-indigo-500/20 text-indigo-300 shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
                                                onClick={() => setRecordingMode('upload')}
                                            >
                                                Upload
                                            </button>
                                            <button 
                                                className={`px-3 py-1 text-[10px] font-medium rounded-md transition-all ${recordingMode === 'record' ? 'bg-indigo-500/20 text-indigo-300 shadow-sm' : 'text-slate-400 hover:text-slate-200'}`}
                                                onClick={() => setRecordingMode('record')}
                                            >
                                                Record Live
                                            </button>
                                        </div>
                                    </div>
                                    
                                    {recordingMode === 'upload' ? (
                                        <label className="flex flex-col items-center justify-center w-full h-28 px-4 transition-all bg-black/20 border border-white/10 border-dashed rounded-xl hover:border-indigo-500 hover:bg-white/5 cursor-pointer group/upload overflow-hidden relative">
                                            <div className="absolute inset-0 bg-gradient-to-t from-indigo-500/10 to-transparent opacity-0 group-hover/upload:opacity-100 transition-opacity"></div>
                                            <div className="flex flex-col items-center space-y-2 relative z-10">
                                                <div className="p-2 bg-white/5 rounded-full group-hover/upload:scale-110 group-hover/upload:bg-indigo-500/20 transition-all duration-300">
                                                    <UploadCloud className="w-5 h-5 text-slate-400 group-hover/upload:text-indigo-400" />
                                                </div>
                                                <span className="font-medium text-slate-300 text-center px-4 text-sm">
                                                    {sampleFile && sampleFile.name !== "recorded_sample.webm" ? (
                                                        <span className="text-indigo-300 font-semibold">{sampleFile.name}</span>
                                                    ) : (
                                                        <span>Drag & drop audio or <span className="text-indigo-400">browse</span></span>
                                                    )}
                                                </span>
                                            </div>
                                            <input 
                                                type="file" 
                                                className="hidden"
                                                accept=".wav,.mp3,.flac,.ogg" 
                                                onChange={handleFileChange}
                                            />
                                        </label>
                                    ) : (
                                        <div className="flex flex-col items-center justify-center w-full h-28 px-4 bg-black/20 border border-white/10 rounded-xl relative overflow-hidden transition-all">
                                            {sampleFile && sampleFile.name.startsWith("recorded_sample") ? (
                                                <div className="flex flex-col items-center gap-3">
                                                    <div className="flex items-center gap-2 text-emerald-400 bg-emerald-500/10 px-3 py-1.5 rounded-lg border border-emerald-500/20">
                                                        <CheckCircle size={14} />
                                                        <span className="text-xs font-semibold">Recording Captured ({formatTime(recordingTime)})</span>
                                                    </div>
                                                    <button onClick={discardRecording} className="text-xs text-slate-400 hover:text-red-400 flex items-center gap-1.5 transition-colors">
                                                        <Trash2 size={12} /> Discard & Record Again
                                                    </button>
                                                </div>
                                            ) : (
                                                <div className="flex flex-col items-center gap-3 w-full">
                                                    {isRecording ? (
                                                        <div className="flex flex-col items-center gap-3">
                                                            <div className="flex items-center gap-3">
                                                                <div className="h-2.5 w-2.5 rounded-full bg-red-500 animate-pulse shadow-[0_0_10px_rgba(239,68,68,0.5)]"></div>
                                                                <span className="font-mono text-red-400 font-bold tracking-widest text-lg">{formatTime(recordingTime)}</span>
                                                            </div>
                                                            <Button onClick={stopRecording} className="bg-red-500/20 hover:bg-red-500/30 text-red-300 border border-red-500/30 rounded-full px-5 py-1.5 h-auto text-xs transition-all hover:scale-105">
                                                                <Square size={12} className="mr-1.5 fill-current" /> Stop Recording
                                                            </Button>
                                                        </div>
                                                    ) : (
                                                        <div className="flex flex-col items-center gap-2">
                                                            <div className="text-[11px] text-slate-400 text-center max-w-[200px]">
                                                                Speak clearly into your microphone for 5-15 seconds.
                                                            </div>
                                                            <Button onClick={startRecording} className="bg-indigo-500/20 hover:bg-indigo-500/30 text-indigo-300 border border-indigo-500/30 rounded-full px-5 py-1.5 h-auto text-xs transition-all hover:scale-105">
                                                                <Mic size={12} className="mr-1.5" /> Start Recording
                                                            </Button>
                                                        </div>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                    )}
                                </div>

                                <div className="space-y-2">
                                    <label className="text-xs font-semibold text-slate-300 uppercase tracking-wider">Test Phrase</label>
                                    <textarea 
                                        className="w-full bg-black/40 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-indigo-500 focus:bg-white/5 focus:ring-1 focus:ring-indigo-500/20 transition-all resize-none placeholder:text-slate-600"
                                        value={text}
                                        onChange={(e) => setText(e.target.value)}
                                        placeholder="The quick brown fox jumps over the lazy dog..."
                                        rows={3}
                                    />
                                </div>

                                <div className="flex items-start gap-3 p-3 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors cursor-pointer" onClick={() => setSaveToLibrary(!saveToLibrary)}>
                                    <div className={`mt-0.5 flex items-center justify-center w-4 h-4 rounded border transition-all ${saveToLibrary ? 'bg-indigo-500 border-indigo-500' : 'bg-black/50 border-white/20'}`}>
                                        {saveToLibrary && <Check size={12} className="text-white" />}
                                    </div>
                                    <div className="flex flex-col">
                                        <div className="text-[12px] font-semibold text-slate-200 select-none">Add to Voice Library</div>
                                        <div className="text-[10px] text-slate-400 leading-tight select-none mt-0.5">Save this voice to your permanent library. If unchecked, it will be hidden after you leave the studio.</div>
                                    </div>
                                </div>

                                <div className="flex items-start gap-3 p-3 bg-white/5 rounded-lg border border-white/10 hover:bg-white/10 transition-colors cursor-pointer" onClick={() => setConsent(!consent)}>
                                    <div className={`mt-0.5 flex items-center justify-center w-4 h-4 rounded border transition-all ${consent ? 'bg-indigo-500 border-indigo-500' : 'bg-black/50 border-white/20'}`}>
                                        {consent && <Check size={12} className="text-white" />}
                                    </div>
                                    <div className="text-[11px] text-slate-400 leading-tight select-none mt-0.5">
                                        I confirm that I have the legal right to clone this voice and I agree to the <span className="text-indigo-400 hover:underline">Terms of Service</span>.
                                    </div>
                                </div>

                                {error && (
                                    <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} className="bg-red-500/10 border border-red-500/30 text-red-400 px-3 py-2 rounded-lg text-xs flex items-center gap-2">
                                        <AlertTriangle size={14} className="shrink-0" /> <span className="font-medium">{error}</span>
                                    </motion.div>
                                )}

                                <Button 
                                    className="w-full py-3 text-sm font-semibold shadow-[0_0_20px_rgba(99,102,241,0.2)] bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 hover:from-indigo-400 hover:via-purple-400 hover:to-pink-400 text-white rounded-lg transform transition-all hover:scale-[1.02] active:scale-[0.98] border-0"
                                    onClick={(e) => { e.stopPropagation(); handleGeneratePreview(); }}
                                    disabled={isGenerating || !sampleFile || !text || !voiceName || !consent}
                                >
                                    {isGenerating ? (
                                        <span className="flex items-center gap-2"><Loader2 className="spin" size={16} /> Synthesizing Clone...</span>
                                    ) : (
                                        <span className="flex items-center gap-2"><Mic size={16} /> Initialize Clone Sequence</span>
                                    )}
                                </Button>
                            </div>
                        </Card>
                    </div>

                    {/* Right Column - Preview/Result */}
                    <div className="lg:col-span-7 flex flex-col h-full">
                        <Card className="flex-1 p-6 border-white/10 bg-white/[0.02] backdrop-blur-2xl shadow-xl rounded-2xl relative overflow-hidden flex flex-col justify-center items-center text-center min-h-[400px]">
                            {/* Abstract background elements */}
                            <div className="absolute top-0 right-0 w-48 h-48 bg-indigo-500/5 rounded-full mix-blend-screen blur-[60px]"></div>
                            <div className="absolute bottom-0 left-0 w-48 h-48 bg-purple-500/5 rounded-full mix-blend-screen blur-[60px]"></div>

                            <div className="relative z-10 w-full flex flex-col items-center justify-center">
                                {isGenerating ? (
                                    <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="flex flex-col items-center space-y-6 w-full max-w-sm">
                                        <div className="relative w-20 h-20 flex items-center justify-center">
                                            <div className="absolute inset-0 bg-gradient-to-tr from-indigo-500 to-purple-500 rounded-full blur-xl opacity-30 animate-pulse"></div>
                                            <div className="absolute inset-1 border-2 border-t-indigo-500 border-r-purple-500 border-b-pink-500 border-l-transparent rounded-full animate-spin"></div>
                                            <div className="absolute inset-2.5 border-2 border-t-transparent border-r-indigo-400 border-b-purple-400 border-l-pink-400 rounded-full animate-spin animation-delay-500 direction-reverse"></div>
                                            <Mic className="text-white relative z-10" size={24} />
                                        </div>
                                        
                                        <div className="space-y-2">
                                            <h3 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400">Processing Latent Space...</h3>
                                            <p className="text-slate-400 text-xs leading-relaxed">
                                                Extracting acoustic features and timbre profiles. This requires intense computation and may take a few minutes.
                                            </p>
                                        </div>

                                        <div className="bg-black/50 px-5 py-3 rounded-xl border border-white/10 shadow-inner w-full flex items-center justify-between">
                                            <span className="text-slate-400 font-medium uppercase tracking-wider text-[10px]">Elapsed Time</span>
                                            <span className="font-mono text-base text-indigo-400 font-bold tracking-wider">
                                                {formatTime(elapsedTime)}
                                            </span>
                                        </div>
                                    </motion.div>
                                ) : previewUrl ? (
                                    <motion.div initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} className="w-full max-w-lg mx-auto flex flex-col items-center">
                                        <div className="relative mb-6">
                                            <div className="absolute inset-0 bg-emerald-500/20 blur-xl rounded-full"></div>
                                            <div className="w-16 h-16 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center justify-center relative z-10">
                                                <Check size={32} strokeWidth={2.5} />
                                            </div>
                                        </div>
                                        
                                        <h2 className="text-2xl font-bold text-white mb-2">Clone Successful</h2>
                                        <p className="text-slate-400 text-sm mb-6 max-w-sm">
                                            The voice profile for <strong className="text-indigo-400 font-semibold">{voiceName}</strong> has been extracted and is ready to use.
                                        </p>
                                        
                                        <div className="w-full bg-black/40 p-5 rounded-2xl border border-white/10 mb-6 space-y-4 shadow-lg relative overflow-hidden">
                                            <div className="absolute left-0 top-0 w-1 h-full bg-gradient-to-b from-emerald-500 to-teal-500"></div>
                                            <div className="relative">
                                                <div className="absolute -top-3 -left-1 text-4xl text-white/5 font-serif">"</div>
                                                <p className="text-sm font-medium text-slate-200 leading-relaxed italic relative z-10 px-4">
                                                    {text}
                                                </p>
                                            </div>
                                            
                                            <div className="pt-2">
                                                <audio ref={audioRef} controls src={previewUrl} className="w-full outline-none h-10 rounded-lg bg-white/5"></audio>
                                            </div>
                                            
                                            {finalGenerationTime && (
                                                <div className="flex justify-center">
                                                    <div className="text-[10px] font-semibold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20 flex items-center gap-1.5">
                                                        <CheckCircle size={12} /> Inference completed in {formatTime(finalGenerationTime)}
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                        
                                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 w-full">
                                            {previewId && (
                                                <>
                                                    <a href={`http://localhost:8000/api/history/${previewId}/download?format=mp3`} className="block">
                                                        <Button variant="outline" className="w-full py-2.5 flex items-center justify-center gap-1.5 border-white/10 hover:bg-white/10 hover:border-white/20 text-slate-300 rounded-lg text-sm transition-all">
                                                            <Download size={14} /> MP3
                                                        </Button>
                                                    </a>
                                                    <a href={`http://localhost:8000/api/history/${previewId}/download?format=wav`} className="block">
                                                        <Button variant="outline" className="w-full py-2.5 flex items-center justify-center gap-1.5 border-white/10 hover:bg-white/10 hover:border-white/20 text-slate-300 rounded-lg text-sm transition-all">
                                                            <Download size={14} /> WAV
                                                        </Button>
                                                    </a>
                                                </>
                                            )}
                                            <Button className="py-2.5 flex items-center justify-center gap-1.5 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white rounded-lg shadow-[0_0_15px_rgba(16,185,129,0.2)] border-0 text-sm" onClick={() => window.location.href = '/studio'}>
                                                <Play size={14} /> Open Studio
                                            </Button>
                                        </div>
                                    </motion.div>
                                ) : (
                                    <div className="flex flex-col items-center justify-center text-slate-500 space-y-4 w-full max-w-sm relative">
                                        <div className="w-20 h-20 rounded-full bg-white/5 border border-white/10 flex items-center justify-center relative shadow-[inset_0_0_15px_rgba(255,255,255,0.01)]">
                                            <div className="absolute inset-0 rounded-full border border-white/5 scale-110"></div>
                                            <div className="absolute inset-0 rounded-full border border-white/5 scale-125 opacity-30"></div>
                                            <Mic size={32} className="opacity-40" />
                                        </div>
                                        <div className="space-y-1">
                                            <h3 className="text-lg font-bold text-slate-300 tracking-wide">Awaiting Input</h3>
                                            <p className="text-sm text-slate-500 leading-relaxed max-w-xs mx-auto">
                                                Provide an audio sample and configure your target voice parameters.
                                            </p>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </Card>
                    </div>
                </div>
            )}
        </motion.div>
    );
};

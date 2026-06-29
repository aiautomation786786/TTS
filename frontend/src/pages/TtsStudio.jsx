import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { generateSpeech, getVoices, getLanguages, startLongFormJob, getLongFormStatus, retryLongFormJob } from '../api/tts';
import { getVoicePreview } from '../api/voices';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { useAudioPlayer } from '../hooks/useAudioPlayer';
import { Play, Square, Loader2, Download, RefreshCw, AlertCircle, Clock, ListMusic, Sparkles, Layers, Settings } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';

const USE_CASES = [
    "Documentary", "Horror", "YouTube", "Audiobook", "Storytelling",
    "Commercial", "Podcast", "News", "Education", "Explainer",
    "Meditation", "Motivation", "Kids", "Gaming", "Trailer",
    "Cinematic", "Social Media", "Drama", "Suspense",
    "Professional Corporate", "Emotional Narration"
].sort();

export const TtsStudio = () => {
    const location = useLocation();
    const { user } = useAuthStore();
    const [mode, setMode] = useState('short_form');
    const [text, setText] = useState(location.state?.scriptText || '');
    
    // Voice Selection State
    const [allVoices, setAllVoices] = useState([]);
    const [availableLanguages, setAvailableLanguages] = useState([]);
    const [selectedLanguage, setSelectedLanguage] = useState('');
    const [selectedUseCase, setSelectedUseCase] = useState('');
    const [selectedVoice, setSelectedVoice] = useState(null);
    const [speed, setSpeed] = useState(1.0);
    
    // Short Form State
    const [audioUrl, setAudioUrl] = useState(null);
    const [loading, setLoading] = useState(false);
    
    // Long Form State
    const [jobId, setJobId] = useState(null);
    const [jobStatus, setJobStatus] = useState(null);
    
    const [error, setError] = useState('');
    const [autoTranslate, setAutoTranslate] = useState(false);
    
    const { playingId, play, stop } = useAudioPlayer();
    const [previewLoading, setPreviewLoading] = useState(false);
    
    // Timer State
    const [startTime, setStartTime] = useState(null);
    const [elapsedTime, setElapsedTime] = useState(0);
    const [finalGenerationTime, setFinalGenerationTime] = useState(null);
    
    const maxChars = mode === 'short_form' ? 5000 : 30000;

    useEffect(() => {
        getLanguages().then(res => {
            const uniqueLangs = [...new Set(res.data.map(l => l.name))].filter(Boolean).sort();
            setAvailableLanguages(uniqueLangs);
        }).catch(err => console.error("Failed to fetch languages"));

        getVoices().then(res => {
            const stateVoiceId = location.state?.selectedVoiceId || location.state?.voiceId;
            const validVoices = res.data.voices.filter(v => v.category !== 'temporary' || v.id === stateVoiceId);
            setAllVoices(validVoices);
            
            if(validVoices.length > 0) {
                if (stateVoiceId) {
                    const match = validVoices.find(v => v.id === stateVoiceId);
                    if (match) {
                        setSelectedVoice(match);
                        setSelectedLanguage(match.language);
                    } else {
                        setSelectedVoice(validVoices[0]);
                        setSelectedLanguage(validVoices[0].language);
                    }
                } else {
                    setSelectedVoice(validVoices[0]);
                    setSelectedLanguage(validVoices[0].language);
                }
            }
        });
    }, [location.state]);

    // Long Form Polling
    useEffect(() => {
        let interval;
        if (jobId && jobStatus && !['completed', 'failed'].includes(jobStatus.status)) {
            interval = setInterval(async () => {
                try {
                    const res = await getLongFormStatus(jobId);
                    setJobStatus(res.data);
                    if (res.data.status === 'completed' || res.data.status === 'failed') {
                        setLoading(false);
                        if (res.data.status === 'completed') {
                            setAudioUrl(`http://localhost:8000${res.data.audio_url}`);
                            setFinalGenerationTime(res.data.generation_time_seconds);
                            toast.success("Long form audio completed!");
                        } else {
                            setError(res.data.error_message || "Job failed");
                            setFinalGenerationTime(res.data.generation_time_seconds);
                            toast.error("Long form generation failed.");
                        }
                        setStartTime(null);
                        clearInterval(interval);
                    }
                } catch (err) {
                    console.error("Status poll failed", err);
                    if (err.response && err.response.status === 404) {
                        setLoading(false);
                        setStartTime(null);
                        setError("Job not found or deleted.");
                        clearInterval(interval);
                    }
                }
            }, 2000);
        }
        return () => clearInterval(interval);
    }, [jobId, jobStatus]);

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

    // Dynamic Recommendation Sorting Logic
    const getSortedVoices = () => {
        let filtered = allVoices.filter(v => selectedLanguage === '' || v.language === selectedLanguage);
        
        if (selectedUseCase) {
            filtered = [...filtered].sort((a, b) => {
                const parseJSON = (str) => { try { return JSON.parse(str || "[]") } catch { return [] } };
                const aUses = parseJSON(a.use_case_tags);
                const bUses = parseJSON(b.use_case_tags);
                
                const aHas = aUses.includes(selectedUseCase);
                const bHas = bUses.includes(selectedUseCase);
                
                if (aHas && !bHas) return -1;
                if (!aHas && bHas) return 1;
                
                // Secondary sort: Premium
                if (a.quality_label === 'Premium' && b.quality_label !== 'Premium') return -1;
                if (a.quality_label !== 'Premium' && b.quality_label === 'Premium') return 1;
                
                return 0;
            });
        }
        return filtered;
    };
    
    const sortedVoices = getSortedVoices();

    const handleLanguageChange = (e) => {
        setSelectedLanguage(e.target.value);
        const filtered = allVoices.filter(v => e.target.value === '' || v.language === e.target.value);
        if (filtered.length > 0) {
            setSelectedVoice(filtered[0]);
        }
        setSpeed(1.0);
        stop();
    };

    const handleUseCaseChange = (e) => {
        setSelectedUseCase(e.target.value);
        // We defer auto-selection to the sorted list
        setTimeout(() => {
            const newSorted = getSortedVoices();
            if (newSorted.length > 0) {
                setSelectedVoice(newSorted[0]);
            }
        }, 50);
        setSpeed(1.0);
        stop();
    };

    const handleVoiceChange = (e) => {
        const voice = allVoices.find(v => v.id === parseInt(e.target.value));
        setSelectedVoice(voice);
        setSpeed(1.0);
        stop();
    };

    const handlePlayPreview = async () => {
        if (!selectedVoice) return;
        if (playingId === 'preview') {
            stop();
            return;
        }
        setPreviewLoading(true);
        try {
            const res = await getVoicePreview(selectedVoice.id);
            play('preview', `http://localhost:8000${res.data.preview_url}`);
        } catch (err) {
            toast.error(err.response?.data?.detail || 'Preview not available. Engine might be offline.');
        } finally {
            setPreviewLoading(false);
        }
    };

    const handleGenerate = async (e) => {
        if (e && e.preventDefault) e.preventDefault();
        if (!text || !selectedVoice) return;
        if (text.length > maxChars) {
            setError(`Text exceeds maximum allowed length of ${maxChars} characters.`);
            return;
        }
        setLoading(true);
        setError('');
        setAudioUrl(null);
        setJobStatus(null);
        setFinalGenerationTime(null);
        setStartTime(Date.now());
        stop();
        
        try {
            if (mode === 'short_form') {
                const res = await generateSpeech({ text, voice_id: selectedVoice.id, speed, pitch: "+0Hz", auto_translate: autoTranslate });
                setAudioUrl(`http://localhost:8000${res.data.audio_url}`);
                setFinalGenerationTime(res.data.generation_time_seconds);
                setLoading(false);
                setStartTime(null);
            } else {
                const res = await startLongFormJob({ text, voice_id: selectedVoice.id, speed, pitch: "+0Hz", auto_translate: autoTranslate });
                if (res && res.data) {
                    setJobId(res.data.id);
                    setJobStatus(res.data);
                    toast.success("Long form job started!");
                } else {
                    throw new Error("Invalid response from server.");
                }
            }
        } catch (err) {
            let errorMsg = 'Generation failed';
            const detail = err.response?.data?.detail;
            if (detail) {
                if (typeof detail === 'string') errorMsg = detail;
                else if (Array.isArray(detail)) errorMsg = detail[0]?.msg || JSON.stringify(detail);
                else errorMsg = JSON.stringify(detail);
            } else if (err.message) {
                errorMsg = err.message;
            }
            setError(errorMsg);
            setLoading(false);
        }
    };

    const handleRetry = async () => {
        if (!jobId) return;
        setLoading(true);
        setError('');
        try {
            await retryLongFormJob(jobId);
            toast.success("Job retry started!");
            const res = await getLongFormStatus(jobId);
            setJobStatus(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Retry failed');
            setLoading(false);
        }
    };

    const estimatedDuration = () => {
        const mins = Math.max(0.1, text.length / 900);
        if (mins < 1) return `${Math.ceil(mins * 60)} secs`;
        return `~${mins.toFixed(1)} mins`;
    };
    
    const estimatedChunks = () => Math.ceil(text.length / 1500) || 1;
    
    // Check if currently selected voice matches use case
    const isRecommended = selectedUseCase && selectedVoice && 
        (() => { try { return JSON.parse(selectedVoice.use_case_tags || "[]").includes(selectedUseCase) } catch { return false } })();

    return (
        <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="max-w-6xl mx-auto flex flex-col lg:flex-row gap-8 relative"
        >
            <div className="absolute top-20 left-1/4 w-96 h-96 bg-indigo-500/10 blur-[120px] pointer-events-none"></div>
            <div className="absolute bottom-20 right-1/4 w-96 h-96 bg-purple-500/10 blur-[120px] pointer-events-none"></div>
            
            <div className="flex-1 flex flex-col gap-6 relative z-10">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-2 gap-4">
                        <div className="flex items-center gap-3">
                            <h2 className="text-4xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-white via-indigo-200 to-slate-400 tracking-tight">TTS Studio</h2>
                        </div>
                    
                    <div className="flex bg-slate-900/80 backdrop-blur-md rounded-xl p-1.5 border border-slate-700/80 shadow-inner">
                        <button 
                            className={`px-5 py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition-all ${mode === 'short_form' ? 'bg-indigo-600 text-white shadow-[0_0_15px_rgba(79,70,229,0.4)]' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}
                            onClick={() => { setMode('short_form'); setAudioUrl(null); setJobId(null); setJobStatus(null); }}
                        >
                            Short Form
                        </button>
                        <button 
                            className={`px-5 py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition-all ${mode === 'long_form' ? 'bg-purple-600 text-white shadow-[0_0_15px_rgba(147,51,234,0.4)]' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}
                            onClick={() => { setMode('long_form'); setAudioUrl(null); setJobId(null); setJobStatus(null); }}
                        >
                            Long Form
                        </button>
                    </div>
                </div>
                
                {error && (
                    <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="bg-red-500/10 border border-red-500/50 text-red-400 p-4 rounded-lg flex items-center gap-3">
                        <AlertCircle size={20} />
                        <p>{error}</p>
                    </motion.div>
                )}

                <Card className="flex-1 flex flex-col p-0 overflow-hidden border border-slate-700/60 shadow-[0_8px_30px_rgb(0,0,0,0.4)] bg-gradient-to-b from-slate-900/90 to-slate-950/90 backdrop-blur-xl rounded-2xl">
                    <div className="p-4 border-b border-slate-800 flex justify-between items-center flex-wrap gap-3">
                        <div className="flex items-center gap-4">
                            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">Text Input</span>
                            <label className="flex items-center gap-2 cursor-pointer group">
                                <div className="relative">
                                    <input 
                                        type="checkbox" 
                                        className="sr-only" 
                                        checked={autoTranslate}
                                        onChange={(e) => setAutoTranslate(e.target.checked)}
                                    />
                                    <div className={`block w-10 h-5 rounded-full transition-colors ${autoTranslate ? (mode === 'long_form' ? 'bg-purple-600 shadow-[0_0_10px_rgba(147,51,234,0.4)]' : 'bg-indigo-600 shadow-[0_0_10px_rgba(79,70,229,0.4)]') : 'bg-slate-800 border border-slate-700'}`}></div>
                                    <div className={`absolute left-0.5 top-0.5 bg-white w-4 h-4 rounded-full transition-transform shadow-md ${autoTranslate ? 'translate-x-5' : 'translate-x-0'}`}></div>
                                </div>
                                <span className="text-xs font-semibold text-slate-400 group-hover:text-white transition-colors">
                                    Auto-Translate
                                </span>
                            </label>
                        </div>
                        <div className="text-xs font-mono font-bold bg-slate-900 px-3 py-1.5 rounded-md border border-slate-800 shadow-inner">
                            <span className={text.length > maxChars ? 'text-red-400' : 'text-indigo-400'}>{text.length}</span>
                            <span className="text-slate-500"> / {maxChars} chars</span>
                        </div>
                    </div>
                    <textarea 
                        className="w-full flex-1 min-h-[300px] bg-transparent p-6 text-lg text-slate-200 focus:outline-none resize-none placeholder-slate-600/70 transition-colors leading-relaxed"
                        placeholder={mode === 'short_form' ? "Enter your text here. The AI will convert it into lifelike speech..." : "Enter your long script here (up to 30,000 characters). We will chunk it automatically..."}
                        value={text} onChange={e => setText(e.target.value)}
                    ></textarea>
                    
                    {mode === 'long_form' && text.length > 0 && (
                        <div className="bg-slate-800 p-4 text-sm text-slate-300 border-t border-slate-700 space-y-3">
                            <div className="flex flex-wrap gap-6">
                                <div className="flex items-center gap-2">
                                    <Clock size={16} className="text-purple-400" />
                                    <span>Estimated Output: {estimatedDuration()}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <ListMusic size={16} className="text-purple-400" />
                                    <span>Estimated Parts: {estimatedChunks()}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Layers size={16} className="text-purple-400" />
                                    <span>Characters: {text.length}</span>
                                </div>
                            </div>
                            
                            {/* Script Analyzer Warnings */}
                            {(() => {
                                const warnings = [];
                                if (text.length > 1500 && !text.includes('\n\n')) warnings.push("No paragraph breaks detected. Chunker may struggle.");
                                if (/[\u200b\u200c\u200d\u200e\u200f\ufeff]/.test(text)) warnings.push("Hidden formatting characters detected (Zero-width spaces).");
                                if (/<[^>]+>/.test(text)) warnings.push("XML/HTML tags detected. May cause Edge-TTS errors.");
                                if (/(.)\1{4,}/.test(text)) warnings.push("Repeated characters detected.");
                                
                                if (warnings.length > 0) {
                                    return (
                                        <div className="mt-3 p-3 bg-amber-900/20 border border-amber-500/30 rounded text-amber-400 text-xs">
                                            <div className="font-bold flex items-center gap-2 mb-1"><AlertCircle size={14}/> Script Warnings Found:</div>
                                            <ul className="list-disc pl-5 space-y-1 mb-3">
                                                {warnings.map((w, i) => <li key={i}>{w}</li>)}
                                            </ul>
                                            <button 
                                                onClick={(e) => {
                                                    e.preventDefault();
                                                    // Simple frontend cleaning
                                                    let cleanText = text.replace(/[\u200b\u200c\u200d\u200e\u200f\ufeff]/g, '');
                                                    cleanText = cleanText.replace(/<[^>]+>/g, '');
                                                    if (!cleanText.includes('\n\n') && cleanText.length > 1500) {
                                                        cleanText = cleanText.replace(/\. /g, '.\n\n');
                                                    }
                                                    setText(cleanText);
                                                    toast.success("Script cleaned!");
                                                }}
                                                className="bg-amber-600 hover:bg-amber-500 text-white px-3 py-1.5 rounded transition-colors"
                                            >
                                                Clean Script for TTS
                                            </button>
                                        </div>
                                    );
                                }
                                return null;
                            })()}
                        </div>
                    )}
                </Card>
                
                {mode === 'long_form' && jobStatus && (
                    <AnimatePresence>
                        <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }} exit={{ opacity: 0, height: 0 }}>
                            <Card className="bg-slate-900 border-purple-500/30 mb-6">
                                <div className="flex justify-between items-center mb-3">
                                    <h3 className="font-bold text-lg text-white flex items-center gap-2">
                                        {jobStatus.status === 'completed' ? 'Generation Complete' : 'Generation in Progress'}
                                        {jobStatus.status !== 'completed' && jobStatus.status !== 'failed' && <Loader2 size={16} className="animate-spin text-purple-400" />}
                                    </h3>
                                    <span className="text-purple-400 font-mono text-sm">
                                        {jobStatus.status !== 'completed' && jobStatus.status !== 'failed' && (
                                            <span className="mr-3 opacity-80">Generating... {formatTime(elapsedTime)} elapsed</span>
                                        )}
                                        {(jobStatus.progress || 0).toFixed(0)}%
                                    </span>
                                </div>
                                
                                <div className="w-full bg-slate-800 rounded-full h-2.5 mb-4 overflow-hidden">
                                    <motion.div 
                                        className={`h-2.5 rounded-full ${jobStatus.status === 'failed' ? 'bg-red-500' : 'bg-purple-600'}`}
                                        initial={{ width: 0 }}
                                        animate={{ width: `${jobStatus.progress || 0}%` }}
                                        transition={{ duration: 0.5 }}
                                    ></motion.div>
                                </div>
                                
                                <div className="flex justify-between text-sm text-slate-400">
                                    <span className="capitalize">{jobStatus.status || 'pending'}...</span>
                                    <span>Chunk {jobStatus.completed_chunks || 0} / {jobStatus.total_chunks || 1}</span>
                                </div>
                                
                                {jobStatus.status === 'failed' && (
                                    <div className="mt-4 flex justify-end">
                                        <Button variant="danger" onClick={handleRetry} className="flex items-center gap-2">
                                            <RefreshCw size={16} /> Retry Failed Chunk
                                        </Button>
                                    </div>
                                )}
                            </Card>
                        </motion.div>
                    </AnimatePresence>
                )}

                {mode === 'short_form' && loading && (
                    <motion.div 
                        initial={{ opacity: 0, scale: 0.95 }} 
                        animate={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 0.95 }}
                        className="relative overflow-hidden flex flex-col items-center justify-center p-12 bg-slate-900 border border-indigo-500/30 rounded-xl shadow-2xl mb-6 text-indigo-400 group"
                    >
                        {/* Animated background glow */}
                        <motion.div 
                            className="absolute inset-0 bg-indigo-500/10"
                            animate={{ opacity: [0.3, 0.7, 0.3] }}
                            transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
                        />
                        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500 animate-pulse"></div>
                        <Loader2 size={40} className="animate-spin mb-4 text-indigo-300 drop-shadow-md z-10" />
                        <h3 className="font-bold text-xl text-white mb-2 z-10">Synthesizing Audio</h3>
                        <span className="font-medium text-slate-400 z-10">Hold tight... {formatTime(elapsedTime)} elapsed</span>
                    </motion.div>
                )}

                {audioUrl && (
                    <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
                        <Card className={`bg-gradient-to-br ${mode === 'long_form' ? 'from-purple-900/30 to-slate-900 border-purple-500/30' : 'from-indigo-900/20 to-slate-900 border-indigo-500/30'} mb-6`}>
                            <div className="flex justify-between items-start mb-4">
                                <h3 className={`text-sm font-bold ${mode === 'long_form' ? 'text-purple-400' : 'text-indigo-400'} uppercase tracking-wider`}>Final Result</h3>
                                {finalGenerationTime && (
                                    <div className={`px-3 py-1 rounded-full text-xs font-semibold ${mode === 'long_form' ? 'bg-purple-900/50 text-purple-300' : 'bg-indigo-900/50 text-indigo-300'}`}>
                                        Generated in {formatTime(finalGenerationTime)}
                                    </div>
                                )}
                            </div>
                            <div className="flex flex-col sm:flex-row items-center gap-4">
                                <audio controls src={audioUrl} className="w-full"></audio>
                                <div className="flex gap-2">
                                    <a href={audioUrl} download className={`flex items-center gap-2 px-4 py-2 rounded-md text-white font-medium whitespace-nowrap transition-colors ${mode === 'long_form' ? 'bg-purple-600 hover:bg-purple-700' : 'bg-indigo-600 hover:bg-indigo-700'}`}>
                                        <Download size={18} /> MP3
                                    </a>
                                </div>
                            </div>
                        </Card>
                    </motion.div>
                )}
            </div>
            
            <div className="w-full lg:w-80 flex-shrink-0 relative z-10">
                <Card className="sticky top-8 flex flex-col gap-6 shadow-[0_8px_30px_rgb(0,0,0,0.4)] border border-slate-700/60 bg-gradient-to-b from-slate-900/95 to-slate-950/95 backdrop-blur-xl rounded-2xl">
                    <div>
                        <h3 className="font-extrabold text-xl text-white tracking-tight mb-5 flex items-center gap-2"><Settings size={18} className="text-indigo-400"/> Voice Settings</h3>
                        
                        <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">1. Language</label>
                        <select 
                            className="w-full bg-slate-900/60 border border-slate-700/60 rounded-xl p-3 text-white text-sm mb-5 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none transition-all shadow-inner"
                            value={selectedLanguage} onChange={handleLanguageChange}
                        >
                            <option value="">All Languages</option>
                            {availableLanguages.map(lang => (
                                <option key={lang} value={lang}>{lang}</option>
                            ))}
                        </select>

                        <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2">2. Content Type (Optional)</label>
                        <select 
                            className="w-full bg-slate-900/60 border border-slate-700/60 rounded-xl p-3 text-white text-sm mb-5 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none transition-all shadow-inner"
                            value={selectedUseCase} onChange={handleUseCaseChange}
                        >
                            <option value="">Any Content Type</option>
                            {USE_CASES.map(uc => (
                                <option key={uc} value={uc}>{uc}</option>
                            ))}
                        </select>

                        <label className="block text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center justify-between">
                            <span>3. Select Voice</span>
                            {selectedUseCase && <span className="text-[10px] text-emerald-400/80 font-medium normal-case">(Sorted by fit)</span>}
                        </label>
                        <select 
                            className="w-full bg-slate-900/60 border border-slate-700/60 rounded-xl p-3 text-white text-sm mb-4 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 focus:outline-none transition-all shadow-inner"
                            value={selectedVoice?.id || ''} onChange={handleVoiceChange}
                        >
                            {(() => {
                                const clonedVoices = sortedVoices.filter(v => v.is_cloned);
                                const premiumVoices = sortedVoices.filter(v => !v.is_cloned && v.quality_label === 'Premium');
                                const standardVoices = sortedVoices.filter(v => !v.is_cloned && v.quality_label !== 'Premium');

                                const renderOption = (v) => {
                                    let isMatch = false;
                                    if (selectedUseCase) {
                                        try { isMatch = JSON.parse(v.use_case_tags || "[]").includes(selectedUseCase); } catch {}
                                    }
                                    return (
                                        <option key={v.id} value={v.id}>
                                            {isMatch ? "⭐ " : ""}{v.name} ({v.language}) {v.category === 'temporary' ? '[Unsaved]' : ''}
                                        </option>
                                    );
                                };

                                return (
                                    <>
                                        {clonedVoices.length > 0 && (
                                            <optgroup label="🎙️ Your Cloned Voices">
                                                {clonedVoices.map(renderOption)}
                                            </optgroup>
                                        )}
                                        {premiumVoices.length > 0 && (
                                            <optgroup label="🌟 Premium System Voices">
                                                {premiumVoices.map(renderOption)}
                                            </optgroup>
                                        )}
                                        {standardVoices.length > 0 && (
                                            <optgroup label="Standard Voices">
                                                {standardVoices.map(renderOption)}
                                            </optgroup>
                                        )}
                                    </>
                                );
                            })()}
                        </select>
                        
                        {selectedVoice && (
                            <div className={`rounded-lg p-3 border transition-colors shadow-inner ${isRecommended ? 'bg-emerald-900/10 border-emerald-500/30' : 'bg-slate-900 border-slate-800'}`}>
                                <div className="flex justify-between items-center mb-2">
                                    <span className="font-medium text-white flex items-center gap-2">
                                        {selectedVoice.name}
                                        {isRecommended && <Sparkles size={14} className="text-emerald-400" />}
                                    </span>
                                    <button 
                                        onClick={handlePlayPreview}
                                        disabled={previewLoading}
                                        className="text-indigo-400 hover:text-indigo-300 p-1.5 rounded hover:bg-slate-800 transition-colors"
                                        title="Preview Voice"
                                    >
                                        {previewLoading ? <Loader2 size={16} className="animate-spin" /> : 
                                         playingId === 'preview' ? <Square size={16} fill="currentColor" /> : <Play size={16} fill="currentColor" />}
                                    </button>
                                </div>
                                <div className="text-xs text-slate-400 flex flex-wrap gap-1.5 mb-2">
                                    <span className="bg-slate-800 border border-slate-700 px-2 py-0.5 rounded">{selectedVoice.gender}</span>
                                    <span className="bg-slate-800 border border-slate-700 px-2 py-0.5 rounded">{selectedVoice.accent || selectedVoice.locale}</span>
                                    <span className="bg-slate-800 border border-slate-700 px-2 py-0.5 rounded">{selectedVoice.engine === 'piper' ? 'Local' : selectedVoice.engine === 'coqui' ? 'Coqui' : 'Online'}</span>
                                    <span className="bg-slate-800 border border-slate-700 px-2 py-0.5 rounded text-indigo-300">{selectedVoice.quality_label}</span>
                                </div>
                                {isRecommended && (
                                    <div className="text-[11px] text-emerald-400/80 mt-1">
                                        Highly recommended for {selectedUseCase} content.
                                    </div>
                                )}
                            </div>
                        )}
                    </div>
                    
                    <div className="pt-4 border-t border-slate-800">
                        <label className="flex justify-between text-sm text-slate-400 mb-2">
                            <span>Speed</span>
                            <span className="text-indigo-400 font-mono">{speed.toFixed(2)}x</span>
                        </label>
                        <div className="relative">
                            <input 
                                type="range" min="0.5" max="1.5" step="0.05" 
                                value={speed} onChange={e => setSpeed(parseFloat(e.target.value))}
                                className="w-full accent-indigo-500 relative z-10"
                            />
                            <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-0.5 h-3 bg-slate-600 rounded pointer-events-none z-0"></div>
                        </div>
                        <div className="flex justify-between text-xs text-slate-500 mt-2">
                            <span>0.5x</span>
                            <span className="text-center font-medium text-slate-400">Normal</span>
                            <span>1.5x</span>
                        </div>
                    </div>

                    <div className="pt-4 mt-auto">
                        <motion.button 
                            whileHover={!(loading || !text) ? { scale: 1.02 } : {}}
                            whileTap={!(loading || !text) ? { scale: 0.98 } : {}}
                            onClick={handleGenerate} 
                            disabled={loading || !text || (mode === 'long_form' && jobStatus && jobStatus.status !== 'completed' && jobStatus.status !== 'failed')} 
                            className={`w-full py-4 text-lg font-bold flex items-center justify-center gap-2 transition-all rounded-md shadow-lg overflow-hidden relative ${
                                loading || !text ? 'bg-slate-700 text-slate-400 cursor-not-allowed' : 
                                mode === 'long_form' ? 'bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white hover:shadow-purple-500/25' : 
                                'bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-500 hover:to-blue-500 text-white hover:shadow-indigo-500/25'
                            }`}
                        >
                            {/* Shiny overlay effect on hover */}
                            {!(loading || !text) && (
                                <div className="absolute inset-0 bg-white/20 translate-y-full hover:translate-y-0 transition-transform duration-300 ease-out"></div>
                            )}
                            <div className="relative z-10 flex items-center gap-2">
                                {loading ? <Loader2 className="animate-spin" size={20} /> : <Sparkles size={20} />}
                                {loading ? (mode === 'long_form' ? 'Processing...' : 'Generating...') : (mode === 'long_form' ? 'Generate Long Audio' : 'Generate Audio')}
                            </div>
                        </motion.button>
                        <p className="text-center text-xs text-slate-500 mt-3">
                            Uses {text.length} characters of your quota
                        </p>
                    </div>
                </Card>
            </div>
        </motion.div>
    );
};

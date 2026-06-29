import os

files = {
    "src/hooks/useAudioPlayer.js": """
import { useState, useRef, useEffect } from 'react';

export const useAudioPlayer = () => {
    const [playingId, setPlayingId] = useState(null);
    const audioRef = useRef(new Audio());

    useEffect(() => {
        const audio = audioRef.current;
        const handleEnded = () => setPlayingId(null);
        audio.addEventListener('ended', handleEnded);
        return () => {
            audio.removeEventListener('ended', handleEnded);
            audio.pause();
        };
    }, []);

    const play = (id, url) => {
        if (playingId === id) {
            audioRef.current.pause();
            setPlayingId(null);
        } else {
            audioRef.current.src = url;
            audioRef.current.play().catch(console.error);
            setPlayingId(id);
        }
    };

    const stop = () => {
        audioRef.current.pause();
        setPlayingId(null);
    };

    return { playingId, play, stop };
};
""",
    "src/api/voices.js": """
import client from './client';
export const getVoices = (params) => client.get('/api/voices/', { params });
export const getVoice = (id) => client.get(`/api/voices/${id}`);
export const cloneVoice = (data) => client.post('/api/voices/clone', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
});
export const getClonedVoices = () => client.get('/api/voices/cloned');
export const deleteClonedVoice = (id) => client.delete(`/api/voices/cloned/${id}`);
export const getVoicePreview = (id) => client.get(`/api/voices/${id}/preview`);
""",
    "src/pages/VoiceLibrary.jsx": """
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getVoices, getVoicePreview } from '../api/voices';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useAudioPlayer } from '../hooks/useAudioPlayer';
import { Play, Square, Loader2, Search, Filter } from 'lucide-react';

export const VoiceLibrary = () => {
    const [voices, setVoices] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({ search: '', gender: '', language: '', category: '' });
    const { playingId, play } = useAudioPlayer();
    const [loadingPreviewId, setLoadingPreviewId] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        setLoading(true);
        const params = new URLSearchParams();
        if (filters.search) params.append('search', filters.search);
        if (filters.gender) params.append('gender', filters.gender);
        if (filters.language) params.append('language', filters.language);
        if (filters.category) params.append('category', filters.category);
        
        getVoices(params).then(res => {
            setVoices(res.data.voices);
            setLoading(false);
        }).catch(console.error);
    }, [filters]);

    const handlePlayPreview = async (voice) => {
        if (playingId === voice.id) {
            play(voice.id, ''); // toggle pause
            return;
        }
        
        setLoadingPreviewId(voice.id);
        try {
            const res = await getVoicePreview(voice.id);
            const url = `http://localhost:8000${res.data.preview_url}`;
            play(voice.id, url);
        } catch (err) {
            alert('Could not load preview. Engine might be unavailable.');
        } finally {
            setLoadingPreviewId(null);
        }
    };

    const handleUseInStudio = (id) => {
        navigate('/studio', { state: { selectedVoiceId: id } });
    };

    return (
        <div className="max-w-7xl mx-auto flex flex-col lg:flex-row gap-8">
            {/* Sidebar Filters */}
            <div className="w-full lg:w-64 flex-shrink-0">
                <div className="sticky top-8">
                    <h2 className="text-xl font-bold mb-4 flex items-center gap-2"><Filter size={20}/> Filters</h2>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Search</label>
                            <div className="relative">
                                <Search className="absolute left-3 top-2.5 text-slate-500" size={16} />
                                <input 
                                    type="text" placeholder="Search voices..."
                                    className="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-700 rounded-md text-white focus:outline-none focus:border-indigo-500"
                                    value={filters.search} onChange={e => setFilters({...filters, search: e.target.value})}
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Gender</label>
                            <select className="w-full bg-slate-900 border border-slate-700 rounded-md p-2 text-white" value={filters.gender} onChange={e => setFilters({...filters, gender: e.target.value})}>
                                <option value="">All</option>
                                <option value="Male">Male</option>
                                <option value="Female">Female</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Language</label>
                            <select className="w-full bg-slate-900 border border-slate-700 rounded-md p-2 text-white" value={filters.language} onChange={e => setFilters({...filters, language: e.target.value})}>
                                <option value="">All</option>
                                <option value="English">English</option>
                                <option value="Spanish">Spanish</option>
                                <option value="French">French</option>
                                <option value="German">German</option>
                            </select>
                        </div>
                    </div>
                </div>
            </div>

            {/* Voice Grid */}
            <div className="flex-1">
                <h1 className="text-3xl font-bold mb-8">Voice Library</h1>
                {loading ? (
                    <div className="flex justify-center items-center h-64"><Loader2 className="animate-spin text-indigo-500" size={48} /></div>
                ) : voices.length === 0 ? (
                    <div className="text-center py-16 text-slate-400">No voices found matching your filters.</div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                        {voices.map(voice => (
                            <Card key={voice.id} className="flex flex-col h-full hover:border-indigo-500/50 transition-colors group relative overflow-hidden">
                                <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 to-purple-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                                <div className="flex justify-between items-start mb-3">
                                    <h3 className="font-bold text-lg text-white">{voice.name}</h3>
                                    <div className="flex gap-2">
                                        {voice.is_cloned && <span className="text-xs bg-green-500/20 text-green-400 px-2 py-1 rounded">Cloned</span>}
                                        <span className="text-xs bg-indigo-500/20 text-indigo-300 px-2 py-1 rounded">{voice.quality_label}</span>
                                    </div>
                                </div>
                                <div className="text-sm text-slate-400 mb-4 flex items-center gap-2">
                                    <span>{voice.language}</span> • <span>{voice.gender}</span> • <span className="uppercase text-xs border border-slate-700 px-1 rounded">{voice.engine}</span>
                                </div>
                                <p className="text-sm text-slate-300 line-clamp-2 mb-4 flex-grow">{voice.description || voice.use_case}</p>
                                
                                <div className="flex items-center gap-3 mt-auto pt-4 border-t border-slate-700/50">
                                    <button 
                                        onClick={() => handlePlayPreview(voice)}
                                        disabled={loadingPreviewId === voice.id}
                                        className="w-10 h-10 rounded-full bg-indigo-600 hover:bg-indigo-700 flex items-center justify-center text-white transition-colors"
                                    >
                                        {loadingPreviewId === voice.id ? <Loader2 size={18} className="animate-spin" /> : 
                                         playingId === voice.id ? <Square size={16} fill="currentColor" /> : <Play size={18} fill="currentColor" className="ml-1" />}
                                    </button>
                                    <Button onClick={() => handleUseInStudio(voice.id)} variant="secondary" className="flex-1 py-2 text-sm">
                                        Use in Studio
                                    </Button>
                                </div>
                            </Card>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};
""",
    "src/pages/TtsStudio.jsx": """
import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { generateSpeech, getVoices } from '../api/tts';
import { getVoicePreview } from '../api/voices';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { useAudioPlayer } from '../hooks/useAudioPlayer';
import { Play, Square, Loader2, Download, RefreshCw, AlertCircle } from 'lucide-react';
import { useAuthStore } from '../store/authStore';

export const TtsStudio = () => {
    const location = useLocation();
    const { user } = useAuthStore();
    const [text, setText] = useState('');
    const [voices, setVoices] = useState([]);
    const [selectedVoice, setSelectedVoice] = useState(null);
    const [speed, setSpeed] = useState(1.0);
    const [audioUrl, setAudioUrl] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    
    const { playingId, play, stop } = useAudioPlayer();
    const [previewLoading, setPreviewLoading] = useState(false);

    useEffect(() => {
        getVoices().then(res => {
            setVoices(res.data.voices);
            if(res.data.voices.length > 0) {
                const stateVoiceId = location.state?.selectedVoiceId;
                if (stateVoiceId) {
                    const match = res.data.voices.find(v => v.id === stateVoiceId);
                    if (match) setSelectedVoice(match);
                    else setSelectedVoice(res.data.voices[0]);
                } else {
                    setSelectedVoice(res.data.voices[0]);
                }
            }
        });
    }, [location.state]);

    const handleVoiceChange = (e) => {
        const voice = voices.find(v => v.id === parseInt(e.target.value));
        setSelectedVoice(voice);
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
            setError('Preview not available. Engine might be offline.');
        } finally {
            setPreviewLoading(false);
        }
    };

    const handleGenerate = async () => {
        if (!text || !selectedVoice) return;
        setLoading(true);
        setError('');
        stop();
        try {
            const res = await generateSpeech({ text, voice_id: selectedVoice.id, speed, pitch: "+0Hz" });
            setAudioUrl(`http://localhost:8000${res.data.audio_url}`);
        } catch (err) {
            setError(err.response?.data?.detail || 'Generation failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-6xl mx-auto flex flex-col lg:flex-row gap-8">
            <div className="flex-1 flex flex-col gap-6">
                <h1 className="text-3xl font-bold">TTS Studio</h1>
                
                {error && (
                    <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-4 rounded-lg flex items-center gap-3">
                        <AlertCircle size={20} />
                        <p>{error}</p>
                    </div>
                )}

                <Card className="flex-1 flex flex-col p-0 overflow-hidden border-slate-700">
                    <div className="p-4 border-b border-slate-700 bg-slate-800/50 flex justify-between items-center">
                        <span className="text-sm text-slate-400 font-medium">Text Input</span>
                        <div className="text-xs font-mono">
                            <span className={text.length > 5000 ? 'text-red-400' : 'text-slate-400'}>{text.length}</span>
                            <span className="text-slate-500"> / 5000 chars</span>
                        </div>
                    </div>
                    <textarea 
                        className="w-full flex-1 min-h-[300px] bg-transparent p-6 text-lg text-white focus:outline-none resize-none placeholder-slate-600"
                        placeholder="Enter your text here. The AI will convert it into lifelike speech..."
                        value={text} onChange={e => setText(e.target.value)}
                    ></textarea>
                </Card>

                {audioUrl && (
                    <Card className="bg-indigo-900/20 border-indigo-500/30">
                        <h3 className="text-sm font-bold text-indigo-400 mb-3 uppercase tracking-wider">Result</h3>
                        <div className="flex flex-col sm:flex-row items-center gap-4">
                            <audio controls src={audioUrl} className="w-full"></audio>
                            <a href={audioUrl} download className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-md text-white whitespace-nowrap transition-colors">
                                <Download size={18} /> Download
                            </a>
                        </div>
                    </Card>
                )}
            </div>
            
            <div className="w-full lg:w-80 flex-shrink-0">
                <Card className="sticky top-8 flex flex-col gap-6">
                    <div>
                        <h3 className="font-bold text-lg mb-4">Voice Settings</h3>
                        <label className="block text-sm text-slate-400 mb-2">Selected Voice</label>
                        <select 
                            className="w-full bg-slate-900 border border-slate-700 rounded-md p-3 text-white mb-3 focus:border-indigo-500 focus:outline-none"
                            value={selectedVoice?.id || ''} onChange={handleVoiceChange}
                        >
                            {voices.map(v => <option key={v.id} value={v.id}>{v.name} ({v.language})</option>)}
                        </select>
                        
                        {selectedVoice && (
                            <div className="bg-slate-900 rounded-lg p-3 border border-slate-800">
                                <div className="flex justify-between items-center mb-2">
                                    <span className="font-medium">{selectedVoice.name}</span>
                                    <button 
                                        onClick={handlePlayPreview}
                                        disabled={previewLoading}
                                        className="text-indigo-400 hover:text-indigo-300 p-1 rounded hover:bg-slate-800 transition-colors"
                                        title="Preview Voice"
                                    >
                                        {previewLoading ? <Loader2 size={16} className="animate-spin" /> : 
                                         playingId === 'preview' ? <Square size={16} fill="currentColor" /> : <Play size={16} fill="currentColor" />}
                                    </button>
                                </div>
                                <div className="text-xs text-slate-400 flex flex-wrap gap-1">
                                    <span className="bg-slate-800 px-1.5 py-0.5 rounded">{selectedVoice.gender}</span>
                                    <span className="bg-slate-800 px-1.5 py-0.5 rounded">{selectedVoice.accent || selectedVoice.locale}</span>
                                    <span className="bg-slate-800 px-1.5 py-0.5 rounded">{selectedVoice.quality_label}</span>
                                </div>
                            </div>
                        )}
                    </div>
                    
                    <div className="pt-4 border-t border-slate-800">
                        <label className="flex justify-between text-sm text-slate-400 mb-2">
                            <span>Speed</span>
                            <span className="text-indigo-400 font-mono">{speed.toFixed(1)}x</span>
                        </label>
                        <input 
                            type="range" min="0.5" max="2.0" step="0.1" 
                            value={speed} onChange={e => setSpeed(parseFloat(e.target.value))}
                            className="w-full accent-indigo-500"
                        />
                        <div className="flex justify-between text-xs text-slate-500 mt-1">
                            <span>Slow</span>
                            <span>Normal</span>
                            <span>Fast</span>
                        </div>
                    </div>

                    <div className="pt-4 mt-auto">
                        <Button onClick={handleGenerate} disabled={loading || !text} className="w-full py-4 text-lg font-bold flex items-center justify-center gap-2">
                            {loading ? <Loader2 className="animate-spin" /> : <RefreshCw size={20} />}
                            {loading ? 'Generating...' : 'Generate Audio'}
                        </Button>
                        <p className="text-center text-xs text-slate-500 mt-3">
                            Uses {text.length} characters of your quota
                        </p>
                    </div>
                </Card>
            </div>
        </div>
    );
};
""",
    "src/pages/VoiceCloning.jsx": """
import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { cloneVoice } from '../api/voices';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { UploadCloud, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';

export const VoiceCloning = () => {
    const [name, setName] = useState('');
    const [description, setDescription] = useState('');
    const [file, setFile] = useState(null);
    const [consent, setConsent] = useState(false);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [isDragOver, setIsDragOver] = useState(false);
    
    const fileInputRef = useRef(null);
    const navigate = useNavigate();

    const handleFileChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragOver(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFile(e.dataTransfer.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!name || !file || !consent) return;
        setLoading(true);
        setMessage('');
        const fd = new FormData();
        fd.append('name', name);
        fd.append('description', description);
        fd.append('file', file);
        fd.append('consent', consent);
        try {
            const res = await cloneVoice(fd);
            setMessage(`Success! Voice "${res.data.name}" cloned.`);
            setTimeout(() => navigate('/voices'), 2000);
        } catch (err) {
            setMessage(err.response?.data?.detail || "Cloning failed. The Coqui TTS engine may be missing or offline.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl mx-auto">
            <h1 className="text-3xl font-bold mb-2">Voice Cloning</h1>
            <p className="text-slate-400 mb-8">Create a custom AI voice from a short audio sample.</p>
            
            <Card className="p-8 border-slate-700">
                <div className="mb-6 bg-slate-800/50 p-4 rounded-lg border border-slate-700 flex items-start gap-3">
                    <AlertCircle className="text-orange-400 mt-0.5 flex-shrink-0" size={20} />
                    <div>
                        <h3 className="font-bold text-orange-400 mb-1">Quality Guidelines</h3>
                        <ul className="text-sm text-slate-300 list-disc pl-4 space-y-1">
                            <li>Provide a clean audio sample without background noise or music.</li>
                            <li>The sample should be between 6 and 20 seconds long.</li>
                            <li>Speak clearly and naturally in the tone you want to capture.</li>
                            <li>Cloning requires the Coqui XTTS-v2 engine to be installed on the backend.</li>
                        </ul>
                    </div>
                </div>
                
                {message && (
                    <div className={`mb-6 p-4 rounded-lg flex items-center gap-3 border ${message.startsWith('Success') ? 'bg-green-500/10 border-green-500/50 text-green-400' : 'bg-red-500/10 border-red-500/50 text-red-400'}`}>
                        {message.startsWith('Success') ? <CheckCircle2 size={20} /> : <AlertCircle size={20} />}
                        <p>{message}</p>
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="flex flex-col gap-4">
                        <Input label="Voice Name" placeholder="e.g. My Custom Voice" value={name} onChange={e => setName(e.target.value)} />
                        <div className="flex flex-col gap-1 mb-4">
                            <label className="text-sm text-slate-400">Description (Optional)</label>
                            <textarea 
                                className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-md text-white focus:outline-none focus:border-indigo-500 resize-none h-24"
                                placeholder="Describe the voice style..."
                                value={description} onChange={e => setDescription(e.target.value)}
                            ></textarea>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm text-slate-400 mb-2">Audio Sample (.wav, .mp3)</label>
                        <div 
                            className={`border-2 border-dashed rounded-xl h-48 flex flex-col items-center justify-center p-6 text-center transition-colors cursor-pointer ${isDragOver ? 'border-indigo-500 bg-indigo-500/10' : 'border-slate-600 hover:border-slate-500 hover:bg-slate-800/50'}`}
                            onDragOver={e => { e.preventDefault(); setIsDragOver(true); }}
                            onDragLeave={() => setIsDragOver(false)}
                            onDrop={handleDrop}
                            onClick={() => fileInputRef.current?.click()}
                        >
                            <input type="file" ref={fileInputRef} accept="audio/*" onChange={handleFileChange} className="hidden" />
                            <UploadCloud className={`mb-3 ${file ? 'text-green-400' : 'text-slate-400'}`} size={40} />
                            {file ? (
                                <div>
                                    <p className="font-medium text-white">{file.name}</p>
                                    <p className="text-xs text-slate-400 mt-1">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                                </div>
                            ) : (
                                <div>
                                    <p className="font-medium text-white mb-1">Click to upload or drag and drop</p>
                                    <p className="text-xs text-slate-400">WAV, MP3, FLAC (Max 50MB)</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                <div className="mt-8 pt-6 border-t border-slate-800">
                    <div className="flex items-start gap-3 mb-6 bg-slate-900 p-4 rounded-lg">
                        <input type="checkbox" id="consent" checked={consent} onChange={e => setConsent(e.target.checked)} className="w-5 h-5 accent-indigo-500 mt-0.5" />
                        <label htmlFor="consent" className="text-sm text-slate-300">
                            I confirm that I have the legal right to clone this voice and that I am not using this technology for deceptive, malicious, or illegal purposes.
                        </label>
                    </div>
                    <div className="flex justify-end">
                        <Button onClick={handleUpload} disabled={loading || !name || !file || !consent} className="py-3 px-8 text-lg flex items-center gap-2">
                            {loading && <Loader2 className="animate-spin" size={20} />}
                            {loading ? 'Cloning in progress...' : 'Clone Voice'}
                        </Button>
                    </div>
                </div>
            </Card>
        </div>
    );
};
"""
}

for filepath, content in files.items():
    full_path = os.path.join("d:/TTS/frontend", filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Phase 3 files successfully built.")

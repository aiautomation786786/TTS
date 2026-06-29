import os

files = {
    "src/pages/VoiceLibrary.jsx": """
import React, { useEffect, useState } from 'react';
import { getVoices } from '../api/voices';
import { Card } from '../components/ui/Card';

export const VoiceLibrary = () => {
    const [voices, setVoices] = useState([]);

    useEffect(() => {
        getVoices().then(res => setVoices(res.data.voices)).catch(console.error);
    }, []);

    return (
        <div className="max-w-6xl mx-auto">
            <h1 className="text-3xl font-bold mb-8">Voice Library</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {voices.map(voice => (
                    <Card key={voice.id} className="hover:border-indigo-500 transition-colors">
                        <div className="flex justify-between items-start mb-2">
                            <h3 className="font-bold text-lg">{voice.name}</h3>
                            <span className="text-xs bg-indigo-500/20 text-indigo-300 px-2 py-1 rounded">{voice.quality_label}</span>
                        </div>
                        <div className="text-sm text-slate-400 mb-4">{voice.language} • {voice.gender}</div>
                        <p className="text-sm text-slate-300 line-clamp-2">{voice.description}</p>
                    </Card>
                ))}
            </div>
        </div>
    );
};
""",
    "src/pages/VoiceCloning.jsx": """
import React, { useState } from 'react';
import { cloneVoice } from '../api/voices';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';

export const VoiceCloning = () => {
    const [name, setName] = useState('');
    const [file, setFile] = useState(null);
    const [consent, setConsent] = useState(false);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');

    const handleUpload = async () => {
        if (!name || !file || !consent) return;
        setLoading(true);
        const fd = new FormData();
        fd.append('name', name);
        fd.append('file', file);
        fd.append('consent', consent);
        try {
            await cloneVoice(fd);
            setMessage("Voice cloned successfully!");
            setName(''); setFile(null); setConsent(false);
        } catch (err) {
            setMessage(err.response?.data?.detail || "Cloning failed. Coqui TTS may be missing.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold mb-8">Voice Cloning</h1>
            <Card>
                <div className="mb-6 bg-slate-800/50 p-4 rounded-lg border border-slate-700">
                    <h3 className="font-bold text-orange-400 mb-2">Notice</h3>
                    <p className="text-sm text-slate-300">
                        Voice cloning requires the Coqui TTS engine to be installed on the backend.
                        If it's not installed, cloning will fail gracefully.
                    </p>
                </div>
                
                {message && <div className="mb-4 text-sm font-bold text-indigo-400">{message}</div>}

                <div className="flex flex-col gap-4">
                    <Input label="Voice Name" value={name} onChange={e => setName(e.target.value)} />
                    <div>
                        <label className="block text-sm text-slate-400 mb-1">Audio Sample (.wav, .mp3)</label>
                        <input type="file" accept="audio/*" onChange={e => setFile(e.target.files[0])} className="text-sm text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-600 file:text-white hover:file:bg-indigo-700" />
                    </div>
                    <div className="flex items-center gap-2 mt-4">
                        <input type="checkbox" id="consent" checked={consent} onChange={e => setConsent(e.target.checked)} className="w-4 h-4 accent-indigo-500" />
                        <label htmlFor="consent" className="text-sm text-slate-300">I confirm I have the right to clone this voice.</label>
                    </div>
                    <Button onClick={handleUpload} disabled={loading || !name || !file || !consent} className="mt-4">
                        {loading ? 'Cloning...' : 'Clone Voice'}
                    </Button>
                </div>
            </Card>
        </div>
    );
};
""",
    "src/pages/History.jsx": """
import React, { useEffect, useState } from 'react';
import { getHistory } from '../api/history';
import { Card } from '../components/ui/Card';

export const History = () => {
    const [history, setHistory] = useState([]);

    useEffect(() => {
        getHistory().then(res => setHistory(res.data.generations)).catch(console.error);
    }, []);

    return (
        <div className="max-w-6xl mx-auto">
            <h1 className="text-3xl font-bold mb-8">Generation History</h1>
            <div className="flex flex-col gap-4">
                {history.length === 0 ? <p className="text-slate-400">No history yet.</p> : history.map(item => (
                    <Card key={item.id} className="flex items-center justify-between">
                        <div className="flex-1">
                            <div className="font-bold mb-1">{item.voice_name}</div>
                            <div className="text-sm text-slate-400 line-clamp-1">{item.text}</div>
                        </div>
                        <div className="flex gap-4 items-center">
                            {item.audio_url && <audio controls src={`http://localhost:8000${item.audio_url}`} className="h-8 w-64"></audio>}
                        </div>
                    </Card>
                ))}
            </div>
        </div>
    );
};
""",
    "src/pages/Settings.jsx": """
import React from 'react';
import { useAuthStore } from '../store/authStore';
import { Card } from '../components/ui/Card';

export const Settings = () => {
    const { user } = useAuthStore();
    return (
        <div className="max-w-3xl mx-auto">
            <h1 className="text-3xl font-bold mb-8">Account Settings</h1>
            <Card>
                <div className="mb-4">
                    <label className="text-sm text-slate-400">Username</label>
                    <div className="font-medium text-lg">{user?.username}</div>
                </div>
                <div className="mb-4">
                    <label className="text-sm text-slate-400">Email</label>
                    <div className="font-medium text-lg">{user?.email}</div>
                </div>
                <div className="mb-4">
                    <label className="text-sm text-slate-400">Role</label>
                    <div className="font-medium text-lg capitalize">{user?.role}</div>
                </div>
            </Card>
        </div>
    );
};
""",
    "src/components/guards/AuthGuard.jsx": """
import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

export const AuthGuard = () => {
    const { isAuthenticated, isLoading } = useAuthStore();
    if (isLoading) return <div>Loading...</div>;
    return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};
""",
    "src/App.jsx": """
import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useAuthStore } from './store/authStore';
import { AppLayout } from './components/layout/AppLayout';
import { AuthGuard } from './components/guards/AuthGuard';

import { Landing } from './pages/Landing';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Dashboard } from './pages/Dashboard';
import { TtsStudio } from './pages/TtsStudio';
import { VoiceLibrary } from './pages/VoiceLibrary';
import { VoiceCloning } from './pages/VoiceCloning';
import { History } from './pages/History';
import { Settings } from './pages/Settings';

export const App = () => {
    const { initialize } = useAuthStore();
    
    useEffect(() => {
        initialize();
    }, []);

    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Landing />} />
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                
                <Route element={<AuthGuard />}>
                    <Route element={<AppLayout />}>
                        <Route path="/dashboard" element={<Dashboard />} />
                        <Route path="/studio" element={<TtsStudio />} />
                        <Route path="/voices" element={<VoiceLibrary />} />
                        <Route path="/clone" element={<VoiceCloning />} />
                        <Route path="/history" element={<History />} />
                        <Route path="/settings" element={<Settings />} />
                    </Route>
                </Route>
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </BrowserRouter>
    );
};
""",
    "src/main.jsx": """
import React from 'react';
import ReactDOM from 'react-dom/client';
import { App } from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
""",
    "vite.config.js": """
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
});
"""
}

for filepath, content in files.items():
    full_path = os.path.join("d:/TTS/frontend", filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Remaining pages and App config created.")

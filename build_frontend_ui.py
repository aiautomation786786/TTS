import os

files = {
    "src/components/ui/Button.jsx": """
import React from 'react';
export const Button = ({ children, variant='primary', onClick, disabled, className='', ...rest }) => {
    const baseClass = "px-4 py-2 rounded-md font-medium transition-all duration-200 cursor-pointer";
    const variants = {
        primary: "bg-indigo-600 text-white hover:bg-indigo-700 shadow-md",
        secondary: "bg-slate-800 text-slate-200 border border-slate-700 hover:bg-slate-700",
        danger: "bg-red-600 text-white hover:bg-red-700",
    };
    return (
        <button 
            className={`${baseClass} ${variants[variant]} ${disabled ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
            onClick={onClick} disabled={disabled} {...rest}
        >
            {children}
        </button>
    );
};
""",
    "src/components/ui/Input.jsx": """
import React from 'react';
export const Input = ({ label, type='text', ...rest }) => (
    <div className="flex flex-col gap-1 mb-4">
        {label && <label className="text-sm text-slate-400">{label}</label>}
        <input 
            type={type}
            className="px-3 py-2 bg-slate-900 border border-slate-700 rounded-md text-white focus:outline-none focus:border-indigo-500"
            {...rest}
        />
    </div>
);
""",
    "src/components/ui/Card.jsx": """
import React from 'react';
export const Card = ({ children, className='' }) => (
    <div className={`bg-[#1a2035] border border-[rgba(255,255,255,0.06)] rounded-xl p-6 shadow-lg ${className}`}>
        {children}
    </div>
);
""",
    "src/components/layout/AppLayout.jsx": """
import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

export const AppLayout = () => {
    const { user, logout } = useAuthStore();
    return (
        <div className="flex h-screen bg-[#0a0e1a] text-slate-200">
            {/* Sidebar */}
            <div className="w-64 bg-[#0f1629] border-r border-slate-800 p-4 flex flex-col">
                <h1 className="text-2xl font-bold text-white mb-8 bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-500">VoxForge</h1>
                <nav className="flex flex-col gap-2 flex-grow">
                    <Link to="/dashboard" className="p-2 rounded hover:bg-slate-800">Dashboard</Link>
                    <Link to="/studio" className="p-2 rounded hover:bg-slate-800">TTS Studio</Link>
                    <Link to="/voices" className="p-2 rounded hover:bg-slate-800">Voice Library</Link>
                    <Link to="/clone" className="p-2 rounded hover:bg-slate-800">Voice Cloning</Link>
                    <Link to="/history" className="p-2 rounded hover:bg-slate-800">History</Link>
                    {user?.role === 'admin' && (
                        <Link to="/admin" className="p-2 rounded hover:bg-slate-800 text-indigo-400 mt-4 border-t border-slate-800 pt-4">Admin Panel</Link>
                    )}
                </nav>
                <div className="p-2 border-t border-slate-800 mt-auto flex justify-between items-center">
                    <span className="text-sm truncate">{user?.username}</span>
                    <button onClick={logout} className="text-xs text-red-400 hover:text-red-300">Logout</button>
                </div>
            </div>
            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                <main className="flex-1 overflow-y-auto p-8">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};
""",
    "src/pages/Landing.jsx": """
import React from 'react';
import { Link } from 'react-router-dom';

export const Landing = () => (
    <div className="min-h-screen bg-[#0a0e1a] text-white flex flex-col items-center justify-center p-8 text-center relative overflow-hidden">
        {/* Decorative background glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-indigo-600 rounded-full blur-[150px] opacity-20 pointer-events-none"></div>
        
        <h1 className="text-6xl font-extrabold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 z-10 relative leading-tight">
            Transform Text Into<br/>Lifelike Speech
        </h1>
        <p className="text-xl text-slate-400 max-w-2xl mb-12 z-10 relative">
            Professional AI-powered text-to-speech with 50+ premium neural voices, 
            voice cloning, and studio-grade audio generation.
        </p>
        <div className="flex gap-4 z-10 relative">
            <Link to="/register" className="px-8 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-bold rounded-lg transition-all shadow-lg shadow-indigo-600/30">
                Get Started Free
            </Link>
            <Link to="/login" className="px-8 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white font-bold rounded-lg transition-all">
                Login
            </Link>
        </div>
    </div>
);
""",
    "src/pages/Login.jsx": """
import React, { useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card } from '../components/ui/Card';

export const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const { loginAction, isLoading } = useAuthStore();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await loginAction(username, password);
            navigate('/dashboard');
        } catch (err) {
            alert('Login failed');
        }
    };

    return (
        <div className="min-h-screen bg-[#0a0e1a] flex items-center justify-center p-4">
            <Card className="w-full max-w-md">
                <h2 className="text-3xl font-bold text-center text-white mb-8">Login to VoxForge</h2>
                <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                    <Input label="Username" value={username} onChange={e => setUsername(e.target.value)} required />
                    <Input label="Password" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
                    <Button type="submit" disabled={isLoading} className="mt-4">
                        {isLoading ? 'Logging in...' : 'Login'}
                    </Button>
                </form>
                <div className="mt-6 text-center text-sm text-slate-400">
                    Don't have an account? <Link to="/register" className="text-indigo-400 hover:underline">Register here</Link>
                </div>
            </Card>
        </div>
    );
};
""",
    "src/pages/Register.jsx": """
import React, { useState } from 'react';
import { register as registerApi } from '../api/auth';
import { useNavigate, Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card } from '../components/ui/Card';

export const Register = () => {
    const [formData, setFormData] = useState({ username: '', email: '', password: '' });
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            await registerApi(formData);
            navigate('/login');
        } catch (err) {
            alert('Registration failed');
        }
    };

    return (
        <div className="min-h-screen bg-[#0a0e1a] flex items-center justify-center p-4">
            <Card className="w-full max-w-md">
                <h2 className="text-3xl font-bold text-center text-white mb-8">Create Account</h2>
                <form onSubmit={handleSubmit} className="flex flex-col gap-4">
                    <Input label="Username" value={formData.username} onChange={e => setFormData({...formData, username: e.target.value})} required />
                    <Input label="Email" type="email" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} required />
                    <Input label="Password" type="password" value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} required />
                    <Button type="submit" className="mt-4">Register</Button>
                </form>
                <div className="mt-6 text-center text-sm text-slate-400">
                    Already have an account? <Link to="/login" className="text-indigo-400 hover:underline">Login here</Link>
                </div>
            </Card>
        </div>
    );
};
""",
    "src/pages/Dashboard.jsx": """
import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { Card } from '../components/ui/Card';
import client from '../api/client';

export const Dashboard = () => {
    const { user } = useAuthStore();
    const [stats, setStats] = useState(null);

    useEffect(() => {
        client.get('/api/users/stats').then(res => setStats(res.data)).catch(console.error);
    }, []);

    if (!user) return null;

    return (
        <div className="max-w-6xl mx-auto">
            <h1 className="text-3xl font-bold mb-8 text-white">Welcome back, {user.username}</h1>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <Card>
                    <div className="text-slate-400 text-sm mb-1">Generations</div>
                    <div className="text-3xl font-bold text-indigo-400">{stats?.generation_count || 0}</div>
                </Card>
                <Card>
                    <div className="text-slate-400 text-sm mb-1">Characters Used</div>
                    <div className="text-3xl font-bold text-purple-400">{stats?.chars_used || 0} / {stats?.char_quota || 0}</div>
                </Card>
                <Card>
                    <div className="text-slate-400 text-sm mb-1">Cloned Voices</div>
                    <div className="text-3xl font-bold text-green-400">{stats?.clone_count || 0}</div>
                </Card>
                <Card>
                    <div className="text-slate-400 text-sm mb-1">Status</div>
                    <div className="text-xl font-bold text-emerald-400 mt-2">Active</div>
                </Card>
            </div>
        </div>
    );
};
""",
    "src/pages/TtsStudio.jsx": """
import React, { useState, useEffect } from 'react';
import { generateSpeech, getVoices } from '../api/tts';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';

export const TtsStudio = () => {
    const [text, setText] = useState('');
    const [voices, setVoices] = useState([]);
    const [selectedVoice, setSelectedVoice] = useState(null);
    const [audioUrl, setAudioUrl] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        getVoices().then(res => {
            setVoices(res.data.voices);
            if(res.data.voices.length > 0) setSelectedVoice(res.data.voices[0].id);
        });
    }, []);

    const handleGenerate = async () => {
        if (!text || !selectedVoice) return;
        setLoading(true);
        try {
            const res = await generateSpeech({ text, voice_id: selectedVoice, speed: 1.0, pitch: "+0Hz" });
            setAudioUrl(`http://localhost:8000${res.data.audio_url}`);
        } catch (err) {
            alert('Generation failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-6xl mx-auto flex flex-col lg:flex-row gap-8">
            <div className="flex-1">
                <h1 className="text-3xl font-bold mb-6">TTS Studio</h1>
                <Card className="mb-6">
                    <textarea 
                        className="w-full h-64 bg-slate-900 border border-slate-700 rounded-lg p-4 text-white focus:outline-none focus:border-indigo-500 resize-none"
                        placeholder="Enter text to generate..."
                        value={text} onChange={e => setText(e.target.value)}
                    ></textarea>
                </Card>
                {audioUrl && (
                    <Card className="flex items-center gap-4">
                        <audio controls src={audioUrl} className="w-full"></audio>
                        <a href={audioUrl} download className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded whitespace-nowrap text-sm font-medium">Download</a>
                    </Card>
                )}
            </div>
            
            <div className="w-full lg:w-80">
                <Card className="sticky top-8">
                    <h3 className="font-bold mb-4 text-lg">Settings</h3>
                    <div className="mb-6">
                        <label className="block text-sm text-slate-400 mb-2">Select Voice</label>
                        <select 
                            className="w-full bg-slate-900 border border-slate-700 rounded-md p-2 text-white"
                            value={selectedVoice || ''} onChange={e => setSelectedVoice(parseInt(e.target.value))}
                        >
                            {voices.map(v => <option key={v.id} value={v.id}>{v.name} ({v.language})</option>)}
                        </select>
                    </div>
                    <Button onClick={handleGenerate} disabled={loading || !text} className="w-full py-3">
                        {loading ? 'Generating...' : 'Generate Audio'}
                    </Button>
                </Card>
            </div>
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

print("UI components and pages created.")

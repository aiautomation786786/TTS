import os

files = {
    "src/pages/Landing.jsx": """
import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';

export const Landing = () => {
    return (
        <div className="min-h-screen bg-slate-950 text-white flex flex-col">
            <header className="p-6 flex justify-between items-center max-w-7xl w-full mx-auto">
                <div className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">VoxForge</div>
                <div className="space-x-4">
                    <Link to="/login" className="text-slate-300 hover:text-white transition-colors">Login</Link>
                    <Link to="/register"><Button>Sign Up</Button></Link>
                </div>
            </header>
            
            <main className="flex-1 flex flex-col items-center justify-center text-center p-6 mt-12 mb-24">
                <div className="inline-block mb-6 px-4 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-sm font-medium">
                    The Next Generation of Local AI Voices
                </div>
                <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8 max-w-4xl leading-tight">
                    Premium Text-to-Speech <br/> <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">For Creators</span>
                </h1>
                <p className="text-lg md:text-xl text-slate-400 max-w-2xl mb-12 leading-relaxed">
                    Generate lifelike, expressive audio for your content using state-of-the-art neural voice models. Clone your voice, browse a premium library, and export high-fidelity audio—all running privately.
                </p>
                <div className="flex gap-4">
                    <Link to="/register"><Button className="px-8 py-4 text-lg">Start Creating Free</Button></Link>
                    <Link to="/login"><Button variant="secondary" className="px-8 py-4 text-lg bg-slate-800 border-slate-700">View Voice Library</Button></Link>
                </div>
            </main>
            
            <div className="w-full bg-slate-900 border-t border-slate-800 py-20 mt-auto">
                <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-12 px-6">
                    <div>
                        <h3 className="text-xl font-bold mb-4 text-white">50+ Premium Voices</h3>
                        <p className="text-slate-400">Curated high-quality neural voices perfect for YouTube, audiobooks, documentaries, and commercials.</p>
                    </div>
                    <div>
                        <h3 className="text-xl font-bold mb-4 text-white">Instant Voice Cloning</h3>
                        <p className="text-slate-400">Upload a 10-second sample and instantly generate audio in your own voice using Coqui XTTS-v2.</p>
                    </div>
                    <div>
                        <h3 className="text-xl font-bold mb-4 text-white">100% Private & Local</h3>
                        <p className="text-slate-400">Run the entire platform on your own hardware. No cloud fees, no usage limits, absolute privacy.</p>
                    </div>
                </div>
            </div>
        </div>
    );
};
""",
    "src/pages/Dashboard.jsx": """
import React, { useEffect, useState } from 'react';
import { useAuthStore } from '../store/authStore';
import { Card } from '../components/ui/Card';
import { Link } from 'react-router-dom';
import { Mic2, PlayCircle, History as HistoryIcon, ArrowRight } from 'lucide-react';

export const Dashboard = () => {
    const { user } = useAuthStore();
    return (
        <div className="max-w-6xl mx-auto">
            <header className="mb-10">
                <h1 className="text-3xl font-bold mb-2">Welcome back, {user?.username}</h1>
                <p className="text-slate-400">What would you like to create today?</p>
            </header>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
                <Link to="/studio" className="block group">
                    <Card className="h-full hover:border-indigo-500/50 transition-all group-hover:-translate-y-1">
                        <div className="w-12 h-12 bg-indigo-500/10 rounded-lg flex items-center justify-center text-indigo-400 mb-4">
                            <PlayCircle size={24} />
                        </div>
                        <h3 className="text-xl font-bold mb-2 flex items-center gap-2">TTS Studio <ArrowRight size={16} className="opacity-0 group-hover:opacity-100 transition-opacity -ml-2 group-hover:ml-0" /></h3>
                        <p className="text-slate-400 text-sm">Generate lifelike speech using our premium neural voices.</p>
                    </Card>
                </Link>
                
                <Link to="/clone" className="block group">
                    <Card className="h-full hover:border-purple-500/50 transition-all group-hover:-translate-y-1">
                        <div className="w-12 h-12 bg-purple-500/10 rounded-lg flex items-center justify-center text-purple-400 mb-4">
                            <Mic2 size={24} />
                        </div>
                        <h3 className="text-xl font-bold mb-2 flex items-center gap-2">Voice Cloning <ArrowRight size={16} className="opacity-0 group-hover:opacity-100 transition-opacity -ml-2 group-hover:ml-0" /></h3>
                        <p className="text-slate-400 text-sm">Create a custom AI voice from a short audio sample.</p>
                    </Card>
                </Link>
                
                <Link to="/history" className="block group">
                    <Card className="h-full hover:border-slate-500/50 transition-all group-hover:-translate-y-1">
                        <div className="w-12 h-12 bg-slate-800 rounded-lg flex items-center justify-center text-slate-400 mb-4">
                            <HistoryIcon size={24} />
                        </div>
                        <h3 className="text-xl font-bold mb-2 flex items-center gap-2">Audio History <ArrowRight size={16} className="opacity-0 group-hover:opacity-100 transition-opacity -ml-2 group-hover:ml-0" /></h3>
                        <p className="text-slate-400 text-sm">Access, download, and manage your previously generated audio.</p>
                    </Card>
                </Link>
            </div>
            
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center">
                <h3 className="text-xl font-bold mb-2">Explore the Voice Library</h3>
                <p className="text-slate-400 mb-6 max-w-xl mx-auto">Browse our curated collection of 50+ premium voices perfect for narration, commercials, and YouTube videos.</p>
                <Link to="/voices">
                    <button className="bg-white text-slate-900 px-6 py-2.5 rounded-md font-medium hover:bg-slate-200 transition-colors">
                        Browse Voices
                    </button>
                </Link>
            </div>
        </div>
    );
};
""",
    "src/pages/History.jsx": """
import React, { useEffect, useState } from 'react';
import { getHistory } from '../api/history';
import { Card } from '../components/ui/Card';
import { Download, Clock, Calendar } from 'lucide-react';

export const History = () => {
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getHistory().then(res => {
            setHistory(res.data.generations);
            setLoading(false);
        }).catch(console.error);
    }, []);

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit'
        });
    };

    return (
        <div className="max-w-6xl mx-auto">
            <h1 className="text-3xl font-bold mb-8">Generation History</h1>
            
            {loading ? (
                <div className="text-slate-400">Loading history...</div>
            ) : history.length === 0 ? (
                <div className="text-center py-16 text-slate-400 bg-slate-900/50 rounded-xl border border-slate-800">
                    <Clock size={48} className="mx-auto mb-4 opacity-50" />
                    <p>No audio generated yet.</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {history.map(item => (
                        <Card key={item.id} className="flex flex-col md:flex-row md:items-center justify-between gap-6 p-6 border-slate-800 bg-slate-900/50 hover:border-slate-700 transition-colors">
                            <div className="flex-1">
                                <div className="flex items-center gap-3 mb-2">
                                    <h3 className="font-bold text-lg">{item.voice_name}</h3>
                                    <span className="text-xs text-slate-500 flex items-center gap-1"><Calendar size={12}/> {formatDate(item.created_at)}</span>
                                </div>
                                <p className="text-sm text-slate-300 line-clamp-2 bg-slate-950 p-3 rounded-md border border-slate-800/50">"{item.text}"</p>
                            </div>
                            <div className="flex flex-col sm:flex-row items-center gap-4">
                                {item.audio_url && <audio controls src={`http://localhost:8000${item.audio_url}`} className="h-10 w-full sm:w-64"></audio>}
                                {item.audio_url && (
                                    <a href={`http://localhost:8000${item.audio_url}`} download className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-md transition-colors" title="Download Audio">
                                        <Download size={20} />
                                    </a>
                                )}
                            </div>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
};
""",
    "src/pages/admin/Dashboard.jsx": """
import React, { useEffect, useState } from 'react';
import client from '../../api/client';
import { Card } from '../../components/ui/Card';
import { Activity, Server, Database, Users, HardDrive } from 'lucide-react';

export const AdminDashboard = () => {
    const [status, setStatus] = useState(null);

    useEffect(() => {
        client.get('/api/admin/status').then(res => setStatus(res.data)).catch(console.error);
    }, []);

    if (!status) return <div>Loading System Status...</div>;

    return (
        <div className="max-w-6xl mx-auto">
            <h1 className="text-3xl font-bold mb-8 flex items-center gap-3"><Server className="text-indigo-500" /> System Status</h1>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
                <Card className="bg-slate-900 border-slate-800">
                    <div className="flex items-center gap-3 mb-2 text-slate-400">
                        <Users size={18} /> <span>Total Users</span>
                    </div>
                    <div className="text-3xl font-bold">{status.metrics.total_users}</div>
                </Card>
                <Card className="bg-slate-900 border-slate-800">
                    <div className="flex items-center gap-3 mb-2 text-slate-400">
                        <Database size={18} /> <span>Total Voices</span>
                    </div>
                    <div className="text-3xl font-bold">{status.metrics.total_voices}</div>
                </Card>
                <Card className="bg-slate-900 border-slate-800">
                    <div className="flex items-center gap-3 mb-2 text-slate-400">
                        <Activity size={18} /> <span>Total Generations</span>
                    </div>
                    <div className="text-3xl font-bold">{status.metrics.total_generations}</div>
                </Card>
                <Card className="bg-slate-900 border-slate-800">
                    <div className="flex items-center gap-3 mb-2 text-slate-400">
                        <HardDrive size={18} /> <span>Storage Used</span>
                    </div>
                    <div className="text-3xl font-bold text-indigo-400">-- MB</div>
                </Card>
            </div>

            <h2 className="text-xl font-bold mb-4">TTS Engines</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {status.engines.map((engine, idx) => (
                    <Card key={idx} className="border-slate-800">
                        <div className="flex justify-between items-start mb-2">
                            <h3 className="font-bold text-lg capitalize">{engine.name}</h3>
                            <span className={`px-2 py-1 rounded text-xs ${engine.available ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'}`}>
                                {engine.available ? 'Available' : 'Unavailable'}
                            </span>
                        </div>
                        <p className="text-sm text-slate-400">{engine.type}</p>
                    </Card>
                ))}
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

print("Phase 4 files successfully built.")

import os

files = {
    "src/components/layout/AppLayout.jsx": """
import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { Toaster } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';

export const AppLayout = () => {
    return (
        <div className="flex h-screen w-full bg-[#0a0e1a] text-slate-300 overflow-hidden">
            <Sidebar />
            <div className="flex-1 flex flex-col min-w-0">
                <Topbar />
                <main className="flex-1 overflow-y-auto p-6 lg:p-8">
                    <AnimatePresence mode="wait">
                        <Outlet />
                    </AnimatePresence>
                </main>
            </div>
            <Toaster 
                position="bottom-right" 
                toastOptions={{
                    duration: 4000,
                    style: { background: '#1e293b', color: '#fff', border: '1px solid #334155' },
                    success: { iconTheme: { primary: '#10b981', secondary: '#fff' } },
                    error: { iconTheme: { primary: '#ef4444', secondary: '#fff' } },
                }} 
            />
        </div>
    );
};
""",
    "src/pages/VoiceLibrary.jsx": """
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getVoices, getVoicePreview } from '../api/voices';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useAudioPlayer } from '../hooks/useAudioPlayer';
import { Play, Square, Loader2, Search, Filter } from 'lucide-react';
import toast from 'react-hot-toast';
import { motion } from 'framer-motion';

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
        }).catch(err => {
            toast.error("Failed to load voices.");
            setLoading(false);
        });
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
            toast.error(err.response?.data?.detail || 'Preview could not be generated. Engine might be unavailable.');
        } finally {
            setLoadingPreviewId(null);
        }
    };

    const handleUseInStudio = (id) => {
        navigate('/studio', { state: { selectedVoiceId: id } });
    };

    const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.05 } } };
    const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } } };

    return (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-7xl mx-auto flex flex-col lg:flex-row gap-8">
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
                                    className="w-full pl-9 pr-3 py-2 bg-slate-900 border border-slate-700 rounded-md text-white focus:outline-none focus:border-indigo-500 transition-colors"
                                    value={filters.search} onChange={e => setFilters({...filters, search: e.target.value})}
                                />
                            </div>
                        </div>
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Gender</label>
                            <select className="w-full bg-slate-900 border border-slate-700 rounded-md p-2 text-white focus:outline-none focus:border-indigo-500 transition-colors" value={filters.gender} onChange={e => setFilters({...filters, gender: e.target.value})}>
                                <option value="">All</option>
                                <option value="Male">Male</option>
                                <option value="Female">Female</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm text-slate-400 mb-1">Language</label>
                            <select className="w-full bg-slate-900 border border-slate-700 rounded-md p-2 text-white focus:outline-none focus:border-indigo-500 transition-colors" value={filters.language} onChange={e => setFilters({...filters, language: e.target.value})}>
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
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-16 text-slate-400">No voices found matching your filters.</motion.div>
                ) : (
                    <motion.div variants={container} initial="hidden" animate="show" className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                        {voices.map(voice => (
                            <motion.div key={voice.id} variants={item} whileHover={{ y: -4 }}>
                                <Card className="flex flex-col h-full hover:border-indigo-500/50 transition-colors group relative overflow-hidden">
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
                                        <motion.button 
                                            whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                                            onClick={() => handlePlayPreview(voice)}
                                            disabled={loadingPreviewId === voice.id}
                                            className="w-10 h-10 rounded-full bg-indigo-600 hover:bg-indigo-700 flex items-center justify-center text-white transition-colors"
                                        >
                                            {loadingPreviewId === voice.id ? <Loader2 size={18} className="animate-spin" /> : 
                                             playingId === voice.id ? <Square size={16} fill="currentColor" /> : <Play size={18} fill="currentColor" className="ml-1" />}
                                        </motion.button>
                                        <Button onClick={() => handleUseInStudio(voice.id)} variant="secondary" className="flex-1 py-2 text-sm">
                                            Use in Studio
                                        </Button>
                                    </div>
                                </Card>
                            </motion.div>
                        ))}
                    </motion.div>
                )}
            </div>
        </motion.div>
    );
};
""",
    "src/pages/Landing.jsx": """
import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from '../components/ui/Button';
import { motion } from 'framer-motion';

export const Landing = () => {
    return (
        <div className="min-h-screen bg-[#0a0e1a] text-white flex flex-col">
            <header className="p-6 flex justify-between items-center max-w-7xl w-full mx-auto relative z-10">
                <div className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400">VoxForge</div>
                <div className="space-x-4">
                    <Link to="/login" className="text-slate-300 hover:text-white transition-colors">Login</Link>
                    <Link to="/register"><Button className="transition-transform hover:scale-105">Sign Up</Button></Link>
                </div>
            </header>
            
            <main className="flex-1 flex flex-col items-center justify-center text-center p-6 mb-24 relative overflow-hidden">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-indigo-500/20 blur-[120px] rounded-full pointer-events-none"></div>
                
                <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8, ease: "easeOut" }} className="relative z-10">
                    <div className="inline-block mb-6 px-4 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-300 text-sm font-medium">
                        The Next Generation of Local AI Voices
                    </div>
                    <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-8 max-w-4xl leading-tight">
                        Premium Text-to-Speech <br/> <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">For Creators</span>
                    </h1>
                    <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto mb-12 leading-relaxed">
                        Generate lifelike, expressive audio for your content using state-of-the-art neural voice models. Clone your voice, browse a premium library, and export high-fidelity audio—all running privately.
                    </p>
                    <div className="flex gap-4 justify-center">
                        <Link to="/register">
                            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                                <Button className="px-8 py-4 text-lg bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 border-none">Start Creating Free</Button>
                            </motion.div>
                        </Link>
                        <Link to="/login">
                            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                                <Button variant="secondary" className="px-8 py-4 text-lg bg-slate-800/80 backdrop-blur-sm border-slate-700 hover:bg-slate-700">View Voice Library</Button>
                            </motion.div>
                        </Link>
                    </div>
                </motion.div>
            </main>
            
            <div className="w-full bg-slate-900 border-t border-slate-800 py-20 mt-auto relative z-10">
                <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-12 px-6">
                    {[
                        { title: "50+ Premium Voices", desc: "Curated high-quality neural voices perfect for YouTube, audiobooks, documentaries, and commercials." },
                        { title: "Instant Voice Cloning", desc: "Upload a 10-second sample and instantly generate audio in your own voice using Coqui XTTS-v2." },
                        { title: "100% Private & Local", desc: "Run the entire platform on your own hardware. No cloud fees, no usage limits, absolute privacy." }
                    ].map((feature, idx) => (
                        <motion.div key={idx} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.1, duration: 0.5 }} viewport={{ once: true }}>
                            <h3 className="text-xl font-bold mb-4 text-white">{feature.title}</h3>
                            <p className="text-slate-400">{feature.desc}</p>
                        </motion.div>
                    ))}
                </div>
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

print("Frontend React UI upgrades finished.")

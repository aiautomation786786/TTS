import React, { useEffect, useState } from 'react';
import { Card } from '../components/ui/Card';
import { Link } from 'react-router-dom';
import { Mic, PlayCircle, History as HistoryIcon, ArrowRight, Server, Activity, CheckCircle2, XCircle, ShieldAlert, Database, HardDrive, Layers } from 'lucide-react';
import client from '../api/client';
import { motion } from 'framer-motion';

export const Dashboard = () => {
    const [stats, setStats] = useState(null);
    const [engineStatus, setEngineStatus] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchDashboardData = () => {
            Promise.all([
                client.get('/api/admin/dashboard'),
                client.get('/api/admin/engine-status')
            ]).then(([statsRes, engineRes]) => {
                setStats(statsRes.data);
                setEngineStatus(engineRes.data);
                setLoading(false);
            }).catch(err => {
                console.error("Failed to load dashboard data", err);
                setLoading(false);
            });
        };

        fetchDashboardData();

        // Automatically poll engine status every 5 seconds
        const interval = setInterval(() => {
            client.get('/api/admin/engine-status')
                .then(res => setEngineStatus(res.data))
                .catch(err => console.error("Polling engine status failed", err));
        }, 5000);

        return () => clearInterval(interval);
    }, []);

    const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.1 } } };
    const item = { hidden: { opacity: 0, y: 15 }, show: { opacity: 1, y: 0 } };

    return (
        <motion.div variants={container} initial="hidden" animate="show" className="max-w-6xl mx-auto flex flex-col gap-5 relative pb-2">
            {/* Premium Background Effects */}
            <div className="absolute -top-20 left-1/4 w-[600px] h-[600px] bg-indigo-500/10 blur-[150px] pointer-events-none"></div>
            <div className="absolute top-40 right-1/4 w-[500px] h-[500px] bg-purple-500/10 blur-[150px] pointer-events-none"></div>

            <header className="relative z-10 flex flex-col gap-1 pt-1 mb-1">
                <h1 className="text-3xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white via-indigo-200 to-slate-400 tracking-tight">Overview</h1>
                <p className="text-slate-400 text-sm font-medium">Your premium text-to-speech and voice cloning workspace.</p>
            </header>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 relative z-10">
                <motion.div variants={item}>
                    <Link to="/studio" className="block group h-full">
                        <Card className="h-full border border-slate-700/60 shadow-[0_8px_30px_rgb(0,0,0,0.4)] bg-gradient-to-b from-slate-900/90 to-slate-950/90 backdrop-blur-xl rounded-2xl hover:border-indigo-500/50 hover:shadow-[0_8px_30px_rgb(99,102,241,0.15)] transition-all duration-300 group-hover:-translate-y-1 p-5 overflow-hidden relative">
                            <div className="absolute -inset-1 bg-gradient-to-br from-indigo-500/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-500 pointer-events-none"></div>
                            <div className="relative z-10">
                                <div className="w-12 h-12 bg-indigo-500/10 rounded-2xl flex items-center justify-center text-indigo-400 mb-4 border border-indigo-500/20 shadow-inner group-hover:scale-110 group-hover:bg-indigo-500/20 group-hover:shadow-[0_0_15px_rgba(79,70,229,0.3)] transition-all duration-300">
                                    <PlayCircle size={24} />
                                </div>
                                <h3 className="text-lg font-extrabold text-white mb-2 group-hover:text-indigo-300 transition-colors tracking-tight">TTS Studio</h3>
                                <p className="text-slate-400 text-sm leading-relaxed font-medium">Synthesize ultra-realistic speech with advanced neural voice models.</p>
                            </div>
                        </Card>
                    </Link>
                </motion.div>
                
                <motion.div variants={item}>
                    <Link to="/clone" className="block group h-full">
                        <Card className="h-full border border-slate-700/60 shadow-[0_8px_30px_rgb(0,0,0,0.4)] bg-gradient-to-b from-slate-900/90 to-slate-950/90 backdrop-blur-xl rounded-2xl hover:border-purple-500/50 hover:shadow-[0_8px_30px_rgb(168,85,247,0.15)] transition-all duration-300 group-hover:-translate-y-1 p-5 overflow-hidden relative">
                            <div className="absolute -inset-1 bg-gradient-to-br from-purple-500/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-500 pointer-events-none"></div>
                            <div className="relative z-10">
                                <div className="w-12 h-12 bg-purple-500/10 rounded-2xl flex items-center justify-center text-purple-400 mb-4 border border-purple-500/20 shadow-inner group-hover:scale-110 group-hover:bg-purple-500/20 group-hover:shadow-[0_0_15px_rgba(168,85,247,0.3)] transition-all duration-300">
                                    <Mic size={24} />
                                </div>
                                <h3 className="text-lg font-extrabold text-white mb-2 group-hover:text-purple-300 transition-colors tracking-tight">Voice Cloning</h3>
                                <p className="text-slate-400 text-sm leading-relaxed font-medium">Instantly clone any voice with just a 5-second audio sample.</p>
                            </div>
                        </Card>
                    </Link>
                </motion.div>
                
                <motion.div variants={item}>
                    <Link to="/history" className="block group h-full">
                        <Card className="h-full border border-slate-700/60 shadow-[0_8px_30px_rgb(0,0,0,0.4)] bg-gradient-to-b from-slate-900/90 to-slate-950/90 backdrop-blur-xl rounded-2xl hover:border-emerald-500/50 hover:shadow-[0_8px_30px_rgb(16,185,129,0.15)] transition-all duration-300 group-hover:-translate-y-1 p-5 overflow-hidden relative">
                            <div className="absolute -inset-1 bg-gradient-to-br from-emerald-500/10 via-transparent to-transparent opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-500 pointer-events-none"></div>
                            <div className="relative z-10">
                                <div className="w-12 h-12 bg-emerald-500/10 rounded-2xl flex items-center justify-center text-emerald-400 mb-4 border border-emerald-500/20 shadow-inner group-hover:scale-110 group-hover:bg-emerald-500/20 group-hover:shadow-[0_0_15px_rgba(16,185,129,0.3)] transition-all duration-300">
                                    <HistoryIcon size={24} />
                                </div>
                                <h3 className="text-lg font-extrabold text-white mb-2 group-hover:text-emerald-300 transition-colors tracking-tight">Audio History</h3>
                                <p className="text-slate-400 text-sm leading-relaxed font-medium">Access, download, and manage your previously generated audio files.</p>
                            </div>
                        </Card>
                    </Link>
                </motion.div>
            </div>

            {loading ? (
                <motion.div variants={item} className="grid grid-cols-2 md:grid-cols-4 gap-5 relative z-10 pt-4">
                    {[1, 2, 3, 4].map(i => (
                        <Card key={i} className="border border-slate-700/60 bg-slate-900/40 backdrop-blur-xl rounded-2xl p-5 shadow-lg">
                            <div className="h-3 bg-slate-800 rounded w-24 mb-4 animate-pulse"></div>
                            <div className="h-8 bg-slate-700/50 rounded w-20 animate-pulse"></div>
                        </Card>
                    ))}
                </motion.div>
            ) : stats && (
                <motion.div variants={item} className="grid grid-cols-2 md:grid-cols-4 gap-5 relative z-10 pt-4">
                    <Card className="border border-slate-700/60 shadow-[0_8px_30px_rgb(0,0,0,0.3)] bg-gradient-to-b from-slate-900/80 to-slate-950/80 backdrop-blur-xl rounded-2xl p-5 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-24 h-24 bg-indigo-500/5 rounded-bl-[100px] group-hover:bg-indigo-500/10 transition-colors"></div>
                        <div className="flex items-center gap-2 mb-2 text-slate-400 relative z-10">
                            <Activity size={16} className="text-indigo-400 drop-shadow-[0_0_8px_rgba(99,102,241,0.5)]" />
                            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-300">Generations</span>
                        </div>
                        <div className="text-3xl font-extrabold text-white relative z-10">{stats.total_generations}</div>
                    </Card>
                    <Card className="border border-slate-700/60 shadow-[0_8px_30px_rgb(0,0,0,0.3)] bg-gradient-to-b from-slate-900/80 to-slate-950/80 backdrop-blur-xl rounded-2xl p-5 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-24 h-24 bg-purple-500/5 rounded-bl-[100px] group-hover:bg-purple-500/10 transition-colors"></div>
                        <div className="flex items-center gap-2 mb-2 text-slate-400 relative z-10">
                            <Database size={16} className="text-purple-400 drop-shadow-[0_0_8px_rgba(168,85,247,0.5)]" />
                            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-300">Total Voices</span>
                        </div>
                        <div className="text-3xl font-extrabold text-white relative z-10">{stats.total_voices}</div>
                    </Card>
                    <Card className="border border-slate-700/60 shadow-[0_8px_30px_rgb(0,0,0,0.3)] bg-gradient-to-b from-slate-900/80 to-slate-950/80 backdrop-blur-xl rounded-2xl p-5 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-24 h-24 bg-emerald-500/5 rounded-bl-[100px] group-hover:bg-emerald-500/10 transition-colors"></div>
                        <div className="flex items-center gap-2 mb-2 text-slate-400 relative z-10">
                            <HardDrive size={16} className="text-emerald-400 drop-shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
                            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-300">Audio Storage</span>
                        </div>
                        <div className="text-3xl font-extrabold text-white relative z-10">{(stats.total_storage / 1024 / 1024).toFixed(1)} <span className="text-lg text-slate-500 font-bold">MB</span></div>
                    </Card>
                    <Card className="border border-slate-700/60 shadow-[0_8px_30px_rgb(0,0,0,0.3)] bg-gradient-to-b from-slate-900/80 to-slate-950/80 backdrop-blur-xl rounded-2xl p-5 relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-24 h-24 bg-pink-500/5 rounded-bl-[100px] group-hover:bg-pink-500/10 transition-colors"></div>
                        <div className="flex items-center gap-2 mb-2 text-slate-400 relative z-10">
                            <Layers size={16} className="text-pink-400 drop-shadow-[0_0_8px_rgba(244,114,182,0.5)]" />
                            <span className="text-[11px] font-bold uppercase tracking-wider text-slate-300">Total Chars</span>
                        </div>
                        <div className="text-3xl font-extrabold text-white relative z-10">{stats.total_characters?.toLocaleString() || 0}</div>
                    </Card>
                </motion.div>
            )}

            {/* Engine Summary */}
            {loading ? (
                <motion.div variants={item} className="relative z-10 pt-4 pb-4">
                    <h2 className="text-xl font-extrabold tracking-tight mb-4 flex items-center gap-2 text-slate-500">
                        <div className="w-5 h-5 rounded-full bg-slate-800 animate-pulse"></div>
                        <div className="h-6 bg-slate-800 rounded w-56 animate-pulse"></div>
                    </h2>
                    <Card className="border border-slate-700/60 p-0 overflow-hidden bg-slate-900/40 backdrop-blur-xl shadow-[0_8px_30px_rgb(0,0,0,0.3)] rounded-2xl">
                        <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-slate-700/50">
                            {[1, 2, 3].map(i => (
                                <div key={i} className="p-6">
                                    <div className="h-5 bg-slate-800 rounded w-36 mb-4 animate-pulse"></div>
                                    <div className="h-6 bg-slate-800/50 rounded w-24 animate-pulse"></div>
                                </div>
                            ))}
                        </div>
                    </Card>
                </motion.div>
            ) : engineStatus && (
                <motion.div variants={item} className="relative z-10 pt-4 pb-4">
                    <h2 className="text-xl font-extrabold tracking-tight mb-4 flex items-center gap-2 text-white">
                        <Server className="text-indigo-400" size={20} /> System Engine Status
                    </h2>
                    <Card className="border border-slate-700/60 p-0 overflow-hidden bg-gradient-to-b from-slate-900/90 to-slate-950/90 backdrop-blur-xl shadow-[0_8px_30px_rgb(0,0,0,0.4)] rounded-2xl">
                        <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-slate-700/50">
                            {engineStatus.engines.map((engine, idx) => (
                                <div key={idx} className="p-6 hover:bg-white/[0.02] transition-colors relative group">
                                    <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                                    <div className="relative z-10 flex justify-between items-start mb-4">
                                        <h3 className="font-bold text-base text-white">{engine.name}</h3>
                                        {engine.available ? 
                                            <CheckCircle2 size={20} className="text-emerald-400 drop-shadow-[0_0_10px_rgba(16,185,129,0.5)]" /> : 
                                            <XCircle size={20} className="text-red-400 drop-shadow-[0_0_10px_rgba(239,68,68,0.5)]" />
                                        }
                                    </div>
                                    <span className={`relative z-10 text-[11px] font-bold uppercase tracking-widest px-2.5 py-1 rounded-md shadow-inner inline-block ${engine.available ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-red-500/10 text-red-400 border border-red-500/30'}`}>
                                        {engine.available ? 'Operational' : 'Failed'}
                                    </span>
                                </div>
                            ))}
                            <div className="p-6 hover:bg-white/[0.02] transition-colors relative group">
                                <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
                                <div className="relative z-10 flex justify-between items-start mb-4">
                                    <h3 className="font-bold text-base text-white">Coqui XTTS Neural</h3>
                                    {engineStatus.coqui_status.model_available ? 
                                        <CheckCircle2 size={20} className="text-emerald-400 drop-shadow-[0_0_10px_rgba(16,185,129,0.5)]" /> : 
                                        <ShieldAlert size={20} className="text-amber-400 drop-shadow-[0_0_10px_rgba(245,158,11,0.5)]" />
                                    }
                                </div>
                                <span className={`relative z-10 text-[11px] font-bold uppercase tracking-widest px-2.5 py-1 rounded-md shadow-inner inline-block ${engineStatus.coqui_status.model_available ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'}`}>
                                    {engineStatus.coqui_status.model_available ? 'Operational' : 'Booting / Sleeping'}
                                </span>
                            </div>
                        </div>
                    </Card>
                </motion.div>
            )}
        </motion.div>
    );
};

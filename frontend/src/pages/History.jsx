import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { getHistory, deleteGeneration, toggleFavorite } from '../api/history';
import { retryLongFormJob } from '../api/tts';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Download, Clock, Calendar, Heart, Trash2, Filter, Layers, Mic, RefreshCw, AlertCircle, PlayCircle, HardDrive, Zap } from 'lucide-react';
import toast from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';

export const History = () => {
    const [searchParams, setSearchParams] = useSearchParams();
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [total, setTotal] = useState(0);
    const [itemToDelete, setItemToDelete] = useState(null);

    const page = parseInt(searchParams.get('page')) || 1;
    // Filters
    const mode = searchParams.get('mode');
    const [showFavorites, setShowFavorites] = useState(false);

    useEffect(() => {
        loadHistory();
    }, [searchParams, showFavorites]);

    const loadHistory = async () => {
        setLoading(true);
        try {
            const params = {};
            if (mode) params.mode = mode;
            if (showFavorites) params.is_favorite = true;
            
            const res = await getHistory(params);
            setHistory(res.data.generations);
            setTotal(res.data.total);
        } catch (err) {
            toast.error("Failed to load history");
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteClick = (id) => {
        setItemToDelete(id);
    };

    const confirmDelete = async () => {
        if (!itemToDelete) return;
        const id = itemToDelete;
        setItemToDelete(null);
        try {
            await deleteGeneration(id);
            setHistory(history.filter(g => g.id !== id));
            toast.success("Deleted successfully");
        } catch (err) {
            toast.error("Failed to delete");
        }
    };

    const cancelDelete = () => {
        setItemToDelete(null);
    };

    const handleRetry = async (id) => {
        try {
            await retryLongFormJob(id);
            toast.success("Job retry started! Please wait.");
            loadHistory();
        } catch (err) {
            toast.error("Failed to retry job");
        }
    };

    const handleToggleFavorite = async (id, currentStatus) => {
        try {
            await toggleFavorite(id, !currentStatus);
            setHistory(history.map(h => h.id === id ? { ...h, is_favorite: !currentStatus } : h));
        } catch (err) {
            toast.error("Failed to update favorite");
        }
    };

    const formatDate = (dateString) => {
        return new Date(dateString).toLocaleDateString('en-US', {
            month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit'
        });
    };
    
    const formatTime = (seconds) => {
        if (!seconds) return '0s';
        if (seconds < 60) return `${seconds.toFixed(1)}s`;
        return `${Math.floor(seconds/60)}m ${Math.floor(seconds%60)}s`;
    };

    const clearFilters = () => {
        setSearchParams({});
        setShowFavorites(false);
    };

    const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.1 } } };
    const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } } };

    return (
        <div className="max-w-6xl mx-auto space-y-8 relative pb-20">
            {/* Background elements */}
            <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-indigo-600/5 rounded-full mix-blend-screen filter blur-[120px] pointer-events-none"></div>
            <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-pink-600/5 rounded-full mix-blend-screen filter blur-[120px] pointer-events-none"></div>

            <header className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b border-white/5 pb-6">
                <div className="space-y-2">
                    <h1 className="text-3xl font-bold flex items-center gap-3 text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 tracking-tight">
                        <div className="p-2 bg-white/5 rounded-xl border border-white/10 shadow-[0_0_15px_rgba(255,255,255,0.05)] text-white">
                            <Clock size={24} />
                        </div>
                        Audio History
                    </h1>
                    <p className="text-slate-400 ml-1">Review, download, and manage your synthesized speech assets.</p>
                </div>
                
                <div className="flex items-center gap-3 bg-black/20 p-1.5 rounded-xl border border-white/5 shadow-inner">
                    <button 
                        onClick={() => setShowFavorites(!showFavorites)} 
                        className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all flex items-center gap-2 ${showFavorites ? 'bg-gradient-to-r from-pink-500 to-rose-500 text-white shadow-[0_0_15px_rgba(236,72,153,0.3)]' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
                    >
                        <Heart size={16} className={showFavorites ? "fill-white" : ""} /> Favorites
                    </button>
                    {(mode) && (
                        <button onClick={clearFilters} className="px-4 py-2 rounded-lg text-sm font-semibold transition-all text-slate-400 hover:text-white hover:bg-white/5 flex items-center gap-2">
                            <Filter size={16} /> Clear Filters
                        </button>
                    )}
                </div>
            </header>
            
            {(mode) && (
                <div className="flex flex-wrap gap-2 text-sm">
                    {mode && <span className="bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 px-3 py-1 rounded-full capitalize font-medium flex items-center gap-1.5"><Layers size={14} /> Mode: {mode.replace('_', ' ')}</span>}
                </div>
            )}

            {loading ? (
                <div className="flex flex-col items-center justify-center py-24 space-y-4">
                    <RefreshCw className="animate-spin text-indigo-500" size={32} />
                    <p className="text-slate-400 font-medium">Loading temporal archives...</p>
                </div>
            ) : (history || []).length === 0 ? (
                <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="relative z-10">
                    <Card className="flex flex-col items-center justify-center py-24 text-slate-400 bg-white/[0.02] border-white/10 backdrop-blur-md rounded-2xl shadow-xl">
                        <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center mb-4 border border-white/5 shadow-inner">
                            <Clock size={32} className="opacity-50" />
                        </div>
                        <h3 className="text-xl font-bold text-slate-300 mb-2">No History Found</h3>
                        <p className="text-sm">You haven't generated any audio matching these filters yet.</p>
                        {showFavorites && <Button className="mt-6 border-white/10 text-white hover:bg-white/10" variant="outline" onClick={clearFilters}>View All History</Button>}
                    </Card>
                </motion.div>
            ) : (
                <motion.div variants={container} initial="hidden" animate="show" className="grid grid-cols-1 lg:grid-cols-2 gap-6 relative z-10">
                    {(history || []).map(gen => (
                        <motion.div variants={item} key={gen.id} className="h-full">
                            <Card className="h-full flex flex-col p-0 border-white/10 bg-white/[0.02] backdrop-blur-xl hover:bg-white/[0.04] hover:border-white/20 transition-all duration-300 shadow-xl rounded-2xl overflow-hidden group">
                                
                                {/* Top Bar */}
                                <div className="px-5 py-4 border-b border-white/5 flex justify-between items-center bg-black/20">
                                    <div className="flex items-center gap-3">
                                        <button 
                                            onClick={() => handleToggleFavorite(gen.id, gen.is_favorite)}
                                            className="text-slate-500 hover:text-pink-500 hover:scale-110 transition-all"
                                        >
                                            <Heart size={18} className={gen.is_favorite ? "fill-pink-500 text-pink-500" : ""} />
                                        </button>
                                        <div className="flex flex-col">
                                            <span className="font-bold text-white tracking-wide group-hover:text-indigo-300 transition-colors">{gen.voice_name}</span>
                                            <span className="text-[10px] text-slate-500 flex items-center gap-1 font-mono uppercase tracking-wider"><Calendar size={10}/> {formatDate(gen.created_at)}</span>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {gen.mode === 'long_form' ? (
                                            <span className="text-[10px] font-bold uppercase tracking-widest bg-purple-500/10 text-purple-400 px-2 py-1 rounded flex items-center gap-1.5 border border-purple-500/20"><Layers size={12}/> Long Form</span>
                                        ) : (
                                            <span className="text-[10px] font-bold uppercase tracking-widest bg-indigo-500/10 text-indigo-400 px-2 py-1 rounded flex items-center gap-1.5 border border-indigo-500/20"><Zap size={12}/> Short Form</span>
                                        )}
                                    </div>
                                </div>

                                {/* Content Body */}
                                <div className="p-5 flex-1 flex flex-col space-y-4">
                                    <div className="relative">
                                        <div className="absolute -left-2 text-3xl text-white/5 font-serif top-0">"</div>
                                        <p className="text-sm text-slate-300 line-clamp-3 leading-relaxed relative z-10 px-2 italic">
                                            {gen.text}
                                        </p>
                                    </div>
                                    
                                    <div className="flex flex-wrap gap-4 mt-auto pt-4 border-t border-white/5">
                                        {gen.generation_time_seconds && (
                                            <div className="flex items-center gap-1.5 text-xs text-slate-400 bg-white/5 px-2.5 py-1 rounded border border-white/5">
                                                <RefreshCw size={12} className="text-slate-500" /> Gen: <span className="font-mono text-slate-300">{formatTime(gen.generation_time_seconds)}</span>
                                            </div>
                                        )}
                                        {gen.audio_duration && (
                                            <div className="flex items-center gap-1.5 text-xs text-slate-400 bg-white/5 px-2.5 py-1 rounded border border-white/5">
                                                <PlayCircle size={12} className="text-slate-500" /> Len: <span className="font-mono text-slate-300">{formatTime(gen.audio_duration)}</span>
                                            </div>
                                        )}
                                        {gen.file_size && (
                                            <div className="flex items-center gap-1.5 text-xs text-slate-400 bg-white/5 px-2.5 py-1 rounded border border-white/5">
                                                <HardDrive size={12} className="text-slate-500" /> Size: <span className="font-mono text-slate-300">{(gen.file_size / 1024).toFixed(1)} KB</span>
                                            </div>
                                        )}
                                    </div>
                                </div>

                                {/* Bottom Player/Controls */}
                                <div className="px-5 py-4 bg-black/40 border-t border-white/5 flex flex-col sm:flex-row items-center gap-4">
                                    {gen.status === 'completed' && gen.audio_url ? (
                                        <>
                                            <div className="flex-1 w-full bg-white/5 rounded-lg p-1 border border-white/10 shadow-inner">
                                                <audio controls src={`http://localhost:8000${gen.audio_url}`} className="h-9 w-full outline-none invert opacity-90 sepia-[20%] hue-rotate-[180deg]"></audio>
                                            </div>
                                            <div className="flex gap-2">
                                                <a href={`http://localhost:8000/api/history/${gen.id}/download?format=mp3`} className="w-9 h-9 flex items-center justify-center bg-white/5 hover:bg-indigo-500 hover:text-white border border-white/10 hover:border-indigo-400 text-slate-400 rounded-lg transition-all shadow-sm" title="Download MP3">
                                                    <Download size={16} />
                                                </a>
                                                <a href={`http://localhost:8000/api/history/${gen.id}/download?format=wav`} className="w-9 h-9 flex items-center justify-center bg-white/5 hover:bg-purple-500 hover:text-white border border-white/10 hover:border-purple-400 text-slate-400 rounded-lg transition-all shadow-sm" title="Download WAV">
                                                    <Download size={16} />
                                                </a>
                                                <button 
                                                    onClick={() => handleDeleteClick(gen.id)}
                                                    className="p-2.5 bg-slate-800/80 hover:bg-red-500/20 text-slate-400 hover:text-red-400 rounded-xl transition-all border border-slate-700 hover:border-red-500/50 shadow-sm group"
                                                    title="Delete"
                                                >
                                                    <Trash2 size={16} className="group-hover:scale-110 transition-transform" />
                                                </button>
                                            </div>
                                        </>
                                    ) : (
                                        <div className="flex items-center justify-between w-full">
                                            <div className="flex items-center gap-3">
                                                <div className={`text-[10px] px-3 py-1.5 rounded font-bold uppercase tracking-widest border shadow-inner ${
                                                    gen.status === 'failed' ? 'bg-red-500/10 text-red-400 border-red-500/20' : 
                                                    'bg-amber-500/10 text-amber-400 border-amber-500/20 flex items-center gap-2'
                                                }`}>
                                                    {gen.status === 'processing' && <RefreshCw size={10} className="animate-spin" />}
                                                    {gen.status} {gen.mode === 'long_form' && gen.status !== 'failed' && `(${(gen.progress || 0).toFixed(0)}%)`}
                                                </div>
                                            </div>
                                            <div className="flex gap-2">
                                                {gen.status === 'failed' && (
                                                    <button onClick={() => handleRetry(gen.id)} className="w-9 h-9 flex items-center justify-center bg-white/5 hover:bg-blue-500 hover:text-white border border-white/10 hover:border-blue-400 text-slate-400 rounded-lg transition-all shadow-sm" title="Retry">
                                                        <RefreshCw size={16} />
                                                    </button>
                                                )}
                                                <button onClick={() => handleDeleteClick(gen.id)} className="w-9 h-9 flex items-center justify-center bg-white/5 hover:bg-red-500 hover:text-white border border-white/10 hover:border-red-400 text-slate-400 rounded-lg transition-all shadow-sm" title="Delete">
                                                    <Trash2 size={16} />
                                                </button>
                                            </div>
                                        </div>
                                    )}
                                </div>
                                
                                {/* Error Section if Failed */}
                                {gen.status === 'failed' && gen.failed_engine_error && (
                                    <div className="px-5 py-3 bg-red-950/40 border-t border-red-500/20 text-xs font-mono text-red-300 w-full overflow-hidden shadow-inner">
                                        <div className="font-bold mb-1.5 flex items-center gap-1.5 text-red-400">
                                            <AlertCircle size={14} /> Chunk {gen.failed_chunk_index !== null ? gen.failed_chunk_index + 1 : '?'} Failed
                                        </div>
                                        <div className="p-2 bg-black/60 rounded border border-red-900/50 break-words text-[10px] leading-relaxed">
                                            {gen.failed_engine_error}
                                        </div>
                                        {gen.failed_chunk_text_preview && (
                                            <>
                                                <div className="font-bold text-[10px] text-slate-500 mt-2 mb-1 uppercase tracking-wider">Chunk Text Preview</div>
                                                <div className="p-2 bg-black/60 rounded border border-white/5 text-slate-400 break-words text-[10px] leading-relaxed italic">
                                                    {gen.failed_chunk_text_preview}
                                                </div>
                                            </>
                                        )}
                                    </div>
                                )}
                            </Card>
                        </motion.div>
                    ))}
                </motion.div>
            )}

            {/* Professional Delete Confirmation Modal */}
            <AnimatePresence>
                {itemToDelete && (
                    <motion.div 
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm p-4"
                    >
                        <motion.div 
                            initial={{ scale: 0.95, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.95, opacity: 0, y: 20 }}
                            className="bg-slate-900 border border-slate-700/60 rounded-2xl p-6 max-w-md w-full shadow-[0_20px_60px_-15px_rgba(0,0,0,0.7)]"
                        >
                            <div className="flex items-center gap-4 mb-4">
                                <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center flex-shrink-0 border border-red-500/20">
                                    <Trash2 className="text-red-400" size={24} />
                                </div>
                                <div>
                                    <h3 className="text-xl font-bold text-white mb-1">Delete Generation</h3>
                                    <p className="text-slate-400 text-sm">Are you sure you want to permanently delete this audio? This action cannot be undone.</p>
                                </div>
                            </div>
                            <div className="flex justify-end gap-3 mt-6">
                                <Button variant="secondary" onClick={cancelDelete} className="px-5">Cancel</Button>
                                <Button onClick={confirmDelete} className="px-5 bg-red-500 hover:bg-red-600 text-white border-red-600 shadow-[0_0_15px_rgba(239,68,68,0.3)]">Yes, Delete</Button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
};

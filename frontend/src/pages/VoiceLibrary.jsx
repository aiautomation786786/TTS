import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getVoices, getVoicePreview, deleteClonedVoice } from '../api/voices';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useAudioPlayer } from '../hooks/useAudioPlayer';
import { Play, Square, Loader2, Search, Filter, X, Mic, Trash2, CheckSquare } from 'lucide-react';
import toast from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import { getLanguages } from '../api/tts';

const USE_CASES = [
    "Documentary", "Horror", "YouTube", "Audiobook", "Storytelling",
    "Commercial", "Podcast", "News", "Education", "Explainer",
    "Meditation", "Motivation", "Kids", "Gaming", "Trailer",
    "Cinematic", "Social Media", "Drama", "Suspense",
    "Professional Corporate", "Emotional Narration"
].sort();

export const VoiceLibrary = () => {
    const [voices, setVoices] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({ search: '', gender: '', language: '', category: '', use_case: '', is_cloned: undefined });
    const { playingId, play } = useAudioPlayer();
    const [loadingPreviewId, setLoadingPreviewId] = useState(null);
    const [itemsToDelete, setItemsToDelete] = useState([]);
    const [selectedVoices, setSelectedVoices] = useState(new Set());
    const [isDeleting, setIsDeleting] = useState(false);
    const navigate = useNavigate();
    const [availableLanguages, setAvailableLanguages] = useState([]);

    useEffect(() => {
        getLanguages().then(res => {
            const uniqueLangs = [...new Set(res.data.map(l => l.name))].filter(Boolean).sort();
            setAvailableLanguages(uniqueLangs);
        }).catch(err => console.error("Failed to fetch languages"));
    }, []);

    useEffect(() => {
        setLoading(true);
        const params = new URLSearchParams();
        if (filters.search) params.append('search', filters.search);
        if (filters.gender) params.append('gender', filters.gender);
        if (filters.language) params.append('language', filters.language);
        if (filters.category) params.append('category', filters.category);
        if (filters.use_case) params.append('use_case', filters.use_case);
        if (filters.is_cloned !== undefined) params.append('is_cloned', filters.is_cloned);
        params.append('per_page', 500);
        
        getVoices(params).then(res => {
            const validVoices = res.data.voices.filter(v => v.category !== 'temporary');
            setVoices(validVoices);
            setSelectedVoices(new Set());
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
        
        if (voice.is_cloned && voice.preview_status !== 'ready') {
            toast('Warming up neural model for cloned voice. This may take a moment...', {
                icon: '⏳',
                style: { borderRadius: '10px', background: '#1e293b', color: '#fff' },
                duration: 5000
            });
        }

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

    const toggleSelection = (id) => {
        const newSet = new Set(selectedVoices);
        if (newSet.has(id)) newSet.delete(id);
        else newSet.add(id);
        setSelectedVoices(newSet);
    };

    const toggleSelectAll = () => {
        const clonedVoices = voices.filter(v => v.is_cloned);
        if (selectedVoices.size === clonedVoices.length && clonedVoices.length > 0) {
            setSelectedVoices(new Set());
        } else {
            setSelectedVoices(new Set(clonedVoices.map(v => v.id)));
        }
    };

    const handleBulkDeleteClick = () => {
        setItemsToDelete(Array.from(selectedVoices));
    };

    const handleDeleteVoice = (id) => {
        setItemsToDelete([id]);
    };

    const confirmDelete = async () => {
        if (itemsToDelete.length === 0) return;
        setIsDeleting(true);
        try {
            await Promise.all(itemsToDelete.map(id => deleteClonedVoice(id)));
            toast.success(`Deleted ${itemsToDelete.length} voice(s) successfully`);
            setVoices(voices.filter(v => !itemsToDelete.includes(v.id)));
            
            const newSet = new Set(selectedVoices);
            itemsToDelete.forEach(id => newSet.delete(id));
            setSelectedVoices(newSet);
        } catch (err) {
            toast.error("Failed to delete voice(s)");
        } finally {
            setIsDeleting(false);
            setItemsToDelete([]);
        }
    };

    const resetFilters = () => {
        setFilters({ search: '', gender: '', language: '', category: '', use_case: '', is_cloned: undefined });
    };

    const parseTags = (jsonString) => {
        try {
            return jsonString ? JSON.parse(jsonString) : [];
        } catch {
            return [];
        }
    };

    const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.05 } } };
    const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } } };

    // Check if we requested a use_case and language, but didn't find exact matches (fallback handling)
    const hasExactMatch = voices.some(v => parseTags(v.use_case_tags).includes(filters.use_case));
    const showFallbackMessage = filters.use_case && filters.language && !hasExactMatch && voices.length > 0;

    return (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="max-w-7xl mx-auto flex flex-col lg:flex-row gap-8">
            {/* Sidebar Filters */}
            <div className="w-full lg:w-72 flex-shrink-0 relative">
                <div className="absolute top-0 right-0 w-full h-full bg-gradient-to-b from-indigo-500/5 to-purple-500/5 blur-3xl pointer-events-none"></div>
                <Card className="sticky top-8 border-slate-200 dark:border-slate-800/60 shadow-[0_8px_30px_rgb(0,0,0,0.4)] bg-gradient-to-b from-slate-900/95 to-slate-950/95 backdrop-blur-xl relative z-10">
                    <div className="flex justify-between items-center mb-6 pb-4 border-b border-slate-200 dark:border-slate-800">
                        <h2 className="text-lg font-extrabold text-slate-900 dark:text-white flex items-center gap-2.5 tracking-tight"><Filter size={18} className="text-indigo-400"/> Filters</h2>
                        {Object.values(filters).some(v => v !== '') && (
                            <button onClick={resetFilters} className="text-xs font-bold text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:text-white bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 px-3 py-1.5 rounded-md transition-all flex items-center gap-1.5 border border-slate-300 dark:border-slate-700 hover:border-slate-600">
                                <X size={12}/> Reset
                            </button>
                        )}
                    </div>
                    <div className="space-y-6">
                        <div>
                            <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-2">Search</label>
                            <div className="relative group">
                                <Search className="absolute left-3.5 top-3 text-slate-500 dark:text-slate-500 group-focus-within:text-indigo-400 transition-colors" size={16} />
                                <input 
                                    type="text" placeholder="Find by name..."
                                    className="w-full pl-10 pr-3 py-2.5 bg-white/90 dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-xl text-slate-900 dark:text-white text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all shadow-inner placeholder:text-slate-500 dark:text-slate-500"
                                    value={filters.search} onChange={e => setFilters({...filters, search: e.target.value})}
                                />
                            </div>
                        </div>
                        
                        <div>
                            <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-2">Language</label>
                            <select className="w-full bg-white/90 dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-xl p-2.5 text-slate-900 dark:text-white text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all shadow-inner" value={filters.language} onChange={e => setFilters({...filters, language: e.target.value})}>
                                <option value="">All Languages</option>
                                {availableLanguages.map(lang => (
                                    <option key={lang} value={lang}>{lang}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-2">Use Case / Style</label>
                            <select className="w-full bg-white/90 dark:bg-slate-900/50 border border-slate-300 dark:border-slate-700/50 rounded-xl p-2.5 text-slate-900 dark:text-white text-sm focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all shadow-inner" value={filters.use_case} onChange={e => setFilters({...filters, use_case: e.target.value})}>
                                <option value="">All Styles</option>
                                {USE_CASES.map(uc => (
                                    <option key={uc} value={uc}>{uc}</option>
                                ))}
                            </select>
                        </div>
                        
                        <div>
                            <label className="block text-xs font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider mb-2">Gender</label>
                            <div className="flex gap-2">
                                <button 
                                    onClick={() => setFilters({...filters, gender: ''})}
                                    className={`flex-1 py-2.5 text-sm font-semibold rounded-xl border transition-all ${filters.gender === '' ? 'bg-indigo-600 border-indigo-500 text-slate-900 dark:text-white shadow-[0_0_15px_rgba(79,70,229,0.3)]' : 'bg-white/90 dark:bg-slate-900/50 border-slate-300 dark:border-slate-700/50 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:text-white hover:border-slate-600'}`}
                                >All</button>
                                <button 
                                    onClick={() => setFilters({...filters, gender: 'Male'})}
                                    className={`flex-1 py-2.5 text-sm font-semibold rounded-xl border transition-all ${filters.gender === 'Male' ? 'bg-indigo-600 border-indigo-500 text-slate-900 dark:text-white shadow-[0_0_15px_rgba(79,70,229,0.3)]' : 'bg-white/90 dark:bg-slate-900/50 border-slate-300 dark:border-slate-700/50 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:text-white hover:border-slate-600'}`}
                                >Male</button>
                                <button 
                                    onClick={() => setFilters({...filters, gender: 'Female'})}
                                    className={`flex-1 py-2.5 text-sm font-semibold rounded-xl border transition-all ${filters.gender === 'Female' ? 'bg-indigo-600 border-indigo-500 text-slate-900 dark:text-white shadow-[0_0_15px_rgba(79,70,229,0.3)]' : 'bg-white/90 dark:bg-slate-900/50 border-slate-300 dark:border-slate-700/50 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:text-white hover:border-slate-600'}`}
                                >Female</button>
                            </div>
                        </div>
                    </div>
                </Card>
            </div>

            {/* Voice Grid */}
            <div className="flex-1">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-end mb-8 gap-4 border-b border-slate-200 dark:border-slate-800/60 pb-6 relative">
                    <div className="absolute -top-10 left-0 w-64 h-64 bg-indigo-500/5 blur-[100px] pointer-events-none"></div>
                    <div className="flex flex-col gap-3 relative z-10">
                        <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-white via-indigo-200 to-slate-400 tracking-tight">Voice Library</h1>
                        <div className="flex gap-2 mt-1">
                            <button 
                                onClick={() => setFilters({...filters, is_cloned: undefined})} 
                                className={`px-5 py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition-all ${filters.is_cloned === undefined ? 'bg-indigo-600 text-slate-900 dark:text-white shadow-[0_0_15px_rgba(79,70,229,0.4)] border border-indigo-500' : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:text-white hover:bg-slate-100 dark:bg-slate-800 hover:border-slate-300 dark:border-slate-700'}`}
                            >All Voices</button>
                            <button 
                                onClick={() => setFilters({...filters, is_cloned: true})} 
                                className={`px-5 py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition-all flex items-center gap-2 ${filters.is_cloned === true ? 'bg-purple-600 text-slate-900 dark:text-white shadow-[0_0_15px_rgba(147,51,234,0.4)] border border-purple-500' : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:text-white hover:bg-slate-100 dark:bg-slate-800 hover:border-slate-300 dark:border-slate-700'}`}
                            ><Mic size={14}/> My Clones</button>
                            {filters.is_cloned && voices.some(v => v.is_cloned) && (
                                <button 
                                    onClick={toggleSelectAll} 
                                    className={`px-4 py-2 ml-2 rounded-lg text-xs font-bold uppercase tracking-wider transition-all flex items-center gap-2 ${selectedVoices.size > 0 ? 'bg-indigo-600 text-slate-900 dark:text-white shadow-[0_0_15px_rgba(79,70,229,0.3)] border border-indigo-500' : 'bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:text-white hover:bg-slate-100 dark:bg-slate-800 hover:border-slate-300 dark:border-slate-700'}`}
                                >
                                    {selectedVoices.size === voices.filter(v => v.is_cloned).length && voices.filter(v => v.is_cloned).length > 0 ? <CheckSquare size={14} /> : <Square size={14} />} 
                                    <span className="hidden sm:inline">{selectedVoices.size === voices.filter(v => v.is_cloned).length && voices.filter(v => v.is_cloned).length > 0 ? 'Deselect All Clones' : 'Select All Clones'}</span>
                                </button>
                            )}
                        </div>
                    </div>
                    <span className="text-slate-600 dark:text-slate-400 text-sm font-semibold relative z-10 bg-white/90 dark:bg-slate-900/50 px-4 py-1.5 rounded-full border border-slate-200 dark:border-slate-800 shadow-inner">{voices.length} voices found</span>
                </div>
                
                {/* Bulk Action Bar */}
                <AnimatePresence>
                {selectedVoices.size > 0 && (
                    <motion.div initial={{ opacity: 0, y: -20, scale: 0.95 }} animate={{ opacity: 1, y: 0, scale: 1 }} exit={{ opacity: 0, y: -20, scale: 0.95 }} className="sticky top-4 z-50 bg-slate-100 dark:bg-slate-800/95 backdrop-blur-xl border border-indigo-500/50 p-2 sm:p-3 rounded-2xl shadow-[0_15px_40px_-10px_rgba(79,70,229,0.4)] flex flex-wrap items-center justify-between gap-3 mb-6">
                        <div className="flex items-center gap-3 px-2">
                            <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-300 font-bold border border-indigo-500/30">{selectedVoices.size}</div>
                            <span className="text-slate-900 dark:text-white font-medium text-sm sm:text-base">cloned voices selected</span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                            <Button onClick={handleBulkDeleteClick} className="bg-red-500/10 hover:bg-red-500/20 text-red-400 hover:text-red-300 border border-red-500/20 h-9 px-3 text-xs sm:text-sm"><Trash2 size={14} className="mr-1.5" /> <span className="hidden sm:inline">Delete Selected</span></Button>
                            <button onClick={() => setSelectedVoices(new Set())} className="text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:text-white h-9 px-2 ml-1 transition-colors"><X size={18} /></button>
                        </div>
                    </motion.div>
                )}
                </AnimatePresence>
                
                <AnimatePresence mode="wait">
                    {showFallbackMessage && (
                        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="mb-6 p-4 rounded-lg bg-indigo-900/30 border border-indigo-500/30 text-indigo-300 flex items-center gap-3">
                            <Filter size={18} />
                            <p>No exact <strong>{filters.use_case}</strong> voices found for <strong>{filters.language}</strong>. Showing closest premium alternatives.</p>
                        </motion.div>
                    )}
                </AnimatePresence>
                
                {loading ? (
                    <div className="flex justify-center items-center h-64"><Loader2 className="animate-spin text-indigo-500" size={48} /></div>
                ) : voices.length === 0 ? (
                    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-16 text-slate-600 dark:text-slate-400 bg-white/90 dark:bg-slate-900/30 rounded-xl border border-slate-200 dark:border-slate-800">
                        <Filter size={48} className="mx-auto mb-4 opacity-30" />
                        No voices found matching your exact filters. Try clearing them.
                    </motion.div>
                ) : (
                    <motion.div variants={container} initial="hidden" animate="show" className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                        {voices.map(voice => {
                            const toneTags = parseTags(voice.tone_tags);
                            const recommendedFor = parseTags(voice.recommended_for);
                            
                            return (
                            <motion.div key={voice.id} variants={item} whileHover={{ y: -4 }}>
                                <Card className="flex flex-col h-full border border-slate-200 dark:border-slate-800/60 bg-gradient-to-b from-slate-900/90 to-slate-950/90 backdrop-blur-xl hover:border-indigo-500/40 hover:shadow-[0_8px_30px_rgb(99,102,241,0.15)] transition-all duration-300 group relative overflow-hidden">
                                    <div className="absolute top-0 inset-x-0 h-px bg-gradient-to-r from-transparent via-indigo-500/80 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                                    <div className="absolute -inset-1 bg-gradient-to-br from-indigo-500/10 via-transparent to-purple-500/10 opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-500 pointer-events-none"></div>
                                    
                                    <div className="relative z-10 flex justify-between items-start mb-4">
                                        <div className="flex gap-3">
                                            {voice.is_cloned && (
                                                <button onClick={() => toggleSelection(voice.id)} className={`mt-1 transition-all ${selectedVoices.has(voice.id) ? 'text-indigo-400 scale-110' : 'text-slate-600 hover:text-indigo-400'}`}>
                                                    {selectedVoices.has(voice.id) ? <CheckSquare size={18} /> : <Square size={18} />}
                                                </button>
                                            )}
                                            <div>
                                                <h3 className="font-extrabold text-xl text-slate-900 dark:text-white group-hover:text-indigo-300 transition-colors tracking-tight">{voice.name}</h3>
                                                <div className="text-xs text-slate-600 dark:text-slate-400 flex items-center gap-2 mt-1.5 font-medium">
                                                    <span className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.8)]"></div> {voice.language}</span> 
                                                    <span className="text-slate-700">•</span>
                                                    <span className="capitalize">{voice.gender}</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="flex flex-col items-end gap-1.5">
                                            {voice.is_cloned ? (
                                                <span className="text-[10px] font-bold uppercase tracking-widest bg-emerald-500/10 text-emerald-400 px-2 py-1 rounded-md border border-emerald-500/20 shadow-[0_0_10px_rgba(16,185,129,0.15)] flex items-center gap-1.5">
                                                    <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></div> Cloned
                                                </span>
                                            ) : (
                                                <div className="flex flex-col items-end gap-1">
                                                    <span className="text-[9px] font-bold uppercase tracking-wider bg-slate-100 dark:bg-slate-800/80 text-slate-700 dark:text-slate-300 px-2 py-1 rounded-md border border-slate-300 dark:border-slate-700/80">{voice.engine === 'piper' ? 'Offline' : voice.engine === 'coqui' ? 'Coqui' : 'Online'}</span>
                                                    <span className="text-[9px] font-bold uppercase tracking-wider bg-gradient-to-r from-indigo-500/10 to-purple-500/10 text-indigo-300 px-2 py-1 rounded-md border border-indigo-500/20">{voice.quality_label}</span>
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                    
                                    <div className="relative z-10 flex flex-wrap gap-2 mb-5 mt-2">
                                        {recommendedFor.length > 0 ? (
                                            <span className="text-[11px] font-semibold text-emerald-300 bg-emerald-500/10 border border-emerald-500/20 px-2.5 py-1 rounded-full shadow-inner">
                                                ★ Best for {recommendedFor[0]}
                                            </span>
                                        ) : null}
                                        {toneTags.slice(0, 2).map((tone, i) => (
                                            <span key={i} className="text-[11px] font-medium text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-800/60 border border-slate-300 dark:border-slate-700/60 px-2.5 py-1 rounded-full">
                                                {tone}
                                            </span>
                                        ))}
                                    </div>
                                    
                                    <div className="relative z-10 flex items-center gap-3 mt-auto pt-5 border-t border-slate-200 dark:border-slate-800/60">
                                        <motion.button 
                                            whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                                            onClick={() => handlePlayPreview(voice)}
                                            disabled={loadingPreviewId === voice.id}
                                            className={`w-11 h-11 rounded-full flex items-center justify-center text-slate-900 dark:text-white transition-all shadow-lg ${playingId === voice.id ? 'bg-indigo-600 shadow-[0_0_20px_rgba(79,70,229,0.5)] ring-2 ring-indigo-400 ring-offset-2 ring-offset-slate-950' : 'bg-slate-100 dark:bg-slate-800 hover:bg-indigo-600 hover:shadow-[0_0_15px_rgba(79,70,229,0.4)] border border-slate-300 dark:border-slate-700 hover:border-indigo-500'}`}
                                        >
                                            {loadingPreviewId === voice.id ? <Loader2 size={18} className="animate-spin" /> : 
                                             playingId === voice.id ? <Square size={16} fill="currentColor" /> : <Play size={18} fill="currentColor" className="ml-1" />}
                                        </motion.button>
                                        <Button onClick={() => handleUseInStudio(voice.id)} variant="secondary" className="flex-1 py-2.5 text-sm font-semibold border border-slate-300 dark:border-slate-700 hover:border-slate-500 hover:bg-slate-100 dark:bg-slate-800 bg-slate-100 dark:bg-slate-800/50 shadow-inner hover:shadow-none transition-all">
                                            Use in Studio
                                        </Button>
                                        {voice.is_cloned && (
                                            <button 
                                                onClick={() => handleDeleteVoice(voice.id, voice.name)}
                                                className="w-11 h-11 rounded-xl flex items-center justify-center text-slate-600 dark:text-slate-400 hover:text-red-400 hover:bg-red-500/10 border border-transparent hover:border-red-500/30 transition-all shadow-sm"
                                                title="Delete Cloned Voice"
                                            >
                                                <Trash2 size={18} />
                                            </button>
                                        )}
                                    </div>
                                </Card>
                            </motion.div>
                            );
                        })}
                    </motion.div>
                )}
            </div>

            {/* Premium Delete Confirmation Modal */}
            <AnimatePresence>
                {itemsToDelete.length > 0 && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
                        <motion.div initial={{ opacity: 0, scale: 0.9, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: 0.9, y: 20 }} className="bg-white dark:bg-slate-900 border border-slate-300 dark:border-slate-700 rounded-2xl p-6 max-w-md w-full shadow-2xl relative overflow-hidden">
                            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-red-500 to-rose-600"></div>
                            <div className="flex items-center justify-center w-12 h-12 rounded-full bg-red-500/10 text-red-500 mb-5 border border-red-500/20 shadow-[0_0_15px_rgba(239,68,68,0.15)]">
                                <Trash2 size={24} />
                            </div>
                            <h3 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Delete {itemsToDelete.length > 1 ? `${itemsToDelete.length} Voices` : 'Voice'}</h3>
                            <p className="text-slate-600 dark:text-slate-400 mb-6 text-sm leading-relaxed">
                                Are you sure you want to permanently delete {itemsToDelete.length > 1 ? `these ${itemsToDelete.length} voices` : "this voice"}? This action cannot be undone and all associated voice data will be securely destroyed.
                            </p>
                            <div className="flex gap-3 justify-end">
                                <Button variant="secondary" onClick={() => setItemsToDelete([])} disabled={isDeleting} className="bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 text-slate-700 dark:text-slate-300 border-slate-300 dark:border-slate-700">Cancel</Button>
                                <Button onClick={confirmDelete} disabled={isDeleting} className="bg-red-600 hover:bg-red-500 text-slate-900 dark:text-white border-transparent shadow-[0_0_15px_rgba(220,38,38,0.4)] flex items-center gap-2">
                                    {isDeleting ? <Loader2 size={16} className="animate-spin" /> : <Trash2 size={16} />}
                                    {isDeleting ? 'Deleting...' : 'Yes, Delete Voice'}
                                </Button>
                            </div>
                        </motion.div>
                    </div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

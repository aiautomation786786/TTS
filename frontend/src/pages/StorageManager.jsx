import React, { useState, useEffect } from 'react';
import { getStorageStats, clearStorage } from '../api/storage';
import { HardDrive, Server, FileAudio, Layers, Trash2, Loader2, Database, AlertCircle, CheckSquare, Square } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { motion, AnimatePresence } from 'framer-motion';
import toast from 'react-hot-toast';

export const StorageManager = () => {
    const [stats, setStats] = useState({});
    const [loading, setLoading] = useState(true);
    const [selectedCategories, setSelectedCategories] = useState(new Set());
    const [isClearing, setIsClearing] = useState(false);
    const [showConfirm, setShowConfirm] = useState(false);

    useEffect(() => {
        loadStats();
    }, []);

    const loadStats = async () => {
        setLoading(true);
        try {
            const res = await getStorageStats();
            setStats(res.data);
            setSelectedCategories(new Set());
        } catch (err) {
            toast.error("Failed to load storage statistics");
        } finally {
            setLoading(false);
        }
    };

    const formatBytes = (bytes) => {
        if (bytes === 0) return '0 B';
        const k = 1024;
        const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };

    const toggleCategory = (cat) => {
        const newSet = new Set(selectedCategories);
        if (newSet.has(cat)) newSet.delete(cat);
        else newSet.add(cat);
        setSelectedCategories(newSet);
    };

    const handleClear = async () => {
        if (selectedCategories.size === 0) return;
        setIsClearing(true);
        try {
            await clearStorage(Array.from(selectedCategories));
            toast.success("Storage cleared successfully");
            await loadStats();
            setShowConfirm(false);
        } catch (err) {
            toast.error("Failed to clear storage");
        } finally {
            setIsClearing(false);
        }
    };

    const getIcon = (key) => {
        switch(key) {
            case 'history': return <Database className="text-indigo-400" size={28} />;
            case 'models': return <Server className="text-emerald-400" size={28} />;
            case 'uploads': return <FileAudio className="text-amber-400" size={28} />;
            case 'temp': return <Layers className="text-rose-400" size={28} />;
            default: return <HardDrive size={28} />;
        }
    };

    const getTotalSize = () => {
        if (!stats) return 0;
        return Object.values(stats).reduce((acc, curr) => acc + curr.size_bytes, 0);
    };

    const getSelectedSize = () => {
        if (!stats) return 0;
        let total = 0;
        selectedCategories.forEach(key => {
            if (stats[key]) total += stats[key].size_bytes;
        });
        return total;
    };

    const container = { hidden: { opacity: 0 }, show: { opacity: 1, transition: { staggerChildren: 0.1 } } };
    const item = { hidden: { opacity: 0, y: 20 }, show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } } };

    return (
        <div className="max-w-5xl mx-auto space-y-8 relative pb-20">
            {/* Background elements */}
            <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-indigo-600/5 rounded-full mix-blend-screen filter blur-[150px] pointer-events-none"></div>
            
            <header className="relative z-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-6 border-b border-slate-800 pb-6">
                <div className="space-y-2">
                    <h1 className="text-4xl font-extrabold flex items-center gap-4 text-transparent bg-clip-text bg-gradient-to-r from-white via-indigo-200 to-slate-400 tracking-tight">
                        <div className="p-3 bg-slate-900/50 rounded-2xl border border-slate-800 shadow-inner text-indigo-400">
                            <HardDrive size={32} />
                        </div>
                        Storage Manager
                    </h1>
                    <p className="text-slate-400 ml-1 font-medium text-lg">Reclaim space by safely clearing offline models and generated audio.</p>
                </div>
                <div className="flex items-center gap-3">
                    <div className="bg-slate-900 border border-slate-800 px-5 py-3 rounded-xl shadow-inner text-right">
                        <div className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-1">Total Space Used</div>
                        <div className="text-2xl font-bold text-white">{formatBytes(getTotalSize())}</div>
                    </div>
                </div>
            </header>

            {loading ? (
                <div className="flex justify-center items-center py-32"><Loader2 className="animate-spin text-indigo-500" size={48} /></div>
            ) : (
                <>
                    <motion.div variants={container} initial="hidden" animate="show" className="grid grid-cols-1 md:grid-cols-2 gap-6 relative z-10">
                        {Object.entries(stats).map(([key, data]) => (
                            <motion.div variants={item} key={key} whileHover={{ y: -4 }}>
                                <Card 
                                    className={`relative overflow-hidden cursor-pointer transition-all duration-300 border-2 ${selectedCategories.has(key) ? 'border-indigo-500 bg-indigo-900/20 shadow-[0_10px_30px_-10px_rgba(79,70,229,0.3)]' : 'border-slate-800/60 bg-slate-900/50 hover:border-slate-700 hover:bg-slate-800/80'}`}
                                    onClick={() => toggleCategory(key)}
                                >
                                    <div className="absolute top-4 right-4 text-slate-500">
                                        {selectedCategories.has(key) ? <CheckSquare size={24} className="text-indigo-500" /> : <Square size={24} />}
                                    </div>
                                    <div className="flex items-start gap-4 mb-4">
                                        <div className={`p-3 rounded-xl border shadow-inner ${selectedCategories.has(key) ? 'bg-indigo-950 border-indigo-500/50' : 'bg-slate-950 border-slate-800'}`}>
                                            {getIcon(key)}
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-bold text-white mb-1">{data.label}</h3>
                                            <p className="text-sm text-slate-400">{data.desc}</p>
                                        </div>
                                    </div>
                                    <div className="flex justify-between items-end mt-6 pt-4 border-t border-slate-800/60">
                                        <div className="text-xs font-medium text-slate-500 uppercase tracking-wider">{data.file_count} files</div>
                                        <div className="text-2xl font-black tracking-tight text-white">{formatBytes(data.size_bytes)}</div>
                                    </div>
                                </Card>
                            </motion.div>
                        ))}
                    </motion.div>

                    {/* Action Bar */}
                    <AnimatePresence>
                        {selectedCategories.size > 0 && (
                            <motion.div 
                                initial={{ opacity: 0, y: 30 }} 
                                animate={{ opacity: 1, y: 0 }} 
                                exit={{ opacity: 0, y: 30 }} 
                                className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 bg-slate-900/95 backdrop-blur-xl border-2 border-indigo-500/50 p-4 rounded-2xl shadow-[0_20px_50px_-10px_rgba(79,70,229,0.4)] flex items-center justify-between gap-6 w-[90%] max-w-2xl"
                            >
                                <div className="flex items-center gap-4">
                                    <div className="w-12 h-12 rounded-full bg-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold border border-indigo-500/30">
                                        {selectedCategories.size}
                                    </div>
                                    <div>
                                        <div className="text-sm font-bold text-slate-300">Selected for cleanup</div>
                                        <div className="text-lg font-black text-white">{formatBytes(getSelectedSize())}</div>
                                    </div>
                                </div>
                                <Button 
                                    onClick={() => setShowConfirm(true)} 
                                    className="bg-red-600 hover:bg-red-500 text-white shadow-[0_0_20px_rgba(220,38,38,0.4)] px-6 py-6 text-lg rounded-xl flex items-center gap-2"
                                >
                                    <Trash2 size={20} /> Clear Selected
                                </Button>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Confirmation Modal */}
                    <AnimatePresence>
                        {showConfirm && (
                            <div className="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
                                <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.95 }} className="bg-slate-900 border border-slate-700 rounded-3xl p-8 max-w-lg w-full shadow-[0_30px_100px_rgba(0,0,0,0.8)] relative overflow-hidden">
                                    <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-red-500 to-rose-600"></div>
                                    <div className="flex items-center gap-5 mb-6">
                                        <div className="w-16 h-16 rounded-2xl bg-red-500/10 flex items-center justify-center flex-shrink-0 border border-red-500/20 shadow-inner">
                                            <AlertCircle className="text-red-500" size={32} />
                                        </div>
                                        <div>
                                            <h3 className="text-2xl font-black text-white mb-1">Confirm Deletion</h3>
                                            <p className="text-slate-400 text-sm leading-relaxed">You are about to permanently wipe <strong className="text-white">{formatBytes(getSelectedSize())}</strong> of data. This action cannot be undone.</p>
                                        </div>
                                    </div>
                                    
                                    <div className="bg-slate-950 rounded-xl p-4 border border-slate-800 mb-8 max-h-[200px] overflow-y-auto">
                                        <h4 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3">Items to be destroyed:</h4>
                                        <ul className="space-y-2">
                                            {Array.from(selectedCategories).map(key => (
                                                <li key={key} className="flex justify-between items-center text-sm">
                                                    <span className="text-slate-300 font-medium">{stats[key]?.label}</span>
                                                    <span className="text-red-400 font-mono">{formatBytes(stats[key]?.size_bytes)}</span>
                                                </li>
                                            ))}
                                        </ul>
                                    </div>

                                    <div className="flex justify-end gap-3">
                                        <Button variant="secondary" onClick={() => setShowConfirm(false)} disabled={isClearing} className="px-6 py-2.5 bg-slate-800 hover:bg-slate-700 text-slate-300 border-slate-700">Cancel</Button>
                                        <Button onClick={handleClear} disabled={isClearing} className="px-6 py-2.5 bg-red-600 hover:bg-red-500 text-white shadow-[0_0_20px_rgba(220,38,38,0.4)] flex items-center gap-2">
                                            {isClearing ? <Loader2 size={18} className="animate-spin" /> : <Trash2 size={18} />}
                                            {isClearing ? 'Erasing Data...' : 'Yes, Permanently Delete'}
                                        </Button>
                                    </div>
                                </motion.div>
                            </div>
                        )}
                    </AnimatePresence>
                </>
            )}
        </div>
    );
};

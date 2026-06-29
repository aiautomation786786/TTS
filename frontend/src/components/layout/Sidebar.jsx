import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Mic, BookOpen, Clock, Activity, Loader2, HardDrive, Sun, Moon } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import client from '../../api/client';

export const Sidebar = () => {
    const { pathname } = useLocation();
    const { theme, toggleTheme } = useTheme();
    const [status, setStatus] = useState('checking');
    
    useEffect(() => {
        const checkStatus = async () => {
            try {
                const res = await client.get('/api/admin/engine-status');
                const engineData = res.data;
                const allOnline = engineData.engines.every(e => e.available) && engineData.coqui_status?.model_available;
                setStatus(allOnline ? 'online' : 'offline');
            } catch (err) {
                setStatus('offline');
            }
        };

        checkStatus();
        const interval = setInterval(checkStatus, 5000);
        return () => clearInterval(interval);
    }, []);
    
    const menuItems = [
        { path: '/dashboard', icon: <LayoutDashboard size={20} />, label: 'Dashboard' },
        { path: '/studio', icon: <Mic size={20} />, label: 'TTS Studio' },
        { path: '/voices', icon: <BookOpen size={20} />, label: 'Voice Library' },
        { path: '/clone', icon: <Activity size={20} />, label: 'Voice Cloning' },
        { path: '/history', icon: <Clock size={20} />, label: 'History' },
        { path: '/storage', icon: <HardDrive size={20} />, label: 'Storage Manager' }
    ];

    return (
        <aside className="w-64 bg-white dark:bg-slate-900/80 border-r border-slate-200 dark:border-slate-800 flex flex-col h-full flex-shrink-0 transition-colors duration-300">
            <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto mt-4">
                {menuItems.map(({ path, icon, label }) => (
                    <Link 
                        key={path} to={path} 
                        className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors font-medium ${pathname === path ? 'bg-indigo-50 dark:bg-indigo-500/10 text-indigo-600 dark:text-indigo-400' : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800/50'}`}
                    >
                        {icon} <span className="pt-0.5">{label}</span>
                    </Link>
                ))}
            </nav>
            
            <div className="p-4 border-t border-slate-200 dark:border-slate-800/50">
                {status === 'checking' && (
                    <div className="flex items-center gap-2 text-slate-600 dark:text-slate-400 bg-slate-500/10 px-3 py-2 rounded-lg border border-slate-500/20 transition-all justify-center">
                        <Loader2 size={14} className="animate-spin" />
                        <span className="text-[11px] font-bold uppercase tracking-wider">Checking Status</span>
                    </div>
                )}
                {status === 'online' && (
                    <div className="flex items-center gap-2 text-emerald-400 bg-emerald-500/10 px-3 py-2 rounded-lg border border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.15)] transition-all justify-center">
                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-[pulse_2s_ease-in-out_infinite]"></div>
                        <span className="text-[11px] font-bold uppercase tracking-wider">System Online</span>
                    </div>
                )}
                {status === 'offline' && (
                    <div className="flex items-center gap-2 text-red-400 bg-red-500/10 px-3 py-2 rounded-lg border border-red-500/20 shadow-[0_0_15px_rgba(239,68,68,0.15)] transition-all justify-center">
                        <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
                        <span className="text-[11px] font-bold uppercase tracking-wider">System Offline</span>
                    </div>
                )}
            </div>
        </aside>
    );
};

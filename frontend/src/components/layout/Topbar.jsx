import React, { useEffect, useState } from 'react';
import client from '../../api/client';
import { Loader2 } from 'lucide-react';

export const Topbar = () => {
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

    return (
        <header className="h-16 bg-slate-900/50 backdrop-blur-md border-b border-slate-800 flex items-center justify-end px-6 sticky top-0 z-10">
            {status === 'checking' && (
                <div className="flex items-center gap-2 text-slate-400 bg-slate-500/10 px-3 py-1.5 rounded-full border border-slate-500/20 transition-all">
                    <Loader2 size={12} className="animate-spin" />
                    <span className="text-[11px] font-bold uppercase tracking-wider">Checking Status</span>
                </div>
            )}
            {status === 'online' && (
                <div className="flex items-center gap-2 text-emerald-400 bg-emerald-500/10 px-3 py-1.5 rounded-full border border-emerald-500/20 shadow-[0_0_15px_rgba(16,185,129,0.15)] transition-all">
                    <div className="w-2 h-2 rounded-full bg-emerald-500 animate-[pulse_2s_ease-in-out_infinite]"></div>
                    <span className="text-[11px] font-bold uppercase tracking-wider">System Online</span>
                </div>
            )}
            {status === 'offline' && (
                <div className="flex items-center gap-2 text-red-400 bg-red-500/10 px-3 py-1.5 rounded-full border border-red-500/20 shadow-[0_0_15px_rgba(239,68,68,0.15)] transition-all">
                    <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></div>
                    <span className="text-[11px] font-bold uppercase tracking-wider">System Offline</span>
                </div>
            )}
        </header>
    );
};

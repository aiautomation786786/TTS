import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Toaster } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';

export const AppLayout = () => {
    return (
        <div className="flex h-screen w-full bg-slate-50 dark:bg-[#0a0e1a] text-slate-800 dark:text-slate-300 overflow-hidden transition-colors duration-300">
            <Sidebar />
            <div className="flex-1 flex flex-col min-w-0">
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

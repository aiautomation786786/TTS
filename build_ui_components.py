import os

files = {
    "src/components/ui/Button.jsx": """
import React from 'react';

export const Button = ({ children, variant = 'primary', className = '', ...props }) => {
    const base = "inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-950 disabled:opacity-50 disabled:cursor-not-allowed";
    const variants = {
        primary: "bg-indigo-600 hover:bg-indigo-700 text-white focus:ring-indigo-500",
        secondary: "bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 focus:ring-slate-500",
        danger: "bg-red-600 hover:bg-red-700 text-white focus:ring-red-500",
        ghost: "bg-transparent hover:bg-slate-800 text-slate-300 hover:text-white focus:ring-slate-500"
    };
    return (
        <button className={`${base} ${variants[variant]} px-4 py-2 ${className}`} {...props}>
            {children}
        </button>
    );
};
""",
    "src/components/ui/Input.jsx": """
import React from 'react';

export const Input = ({ label, ...props }) => {
    return (
        <div className="flex flex-col gap-1.5 w-full">
            {label && <label className="text-sm font-medium text-slate-300">{label}</label>}
            <input 
                className="w-full px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-colors placeholder:text-slate-500"
                {...props} 
            />
        </div>
    );
};
""",
    "src/components/ui/Card.jsx": """
import React from 'react';

export const Card = ({ children, className = '', ...props }) => {
    return (
        <div className={`bg-slate-900/50 backdrop-blur-sm border border-slate-800/80 rounded-xl p-6 shadow-xl ${className}`} {...props}>
            {children}
        </div>
    );
};
""",
    "src/components/layout/Sidebar.jsx": """
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, Mic2, PlayCircle, History, Settings, ShieldAlert } from 'lucide-react';
import { useAuthStore } from '../../store/authStore';

export const Sidebar = () => {
    const { pathname } = useLocation();
    const { user } = useAuthStore();
    
    const links = [
        { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
        { to: '/studio', icon: PlayCircle, label: 'TTS Studio' },
        { to: '/voices', icon: Mic2, label: 'Voice Library' },
        { to: '/clone', icon: Mic2, label: 'Voice Cloning' },
        { to: '/history', icon: History, label: 'History' },
        { to: '/settings', icon: Settings, label: 'Settings' }
    ];

    return (
        <aside className="w-64 bg-slate-900/80 border-r border-slate-800 flex flex-col h-full flex-shrink-0">
            <div className="p-6 border-b border-slate-800">
                <Link to="/dashboard" className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400 tracking-tight">VoxForge</Link>
            </div>
            <nav className="flex-1 p-4 space-y-1.5 overflow-y-auto">
                {links.map(({ to, icon: Icon, label }) => (
                    <Link 
                        key={to} to={to} 
                        className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors font-medium ${pathname === to ? 'bg-indigo-500/10 text-indigo-400' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}
                    >
                        <Icon size={18} /> {label}
                    </Link>
                ))}
                
                {user?.role === 'admin' && (
                    <div className="mt-8 pt-4 border-t border-slate-800">
                        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider px-3 mb-2 block">Admin</span>
                        <Link to="/admin/dashboard" className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors font-medium ${pathname.startsWith('/admin') ? 'bg-orange-500/10 text-orange-400' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'}`}>
                            <ShieldAlert size={18} /> Admin Panel
                        </Link>
                    </div>
                )}
            </nav>
        </aside>
    );
};
""",
    "src/components/layout/Topbar.jsx": """
import React from 'react';
import { useAuthStore } from '../../store/authStore';
import { Button } from '../ui/Button';

export const Topbar = () => {
    const { user, logout } = useAuthStore();
    return (
        <header className="h-16 bg-slate-900/50 backdrop-blur-md border-b border-slate-800 flex items-center justify-end px-6 sticky top-0 z-10">
            <div className="flex items-center gap-4">
                <div className="flex flex-col items-end">
                    <span className="text-sm font-medium text-white">{user?.username}</span>
                    <span className="text-xs text-slate-500 capitalize">{user?.role}</span>
                </div>
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-white font-bold">
                    {user?.username?.charAt(0).toUpperCase()}
                </div>
                <Button variant="ghost" onClick={logout} className="ml-2 text-sm px-3 py-1.5">Logout</Button>
            </div>
        </header>
    );
};
""",
    "src/components/layout/AppLayout.jsx": """
import React from 'react';
import { Outlet } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';

export const AppLayout = () => {
    return (
        <div className="flex h-screen w-full bg-[#0a0e1a] text-slate-300 overflow-hidden">
            <Sidebar />
            <div className="flex-1 flex flex-col min-w-0">
                <Topbar />
                <main className="flex-1 overflow-y-auto p-6 lg:p-8">
                    <Outlet />
                </main>
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

print("Components and Layout successfully rewritten.")

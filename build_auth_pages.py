import os

files = {
    "src/pages/Login.jsx": """
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card } from '../components/ui/Card';
import { Loader2, AlertCircle, ArrowRight } from 'lucide-react';

export const Login = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const { login } = useAuthStore();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            await login(username, password);
            navigate('/dashboard');
        } catch (err) {
            setError(err.response?.data?.detail || 'Login failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#0a0e1a] flex items-center justify-center p-6 relative overflow-hidden">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full max-w-4xl h-96 bg-indigo-500/20 blur-[120px] rounded-full pointer-events-none"></div>
            
            <Card className="w-full max-w-md relative z-10 border-slate-800 bg-slate-900/80 backdrop-blur-xl shadow-2xl p-8">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-purple-400 tracking-tight mb-2">Welcome Back</h1>
                    <p className="text-slate-400">Sign in to VoxForge to continue creating.</p>
                </div>

                {error && (
                    <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/50 text-red-400 flex items-start gap-3">
                        <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
                        <span className="text-sm">{error}</span>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-5">
                    <Input 
                        label="Username" 
                        type="text" 
                        value={username} 
                        onChange={(e) => setUsername(e.target.value)} 
                        required 
                        placeholder="Enter your username"
                    />
                    <Input 
                        label="Password" 
                        type="password" 
                        value={password} 
                        onChange={(e) => setPassword(e.target.value)} 
                        required 
                        placeholder="••••••••"
                    />
                    
                    <Button type="submit" disabled={loading} className="w-full py-3 mt-4 text-base font-semibold group flex items-center justify-center gap-2">
                        {loading ? <Loader2 className="animate-spin" size={18} /> : 
                        <>Sign In <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" /></>}
                    </Button>
                </form>

                <div className="mt-8 text-center text-sm text-slate-400 border-t border-slate-800 pt-6">
                    Don't have an account? <Link to="/register" className="text-indigo-400 hover:text-indigo-300 font-medium ml-1 transition-colors">Sign up for free</Link>
                </div>
            </Card>
        </div>
    );
};
""",
    "src/pages/Register.jsx": """
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import client from '../api/client';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Card } from '../components/ui/Card';
import { Loader2, AlertCircle, Sparkles } from 'lucide-react';

export const Register = () => {
    const [form, setForm] = useState({ username: '', email: '', password: '' });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        try {
            await client.post('/api/auth/register', form);
            navigate('/login');
        } catch (err) {
            setError(err.response?.data?.detail || 'Registration failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[#0a0e1a] flex items-center justify-center p-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-full max-w-2xl h-[500px] bg-purple-500/10 blur-[150px] rounded-full pointer-events-none"></div>
            <div className="absolute bottom-0 left-0 w-full max-w-2xl h-[500px] bg-indigo-500/10 blur-[150px] rounded-full pointer-events-none"></div>

            <Card className="w-full max-w-md relative z-10 border-slate-800 bg-slate-900/80 backdrop-blur-xl shadow-2xl p-8">
                <div className="text-center mb-8">
                    <h1 className="text-3xl font-bold text-white tracking-tight mb-2 flex items-center justify-center gap-2">
                        Create Account <Sparkles className="text-purple-400" size={24} />
                    </h1>
                    <p className="text-slate-400">Join VoxForge to start generating premium audio.</p>
                </div>

                {error && (
                    <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/50 text-red-400 flex items-start gap-3">
                        <AlertCircle className="flex-shrink-0 mt-0.5" size={18} />
                        <span className="text-sm">{error}</span>
                    </div>
                )}

                <form onSubmit={handleSubmit} className="space-y-5">
                    <Input 
                        label="Username" 
                        type="text" 
                        value={form.username} 
                        onChange={(e) => setForm({...form, username: e.target.value})} 
                        required 
                        placeholder="Choose a username"
                    />
                    <Input 
                        label="Email Address" 
                        type="email" 
                        value={form.email} 
                        onChange={(e) => setForm({...form, email: e.target.value})} 
                        required 
                        placeholder="you@example.com"
                    />
                    <Input 
                        label="Password" 
                        type="password" 
                        value={form.password} 
                        onChange={(e) => setForm({...form, password: e.target.value})} 
                        required 
                        placeholder="Create a strong password"
                    />
                    
                    <Button type="submit" disabled={loading} className="w-full py-3 mt-4 text-base font-semibold">
                        {loading ? <Loader2 className="animate-spin mx-auto" size={18} /> : 'Create Free Account'}
                    </Button>
                </form>

                <div className="mt-8 text-center text-sm text-slate-400 border-t border-slate-800 pt-6">
                    Already have an account? <Link to="/login" className="text-indigo-400 hover:text-indigo-300 font-medium ml-1 transition-colors">Sign in here</Link>
                </div>
            </Card>
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

print("Auth pages successfully rewritten.")

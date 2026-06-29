import os

files = {
    "src/index.css": """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --color-bg-primary: #0a0e1a;
  --color-bg-secondary: #0f1629;
  --color-bg-tertiary: #1a2035;
  --color-bg-surface: #222b45;
  --color-bg-elevated: #2a3555;
  --color-bg-hover: #323d5a;
  --color-bg-input: #151d30;
  --color-accent-primary: #6366f1;
  --color-accent-secondary: #818cf8;
  --color-accent-tertiary: #a78bfa;
  --color-accent-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%);
  --color-accent-glow: rgba(99, 102, 241, 0.15);
  --color-text-primary: #f1f5f9;
  --color-text-secondary: #94a3b8;
  --color-text-muted: #64748b;
  --color-text-accent: #818cf8;
  --color-border: rgba(255, 255, 255, 0.06);
  --color-border-hover: rgba(255, 255, 255, 0.12);
  --color-border-focus: rgba(99, 102, 241, 0.5);
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
}

* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Inter', sans-serif; background: var(--color-bg-primary); color: var(--color-text-primary); }
a { color: var(--color-accent-primary); text-decoration: none; }
""",
    "src/api/client.js": """
import axios from 'axios';
const client = axios.create({ baseURL: 'http://localhost:8000' });
client.interceptors.request.use((config) => {
    const token = localStorage.getItem('voxforge_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});
export default client;
""",
    "src/api/auth.js": """
import client from './client';
export const login = (username, password) => {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    return client.post('/api/auth/login', params);
};
export const register = (data) => client.post('/api/auth/register', data);
export const getMe = () => client.get('/api/auth/me');
""",
    "src/api/tts.js": """
import client from './client';
export const generateSpeech = (data) => client.post('/api/tts/generate', data);
export const getVoices = (params) => client.get('/api/tts/voices', { params });
export const getLanguages = () => client.get('/api/tts/languages');
""",
    "src/api/voices.js": """
import client from './client';
export const getVoices = (params) => client.get('/api/voices/', { params });
export const getVoice = (id) => client.get(`/api/voices/${id}`);
export const cloneVoice = (data) => client.post('/api/voices/clone', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
});
export const getClonedVoices = () => client.get('/api/voices/cloned');
export const deleteClonedVoice = (id) => client.delete(`/api/voices/cloned/${id}`);
""",
    "src/api/history.js": """
import client from './client';
export const getHistory = (params) => client.get('/api/history/', { params });
export const deleteGeneration = (id) => client.delete(`/api/history/${id}`);
""",
    "src/api/admin.js": """
import client from './client';
export const getDashboard = () => client.get('/api/admin/dashboard');
export const getUsers = (params) => client.get('/api/admin/users', { params });
export const getSystemStatus = () => client.get('/api/admin/system/status');
""",
    "src/store/authStore.js": """
import { create } from 'zustand';
import { login, register, getMe } from '../api/auth';
export const useAuthStore = create((set) => ({
    user: null, token: localStorage.getItem('voxforge_token'), isAuthenticated: false, isLoading: false,
    loginAction: async (u, p) => {
        set({ isLoading: true });
        try {
            const { data } = await login(u, p);
            localStorage.setItem('voxforge_token', data.access_token);
            set({ user: data.user, token: data.access_token, isAuthenticated: true, isLoading: false });
        } catch(e) { set({ isLoading: false }); throw e; }
    },
    logout: () => { localStorage.removeItem('voxforge_token'); set({ user: null, token: null, isAuthenticated: false }); },
    initialize: async () => {
        const token = localStorage.getItem('voxforge_token');
        if (token) {
            try { const { data } = await getMe(); set({ user: data, isAuthenticated: true }); }
            catch(e) { localStorage.removeItem('voxforge_token'); set({ user: null, isAuthenticated: false, token: null }); }
        }
    }
}));
""",
    "src/store/appStore.js": """
import { create } from 'zustand';
export const useAppStore = create((set) => ({
    sidebarCollapsed: false,
    toggleSidebar: () => set((state) => ({ sidebarCollapsed: !state.sidebarCollapsed })),
    pageTitle: '',
    setPageTitle: (title) => set({ pageTitle: title })
}));
"""
}

for filepath, content in files.items():
    full_path = os.path.join("d:/TTS/frontend", filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Helper files created.")

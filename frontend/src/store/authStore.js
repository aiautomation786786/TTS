
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
    logout: () => { 
        localStorage.removeItem('voxforge_token'); 
        sessionStorage.removeItem('admin_gate_token');
        set({ user: null, token: null, isAuthenticated: false }); 
    },
    initialize: async () => {
        const token = localStorage.getItem('voxforge_token');
        if (token) {
            try { const { data } = await getMe(); set({ user: data, isAuthenticated: true }); }
            catch(e) { localStorage.removeItem('voxforge_token'); set({ user: null, isAuthenticated: false, token: null }); }
        }
    }
}));

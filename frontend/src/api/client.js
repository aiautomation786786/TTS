
import axios from 'axios';
const client = axios.create({ baseURL: 'http://localhost:8000' });
client.interceptors.request.use((config) => {
    const token = localStorage.getItem('voxforge_token');
    const adminGateToken = sessionStorage.getItem('admin_gate_token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    if (adminGateToken) config.headers['x-admin-gate'] = adminGateToken;
    return config;
});
export default client;


import client from './client';
export const login = (username, password) => {
    const params = new URLSearchParams();
    params.append('username', username);
    params.append('password', password);
    return client.post('/api/auth/login', params);
};
export const register = (data) => client.post('/api/auth/register', data);
export const getMe = () => client.get('/api/auth/me');

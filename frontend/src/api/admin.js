
import client from './client';
export const getDashboard = () => client.get('/api/admin/dashboard');
export const getUsers = (params) => client.get('/api/admin/users', { params });
export const getSystemStatus = () => client.get('/api/admin/system/status');

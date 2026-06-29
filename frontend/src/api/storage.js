import client from './client';

export const getStorageStats = () => client.get('/api/storage/');
export const clearStorage = (categories) => client.post('/api/storage/clear', { categories });

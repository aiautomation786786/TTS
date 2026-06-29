import client from './client';

export const getStorageStats = () => client.get('/api/storage/');
export const clearStorage = (categories) => client.post('/api/storage/clear', { categories });
export const getCategoryFiles = (category) => client.get(`/api/storage/${category}/files`);
export const clearCategoryFiles = (category, files) => client.post(`/api/storage/${category}/clear_files`, { files });

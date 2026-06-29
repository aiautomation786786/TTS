import client from './client';
export const getHistory = (params) => client.get('/api/history/', { params });
export const deleteGeneration = (id) => client.delete(`/api/history/${id}`);
export const toggleFavorite = (id, is_favorite) => client.put(`/api/history/${id}/favorite`, null, { params: { is_favorite } });

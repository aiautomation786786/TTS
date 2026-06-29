import client from './client';

export const presetApi = {
    getAll: () => client.get('/api/presets/'),
    create: (data) => client.post('/api/presets/', data),
    update: (id, data) => client.put(`/api/presets/${id}`, data),
    delete: (id) => client.delete(`/api/presets/${id}`)
};

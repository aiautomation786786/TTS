
import client from './client';
export const getVoices = (params) => client.get('/api/voices/', { params });
export const getVoice = (id) => client.get(`/api/voices/${id}`);
export const cloneVoice = (data) => client.post('/api/voices/clone', data, {
    headers: { 'Content-Type': 'multipart/form-data' }
});
export const getClonedVoices = () => client.get('/api/voices/cloned');
export const deleteClonedVoice = (id) => client.delete(`/api/voices/cloned/${id}`);
export const getVoicePreview = (id) => client.get(`/api/voices/${id}/preview`);

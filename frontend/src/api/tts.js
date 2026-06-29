
import client from './client';
export const generateSpeech = (data) => client.post('/api/tts/generate', data);
export const getVoices = (params) => client.get('/api/tts/voices', { params });
export const getLanguages = () => client.get('/api/tts/languages');

// Long Form
export const startLongFormJob = (data) => client.post('/api/tts/long-form/start', data);
export const getLongFormStatus = (jobId) => client.get(`/api/tts/long-form/${jobId}/status`);
export const retryLongFormJob = (jobId) => client.post(`/api/tts/long-form/${jobId}/retry`);

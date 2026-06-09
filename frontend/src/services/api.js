import axios from 'axios';

const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_BASE = BASE.replace('http', 'ws');
const API = axios.create({ baseURL: BASE });

export const getStats        = ()           => API.get('/api/stats');
export const getArticles     = (params={})  => API.get('/api/articles', { params });
export const getArticle      = (id)         => API.get(`/api/articles/${id}`);
export const ingestArticle   = (data)       => API.post('/api/articles', data);
export const transcribeContent = (data)     => API.post('/api/transcribe', data);
export const editorAction    = (id, data)   => API.post(`/api/articles/${id}/action`, data);
export const getArticleSummary = (id, lang='en') => API.get(`/api/articles/${id}/summary`, { params: { language: lang } });
export const checkTone       = (id, code='en') => API.get(`/api/articles/${id}/tone-check`, { params: { language_code: code } });
export const getLanguages    = ()           => API.get('/api/languages');

export const createWebSocket = (onMessage) => {
  const ws = new WebSocket(`${WS_BASE}/ws`);
  ws.onmessage = (e) => {
    try { onMessage(JSON.parse(e.data)); } catch(_) {}
  };
  ws.onerror = () => {};
  return ws;
};

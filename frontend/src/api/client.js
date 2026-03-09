import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5001/api',
  timeout: 10000,
})

export const fetchThemes = () => api.get('/themes')
export const fetchThemeDetail = (slug) => api.get(`/themes/${slug}`)
export const fetchThemeArticles = (slug, date) =>
  api.get(`/themes/${slug}/articles`, { params: { date } })
export const searchMemory = ({ q, from, to } = {}) =>
  api.get('/memory/search', { params: { q, from, to } })
export const fetchStatus = () => api.get('/status')

export default api

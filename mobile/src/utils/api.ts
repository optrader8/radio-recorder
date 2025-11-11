import axios, { AxiosInstance, AxiosError } from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient: AxiosInstance = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add request interceptor to include auth token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API endpoints
export const playbackAPI = {
  getStations: () => apiClient.get('/playback/stations'),
  startStream: (stationId: string, bitrate: number = 192, skipAds: boolean = true) =>
    apiClient.get(`/playback/stream/${stationId}`, {
      params: { bitrate, skip_ads: skipAds },
    }),
  pauseSession: (sessionId: string) => apiClient.post(`/playback/session/${sessionId}/pause`),
  resumeSession: (sessionId: string) => apiClient.post(`/playback/session/${sessionId}/resume`),
  getSessionStatus: (sessionId: string) => apiClient.get(`/playback/session/${sessionId}`),
  listSessions: () => apiClient.get('/playback/sessions'),
}

export const recordingAPI = {
  startRecording: (stationId: string, bitrate: number = 192) =>
    apiClient.post('/recordings/start', { station_id: stationId, bitrate }),
  stopRecording: (recordingId: string) => apiClient.post(`/recordings/${recordingId}/stop`),
  pauseRecording: (recordingId: string) => apiClient.post(`/recordings/${recordingId}/pause`),
  resumeRecording: (recordingId: string) => apiClient.post(`/recordings/${recordingId}/resume`),
  getRecordingStatus: (recordingId: string) => apiClient.get(`/recordings/${recordingId}/status`),
  getActiveRecordings: () => apiClient.get('/recordings/active'),
}

export const analysisAPI = {
  getAnalysis: (recordingId: string) => apiClient.get(`/analysis/recording/${recordingId}`),
  transcribe: (recordingId: string, filePath: string, language?: string) =>
    apiClient.post(`/analysis/recording/${recordingId}/transcribe`, {
      file_path: filePath,
      language,
    }),
  analyzeVoice: (recordingId: string, filePath: string) =>
    apiClient.post(`/analysis/recording/${recordingId}/voice-analysis`, {
      file_path: filePath,
    }),
  getPlaybackHistory: (limit: number = 50) =>
    apiClient.get('/analysis/playback-history', { params: { limit } }),
  submitAdFeedback: (
    recordingId: string | null,
    startTime: number,
    endTime: number,
    feedbackType: string,
    notes?: string
  ) =>
    apiClient.post('/analysis/ad-feedback', {
      recording_id: recordingId,
      start_time: startTime,
      end_time: endTime,
      feedback_type: feedbackType,
      notes,
    }),
}

export const converterAPI = {
  getFormats: () => apiClient.get('/converter/formats'),
  convert: (filePath: string, targetFormat: string, bitrate: number = 192) =>
    apiClient.post('/converter/convert', {
      file_path: filePath,
      target_format: targetFormat,
      bitrate,
    }),
  getAudioInfo: (filename: string) => apiClient.get(`/converter/audio-info/${filename}`),
}

export const authAPI = {
  login: (email: string, password: string) =>
    apiClient.post('/auth/login', { email, password }),
  register: (email: string, password: string, username: string) =>
    apiClient.post('/auth/register', { email, password, username }),
  logout: () => apiClient.post('/auth/logout'),
  refreshToken: (refreshToken: string) =>
    apiClient.post('/auth/refresh', { refresh_token: refreshToken }),
}

export const webhooksAPI = {
  createWebhook: (url: string, eventTypes: string[], description?: string) =>
    apiClient.post('/webhooks', { url, event_types: eventTypes, description }),
  listWebhooks: () => apiClient.get('/webhooks'),
  getWebhook: (webhookId: string) => apiClient.get(`/webhooks/${webhookId}`),
  updateWebhook: (
    webhookId: string,
    url?: string,
    eventTypes?: string[],
    description?: string,
    isActive?: boolean
  ) =>
    apiClient.patch(`/webhooks/${webhookId}`, {
      url,
      event_types: eventTypes,
      description,
      is_active: isActive,
    }),
  deleteWebhook: (webhookId: string) => apiClient.delete(`/webhooks/${webhookId}`),
  testWebhook: (webhookId: string) => apiClient.post(`/webhooks/${webhookId}/test`),
}

export default apiClient

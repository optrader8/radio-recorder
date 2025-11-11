import { apiClient } from './client'

export interface RecordingSession {
  session_id: string
  station_id: string
  station_name: string
  title: string
  file_path: string
  status: 'pending' | 'buffering' | 'recording' | 'paused' | 'stopping' | 'completed' | 'error'
  duration_seconds: number
  file_size_bytes: number
  file_size_mb: number
  bitrate: number
  sample_rate: number
  format: string
  skip_ads: boolean
  quality: string
  started_at?: string
  paused_at?: string
  completed_at?: string
  elapsed_seconds: number
  total_paused_seconds: number
  error_message?: string
}

export interface StartRecordingRequest {
  station_id: string
  title: string
  bitrate?: number
  sample_rate?: number
  format?: string
  skip_ads?: boolean
  duration_minutes?: number
}

// Start a new recording
export async function startRecording(
  request: StartRecordingRequest
): Promise<{ session_id: string; status: string; station: string; file_path: string; data: RecordingSession }> {
  const { data } = await apiClient.post('/recordings/start', request)
  return data
}

// Stop an active recording
export async function stopRecording(sessionId: string): Promise<{ session_id: string; status: string; data: RecordingSession }> {
  const { data } = await apiClient.post(`/recordings/${sessionId}/stop`)
  return data
}

// Pause a recording
export async function pauseRecording(sessionId: string): Promise<{ session_id: string; status: string; data: RecordingSession }> {
  const { data } = await apiClient.post(`/recordings/${sessionId}/pause`)
  return data
}

// Resume a paused recording
export async function resumeRecording(sessionId: string): Promise<{ session_id: string; status: string; data: RecordingSession }> {
  const { data } = await apiClient.post(`/recordings/${sessionId}/resume`)
  return data
}

// Get recording status
export async function getRecordingStatus(sessionId: string): Promise<{ session_id: string; data: RecordingSession }> {
  const { data } = await apiClient.get(`/recordings/${sessionId}/status`)
  return data
}

// Get active recordings
export async function getActiveRecordings(): Promise<{ active_recordings: RecordingSession[]; total: number }> {
  const { data } = await apiClient.get('/recordings/active')
  return data
}

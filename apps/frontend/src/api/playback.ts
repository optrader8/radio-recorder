import { apiClient } from './client'

export interface RadioStation {
  id: string
  name: string
  stream_url: string
  description?: string
  genre?: string
  country?: string
  language?: string
}

export interface PlaybackSession {
  session_id: string
  station_id: string
  station_name: string
  status: 'idle' | 'playing' | 'paused' | 'stopped' | 'buffering' | 'error'
  current_position: number
  duration?: number
  bitrate: number
  sample_rate: number
  skip_ads: boolean
  volume: number
  started_at?: string
  paused_at?: string
  error_message?: string
}

// Get list of radio stations
export async function fetchStations(): Promise<RadioStation[]> {
  try {
    const { data } = await apiClient.get<{ stations: RadioStation[] }>('/playback/stations')
    return data.stations
  } catch (error) {
    console.error('Failed to fetch stations:', error)
    return []
  }
}

// Start streaming a station (returns blob stream)
export async function startStream(
  stationId: string,
  options?: {
    bitrate?: number
    format?: string
    skip_ads?: boolean
  }
): Promise<Response> {
  const params = new URLSearchParams()
  if (options?.bitrate) params.append('bitrate', options.bitrate.toString())
  if (options?.format) params.append('format', options.format)
  if (options?.skip_ads) params.append('skip_ads', 'true')

  const apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
  const token = localStorage.getItem('authToken')

  const response = await fetch(
    `${apiBaseUrl}/api/v1/playback/stream/${stationId}?${params.toString()}`,
    {
      method: 'GET',
      headers: {
        'Authorization': token ? `Bearer ${token}` : '',
      },
    }
  )

  if (!response.ok) {
    throw new Error(`Failed to start stream: ${response.statusText}`)
  }

  return response
}

// Pause playback session
export async function pauseSession(sessionId: string): Promise<{ session: PlaybackSession }> {
  const { data } = await apiClient.post(`/playback/session/${sessionId}/pause`)
  return data
}

// Resume playback session
export async function resumeSession(sessionId: string): Promise<{ session: PlaybackSession }> {
  const { data } = await apiClient.post(`/playback/session/${sessionId}/resume`)
  return data
}

// Get session status
export async function getSessionStatus(sessionId: string): Promise<{ session: PlaybackSession }> {
  const { data } = await apiClient.get(`/playback/session/${sessionId}`)
  return data
}

// List all playback sessions
export async function listSessions(): Promise<{ sessions: PlaybackSession[]; total: number }> {
  const { data } = await apiClient.get('/playback/sessions')
  return data
}

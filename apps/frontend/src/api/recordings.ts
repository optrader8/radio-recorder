import axios from 'axios'

import { apiClient } from './client'

export interface Recording {
  id: string
  station_id: string
  schedule_id: string | null
  title?: string | null
  status: string
  format?: string | null
  bitrate?: number | null
  sample_rate?: number | null
  duration_seconds?: number | null
  started_at?: string | null
  completed_at?: string | null
  created_at?: string | null
}

export async function fetchRecordings(): Promise<Recording[]> {
  try {
    const { data } = await apiClient.get<Recording[]>('/recordings')
    return data
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      return []
    }
    throw error
  }
}

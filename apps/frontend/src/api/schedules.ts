import axios from 'axios'

import { apiClient } from './client'

export interface Schedule {
  id: string
  station_id: string
  user_id: string
  name: string
  cron_expression: string
  duration_minutes: number
  format: string
  bitrate: number
  sample_rate: number
  is_active: boolean
  created_at?: string | null
  next_run_at?: string | null
}

export async function fetchSchedules(): Promise<Schedule[]> {
  try {
    const { data } = await apiClient.get<Schedule[]>('/schedules')
    return data
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 401) {
      return []
    }
    throw error
  }
}

export interface CreateSchedulePayload {
  station_id: string
  name: string
  cron_expression: string
  duration_minutes: number
  format?: string
  bitrate?: number
  sample_rate?: number
  is_active?: boolean
}

export async function createSchedule(payload: CreateSchedulePayload): Promise<void> {
  try {
    await apiClient.post('/schedules', payload)
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      throw new Error('존재하지 않는 스테이션입니다.')
    }
    if (axios.isAxiosError(error) && error.response?.data?.detail) {
      throw new Error(error.response.data.detail)
    }
    throw new Error('스케줄 생성에 실패했습니다.')
  }
}

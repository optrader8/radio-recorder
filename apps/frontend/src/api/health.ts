import { apiClient } from './client'

export interface ServiceStatus {
  status: string
  message?: string
  free_space_gb?: number
  total_space_gb?: number
  used_space_gb?: number
}

export interface DetailedHealth {
  status: string
  environment: string
  version: string
  timestamp: string
  services: {
    database?: ServiceStatus
    redis?: ServiceStatus
    storage?: ServiceStatus
  }
  system?: {
    cpu_percent?: number
    memory_percent?: number
    memory_available_gb?: number
    memory_total_gb?: number
  }
}

export async function fetchDetailedHealth(): Promise<DetailedHealth> {
  const { data } = await apiClient.get<DetailedHealth>('/health/detailed')
  return data
}

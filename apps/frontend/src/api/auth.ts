import axios from 'axios'

import { apiClient } from './client'

export interface AuthResponse {
  access_token: string
  token_type: string
}

export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload extends LoginPayload {
  email: string
}

export async function login(payload: LoginPayload): Promise<AuthResponse> {
  try {
    const { data } = await apiClient.post<AuthResponse>('/auth/login', payload)
    return data
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data?.detail ?? '인증에 실패했습니다.')
    }
    throw new Error('네트워크 오류가 발생했습니다.')
  }
}

export async function register(payload: RegisterPayload): Promise<void> {
  try {
    await apiClient.post('/auth/register', payload)
  } catch (error) {
    if (axios.isAxiosError(error) && error.response) {
      throw new Error(error.response.data?.detail ?? '회원가입에 실패했습니다.')
    }
    throw new Error('네트워크 오류가 발생했습니다.')
  }
}

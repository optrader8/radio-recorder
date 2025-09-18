import { create } from 'zustand'

import { clearToken, getToken, setToken } from '@/lib/auth'

interface AuthState {
  token: string | null
  setToken: (token: string) => void
  clear: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: getToken(),
  setToken: (token: string) => {
    setToken(token)
    set({ token })
  },
  clear: () => {
    clearToken()
    set({ token: null })
  },
}))

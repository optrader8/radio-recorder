import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type Theme = 'light' | 'dark' | 'system'

interface ThemeStore {
  theme: Theme
  setTheme: (theme: Theme) => void
  isDark: boolean
  setIsDark: (isDark: boolean) => void
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set) => ({
      theme: 'system',
      isDark: window.matchMedia('(prefers-color-scheme: dark)').matches,
      setTheme: (theme: Theme) => {
        set({ theme })
        applyTheme(theme)
      },
      setIsDark: (isDark: boolean) => set({ isDark }),
    }),
    {
      name: 'theme-store',
    }
  )
)

function applyTheme(theme: Theme) {
  const isDark = theme === 'dark' ||
    (theme === 'system' && window.matchMedia('(prefers-color-scheme: dark)').matches)

  const html = document.documentElement
  if (isDark) {
    html.classList.add('dark')
  } else {
    html.classList.remove('dark')
  }
}

// Apply theme on initialization
if (typeof window !== 'undefined') {
  const theme = useThemeStore.getState().theme
  applyTheme(theme)
}

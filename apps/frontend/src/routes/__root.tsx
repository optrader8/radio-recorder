import { Outlet, Link } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/router-devtools'

import { useAuthStore } from '@/stores/auth'

function RootComponent() {
  const token = useAuthStore((state) => state.token)
  const clear = useAuthStore((state) => state.clear)

  return (
    <>
      <div className="min-h-screen bg-background font-sans antialiased">
        <header className="border-b bg-white">
          <div className="container mx-auto flex items-center justify-between px-4 py-4">
            <Link to="/" className="text-lg font-semibold text-gray-900">
              Radio Recorder
            </Link>
            <nav className="flex items-center gap-4 text-sm text-gray-700">
              {token ? (
                <>
                  <Link to="/dashboard" className="hover:text-indigo-600">
                    Dashboard
                  </Link>
                  <Link to="/radio-player" className="hover:text-indigo-600">
                    라디오
                  </Link>
                  <Link to="/schedules" className="hover:text-indigo-600">
                    Schedules
                  </Link>
                  <button
                    type="button"
                    onClick={() => {
                      if (window.confirm('로그아웃하시겠습니까?')) {
                        clear()
                      }
                    }}
                    className="rounded-md border border-gray-300 px-3 py-1 hover:bg-gray-100"
                  >
                    로그아웃
                  </button>
                </>
              ) : (
                <>
                  <Link to="/login" className="hover:text-indigo-600">
                    로그인
                  </Link>
                  <Link to="/register" className="hover:text-indigo-600">
                    회원가입
                  </Link>
                </>
              )}
            </nav>
          </div>
        </header>
        <Outlet />
      </div>
      <TanStackRouterDevtools />
    </>
  )
}

export default RootComponent

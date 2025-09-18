import { FormEvent, useState } from 'react'

import { useNavigate, Link } from '@tanstack/react-router'

import { login } from '@/api/auth'
import { useAuthStore } from '@/stores/auth'

function LoginPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const setToken = useAuthStore((state) => state.setToken)
  const navigate = useNavigate()

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setSubmitting(true)
    setError(null)

    try {
      const result = await login({ username, password })
      setToken(result.access_token)
      navigate({ to: '/dashboard' })
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('로그인에 실패했습니다. 정보를 확인하세요.')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4">
      <div className="w-full max-w-md rounded-lg bg-white p-8 shadow">
        <h1 className="mb-6 text-2xl font-semibold text-gray-900">로그인</h1>
        <form className="space-y-5" onSubmit={handleSubmit}>
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="username">
              사용자명
            </label>
            <input
              id="username"
              name="username"
              type="text"
              required
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="password">
              비밀번호
            </label>
            <input
              id="password"
              name="password"
              type="password"
              required
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="w-full rounded-md border border-gray-300 px-3 py-2 shadow-sm focus:border-indigo-500 focus:outline-none"
            />
          </div>

          {error ? <p className="text-sm text-red-600">{error}</p> : null}

          <button
            type="submit"
            disabled={submitting}
            className="w-full rounded-md bg-indigo-600 px-4 py-2 text-white shadow hover:bg-indigo-500 disabled:opacity-60"
          >
            {submitting ? '로그인 중...' : '로그인'}
          </button>
        </form>

        <p className="mt-4 text-sm text-gray-600">
          아직 계정이 없나요?{' '}
          <Link to="/register" className="text-indigo-600 hover:underline">
            회원가입
          </Link>
        </p>
      </div>
    </div>
  )
}

export default LoginPage

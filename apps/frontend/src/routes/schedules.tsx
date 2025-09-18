import { FormEvent, useEffect, useMemo, useState } from 'react'

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'

import { createSchedule, fetchSchedules } from '@/api/schedules'
import { useAuthStore } from '@/stores/auth'

const defaultForm = {
  station_id: '',
  name: '',
  cron_expression: '0 * * * *',
  duration_minutes: 60,
  format: 'mp3',
  bitrate: 128,
  sample_rate: 44100,
}

function SchedulesPage() {
  const token = useAuthStore((state) => state.token)
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [form, setForm] = useState(defaultForm)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) {
      navigate({ to: '/login' })
    }
  }, [navigate, token])

  const { data: schedules = [], isLoading } = useQuery({
    queryKey: ['schedules'],
    queryFn: fetchSchedules,
    enabled: Boolean(token),
    placeholderData: [],
  })

  const mutation = useMutation({
    mutationFn: createSchedule,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ['schedules'] })
      setForm(defaultForm)
      setError(null)
    },
    onError: (err) => {
      if (err instanceof Error) {
        setError(err.message)
      } else {
        setError('스케줄 생성 중 오류가 발생했습니다.')
      }
    },
  })

  if (!token) {
    return null
  }

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    mutation.mutate({
      station_id: form.station_id,
      name: form.name,
      cron_expression: form.cron_expression,
      duration_minutes: Number(form.duration_minutes),
      format: form.format,
      bitrate: Number(form.bitrate),
      sample_rate: Number(form.sample_rate),
    })
  }

  const upcomingSchedules = useMemo(
    () =>
      schedules
        .slice()
        .sort((a, b) => {
          const aTime = a.next_run_at ? new Date(a.next_run_at).getTime() : Number.MAX_SAFE_INTEGER
          const bTime = b.next_run_at ? new Date(b.next_run_at).getTime() : Number.MAX_SAFE_INTEGER
          return aTime - bTime
        }),
    [schedules],
  )

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8 flex items-center justify-between">
        <h1 className="text-3xl font-bold">스케줄 관리</h1>
      </div>

      <div className="grid gap-8 lg:grid-cols-2">
        <div className="rounded-lg bg-white p-6 shadow">
          <h2 className="mb-4 text-xl font-semibold">새 스케줄 추가</h2>
          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="station_id">
                스테이션 ID
              </label>
              <input
                id="station_id"
                name="station_id"
                required
                value={form.station_id}
                onChange={(event) => setForm((prev) => ({ ...prev, station_id: event.target.value }))}
                className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="name">
                스케줄 이름
              </label>
              <input
                id="name"
                name="name"
                required
                value={form.name}
                onChange={(event) => setForm((prev) => ({ ...prev, name: event.target.value }))}
                className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="cron_expression">
                Cron 표현식
              </label>
              <input
                id="cron_expression"
                name="cron_expression"
                required
                value={form.cron_expression}
                onChange={(event) => setForm((prev) => ({ ...prev, cron_expression: event.target.value }))}
                className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none"
              />
              <p className="mt-1 text-xs text-gray-500">예: 매시간 0분에 실행 - <code>0 * * * *</code></p>
            </div>

            <div className="grid gap-4 sm:grid-cols-3">
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="duration_minutes">
                  길이(분)
                </label>
                <input
                  id="duration_minutes"
                  type="number"
                  min={1}
                  value={form.duration_minutes}
                  onChange={(event) => setForm((prev) => ({ ...prev, duration_minutes: Number(event.target.value) }))}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="format">
                  포맷
                </label>
                <input
                  id="format"
                  value={form.format}
                  onChange={(event) => setForm((prev) => ({ ...prev, format: event.target.value }))}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none"
                />
              </div>
              <div>
                <label className="mb-1 block text-sm font-medium text-gray-700" htmlFor="bitrate">
                  비트레이트
                </label>
                <input
                  id="bitrate"
                  type="number"
                  min={32}
                  step={32}
                  value={form.bitrate}
                  onChange={(event) => setForm((prev) => ({ ...prev, bitrate: Number(event.target.value) }))}
                  className="w-full rounded-md border border-gray-300 px-3 py-2 focus:border-indigo-500 focus:outline-none"
                />
              </div>
            </div>

            {error ? <p className="text-sm text-red-600">{error}</p> : null}

            <button
              type="submit"
              disabled={mutation.isPending}
              className="w-full rounded-md bg-indigo-600 px-4 py-2 text-white shadow hover:bg-indigo-500 disabled:opacity-60"
            >
              {mutation.isPending ? '생성 중...' : '스케줄 생성'}
            </button>
          </form>
        </div>

        <div className="rounded-lg bg-white p-6 shadow">
          <h2 className="mb-4 text-xl font-semibold">등록된 스케줄</h2>
          {isLoading ? (
            <p className="text-sm text-gray-500">불러오는 중...</p>
          ) : upcomingSchedules.length === 0 ? (
            <p className="text-sm text-gray-500">등록된 스케줄이 없습니다.</p>
          ) : (
            <ul className="space-y-3">
              {upcomingSchedules.map((schedule) => (
                <li key={schedule.id} className="rounded border border-gray-200 p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{schedule.name}</p>
                      <p className="text-sm text-gray-500">{schedule.cron_expression}</p>
                    </div>
                    <span className="text-sm text-indigo-600">
                      {schedule.next_run_at
                        ? new Date(schedule.next_run_at).toLocaleString()
                        : '계산 중'}
                    </span>
                  </div>
                  <div className="mt-2 grid gap-4 text-sm text-gray-600 sm:grid-cols-3">
                    <span>길이: {schedule.duration_minutes}분</span>
                    <span>포맷: {schedule.format}</span>
                    <span>활성화: {schedule.is_active ? '예' : '아니오'}</span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}

export default SchedulesPage

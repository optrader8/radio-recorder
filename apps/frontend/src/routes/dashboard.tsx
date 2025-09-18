import { useEffect, useMemo } from 'react'

import { useQuery } from '@tanstack/react-query'
import { useNavigate } from '@tanstack/react-router'

import { fetchDetailedHealth } from '@/api/health'
import { fetchRecordings } from '@/api/recordings'
import { fetchSchedules } from '@/api/schedules'
import { useAuthStore } from '@/stores/auth'

function DashboardPage() {
  const token = useAuthStore((state) => state.token)
  const navigate = useNavigate()

  useEffect(() => {
    if (!token) {
      navigate({ to: '/login' })
    }
  }, [navigate, token])

  if (!token) {
    return null
  }

  const {
    data: healthData,
    isLoading: isHealthLoading,
    isError: isHealthError,
  } = useQuery({
    queryKey: ['health', 'detailed'],
    queryFn: fetchDetailedHealth,
    staleTime: 60_000,
    retry: 1,
  })

  const { data: recordings = [] } = useQuery({
    queryKey: ['recordings'],
    queryFn: fetchRecordings,
    staleTime: 30_000,
    retry: false,
    placeholderData: [],
  })

  const { data: schedules = [] } = useQuery({
    queryKey: ['schedules'],
    queryFn: fetchSchedules,
    staleTime: 30_000,
    retry: false,
    placeholderData: [],
  })

  const activeRecordings = useMemo(
    () => recordings.filter((recording) => recording.status === 'recording').length,
    [recordings],
  )

  const totalRecordings = recordings.length
  const scheduledJobs = schedules.length

  const storageUsage = healthData?.services.storage
  const storageUsed = storageUsage?.used_space_gb ?? 0
  const storageTotal = storageUsage?.total_space_gb

  const apiStatus = isHealthError
    ? 'Unavailable'
    : isHealthLoading
      ? 'Loading...'
      : healthData?.status ?? 'Unknown'
  const databaseStatus = healthData?.services.database?.status ?? 'unknown'
  const redisStatus = healthData?.services.redis?.status ?? 'unknown'

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Active Recordings</h3>
          <p className="text-2xl font-bold text-gray-900">{activeRecordings}</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Total Recordings</h3>
          <p className="text-2xl font-bold text-gray-900">{totalRecordings}</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Scheduled Jobs</h3>
          <p className="text-2xl font-bold text-gray-900">{scheduledJobs}</p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-sm font-medium text-gray-500">Storage Used</h3>
          <p className="text-2xl font-bold text-gray-900">
            {storageTotal ? `${storageUsed.toFixed(1)} / ${storageTotal.toFixed(1)} GB` : `${storageUsed.toFixed(1)} GB`}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Recent Recordings</h2>
          {totalRecordings === 0 ? (
            <p className="text-gray-500">
              No recordings yet. Start your first recording to see it here.
            </p>
          ) : (
            <ul className="space-y-3">
              {recordings.slice(0, 5).map((recording) => (
                <li key={recording.id} className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">{recording.title ?? 'Untitled Recording'}</p>
                    <p className="text-sm text-gray-500">
                      Status: {recording.status}
                    </p>
                  </div>
                  <span className="text-sm text-gray-500">
                    {recording.started_at
                      ? new Date(recording.started_at).toLocaleString()
                      : 'Pending'}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">System Status</h2>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>API Status</span>
              <span className={apiStatus.toLowerCase().includes('healthy') ? 'text-green-600' : 'text-yellow-600'}>
                {apiStatus}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Database</span>
              <span className={databaseStatus === 'healthy' ? 'text-green-600' : 'text-yellow-600'}>
                {databaseStatus}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Redis</span>
              <span className={redisStatus === 'healthy' ? 'text-green-600' : 'text-yellow-600'}>
                {redisStatus}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage

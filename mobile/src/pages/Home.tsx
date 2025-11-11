import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { StatusBar, Style } from '@capacitor/status-bar'

export default function Home() {
  const navigate = useNavigate()
  const [stats, setStats] = useState({
    totalRecordings: 0,
    totalDuration: 0,
    lastRecording: null as any,
  })

  useEffect(() => {
    // Set status bar color for home page
    const setStatusBar = async () => {
      try {
        await StatusBar.setStyle({ style: Style.Light })
        await StatusBar.setBackgroundColor({ color: '#0066cc' })
      } catch (e) {
        // Ignore if not supported
      }
    }
    setStatusBar()
  }, [])

  useEffect(() => {
    // Fetch user stats from API
    const fetchStats = async () => {
      try {
        // This would fetch from your backend
        setStats({
          totalRecordings: 24,
          totalDuration: 3600, // seconds
          lastRecording: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
        })
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      }
    }
    fetchStats()
  }, [])

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  return (
    <div className="flex flex-col h-full">
      {/* Hero Section */}
      <div className="bg-gradient-to-b from-blue-500 to-blue-600 text-white p-6 pt-6">
        <div className="text-center mb-8">
          <div className="text-5xl font-bold mb-2">📻</div>
          <h1 className="text-3xl font-bold mb-2">Radio Recorder</h1>
          <p className="text-blue-100">Record, analyze, and enjoy radio stations</p>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white bg-opacity-20 rounded-lg p-4 backdrop-blur">
            <div className="text-3xl font-bold">{stats.totalRecordings}</div>
            <div className="text-sm text-blue-100">Total Recordings</div>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-4 backdrop-blur">
            <div className="text-3xl font-bold">{formatDuration(stats.totalDuration)}</div>
            <div className="text-sm text-blue-100">Total Duration</div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="flex-1 p-6 overflow-y-auto">
        <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Quick Actions</h2>

        <div className="grid grid-cols-1 gap-4">
          {/* Listen Now */}
          <button
            onClick={() => navigate('/radio-player')}
            className="group bg-gradient-to-r from-green-400 to-green-500 text-white rounded-lg p-6 shadow-lg hover:shadow-xl transition active:scale-95"
          >
            <div className="text-4xl mb-2">🎵</div>
            <h3 className="text-lg font-bold">Listen Now</h3>
            <p className="text-sm text-green-100">Stream your favorite stations</p>
          </button>

          {/* Start Recording */}
          <button
            onClick={() => navigate('/recorder')}
            className="group bg-gradient-to-r from-red-400 to-red-500 text-white rounded-lg p-6 shadow-lg hover:shadow-xl transition active:scale-95"
          >
            <div className="text-4xl mb-2">🎙️</div>
            <h3 className="text-lg font-bold">Start Recording</h3>
            <p className="text-sm text-red-100">Record radio broadcasts</p>
          </button>

          {/* View Analytics */}
          <button
            onClick={() => navigate('/dashboard')}
            className="group bg-gradient-to-r from-purple-400 to-purple-500 text-white rounded-lg p-6 shadow-lg hover:shadow-xl transition active:scale-95"
          >
            <div className="text-4xl mb-2">📊</div>
            <h3 className="text-lg font-bold">Analytics</h3>
            <p className="text-sm text-purple-100">View recordings and analysis</p>
          </button>
        </div>

        {/* Recent Recordings */}
        <div className="mt-8">
          <h2 className="text-lg font-bold mb-4 text-gray-900 dark:text-white">Features</h2>
          <div className="space-y-3">
            <div className="flex items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <span className="text-2xl mr-3">✨</span>
              <div className="flex-1">
                <p className="font-semibold text-gray-900 dark:text-white">Real-time Streaming</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Stream from thousands of stations</p>
              </div>
            </div>

            <div className="flex items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <span className="text-2xl mr-3">🤖</span>
              <div className="flex-1">
                <p className="font-semibold text-gray-900 dark:text-white">AI Analysis</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Transcription & voice analysis</p>
              </div>
            </div>

            <div className="flex items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <span className="text-2xl mr-3">📵</span>
              <div className="flex-1">
                <p className="font-semibold text-gray-900 dark:text-white">Smart Ad Skipping</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Automatic ad detection & removal</p>
              </div>
            </div>

            <div className="flex items-center p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <span className="text-2xl mr-3">📱</span>
              <div className="flex-1">
                <p className="font-semibold text-gray-900 dark:text-white">Mobile Optimized</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">Works seamlessly on all devices</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

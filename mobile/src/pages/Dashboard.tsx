import { useState, useEffect } from 'react'

interface AnalysisResult {
  id: string
  recordingId: string
  stationName: string
  transcriptionText: string
  language: string
  confidence: number
  voiceQuality: {
    clarityScore: number
    noiseLevel: number
    overall: number
  }
  detectedAds: Array<{ start: number; end: number; confidence: number }>
  processedAt: Date
}

interface PlaybackHistory {
  id: string
  stationName: string
  duration: number
  date: Date
}

export default function Dashboard() {
  const [analysis, setAnalysis] = useState<AnalysisResult[]>([])
  const [playbackHistory, setPlaybackHistory] = useState<PlaybackHistory[]>([])
  const [stats, setStats] = useState({
    totalListeningTime: 0,
    totalRecordings: 0,
    adsDetected: 0,
    totalTranscriptions: 0,
  })
  const [selectedTab, setSelectedTab] = useState<'overview' | 'transcriptions' | 'history'>('overview')

  useEffect(() => {
    // Mock data for development
    setStats({
      totalListeningTime: 43200, // 12 hours
      totalRecordings: 8,
      adsDetected: 24,
      totalTranscriptions: 5,
    })

    setAnalysis([
      {
        id: '1',
        recordingId: 'rec-1',
        stationName: 'BBC Radio 1',
        transcriptionText: 'Welcome to BBC Radio 1. Today we have...',
        language: 'en',
        confidence: 0.95,
        voiceQuality: { clarityScore: 0.88, noiseLevel: -35, overall: 0.85 },
        detectedAds: [
          { start: 600, end: 660, confidence: 0.92 },
          { start: 1800, end: 1860, confidence: 0.88 },
        ],
        processedAt: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000),
      },
      {
        id: '2',
        recordingId: 'rec-2',
        stationName: 'Radio FG',
        transcriptionText: 'Electronic music for your weekend...',
        language: 'fr',
        confidence: 0.92,
        voiceQuality: { clarityScore: 0.82, noiseLevel: -32, overall: 0.80 },
        detectedAds: [{ start: 120, end: 180, confidence: 0.85 }],
        processedAt: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
      },
    ])

    setPlaybackHistory([
      {
        id: '1',
        stationName: 'BBC Radio 1',
        duration: 3600,
        date: new Date(Date.now() - 1 * 60 * 60 * 1000),
      },
      {
        id: '2',
        stationName: 'Capital FM',
        duration: 1800,
        date: new Date(Date.now() - 3 * 60 * 60 * 1000),
      },
      {
        id: '3',
        stationName: 'NTS Radio',
        duration: 2700,
        date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000),
      },
    ])
  }, [])

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    if (hours > 0) {
      return `${hours}h ${minutes}m`
    }
    return `${minutes}m`
  }

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date)
  }

  const formatPercent = (value: number) => {
    return `${Math.round(value * 100)}%`
  }

  return (
    <div className="flex flex-col h-full bg-white dark:bg-slate-950">
      {/* Header */}
      <div className="bg-gradient-to-b from-purple-500 to-purple-600 text-white p-6">
        <h1 className="text-2xl font-bold mb-4">📊 Analytics Dashboard</h1>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-white bg-opacity-20 rounded-lg p-3 backdrop-blur">
            <p className="text-2xl font-bold">{formatTime(stats.totalListeningTime)}</p>
            <p className="text-xs text-purple-100">Total Listening</p>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-3 backdrop-blur">
            <p className="text-2xl font-bold">{stats.totalRecordings}</p>
            <p className="text-xs text-purple-100">Recordings</p>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-3 backdrop-blur">
            <p className="text-2xl font-bold">{stats.adsDetected}</p>
            <p className="text-xs text-purple-100">Ads Detected</p>
          </div>
          <div className="bg-white bg-opacity-20 rounded-lg p-3 backdrop-blur">
            <p className="text-2xl font-bold">{stats.totalTranscriptions}</p>
            <p className="text-xs text-purple-100">Transcriptions</p>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900">
        <button
          onClick={() => setSelectedTab('overview')}
          className={`flex-1 py-4 px-4 text-center font-semibold transition ${
            selectedTab === 'overview'
              ? 'border-b-2 border-purple-500 text-purple-600 dark:text-purple-400'
              : 'text-gray-600 dark:text-gray-400'
          }`}
        >
          Overview
        </button>
        <button
          onClick={() => setSelectedTab('transcriptions')}
          className={`flex-1 py-4 px-4 text-center font-semibold transition ${
            selectedTab === 'transcriptions'
              ? 'border-b-2 border-purple-500 text-purple-600 dark:text-purple-400'
              : 'text-gray-600 dark:text-gray-400'
          }`}
        >
          Transcriptions
        </button>
        <button
          onClick={() => setSelectedTab('history')}
          className={`flex-1 py-4 px-4 text-center font-semibold transition ${
            selectedTab === 'history'
              ? 'border-b-2 border-purple-500 text-purple-600 dark:text-purple-400'
              : 'text-gray-600 dark:text-gray-400'
          }`}
        >
          History
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {selectedTab === 'overview' && (
          <div className="space-y-6">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Listening Patterns</h2>

            {/* Quality Score Card */}
            <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900 dark:to-green-800 rounded-lg p-6">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Average Voice Quality</h3>
              <div className="text-center">
                <div className="text-4xl font-bold text-green-600 dark:text-green-400 mb-2">
                  {formatPercent(0.85)}
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div
                    className="bg-green-600 dark:bg-green-400 h-2 rounded-full"
                    style={{ width: '85%' }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Noise Level */}
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900 dark:to-blue-800 rounded-lg p-6">
              <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Average Noise Level</h3>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 dark:text-blue-400 mb-2">
                  -33 dB
                </div>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  Lower is better (less noise)
                </p>
              </div>
            </div>

            {/* Top Stations */}
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Top Stations</h3>
              <div className="space-y-2">
                {[
                  { name: 'BBC Radio 1', listens: 12 },
                  { name: 'Capital FM', listens: 8 },
                  { name: 'NTS Radio', listens: 6 },
                ].map((station) => (
                  <div key={station.name} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                    <span className="font-semibold text-gray-900 dark:text-white">{station.name}</span>
                    <span className="text-sm text-gray-500 dark:text-gray-400">{station.listens} listens</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {selectedTab === 'transcriptions' && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Analysis Results</h2>

            {analysis.length === 0 ? (
              <p className="text-center text-gray-500 dark:text-gray-400 py-8">No transcriptions yet</p>
            ) : (
              analysis.map((item) => (
                <div
                  key={item.id}
                  className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 space-y-3"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="font-semibold text-gray-900 dark:text-white">
                        {item.stationName}
                      </h3>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {formatDate(item.processedAt)}
                      </p>
                    </div>
                    <span className="text-2xl">📄</span>
                  </div>

                  {/* Transcription Preview */}
                  <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-2">
                    {item.transcriptionText}
                  </p>

                  {/* Quality Metrics */}
                  <div className="grid grid-cols-3 gap-2 text-xs">
                    <div className="bg-white dark:bg-gray-700 rounded p-2">
                      <p className="text-gray-500 dark:text-gray-400">Language</p>
                      <p className="font-semibold text-gray-900 dark:text-white">
                        {item.language.toUpperCase()} ({formatPercent(item.confidence)})
                      </p>
                    </div>
                    <div className="bg-white dark:bg-gray-700 rounded p-2">
                      <p className="text-gray-500 dark:text-gray-400">Clarity</p>
                      <p className="font-semibold text-gray-900 dark:text-white">
                        {formatPercent(item.voiceQuality.clarityScore)}
                      </p>
                    </div>
                    <div className="bg-white dark:bg-gray-700 rounded p-2">
                      <p className="text-gray-500 dark:text-gray-400">Ads Found</p>
                      <p className="font-semibold text-gray-900 dark:text-white">
                        {item.detectedAds.length}
                      </p>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {selectedTab === 'history' && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Playback History</h2>

            {playbackHistory.length === 0 ? (
              <p className="text-center text-gray-500 dark:text-gray-400 py-8">No history yet</p>
            ) : (
              playbackHistory.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg"
                >
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">{item.stationName}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {formatDate(item.date)} • {formatTime(item.duration)}
                    </p>
                  </div>
                  <span className="text-2xl">🎵</span>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  )
}

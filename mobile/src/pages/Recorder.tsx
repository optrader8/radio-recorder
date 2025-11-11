import { useState, useEffect } from 'react'
import { IonSpinner } from '@ionic/react'

interface RecordingSession {
  id: string
  stationId: string
  stationName: string
  status: 'idle' | 'recording' | 'paused' | 'stopped' | 'error'
  duration: number
  fileSize: number
  bitrate: number
  startTime: Date
}

interface Station {
  id: string
  name: string
  genre: string
}

const MOCK_STATIONS: Station[] = [
  { id: '1', name: 'BBC Radio 1', genre: 'Pop' },
  { id: '2', name: 'Radio FG', genre: 'House' },
  { id: '3', name: 'Capital FM', genre: 'Pop' },
  { id: '4', name: 'NTS Radio', genre: 'Electronic' },
  { id: '5', name: 'KEXP', genre: 'Alternative' },
]

export default function Recorder() {
  const [stations, setStations] = useState<Station[]>(MOCK_STATIONS)
  const [selectedStation, setSelectedStation] = useState<Station | null>(null)
  const [recordings, setRecordings] = useState<RecordingSession[]>([])
  const [currentRecording, setCurrentRecording] = useState<RecordingSession | null>(null)
  const [selectedBitrate, setSelectedBitrate] = useState(192)
  const [isLoading, setIsLoading] = useState(false)

  // Update recording duration every second
  useEffect(() => {
    if (currentRecording?.status === 'recording') {
      const timer = setInterval(() => {
        setCurrentRecording((prev) => {
          if (!prev) return null
          return {
            ...prev,
            duration: prev.duration + 1,
            fileSize: Math.floor((prev.bitrate * 1000) / 8 * (prev.duration + 1) / 1024 / 1024),
          }
        })
      }, 1000)
      return () => clearInterval(timer)
    }
  }, [currentRecording?.status])

  const handleStartRecording = async () => {
    if (!selectedStation) return

    setIsLoading(true)
    try {
      const newRecording: RecordingSession = {
        id: 'rec-' + Date.now(),
        stationId: selectedStation.id,
        stationName: selectedStation.name,
        status: 'recording',
        duration: 0,
        fileSize: 0,
        bitrate: selectedBitrate,
        startTime: new Date(),
      }
      setCurrentRecording(newRecording)
      setIsLoading(false)
    } catch (error) {
      console.error('Failed to start recording:', error)
      setIsLoading(false)
    }
  }

  const handlePauseRecording = () => {
    if (currentRecording) {
      setCurrentRecording({ ...currentRecording, status: 'paused' })
    }
  }

  const handleResumeRecording = () => {
    if (currentRecording) {
      setCurrentRecording({ ...currentRecording, status: 'recording' })
    }
  }

  const handleStopRecording = () => {
    if (currentRecording) {
      const stoppedRecording = { ...currentRecording, status: 'stopped' as const }
      setRecordings([stoppedRecording, ...recordings])
      setCurrentRecording(null)
      setSelectedStation(null)
    }
  }

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)
    if (hours > 0) {
      return `${hours}:${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`
    }
    return `${minutes}:${String(secs).padStart(2, '0')}`
  }

  const formatFileSize = (mb: number) => {
    if (mb > 1024) {
      return `${(mb / 1024).toFixed(2)} GB`
    }
    return `${mb.toFixed(2)} MB`
  }

  const statusColor = {
    idle: 'text-gray-500',
    recording: 'text-red-500',
    paused: 'text-yellow-500',
    stopped: 'text-gray-500',
    error: 'text-red-600',
  }

  return (
    <div className="flex flex-col h-full bg-white dark:bg-slate-950">
      {/* Recording Status */}
      {currentRecording && (
        <div className="bg-gradient-to-b from-red-500 to-red-600 text-white p-6">
          <div className="text-center mb-6">
            <div className="text-6xl mb-4 animate-pulse">🎙️</div>
            <h2 className="text-2xl font-bold mb-2">{currentRecording.stationName}</h2>
          </div>

          {/* Recording Stats */}
          <div className="bg-white bg-opacity-20 rounded-lg p-4 backdrop-blur mb-6">
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <p className="text-3xl font-bold">{formatTime(currentRecording.duration)}</p>
                <p className="text-sm text-red-100">Duration</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold">{formatFileSize(currentRecording.fileSize)}</p>
                <p className="text-sm text-red-100">File Size</p>
              </div>
            </div>
          </div>

          {/* Control Buttons */}
          <div className="flex justify-center gap-4">
            {currentRecording.status === 'recording' ? (
              <>
                <button
                  onClick={handlePauseRecording}
                  className="bg-white text-red-500 rounded-full p-4 shadow-lg hover:bg-red-50 transition active:scale-95"
                >
                  <span className="text-2xl">⏸</span>
                </button>
                <button
                  onClick={handleStopRecording}
                  className="bg-yellow-500 text-white rounded-full p-4 shadow-lg hover:bg-yellow-600 transition active:scale-95"
                >
                  <span className="text-2xl">⏹</span>
                </button>
              </>
            ) : (
              <>
                <button
                  onClick={handleResumeRecording}
                  className="bg-white text-red-500 rounded-full p-4 shadow-lg hover:bg-red-50 transition active:scale-95"
                >
                  <span className="text-2xl">▶</span>
                </button>
                <button
                  onClick={handleStopRecording}
                  className="bg-yellow-500 text-white rounded-full p-4 shadow-lg hover:bg-yellow-600 transition active:scale-95"
                >
                  <span className="text-2xl">⏹</span>
                </button>
              </>
            )}
          </div>

          <p className={`text-center mt-4 font-semibold ${statusColor[currentRecording.status]}`}>
            {currentRecording.status === 'recording' && '🔴 Recording'}
            {currentRecording.status === 'paused' && '⏸ Paused'}
          </p>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-6">
          {!currentRecording ? (
            <>
              {/* Station Selection */}
              <h3 className="text-lg font-bold mb-4 text-gray-900 dark:text-white">Select Station</h3>

              <div className="grid grid-cols-1 gap-3 mb-6">
                {stations.map((station) => (
                  <button
                    key={station.id}
                    onClick={() => setSelectedStation(station)}
                    className={`p-4 rounded-lg text-left transition active:scale-95 ${
                      selectedStation?.id === station.id
                        ? 'bg-red-500 text-white shadow-lg'
                        : 'bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    <div className="font-semibold">{station.name}</div>
                    <div className="text-sm opacity-75">{station.genre}</div>
                  </button>
                ))}
              </div>

              {/* Settings */}
              {selectedStation && (
                <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-4">Recording Settings</h4>

                  {/* Bitrate Selection */}
                  <div className="mb-4">
                    <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                      Quality
                    </label>
                    <select
                      value={selectedBitrate}
                      onChange={(e) => setSelectedBitrate(Number(e.target.value))}
                      className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    >
                      <option value={128}>128 kbps (Standard)</option>
                      <option value={192}>192 kbps (High)</option>
                      <option value={256}>256 kbps (Very High)</option>
                      <option value={320}>320 kbps (Maximum)</option>
                    </select>
                  </div>
                </div>
              )}
            </>
          ) : (
            <>
              {/* Recent Recordings */}
              <h3 className="text-lg font-bold mb-4 text-gray-900 dark:text-white">Recent Recordings</h3>
              {recordings.length === 0 ? (
                <p className="text-center text-gray-500 dark:text-gray-400 py-8">No recordings yet</p>
              ) : (
                <div className="grid grid-cols-1 gap-3">
                  {recordings.map((recording) => (
                    <div
                      key={recording.id}
                      className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4"
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="font-semibold text-gray-900 dark:text-white">
                            {recording.stationName}
                          </p>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            {formatTime(recording.duration)} • {formatFileSize(recording.fileSize)}
                          </p>
                        </div>
                        <span className="text-2xl">✅</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Start Recording Button */}
      {!currentRecording && selectedStation && (
        <div className="p-6 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={handleStartRecording}
            disabled={isLoading}
            className="w-full bg-red-500 hover:bg-red-600 text-white font-bold py-4 px-6 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed active:scale-95 flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <IonSpinner name="crescent" />
                Starting...
              </>
            ) : (
              <>
                <span>🎙️</span>
                Start Recording
              </>
            )}
          </button>
        </div>
      )}
    </div>
  )
}

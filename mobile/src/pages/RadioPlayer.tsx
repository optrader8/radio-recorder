import { useState, useEffect, useRef } from 'react'
import { IonSpinner } from '@ionic/react'

interface Station {
  id: string
  name: string
  genre: string
  bitrate: number
  country: string
  logo?: string
}

interface PlaybackSession {
  id: string
  stationId: string
  status: 'idle' | 'playing' | 'paused' | 'buffering' | 'error'
  currentTime: number
  duration: number
  bitrate: number
}

const MOCK_STATIONS: Station[] = [
  {
    id: '1',
    name: 'BBC Radio 1',
    genre: 'Pop',
    bitrate: 128,
    country: 'UK',
  },
  {
    id: '2',
    name: 'Radio FG',
    genre: 'House',
    bitrate: 192,
    country: 'France',
  },
  {
    id: '3',
    name: 'Capital FM',
    genre: 'Pop',
    bitrate: 128,
    country: 'UK',
  },
  {
    id: '4',
    name: 'NTS Radio',
    genre: 'Electronic',
    bitrate: 128,
    country: 'UK',
  },
  {
    id: '5',
    name: 'KEXP',
    genre: 'Alternative',
    bitrate: 192,
    country: 'USA',
  },
]

export default function RadioPlayer() {
  const [stations, setStations] = useState<Station[]>(MOCK_STATIONS)
  const [selectedStation, setSelectedStation] = useState<Station | null>(null)
  const [playback, setPlayback] = useState<PlaybackSession | null>(null)
  const [volume, setVolume] = useState(80)
  const [selectedBitrate, setSelectedBitrate] = useState(128)
  const [skipAds, setSkipAds] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const audioRef = useRef<HTMLAudioElement>(null)

  const handleStationSelect = (station: Station) => {
    if (selectedStation?.id === station.id && playback?.status === 'playing') {
      // Stop current playback
      handleStop()
    } else {
      setSelectedStation(station)
      setPlayback(null)
    }
  }

  const handlePlay = async () => {
    if (!selectedStation) return

    setIsLoading(true)
    try {
      // In a real app, this would call the backend API
      const mockSession: PlaybackSession = {
        id: 'session-' + Date.now(),
        stationId: selectedStation.id,
        status: 'playing',
        currentTime: 0,
        duration: 0,
        bitrate: selectedBitrate,
      }
      setPlayback(mockSession)
      setIsLoading(false)
    } catch (error) {
      console.error('Failed to start playback:', error)
      setIsLoading(false)
    }
  }

  const handlePause = () => {
    if (playback) {
      setPlayback({ ...playback, status: 'paused' })
    }
  }

  const handleResume = () => {
    if (playback) {
      setPlayback({ ...playback, status: 'playing' })
    }
  }

  const handleStop = () => {
    setPlayback(null)
    setSelectedStation(null)
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

  const statusColor = {
    idle: 'text-gray-500',
    playing: 'text-green-500',
    paused: 'text-yellow-500',
    buffering: 'text-blue-500',
    error: 'text-red-500',
  }

  return (
    <div className="flex flex-col h-full bg-white dark:bg-slate-950">
      {/* Now Playing */}
      {selectedStation && (
        <div className="bg-gradient-to-b from-blue-500 to-blue-600 text-white p-6">
          <div className="text-center">
            <div className="text-6xl mb-4">🎵</div>
            <h2 className="text-2xl font-bold mb-2">{selectedStation.name}</h2>
            <p className="text-blue-100 text-sm">
              {selectedStation.genre} • {selectedStation.country}
            </p>
          </div>

          {/* Player Controls */}
          {playback && (
            <div className="mt-8">
              {/* Status */}
              <div className="text-center mb-6">
                <p className={`text-lg font-semibold ${statusColor[playback.status]}`}>
                  {playback.status === 'playing' && '🔴 Now Playing'}
                  {playback.status === 'paused' && '⏸ Paused'}
                  {playback.status === 'buffering' && '⏳ Buffering'}
                  {playback.status === 'error' && '❌ Error'}
                </p>
                <p className="text-sm text-blue-100 mt-2">
                  Bitrate: {playback.bitrate} kbps
                </p>
              </div>

              {/* Control Buttons */}
              <div className="flex justify-center gap-6">
                {playback.status === 'playing' ? (
                  <>
                    <button
                      onClick={handlePause}
                      className="bg-white text-blue-500 rounded-full p-4 shadow-lg hover:bg-blue-50 transition active:scale-95"
                    >
                      <span className="text-2xl">⏸</span>
                    </button>
                    <button
                      onClick={handleStop}
                      className="bg-red-500 text-white rounded-full p-4 shadow-lg hover:bg-red-600 transition active:scale-95"
                    >
                      <span className="text-2xl">⏹</span>
                    </button>
                  </>
                ) : (
                  <>
                    <button
                      onClick={handleResume}
                      className="bg-white text-blue-500 rounded-full p-4 shadow-lg hover:bg-blue-50 transition active:scale-95"
                    >
                      <span className="text-2xl">▶</span>
                    </button>
                    <button
                      onClick={handleStop}
                      className="bg-red-500 text-white rounded-full p-4 shadow-lg hover:bg-red-600 transition active:scale-95"
                    >
                      <span className="text-2xl">⏹</span>
                    </button>
                  </>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Station List or Selection */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-6">
          {selectedStation && playback ? (
            <>
              {/* Settings when playing */}
              <h3 className="text-lg font-bold mb-4 text-gray-900 dark:text-white">Settings</h3>

              {/* Volume Control */}
              <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  Volume: {volume}%
                </label>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={volume}
                  onChange={(e) => setVolume(Number(e.target.value))}
                  className="w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer"
                />
              </div>

              {/* Bitrate Selection */}
              <div className="mb-6">
                <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                  Bitrate
                </label>
                <select
                  value={selectedBitrate}
                  onChange={(e) => setSelectedBitrate(Number(e.target.value))}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                >
                  <option value={64}>64 kbps (Low)</option>
                  <option value={128}>128 kbps (Standard)</option>
                  <option value={192}>192 kbps (High)</option>
                  <option value={256}>256 kbps (Very High)</option>
                  <option value={320}>320 kbps (Maximum)</option>
                </select>
              </div>

              {/* Skip Ads Toggle */}
              <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                <label className="font-semibold text-gray-700 dark:text-gray-300">Skip Ads</label>
                <button
                  onClick={() => setSkipAds(!skipAds)}
                  className={`relative inline-flex h-8 w-14 items-center rounded-full transition ${
                    skipAds ? 'bg-green-500' : 'bg-gray-300'
                  }`}
                >
                  <span
                    className={`inline-block h-6 w-6 transform rounded-full bg-white transition ${
                      skipAds ? 'translate-x-7' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>
            </>
          ) : (
            <>
              <h3 className="text-lg font-bold mb-4 text-gray-900 dark:text-white">Available Stations</h3>

              <div className="grid grid-cols-1 gap-3">
                {stations.map((station) => (
                  <button
                    key={station.id}
                    onClick={() => handleStationSelect(station)}
                    className={`p-4 rounded-lg text-left transition active:scale-95 ${
                      selectedStation?.id === station.id
                        ? 'bg-blue-500 text-white shadow-lg'
                        : 'bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    <div className="font-semibold">{station.name}</div>
                    <div className="text-sm opacity-75">
                      {station.genre} • {station.bitrate} kbps
                    </div>
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
      </div>

      {/* Play Button */}
      {selectedStation && !playback && (
        <div className="p-6 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={handlePlay}
            disabled={isLoading}
            className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-4 px-6 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed active:scale-95 flex items-center justify-center gap-2"
          >
            {isLoading ? (
              <>
                <IonSpinner name="crescent" />
                Connecting...
              </>
            ) : (
              <>
                <span>▶</span>
                Play
              </>
            )}
          </button>
        </div>
      )}

      {/* Hidden audio element */}
      <audio
        ref={audioRef}
        crossOrigin="anonymous"
        style={{ display: 'none' }}
      />
    </div>
  )
}

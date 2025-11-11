import React, { useState, useEffect, useRef } from 'react'
import { fetchStations, startStream, RadioStation } from '@/api/playback'
import { PlaybackWebSocket } from '@/api/websocket'

interface RadioPlayerProps {
  userId?: string
}

export const RadioPlayer: React.FC<RadioPlayerProps> = ({ userId = 'default' }) => {
  const [stations, setStations] = useState<RadioStation[]>([])
  const [selectedStation, setSelectedStation] = useState<RadioStation | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [volume, setVolume] = useState(1.0)
  const [bitrate, setBitrate] = useState(128)
  const [skipAds, setSkipAds] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const audioRef = useRef<HTMLAudioElement>(null)
  const wsRef = useRef<PlaybackWebSocket | null>(null)

  // Load stations on mount
  useEffect(() => {
    const loadStations = async () => {
      try {
        const data = await fetchStations()
        setStations(data)
        if (data.length > 0) {
          setSelectedStation(data[0])
        }
      } catch (err) {
        console.error('Failed to load stations:', err)
        setError('라디오 스테이션을 불러올 수 없습니다.')
      }
    }

    loadStations()
  }, [])

  // Setup WebSocket on mount
  useEffect(() => {
    if (!userId) return

    wsRef.current = new PlaybackWebSocket(userId)

    wsRef.current
      .connect({
        onOpen: () => {
          console.log('Playback WebSocket connected')
        },
        onMessage: (message) => {
          console.log('Received:', message)
          if (message.type === 'status_change') {
            // Handle status updates
          }
        },
        onError: (error) => {
          console.error('WebSocket error:', error)
        },
        onClose: () => {
          console.log('WebSocket disconnected')
        },
      })
      .catch((err) => {
        console.error('Failed to connect WebSocket:', err)
      })

    return () => {
      wsRef.current?.disconnect()
    }
  }, [userId])

  const handlePlay = async () => {
    if (!selectedStation) return

    try {
      setIsLoading(true)
      setError(null)

      const response = await startStream(selectedStation.id, {
        bitrate,
        format: 'mp3',
        skip_ads: skipAds,
      })

      const blob = await response.blob()
      const url = URL.createObjectURL(blob)

      if (audioRef.current) {
        audioRef.current.src = url
        audioRef.current.play()
        setIsPlaying(true)
      }
    } catch (err) {
      console.error('Failed to play station:', err)
      setError(err instanceof Error ? err.message : '재생 실패')
      setIsPlaying(false)
    } finally {
      setIsLoading(false)
    }
  }

  const handlePause = () => {
    if (audioRef.current) {
      audioRef.current.pause()
      setIsPlaying(false)
    }
  }

  const handleStop = () => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      setIsPlaying(false)
    }
  }

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value)
    setVolume(newVolume)
    if (audioRef.current) {
      audioRef.current.volume = newVolume
    }
  }

  return (
    <div className="w-full max-w-md rounded-lg border border-gray-300 bg-white p-6 shadow-lg">
      <h2 className="mb-4 text-xl font-bold text-gray-900">라디오 재생기</h2>

      {error && <div className="mb-4 rounded-md bg-red-100 p-3 text-sm text-red-700">{error}</div>}

      {/* Station Select */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700">라디오 스테이션</label>
        <select
          value={selectedStation?.id || ''}
          onChange={(e) => {
            const station = stations.find((s) => s.id === e.target.value)
            setSelectedStation(station || null)
          }}
          className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 focus:border-indigo-500 focus:outline-none"
        >
          {stations.map((station) => (
            <option key={station.id} value={station.id}>
              {station.name}
            </option>
          ))}
        </select>
      </div>

      {/* Audio Element */}
      <audio ref={audioRef} crossOrigin="anonymous" />

      {/* Playback Controls */}
      <div className="mb-4 flex gap-2">
        <button
          onClick={handlePlay}
          disabled={isLoading || isPlaying}
          className="flex-1 rounded-md bg-indigo-600 px-4 py-2 text-white disabled:bg-gray-400 hover:bg-indigo-700"
        >
          {isLoading ? '로딩중...' : isPlaying ? '재생중' : '재생'}
        </button>
        <button
          onClick={handlePause}
          disabled={!isPlaying}
          className="flex-1 rounded-md bg-yellow-600 px-4 py-2 text-white disabled:bg-gray-400 hover:bg-yellow-700"
        >
          일시정지
        </button>
        <button
          onClick={handleStop}
          disabled={!isPlaying}
          className="flex-1 rounded-md bg-red-600 px-4 py-2 text-white disabled:bg-gray-400 hover:bg-red-700"
        >
          정지
        </button>
      </div>

      {/* Volume Control */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700">음량</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.1"
          value={volume}
          onChange={handleVolumeChange}
          className="mt-1 w-full"
        />
      </div>

      {/* Bitrate Selection */}
      <div className="mb-4">
        <label className="block text-sm font-medium text-gray-700">비트레이트 (kbps)</label>
        <select
          value={bitrate}
          onChange={(e) => setBitrate(parseInt(e.target.value))}
          disabled={isPlaying}
          className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 focus:border-indigo-500 focus:outline-none disabled:bg-gray-100"
        >
          <option value={64}>64 kbps (낮음)</option>
          <option value={96}>96 kbps</option>
          <option value={128}>128 kbps (보통)</option>
          <option value={192}>192 kbps (높음)</option>
          <option value={256}>256 kbps (매우높음)</option>
          <option value={320}>320 kbps (최고)</option>
        </select>
      </div>

      {/* Ad Skip */}
      <div className="mb-4 flex items-center">
        <input
          type="checkbox"
          id="skipAds"
          checked={skipAds}
          onChange={(e) => setSkipAds(e.target.checked)}
          disabled={isPlaying}
          className="h-4 w-4 rounded border-gray-300 text-indigo-600"
        />
        <label htmlFor="skipAds" className="ml-2 text-sm text-gray-700">
          광고 회피
        </label>
      </div>

      {/* Station Info */}
      {selectedStation && (
        <div className="rounded-md bg-gray-50 p-3 text-sm text-gray-600">
          <p className="font-semibold">{selectedStation.name}</p>
          {selectedStation.description && <p className="text-xs text-gray-500">{selectedStation.description}</p>}
          {selectedStation.genre && <p className="text-xs text-gray-500">장르: {selectedStation.genre}</p>}
        </div>
      )}
    </div>
  )
}

export default RadioPlayer

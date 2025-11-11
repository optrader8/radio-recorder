import React, { useState, useEffect, useRef } from 'react'
import {
  startRecording,
  stopRecording,
  pauseRecording,
  resumeRecording,
  getActiveRecordings,
  RecordingSession,
} from '@/api/recording-control'
import { fetchStations, RadioStation } from '@/api/playback'
import { RecordingWebSocket } from '@/api/websocket'

interface RecordingRecorderProps {
  userId?: string
}

export const RecordingRecorder: React.FC<RecordingRecorderProps> = ({ userId = 'default' }) => {
  const [stations, setStations] = useState<RadioStation[]>([])
  const [selectedStationId, setSelectedStationId] = useState<string>('')
  const [recordingTitle, setRecordingTitle] = useState('New Recording')
  const [bitrate, setBitrate] = useState(128)
  const [durationMinutes, setDurationMinutes] = useState(0)
  const [skipAds, setSkipAds] = useState(false)
  const [isRecording, setIsRecording] = useState(false)
  const [activeRecordings, setActiveRecordings] = useState<RecordingSession[]>([])
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  const wsRef = useRef<RecordingWebSocket | null>(null)

  // Load stations on mount
  useEffect(() => {
    const loadStations = async () => {
      try {
        const data = await fetchStations()
        setStations(data)
        if (data.length > 0) {
          setSelectedStationId(data[0].id)
        }
      } catch (err) {
        console.error('Failed to load stations:', err)
        setError('라디오 스테이션을 불러올 수 없습니다.')
      }
    }

    loadStations()
  }, [])

  // Load active recordings
  useEffect(() => {
    const loadActiveRecordings = async () => {
      try {
        const data = await getActiveRecordings()
        setActiveRecordings(data.active_recordings)
        setIsRecording(data.active_recordings.length > 0)
      } catch (err) {
        console.error('Failed to load active recordings:', err)
      }
    }

    loadActiveRecordings()
    const interval = setInterval(loadActiveRecordings, 2000) // Refresh every 2 seconds

    return () => clearInterval(interval)
  }, [])

  // Setup WebSocket on mount
  useEffect(() => {
    if (!userId) return

    wsRef.current = new RecordingWebSocket(userId)

    wsRef.current
      .connect({
        onOpen: () => {
          console.log('Recording WebSocket connected')
        },
        onMessage: (message) => {
          console.log('Received:', message)
          if (message.type === 'recording_started') {
            setMessage('녹음이 시작되었습니다.')
            setActiveRecordings((prev) => [...prev, message.data])
          } else if (message.type === 'recording_completed') {
            setMessage('녹음이 완료되었습니다.')
            setActiveRecordings((prev) => prev.filter((r) => r.session_id !== message.session_id))
          } else if (message.type === 'recording_error') {
            setError(`녹음 오류: ${message.error}`)
            setActiveRecordings((prev) => prev.filter((r) => r.session_id !== message.session_id))
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

  const handleStartRecording = async () => {
    if (!selectedStationId) {
      setError('라디오 스테이션을 선택해주세요.')
      return
    }

    try {
      setError(null)
      setMessage(null)
      const result = await startRecording({
        station_id: selectedStationId,
        title: recordingTitle || 'New Recording',
        bitrate,
        sample_rate: 44100,
        format: 'mp3',
        skip_ads: skipAds,
        duration_minutes: durationMinutes,
      })

      setMessage(`녹음 시작: ${result.session_id}`)
      setIsRecording(true)

      // Send to WebSocket
      if (wsRef.current?.isConnected()) {
        wsRef.current.send({
          action: 'start',
          session_id: result.session_id,
        })
      }
    } catch (err) {
      console.error('Failed to start recording:', err)
      setError(err instanceof Error ? err.message : '녹음 시작 실패')
    }
  }

  const handleStopRecording = async (sessionId: string) => {
    try {
      setError(null)
      const result = await stopRecording(sessionId)
      setMessage('녹음 중지 요청됨')
      setActiveRecordings((prev) => prev.filter((r) => r.session_id !== sessionId))

      // Send to WebSocket
      if (wsRef.current?.isConnected()) {
        wsRef.current.send({
          action: 'stop',
          session_id: sessionId,
        })
      }
    } catch (err) {
      console.error('Failed to stop recording:', err)
      setError(err instanceof Error ? err.message : '녹음 중지 실패')
    }
  }

  const handlePauseRecording = async (sessionId: string) => {
    try {
      setError(null)
      await pauseRecording(sessionId)
      setMessage('녹음 일시정지됨')

      // Update local state
      setActiveRecordings((prev) =>
        prev.map((r) => (r.session_id === sessionId ? { ...r, status: 'paused' } : r))
      )

      if (wsRef.current?.isConnected()) {
        wsRef.current.send({
          action: 'pause',
          session_id: sessionId,
        })
      }
    } catch (err) {
      console.error('Failed to pause recording:', err)
      setError(err instanceof Error ? err.message : '녹음 일시정지 실패')
    }
  }

  const handleResumeRecording = async (sessionId: string) => {
    try {
      setError(null)
      await resumeRecording(sessionId)
      setMessage('녹음 재개됨')

      // Update local state
      setActiveRecordings((prev) =>
        prev.map((r) => (r.session_id === sessionId ? { ...r, status: 'recording' } : r))
      )

      if (wsRef.current?.isConnected()) {
        wsRef.current.send({
          action: 'resume',
          session_id: sessionId,
        })
      }
    } catch (err) {
      console.error('Failed to resume recording:', err)
      setError(err instanceof Error ? err.message : '녹음 재개 실패')
    }
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i]
  }

  const formatDuration = (seconds: number): string => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="w-full max-w-2xl rounded-lg border border-gray-300 bg-white p-6 shadow-lg">
      <h2 className="mb-4 text-xl font-bold text-gray-900">녹음 제어기</h2>

      {error && <div className="mb-4 rounded-md bg-red-100 p-3 text-sm text-red-700">{error}</div>}

      {message && <div className="mb-4 rounded-md bg-green-100 p-3 text-sm text-green-700">{message}</div>}

      {/* Recording Form */}
      {!isRecording && (
        <div className="mb-6 space-y-4 rounded-md bg-gray-50 p-4">
          {/* Station Select */}
          <div>
            <label className="block text-sm font-medium text-gray-700">라디오 스테이션</label>
            <select
              value={selectedStationId}
              onChange={(e) => setSelectedStationId(e.target.value)}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 focus:border-indigo-500 focus:outline-none"
            >
              {stations.map((station) => (
                <option key={station.id} value={station.id}>
                  {station.name}
                </option>
              ))}
            </select>
          </div>

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-gray-700">녹음 제목</label>
            <input
              type="text"
              value={recordingTitle}
              onChange={(e) => setRecordingTitle(e.target.value)}
              placeholder="New Recording"
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 focus:border-indigo-500 focus:outline-none"
            />
          </div>

          {/* Duration */}
          <div>
            <label className="block text-sm font-medium text-gray-700">녹음 시간 (분) - 0은 무제한</label>
            <input
              type="number"
              value={durationMinutes}
              onChange={(e) => setDurationMinutes(parseInt(e.target.value) || 0)}
              min="0"
              max="1440"
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 focus:border-indigo-500 focus:outline-none"
            />
          </div>

          {/* Bitrate */}
          <div>
            <label className="block text-sm font-medium text-gray-700">비트레이트 (kbps)</label>
            <select
              value={bitrate}
              onChange={(e) => setBitrate(parseInt(e.target.value))}
              className="mt-1 w-full rounded-md border border-gray-300 px-3 py-2 text-gray-900 focus:border-indigo-500 focus:outline-none"
            >
              <option value={64}>64 kbps (낮음)</option>
              <option value={96}>96 kbps</option>
              <option value={128}>128 kbps (보통)</option>
              <option value={192}>192 kbps (높음)</option>
              <option value={256}>256 kbps (매우높음)</option>
              <option value={320}>320 kbps (최고)</option>
            </select>
          </div>

          {/* Skip Ads */}
          <div className="flex items-center">
            <input
              type="checkbox"
              id="skipAds"
              checked={skipAds}
              onChange={(e) => setSkipAds(e.target.checked)}
              className="h-4 w-4 rounded border-gray-300 text-indigo-600"
            />
            <label htmlFor="skipAds" className="ml-2 text-sm text-gray-700">
              광고 회피
            </label>
          </div>

          {/* Start Button */}
          <button
            onClick={handleStartRecording}
            className="w-full rounded-md bg-green-600 px-4 py-2 text-white hover:bg-green-700"
          >
            녹음 시작
          </button>
        </div>
      )}

      {/* Active Recordings */}
      {activeRecordings.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-gray-900">진행 중인 녹음</h3>
          {activeRecordings.map((recording) => (
            <div key={recording.session_id} className="rounded-md border border-gray-200 bg-gray-50 p-4">
              <div className="mb-3">
                <p className="font-semibold text-gray-900">{recording.title}</p>
                <p className="text-sm text-gray-600">{recording.station_name}</p>
                <p className="text-sm text-gray-500">상태: {recording.status}</p>
              </div>

              {/* Progress Bar */}
              <div className="mb-3">
                <div className="flex justify-between text-xs text-gray-600">
                  <span>{formatDuration(recording.elapsed_seconds)}</span>
                  <span>{formatFileSize(recording.file_size_bytes)}</span>
                </div>
                <div className="mt-1 h-2 w-full rounded-full bg-gray-300">
                  <div className="h-full w-1/4 rounded-full bg-indigo-600"></div>
                </div>
              </div>

              {/* Controls */}
              <div className="flex gap-2">
                {recording.status === 'recording' && (
                  <>
                    <button
                      onClick={() => handlePauseRecording(recording.session_id)}
                      className="flex-1 rounded-md bg-yellow-600 px-3 py-1 text-sm text-white hover:bg-yellow-700"
                    >
                      일시정지
                    </button>
                    <button
                      onClick={() => handleStopRecording(recording.session_id)}
                      className="flex-1 rounded-md bg-red-600 px-3 py-1 text-sm text-white hover:bg-red-700"
                    >
                      정지
                    </button>
                  </>
                )}
                {recording.status === 'paused' && (
                  <>
                    <button
                      onClick={() => handleResumeRecording(recording.session_id)}
                      className="flex-1 rounded-md bg-green-600 px-3 py-1 text-sm text-white hover:bg-green-700"
                    >
                      재개
                    </button>
                    <button
                      onClick={() => handleStopRecording(recording.session_id)}
                      className="flex-1 rounded-md bg-red-600 px-3 py-1 text-sm text-white hover:bg-red-700"
                    >
                      정지
                    </button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {activeRecordings.length === 0 && !isRecording && (
        <div className="rounded-md bg-gray-100 p-4 text-center text-sm text-gray-600">진행 중인 녹음이 없습니다.</div>
      )}
    </div>
  )
}

export default RecordingRecorder

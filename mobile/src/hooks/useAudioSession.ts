import { useState, useCallback, useRef } from 'react'

export type SessionStatus = 'idle' | 'playing' | 'paused' | 'buffering' | 'error'

export interface AudioSession {
  id: string
  status: SessionStatus
  currentTime: number
  duration: number
  bitrate: number
  error?: string
}

interface UseAudioSessionOptions {
  onStatusChange?: (status: SessionStatus) => void
  onTimeUpdate?: (currentTime: number) => void
  onError?: (error: string) => void
}

export const useAudioSession = (options: UseAudioSessionOptions = {}) => {
  const { onStatusChange, onTimeUpdate, onError } = options

  const [session, setSession] = useState<AudioSession | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const updateIntervalRef = useRef<NodeJS.Timeout | null>(null)

  const createSession = useCallback(
    (id: string, bitrate: number = 192): AudioSession => {
      return {
        id,
        status: 'idle',
        currentTime: 0,
        duration: 0,
        bitrate,
      }
    },
    []
  )

  const initializeAudio = useCallback(
    (url: string, session: AudioSession) => {
      try {
        if (!audioRef.current) {
          audioRef.current = new Audio()
          audioRef.current.crossOrigin = 'anonymous'
        }

        audioRef.current.src = url

        audioRef.current.onplay = () => {
          setSession((prev) => {
            if (prev) {
              const updated = { ...prev, status: 'playing' as SessionStatus }
              onStatusChange?.('playing')
              return updated
            }
            return prev
          })

          // Start time update interval
          if (updateIntervalRef.current) {
            clearInterval(updateIntervalRef.current)
          }
          updateIntervalRef.current = setInterval(() => {
            if (audioRef.current) {
              onTimeUpdate?.(audioRef.current.currentTime)
              setSession((prev) => {
                if (prev) {
                  return {
                    ...prev,
                    currentTime: audioRef.current?.currentTime || 0,
                  }
                }
                return prev
              })
            }
          }, 1000)
        }

        audioRef.current.onpause = () => {
          setSession((prev) => {
            if (prev) {
              const updated = { ...prev, status: 'paused' as SessionStatus }
              onStatusChange?.('paused')
              return updated
            }
            return prev
          })
          if (updateIntervalRef.current) {
            clearInterval(updateIntervalRef.current)
          }
        }

        audioRef.current.onended = () => {
          setSession((prev) => {
            if (prev) {
              return { ...prev, status: 'idle' as SessionStatus }
            }
            return prev
          })
          if (updateIntervalRef.current) {
            clearInterval(updateIntervalRef.current)
          }
        }

        audioRef.current.onerror = (error) => {
          const errorMessage = `Error loading audio: ${error}`
          console.error(errorMessage)
          setSession((prev) => {
            if (prev) {
              return {
                ...prev,
                status: 'error' as SessionStatus,
                error: errorMessage,
              }
            }
            return prev
          })
          onError?.(errorMessage)
        }

        audioRef.current.onloadedmetadata = () => {
          setSession((prev) => {
            if (prev) {
              return {
                ...prev,
                duration: audioRef.current?.duration || 0,
              }
            }
            return prev
          })
        }

        setSession(session)
      } catch (err) {
        const errorMessage = `Failed to initialize audio: ${err}`
        console.error(errorMessage)
        setSession((prev) => {
          if (prev) {
            return {
              ...prev,
              status: 'error' as SessionStatus,
              error: errorMessage,
            }
          }
          return prev
        })
        onError?.(errorMessage)
      }
    },
    [onStatusChange, onTimeUpdate, onError]
  )

  const play = useCallback(async () => {
    try {
      if (audioRef.current) {
        setSession((prev) => {
          if (prev) {
            return { ...prev, status: 'buffering' as SessionStatus }
          }
          return prev
        })
        onStatusChange?.('buffering')

        await audioRef.current.play()
      }
    } catch (err) {
      const errorMessage = `Play error: ${err}`
      console.error(errorMessage)
      setSession((prev) => {
        if (prev) {
          return {
            ...prev,
            status: 'error' as SessionStatus,
            error: errorMessage,
          }
        }
        return prev
      })
      onError?.(errorMessage)
    }
  }, [onStatusChange, onError])

  const pause = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause()
    }
  }, [])

  const resume = useCallback(() => {
    play()
  }, [play])

  const stop = useCallback(() => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      setSession((prev) => {
        if (prev) {
          return { ...prev, status: 'idle' as SessionStatus, currentTime: 0 }
        }
        return prev
      })
    }
  }, [])

  const setVolume = useCallback((volume: number) => {
    if (audioRef.current) {
      audioRef.current.volume = Math.max(0, Math.min(1, volume / 100))
    }
  }, [])

  const seek = useCallback((time: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime = time
    }
  }, [])

  const cleanup = useCallback(() => {
    stop()
    if (updateIntervalRef.current) {
      clearInterval(updateIntervalRef.current)
    }
    if (audioRef.current) {
      audioRef.current.src = ''
      audioRef.current = null
    }
  }, [stop])

  return {
    session,
    audioRef,
    createSession,
    initializeAudio,
    play,
    pause,
    resume,
    stop,
    setVolume,
    seek,
    cleanup,
  }
}

export default useAudioSession

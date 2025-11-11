import { useEffect, useRef, useState, useCallback } from 'react'

interface WebSocketOptions {
  onOpen?: () => void
  onClose?: () => void
  onError?: (error: Event) => void
  onMessage?: (data: any) => void
  reconnectAttempts?: number
  reconnectInterval?: number
}

export const useWebSocket = (
  url: string,
  options: WebSocketOptions = {}
) => {
  const {
    onOpen,
    onClose,
    onError,
    onMessage,
    reconnectAttempts = 5,
    reconnectInterval = 3000,
  } = options

  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const wsRef = useRef<WebSocket | null>(null)
  const reconnectCountRef = useRef(0)
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    setIsConnecting(true)
    setError(null)

    try {
      wsRef.current = new WebSocket(url)

      wsRef.current.onopen = () => {
        console.log('WebSocket connected:', url)
        setIsConnected(true)
        setIsConnecting(false)
        reconnectCountRef.current = 0
        onOpen?.()
      }

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          onMessage?.(data)
        } catch (err) {
          console.error('Error parsing WebSocket message:', err)
          onMessage?.(event.data)
        }
      }

      wsRef.current.onerror = (event) => {
        console.error('WebSocket error:', event)
        setError('WebSocket connection error')
        setIsConnecting(false)
        onError?.(event)
      }

      wsRef.current.onclose = () => {
        console.log('WebSocket disconnected')
        setIsConnected(false)
        setIsConnecting(false)
        onClose?.()

        // Attempt to reconnect
        if (reconnectCountRef.current < reconnectAttempts) {
          reconnectCountRef.current += 1
          console.log(
            `Reconnecting... (attempt ${reconnectCountRef.current}/${reconnectAttempts})`
          )
          reconnectTimeoutRef.current = setTimeout(() => {
            connect()
          }, reconnectInterval * reconnectCountRef.current)
        }
      }
    } catch (err) {
      console.error('Error creating WebSocket:', err)
      setError('Failed to create WebSocket connection')
      setIsConnecting(false)
    }
  }, [url, reconnectAttempts, reconnectInterval, onOpen, onClose, onError, onMessage])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
    }
    wsRef.current?.close()
    setIsConnected(false)
    setIsConnecting(false)
  }, [])

  const send = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      try {
        const message = typeof data === 'string' ? data : JSON.stringify(data)
        wsRef.current.send(message)
      } catch (err) {
        console.error('Error sending WebSocket message:', err)
      }
    } else {
      console.warn('WebSocket is not connected')
    }
  }, [])

  useEffect(() => {
    connect()

    return () => {
      disconnect()
    }
  }, [url])

  return {
    isConnected,
    isConnecting,
    error,
    send,
    disconnect,
    reconnect: connect,
  }
}

export default useWebSocket

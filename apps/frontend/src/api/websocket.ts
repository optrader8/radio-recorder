/**
 * WebSocket utilities for real-time playback and recording updates
 */

export interface WebSocketMessage {
  type: string
  session_id?: string
  message?: string
  data?: any
  timestamp?: string
  error?: string
}

export class PlaybackWebSocket {
  private ws: WebSocket | null = null
  private userId: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000 // Start with 1 second

  private handlers: {
    onOpen?: () => void
    onClose?: () => void
    onError?: (error: Error) => void
    onMessage?: (message: WebSocketMessage) => void
  } = {}

  constructor(userId: string) {
    this.userId = userId
  }

  connect(handlers: typeof this.handlers): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.handlers = handlers

        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
        const wsUrl = wsBaseUrl.replace(/^https?:/, wsProtocol)
        const token = localStorage.getItem('authToken')

        const url = `${wsUrl}/api/v1/ws/playback/${this.userId}${token ? `?token=${token}` : ''}`

        this.ws = new WebSocket(url)

        this.ws.onopen = () => {
          console.log('Playback WebSocket connected')
          this.reconnectAttempts = 0
          this.reconnectDelay = 1000
          handlers.onOpen?.()
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            console.log('Playback WebSocket message:', message)
            handlers.onMessage?.(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.ws.onerror = (event) => {
          const error = new Error('WebSocket error')
          console.error('Playback WebSocket error:', event)
          handlers.onError?.(error)
          reject(error)
        }

        this.ws.onclose = () => {
          console.log('Playback WebSocket closed')
          handlers.onClose?.()
          this.attemptReconnect()
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected')
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)

      setTimeout(() => {
        this.connect(this.handlers).catch((error) => {
          console.error('Reconnection failed:', error)
        })
      }, this.reconnectDelay)

      this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000) // Max 30 seconds
    } else {
      console.error('Max reconnection attempts reached')
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

export class RecordingWebSocket {
  private ws: WebSocket | null = null
  private userId: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

  private handlers: {
    onOpen?: () => void
    onClose?: () => void
    onError?: (error: Error) => void
    onMessage?: (message: WebSocketMessage) => void
  } = {}

  constructor(userId: string) {
    this.userId = userId
  }

  connect(handlers: typeof this.handlers): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.handlers = handlers

        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
        const wsUrl = wsBaseUrl.replace(/^https?:/, wsProtocol)
        const token = localStorage.getItem('authToken')

        const url = `${wsUrl}/api/v1/ws/recording/${this.userId}${token ? `?token=${token}` : ''}`

        this.ws = new WebSocket(url)

        this.ws.onopen = () => {
          console.log('Recording WebSocket connected')
          this.reconnectAttempts = 0
          this.reconnectDelay = 1000
          handlers.onOpen?.()
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            console.log('Recording WebSocket message:', message)
            handlers.onMessage?.(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.ws.onerror = (event) => {
          const error = new Error('WebSocket error')
          console.error('Recording WebSocket error:', event)
          handlers.onError?.(error)
          reject(error)
        }

        this.ws.onclose = () => {
          console.log('Recording WebSocket closed')
          handlers.onClose?.()
          this.attemptReconnect()
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected')
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)

      setTimeout(() => {
        this.connect(this.handlers).catch((error) => {
          console.error('Reconnection failed:', error)
        })
      }, this.reconnectDelay)

      this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000)
    } else {
      console.error('Max reconnection attempts reached')
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

export class SystemWebSocket {
  private ws: WebSocket | null = null
  private userId: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

  private handlers: {
    onOpen?: () => void
    onClose?: () => void
    onError?: (error: Error) => void
    onMessage?: (message: WebSocketMessage) => void
  } = {}

  constructor(userId: string) {
    this.userId = userId
  }

  connect(handlers: typeof this.handlers): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.handlers = handlers

        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const wsBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
        const wsUrl = wsBaseUrl.replace(/^https?:/, wsProtocol)
        const token = localStorage.getItem('authToken')

        const url = `${wsUrl}/api/v1/ws/system/${this.userId}${token ? `?token=${token}` : ''}`

        this.ws = new WebSocket(url)

        this.ws.onopen = () => {
          console.log('System WebSocket connected')
          this.reconnectAttempts = 0
          this.reconnectDelay = 1000
          handlers.onOpen?.()
          resolve()
        }

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            console.log('System WebSocket message:', message)
            handlers.onMessage?.(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.ws.onerror = (event) => {
          const error = new Error('WebSocket error')
          console.error('System WebSocket error:', event)
          handlers.onError?.(error)
          reject(error)
        }

        this.ws.onclose = () => {
          console.log('System WebSocket closed')
          handlers.onClose?.()
          this.attemptReconnect()
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  send(message: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('WebSocket is not connected')
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`)

      setTimeout(() => {
        this.connect(this.handlers).catch((error) => {
          console.error('Reconnection failed:', error)
        })
      }, this.reconnectDelay)

      this.reconnectDelay = Math.min(this.reconnectDelay * 2, 30000)
    } else {
      console.error('Max reconnection attempts reached')
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN
  }
}

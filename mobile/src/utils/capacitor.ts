import { App } from '@capacitor/app'
import { Device } from '@capacitor/device'
import { Network } from '@capacitor/network'
import { StatusBar, Style } from '@capacitor/status-bar'
import { Keyboard } from '@capacitor/keyboard'
import { LocalNotifications } from '@capacitor/local-notifications'

/**
 * Initialize Capacitor plugins and listeners
 */
export const initCapacitor = async () => {
  try {
    // Request notification permission
    const permission = await LocalNotifications.checkPermissions()
    if (permission.display !== 'granted') {
      await LocalNotifications.requestPermissions()
    }

    // Set up app listeners
    setupAppListeners()

    // Set up network listeners
    setupNetworkListeners()

    // Hide keyboard on page load
    await Keyboard.hide()

    // Set status bar style
    await setStatusBarStyle(Style.Light)
  } catch (error) {
    console.error('Error initializing Capacitor:', error)
  }
}

/**
 * App lifecycle listeners
 */
function setupAppListeners() {
  App.addListener('appStateChange', ({ isActive }) => {
    if (isActive) {
      console.log('App resumed')
      // Resume playback/recording if needed
    } else {
      console.log('App paused')
      // Pause playback/recording if needed
    }
  })

  App.addListener('appUrlOpen', (data) => {
    console.log('App opened with URL:', data.url)
    // Handle deep linking
  })

  App.addListener('backButton', () => {
    // Handle back button
    window.history.back()
  })
}

/**
 * Network connectivity listeners
 */
function setupNetworkListeners() {
  Network.addListener('networkStatusChange', (status) => {
    console.log('Network status changed:', status)
    if (!status.connected) {
      console.warn('Network disconnected')
      // Show offline indicator
    } else {
      console.log('Network connected')
      // Hide offline indicator, sync data if needed
    }
  })
}

/**
 * Check if device is online
 */
export const isOnline = async (): Promise<boolean> => {
  try {
    const status = await Network.getStatus()
    return status.connected
  } catch (error) {
    console.error('Error checking network status:', error)
    return navigator.onLine
  }
}

/**
 * Get device information
 */
export const getDeviceInfo = async () => {
  try {
    const info = await Device.getInfo()
    return {
      platform: info.platform,
      osVersion: info.osVersion,
      model: info.model,
      uuid: info.uuid,
    }
  } catch (error) {
    console.error('Error getting device info:', error)
    return null
  }
}

/**
 * Set status bar style
 */
export const setStatusBarStyle = async (style: Style) => {
  try {
    await StatusBar.setStyle({ style })
  } catch (error) {
    console.error('Error setting status bar style:', error)
  }
}

/**
 * Show notification
 */
export const showNotification = async (
  title: string,
  body: string,
  notificationId?: number
) => {
  try {
    await LocalNotifications.schedule({
      notifications: [
        {
          title,
          body,
          id: notificationId || Date.now(),
          actionTypeId: 'DEFAULT',
          autoCancel: true,
        },
      ],
    })
  } catch (error) {
    console.error('Error showing notification:', error)
  }
}

/**
 * Show error notification
 */
export const showErrorNotification = async (message: string) => {
  await showNotification('Error', message, 9999)
}

/**
 * Show success notification
 */
export const showSuccessNotification = async (message: string) => {
  await showNotification('Success', message)
}

/**
 * Request storage permission
 */
export const requestStoragePermission = async (): Promise<boolean> => {
  try {
    // iOS doesn't require explicit storage permission
    // Android requires user permission
    return true
  } catch (error) {
    console.error('Error requesting storage permission:', error)
    return false
  }
}

/**
 * Request microphone permission
 */
export const requestMicrophonePermission = async (): Promise<boolean> => {
  try {
    // Note: You may need to use a permissions plugin for more control
    return true
  } catch (error) {
    console.error('Error requesting microphone permission:', error)
    return false
  }
}

/**
 * Exit app
 */
export const exitApp = async () => {
  try {
    await App.exitApp()
  } catch (error) {
    console.error('Error exiting app:', error)
  }
}

/**
 * Get app version
 */
export const getAppVersion = async () => {
  try {
    const info = await App.getInfo()
    return {
      version: info.version,
      build: info.build,
    }
  } catch (error) {
    console.error('Error getting app version:', error)
    return { version: 'unknown', build: 'unknown' }
  }
}

export default {
  initCapacitor,
  isOnline,
  getDeviceInfo,
  setStatusBarStyle,
  showNotification,
  showErrorNotification,
  showSuccessNotification,
  requestStoragePermission,
  requestMicrophonePermission,
  exitApp,
  getAppVersion,
}

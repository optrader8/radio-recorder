import { useState, useEffect } from 'react'
import { Device } from '@capacitor/device'

interface Settings {
  autoStartRecording: boolean
  skipAdsAutomatically: boolean
  highQualityRecording: boolean
  notificationsEnabled: boolean
  analyticsEnabled: boolean
  darkMode: boolean
  apiUrl: string
}

export default function Settings() {
  const [settings, setSettings] = useState<Settings>({
    autoStartRecording: false,
    skipAdsAutomatically: true,
    highQualityRecording: true,
    notificationsEnabled: true,
    analyticsEnabled: true,
    darkMode: false,
    apiUrl: 'https://api.radiorecorder.com',
  })

  const [deviceInfo, setDeviceInfo] = useState({
    platform: '',
    osVersion: '',
    model: '',
    appVersion: '1.0.0',
  })

  useEffect(() => {
    const loadDeviceInfo = async () => {
      try {
        const info = await Device.getInfo()
        setDeviceInfo({
          platform: info.platform || 'Unknown',
          osVersion: info.osVersion || 'Unknown',
          model: info.model || 'Unknown',
          appVersion: '1.0.0',
        })
      } catch (error) {
        console.error('Failed to load device info:', error)
      }
    }
    loadDeviceInfo()

    // Load settings from localStorage
    const savedSettings = localStorage.getItem('app-settings')
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings))
    }
  }, [])

  const handleToggle = (key: keyof Settings) => {
    const newSettings = {
      ...settings,
      [key]: !settings[key],
    }
    setSettings(newSettings)
    localStorage.setItem('app-settings', JSON.stringify(newSettings))
  }

  const handleApiUrlChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newSettings = {
      ...settings,
      apiUrl: e.target.value,
    }
    setSettings(newSettings)
    localStorage.setItem('app-settings', JSON.stringify(newSettings))
  }

  return (
    <div className="flex flex-col h-full bg-white dark:bg-slate-950">
      {/* Header */}
      <div className="bg-gradient-to-b from-blue-500 to-blue-600 text-white p-6">
        <h1 className="text-2xl font-bold">⚙️ Settings</h1>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-6 space-y-6">
          {/* Recording Settings */}
          <section>
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Recording</h2>
            <div className="space-y-3">
              <ToggleSetting
                label="High Quality Recording"
                description="Record at maximum bitrate (320 kbps)"
                checked={settings.highQualityRecording}
                onChange={() => handleToggle('highQualityRecording')}
              />
              <ToggleSetting
                label="Auto-start Recording"
                description="Automatically start recording when station loads"
                checked={settings.autoStartRecording}
                onChange={() => handleToggle('autoStartRecording')}
              />
            </div>
          </section>

          {/* Playback Settings */}
          <section>
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Playback</h2>
            <div className="space-y-3">
              <ToggleSetting
                label="Skip Ads Automatically"
                description="Use AI to detect and skip advertisements"
                checked={settings.skipAdsAutomatically}
                onChange={() => handleToggle('skipAdsAutomatically')}
              />
            </div>
          </section>

          {/* Notification Settings */}
          <section>
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Notifications</h2>
            <div className="space-y-3">
              <ToggleSetting
                label="Enable Notifications"
                description="Receive alerts for recording and analysis"
                checked={settings.notificationsEnabled}
                onChange={() => handleToggle('notificationsEnabled')}
              />
            </div>
          </section>

          {/* Privacy Settings */}
          <section>
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Privacy</h2>
            <div className="space-y-3">
              <ToggleSetting
                label="Analytics"
                description="Share usage analytics to improve the app"
                checked={settings.analyticsEnabled}
                onChange={() => handleToggle('analyticsEnabled')}
              />
            </div>
          </section>

          {/* API Configuration */}
          <section>
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">API Configuration</h2>
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4">
              <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                API Server URL
              </label>
              <input
                type="url"
                value={settings.apiUrl}
                onChange={handleApiUrlChange}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm"
                placeholder="https://api.radiorecorder.com"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                Changes require app restart
              </p>
            </div>
          </section>

          {/* Device Information */}
          <section>
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Device Information</h2>
            <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 space-y-3">
              <InfoRow label="Platform" value={deviceInfo.platform} />
              <InfoRow label="OS Version" value={deviceInfo.osVersion} />
              <InfoRow label="Model" value={deviceInfo.model} />
              <InfoRow label="App Version" value={deviceInfo.appVersion} />
            </div>
          </section>

          {/* Legal */}
          <section>
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Legal</h2>
            <div className="space-y-3">
              <Link href="#" label="Terms of Service" />
              <Link href="#" label="Privacy Policy" />
              <Link href="#" label="Open Source Licenses" />
            </div>
          </section>

          {/* About */}
          <section>
            <div className="bg-gradient-to-r from-blue-50 to-blue-100 dark:from-blue-900 dark:to-blue-800 rounded-lg p-6 text-center">
              <div className="text-4xl mb-2">📻</div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                Radio Recorder
              </h2>
              <p className="text-sm text-gray-600 dark:text-gray-300 mb-4">
                Version {deviceInfo.appVersion}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Built with ❤️ for radio enthusiasts
              </p>
            </div>
          </section>

          {/* Clear Cache Button */}
          <div>
            <button className="w-full bg-red-500 hover:bg-red-600 text-white font-semibold py-3 px-4 rounded-lg transition active:scale-95">
              Clear Cache & Data
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

interface ToggleSettingProps {
  label: string
  description: string
  checked: boolean
  onChange: () => void
}

function ToggleSetting({ label, description, checked, onChange }: ToggleSettingProps) {
  return (
    <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
      <div className="flex-1">
        <p className="font-semibold text-gray-900 dark:text-white">{label}</p>
        <p className="text-sm text-gray-500 dark:text-gray-400">{description}</p>
      </div>
      <button
        onClick={onChange}
        className={`relative inline-flex h-8 w-14 items-center rounded-full transition ${
          checked ? 'bg-blue-500' : 'bg-gray-300'
        }`}
      >
        <span
          className={`inline-block h-6 w-6 transform rounded-full bg-white transition ${
            checked ? 'translate-x-7' : 'translate-x-1'
          }`}
        />
      </button>
    </div>
  )
}

interface InfoRowProps {
  label: string
  value: string
}

function InfoRow({ label, value }: InfoRowProps) {
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-200 dark:border-gray-700 last:border-b-0">
      <span className="text-sm text-gray-600 dark:text-gray-400">{label}</span>
      <span className="font-semibold text-gray-900 dark:text-white">{value}</span>
    </div>
  )
}

interface LinkProps {
  href: string
  label: string
}

function Link({ href, label }: LinkProps) {
  return (
    <a
      href={href}
      className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition"
    >
      <span className="font-semibold text-gray-900 dark:text-white">{label}</span>
      <span className="text-gray-400">→</span>
    </a>
  )
}

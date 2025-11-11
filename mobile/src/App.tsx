import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import { IonApp, IonMenu, IonMenuButton, IonContent, IonItem, IonLabel, IonIcon } from '@ionic/react'
import {
  radioOutline,
  recordingOutline,
  statsChartOutline,
  settingsOutline,
  homeOutline,
  moonOutline,
  sunnyOutline,
} from 'ionicons/icons'
import '@ionic/react/css/core.css'
import '@ionic/react/css/normalize.css'
import '@ionic/react/css/structure.css'
import '@ionic/react/css/typography.css'
import '@ionic/react/css/padding.css'
import '@ionic/react/css/float-elements.css'
import '@ionic/react/css/text-alignment.css'
import '@ionic/react/css/text-transformation.css'
import '@ionic/react/css/flex-utils.css'
import '@ionic/react/css/display.css'

import RadioPlayer from './pages/RadioPlayer'
import Recorder from './pages/Recorder'
import Dashboard from './pages/Dashboard'
import Settings from './pages/Settings'
import Home from './pages/Home'
import './App.css'

const Navigation = () => {
  const location = useLocation()
  const [isDark, setIsDark] = useState(false)

  useEffect(() => {
    const html = document.documentElement
    if (isDark) {
      html.classList.add('dark')
    } else {
      html.classList.remove('dark')
    }
  }, [isDark])

  const isActive = (path: string) => location.pathname === path

  const navItems = [
    { path: '/', icon: homeOutline, label: 'Home' },
    { path: '/radio-player', icon: radioOutline, label: 'Radio' },
    { path: '/recorder', icon: recordingOutline, label: 'Recorder' },
    { path: '/dashboard', icon: statsChartOutline, label: 'Dashboard' },
    { path: '/settings', icon: settingsOutline, label: 'Settings' },
  ]

  return (
    <div className="flex flex-col h-screen bg-white dark:bg-slate-950">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 pt-[calc(env(safe-area-inset-top)+1rem)]">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold">Radio Recorder</h1>
          <button
            onClick={() => setIsDark(!isDark)}
            className="p-2 hover:bg-blue-700 rounded-lg transition"
            title={isDark ? 'Light mode' : 'Dark mode'}
          >
            {isDark ? <sunnyOutline fontSize={24} /> : <moonOutline fontSize={24} />}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/radio-player" element={<RadioPlayer />} />
          <Route path="/recorder" element={<Recorder />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </div>

      {/* Bottom Navigation */}
      <nav className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-slate-900">
        <div className="grid grid-cols-5 gap-0 pb-[calc(env(safe-area-inset-bottom)+0.5rem)]">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex flex-col items-center justify-center py-3 transition ${
                isActive(item.path)
                  ? 'text-blue-500 border-t-2 border-blue-500'
                  : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200'
              }`}
            >
              <ion-icon name={item.icon} style={{ fontSize: '24px' }} />
              <span className="text-xs mt-1">{item.label}</span>
            </Link>
          ))}
        </div>
      </nav>
    </div>
  )
}

export default function App() {
  return (
    <Router>
      <Navigation />
    </Router>
  )
}

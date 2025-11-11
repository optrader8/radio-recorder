import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.radiorecorder.app',
  appName: 'Radio Recorder',
  webDir: 'dist',
  server: {
    androidScheme: 'https',
    // 개발 시에만 사용
    // url: 'http://localhost:5173',
    // cleartext: true,
  },
  ios: {
    contentInset: 'automatic',
    scrollEnabled: true,
    limitsNavigationsToAppBoundDomains: true,
    allowsInlineMediaPlayback: true,
  },
  android: {
    allowMixedContent: true,
    webContentsDebuggingEnabled: false,
  },
  plugins: {
    LocalNotifications: {
      smallIcon: 'ic_stat_notification',
      iconColor: '#488AFF',
      sound: 'notification',
      requestPermissions: true,
    },
    Camera: {
      cameraDirection: 'rear',
    },
    Filesystem: {
      directory: 'Documents',
    },
    Device: {
      // Device plugin 설정
    },
    App: {
      // App plugin 설정
    },
    Network: {
      // Network plugin 설정
    },
    Keyboard: {
      resize: 'ionic',
      style: 'dark',
    },
  },
};

export default config;

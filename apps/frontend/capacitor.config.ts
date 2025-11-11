import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.radiorecorder.app',
  appName: 'Radio Recorder',
  webDir: 'dist',
  server: {
    androidScheme: 'https',
    url: 'http://localhost:3000',
    cleartext: true,
  },
  ios: {
    contentInset: 'automatic',
  },
  android: {
    allowMixedContent: true,
  },
  plugins: {
    CapacitorHttp: {
      enabled: true,
    },
    LocalNotifications: {
      smallIcon: 'ic_stat_icon_config_sample',
      iconColor: '#488AFF',
      sound: 'beep.wav',
    },
    BackgroundTask: {
      label: 'background-sync',
    },
    BackgroundGeolocation: {
      enableNotifications: true,
      logLevel: 'VERBOSE',
      stopOnTerminate: false,
      startOnBoot: true,
    },
  },
};

export default config;

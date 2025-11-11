# Radio Recorder Mobile App

모바일 플랫폼(iOS/Android)을 위한 Radio Recorder 앱입니다. Capacitor를 사용하여 웹 기술과 네이티브 기능을 결합했습니다.

## 🚀 시작하기

### 요구사항

- **Node.js**: v18.0.0 이상
- **npm**: v9.0.0 이상
- **Capacitor CLI**: 최신 버전

#### iOS 개발
- **macOS**: Big Sur 이상
- **Xcode**: 14.0 이상
- **CocoaPods**: 최신 버전

#### Android 개발
- **Android Studio**: 최신 버전
- **Java**: JDK 11 이상
- **Android SDK**: API 21 이상

### 설치

```bash
# 의존성 설치
npm install

# Capacitor 설정
npx cap init

# 환경 설정
cp .env.example .env.development
cp .env.example .env.production
```

## 📱 빌드 & 배포

### 웹 버전 빌드

```bash
npm run build
npm run preview
```

### iOS 빌드

```bash
# 스크립트 사용 (macOS)
./scripts/build.sh ios

# 또는 수동으로
npm run build
npx cap sync ios
npx cap open ios
```

Xcode에서:
1. 프로젝트 설정에서 팀 선택
2. Product → Build
3. 시뮬레이터 또는 장치에서 실행

### Android 빌드

```bash
# 스크립트 사용
./scripts/build.sh android

# 또는 수동으로
npm run build
npx cap sync android
npx cap open android
```

Android Studio에서:
1. Gradle sync 완료 대기
2. Build → Build Bundle(s) / APK(s) → Build APK(s)
3. 에뮬레이터 또는 장치에서 실행

### 배포

#### iOS App Store
```bash
# TestFlight 업로드 (자동 CI/CD)
# GitHub Actions가 자동으로 빌드 및 배포

# 수동 배포
npx cap open ios
# Xcode에서 Product → Archive
```

#### Google Play Store
```bash
# 내부 테스트 (자동 CI/CD)
# main 브랜치에 푸시하면 자동으로 배포

# 수동 배포
./scripts/build.sh android
# Android Studio에서 Build → Build Bundle(s)
```

## 🏗️ 프로젝트 구조

```
mobile/
├── src/                          # 소스 코드
├── dist/                         # 빌드 출력
├── ios/                          # iOS 네이티브 코드
│   └── App/                      # Xcode 프로젝트
├── android/                      # Android 네이티브 코드
│   └── app/                      # Android Studio 프로젝트
├── scripts/                      # 빌드 스크립트
│   ├── build.sh                  # Unix/Mac 스크립트
│   └── build.bat                 # Windows 스크립트
├── .github/workflows/            # CI/CD 설정
│   ├── build-ios.yml            # iOS 자동 빌드
│   └── build-android.yml        # Android 자동 빌드
├── capacitor.config.ts          # Capacitor 설정
├── vite.config.ts               # Vite 설정
├── tailwind.config.ts           # Tailwind CSS 설정
└── tsconfig.json                # TypeScript 설정
```

## 🔧 설정

### 환경 변수

`.env.development` 또는 `.env.production` 파일을 생성하여 설정:

```env
# API
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=30000

# 앱
VITE_APP_NAME=Radio Recorder
VITE_APP_VERSION=1.0.0

# 기능
VITE_ENABLE_ANALYTICS=true
VITE_ENABLE_PUSH_NOTIFICATIONS=true

# 오디오
VITE_AUDIO_BITRATE=128
VITE_AUDIO_SAMPLE_RATE=44100
```

### Capacitor 플러그인

프로젝트에 포함된 플러그인:

- **LocalNotifications**: 로컬 푸시 알림
- **Camera**: 카메라 접근
- **Filesystem**: 파일 시스템 접근
- **Geolocation**: GPS 위치 추적
- **Device**: 디바이스 정보
- **App**: 앱 정보
- **Network**: 네트워크 상태
- **Keyboard**: 키보드 제어

플러그인 추가:
```bash
npm install @capacitor/plugin-name
npx cap sync
```

## 📋 기능

- ✅ 실시간 라디오 스트리밍
- ✅ 라디오 녹음
- ✅ 광고 감지 및 회피
- ✅ 트랜스크립션 (음성→텍스트)
- ✅ 음성 분석
- ✅ 다크모드
- ✅ 오프라인 지원
- ✅ 푸시 알림
- ✅ 백그라운드 재생

## 🧪 테스트

```bash
# 웹 버전 테스트
npm run dev

# iOS 시뮬레이터 테스트
npx cap open ios
# Xcode에서 시뮬레이터 선택 및 실행

# Android 에뮬레이터 테스트
npx cap open android
# Android Studio에서 에뮬레이터 실행
```

## 🔐 보안

### iOS 권한 설정

`ios/App/Info.plist`에서 권한 설명 추가:

```xml
<key>NSMicrophoneUsageDescription</key>
<string>마이크 접근 권한이 필요합니다</string>
<key>NSPhotoLibraryUsageDescription</key>
<string>녹음 저장을 위해 사진 라이브러리 접근이 필요합니다</string>
```

### Android 권한 설정

`android/app/src/main/AndroidManifest.xml`에서 권한 요청:

```xml
<uses-permission android:name="android.permission.RECORD_AUDIO" />
<uses-permission android:name="android.permission.INTERNET" />
```

## 🐛 트러블슈팅

### iOS 빌드 오류
```bash
# CocoaPods 재설정
rm -rf ios/App/Pods
cd ios/App
pod install
cd ../..
```

### Android 빌드 오류
```bash
# Gradle 캐시 삭제
rm -rf android/.gradle
./android/gradlew clean
```

### Capacitor 동기화 문제
```bash
# 완전 재동기화
rm -rf ios/App/Pods
rm -rf node_modules/@capacitor
npx cap sync
```

## 📚 참고 자료

- [Capacitor 공식 문서](https://capacitorjs.com/)
- [React 문서](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Vite 문서](https://vitejs.dev/)

## 📞 지원

문제가 발생하면 GitHub Issues를 통해 보고해주세요.

## 📄 라이센스

MIT License - 자세한 내용은 LICENSE 파일을 참조하세요.

## 🤝 기여

기여는 환영합니다! Pull Request를 통해 개선사항을 제안해주세요.

### 개발 가이드

1. Fork 저장소
2. Feature 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 변경사항 커밋 (`git commit -m 'Add some AmazingFeature'`)
4. 브랜치에 Push (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

---

**Version**: 1.0.0
**Last Updated**: 2024년 11월

# Mobile App 초기 설정 가이드

이 가이드는 Radio Recorder 모바일 앱을 처음 설정할 때 따라야 할 단계를 설명합니다.

## 1️⃣ 전제 조건 확인

### 필수 설치
```bash
# Node.js 버전 확인
node --version  # v18.0.0 이상

# npm 버전 확인
npm --version   # v9.0.0 이상

# Xcode 설치 (macOS)
# AppStore에서 Xcode 다운로드

# Android Studio 설치
# https://developer.android.com/studio에서 다운로드
```

## 2️⃣ 모바일 앱 초기화

### 단계 1: 프로젝트 설정
```bash
cd mobile

# 의존성 설치
npm install

# Capacitor 초기화
npx cap init

# 웹 빌드
npm run build
```

### 단계 2: iOS 프로젝트 생성
```bash
# Xcode 프로젝트 생성
npx cap add ios

# 설정 파일 업데이트
npx cap sync ios

# Xcode에서 열기
npx cap open ios
```

**Xcode에서:**
1. 좌측 네비게이터에서 "App" 선택
2. "Signing & Capabilities" 탭 선택
3. Team 선택 (Apple Developer Account 필요)
4. Bundle Identifier 확인: `com.radiorecorder.app`
5. Product → Build for Running

### 단계 3: Android 프로젝트 생성
```bash
# Android 프로젝트 생성
npx cap add android

# 설정 파일 업데이트
npx cap sync android

# Android Studio에서 열기
npx cap open android
```

**Android Studio에서:**
1. File → Open → `mobile/android` 폴더 선택
2. Gradle sync 완료 대기
3. 설정 확인:
   - Package Name: `com.radiorecorder.app`
   - compileSdkVersion: 33
   - targetSdkVersion: 33
4. Build → Make Project

## 3️⃣ 환경 설정

### 개발 환경
```bash
# .env.development 생성
cp .env.example .env.development

# 수정 사항
VITE_API_URL=http://localhost:8000
VITE_ENVIRONMENT=development
```

### 프로덕션 환경
```bash
# .env.production 생성
cp .env.example .env.production

# 수정 사항
VITE_API_URL=https://api.radiorecorder.com
VITE_ENVIRONMENT=production
VITE_ENABLE_ANALYTICS=true
```

## 4️⃣ 개발 시작

### 웹 버전 (개발/테스트)
```bash
# 개발 서버 실행
npm run dev

# 브라우저에서 http://localhost:5173 접속
```

### iOS 개발
```bash
# 웹 빌드 및 동기화
npm run build:ios

# Xcode에서 앱 실행
# Command + R (시뮬레이터)
# 또는 실제 기기에 연결 후 실행
```

### Android 개발
```bash
# 웹 빌드 및 동기화
npm run build:android

# Android Studio에서 앱 실행
# Run → Run 'app' (에뮬레이터)
# 또는 실제 기기에 연결 후 실행
```

## 5️⃣ 빌드 스크립트 사용

### Unix/Mac
```bash
# 모든 플랫폼
./scripts/build.sh web
./scripts/build.sh ios
./scripts/build.sh android

# 프로덕션 빌드
./scripts/build.sh web production
./scripts/build.sh ios production
./scripts/build.sh android production
```

### Windows
```bash
# 모든 플랫폼
scripts\build.bat web
scripts\build.bat ios
scripts\build.bat android

# 프로덕션 빌드
scripts\build.bat web production
scripts\build.bat ios production
scripts\build.bat android production
```

## 6️⃣ 앱 스토어 배포 준비

### iOS App Store
```bash
# 1. Apple Developer Account 생성
# https://developer.apple.com

# 2. Certificates 생성
# Xcode → Preferences → Accounts → Manage Certificates

# 3. Provisioning Profile 생성
# https://developer.apple.com/account/resources/certificates/list

# 4. Xcode에서 설정
#    - Team 선택
#    - Bundle Identifier 확인
#    - Signing Certificate 설정

# 5. Archive 생성
# Product → Archive

# 6. App Store Connect에 업로드
```

### Google Play Store
```bash
# 1. Google Play Console 계정 생성
# https://play.google.com/console

# 2. 앱 생성 및 기본 정보 설정

# 3. 서명 키 생성
keytool -genkey -v -keystore radio-recorder-key.jks \
  -keyalg RSA -keysize 2048 -validity 10000 \
  -alias radio-recorder

# 4. app/build.gradle에 서명 설정
# signingConfigs 추가

# 5. Release AAB 빌드
./android/gradlew bundleRelease

# 6. Google Play Console에 업로드
#    - app/build/outputs/bundle/release/app-release.aab
```

## 7️⃣ 지속적 통합 (CI/CD)

### GitHub Actions 설정

#### 필수 Secrets 설정
GitHub 저장소 Settings → Secrets에서:

**iOS:**
```
- XCODE_TEAM_ID: Apple Team ID
- XCODE_TEAM_NAME: Apple Team Name
- XCODE_PROJECT: App.xcworkspace 경로
```

**Android:**
```
- ANDROID_SIGNING_KEY: Base64로 인코딩된 keystore
- ANDROID_SIGNING_KEY_ALIAS: 키 별칭
- ANDROID_SIGNING_STORE_PASSWORD: keystore 비밀번호
- ANDROID_SIGNING_KEY_PASSWORD: 키 비밀번호
- PLAY_STORE_SERVICE_ACCOUNT_JSON: Google Play 서비스 계정 JSON
```

### 자동 배포 워크플로우
```
1. main 브랜치에 푸시
2. GitHub Actions 자동 실행
3. 빌드 및 테스트 완료
4. 앱 스토어 자동 업로드 (선택적)
```

## 8️⃣ 네이티브 플러그인 추가

### 카메라 플러그인 추가
```bash
npm install @capacitor/camera
npx cap sync
```

### 파일시스템 플러그인 추가
```bash
npm install @capacitor/filesystem
npx cap sync
```

## 🔍 문제 해결

### Pod 오류 (iOS)
```bash
rm -rf ios/App/Pods
rm -rf node_modules/@capacitor
npx cap sync ios
```

### Gradle 오류 (Android)
```bash
rm -rf android/.gradle
./android/gradlew clean
npx cap sync android
```

### Capacitor 버전 불일치
```bash
npx cap doctor
# 버전 확인 및 업데이트

npx cap sync
```

## 📚 추가 리소스

- [Capacitor 공식 문서](https://capacitorjs.com/docs)
- [iOS 배포 가이드](https://capacitorjs.com/docs/ios)
- [Android 배포 가이드](https://capacitorjs.com/docs/android)
- [GitHub Actions 문서](https://docs.github.com/en/actions)

## ✅ 체크리스트

초기 설정 완료 확인:

- [ ] Node.js v18+ 설치
- [ ] Xcode/Android Studio 설치
- [ ] `npm install` 실행
- [ ] iOS 프로젝트 생성 및 설정
- [ ] Android 프로젝트 생성 및 설정
- [ ] 환경 파일 생성
- [ ] 개발 서버 실행 테스트
- [ ] iOS/Android 빌드 테스트
- [ ] GitHub Actions Secrets 설정
- [ ] 앱 스토어 계정 생성

---

문제가 발생하면 Issues를 통해 보고해주세요!

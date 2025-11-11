@echo off
REM Build script for Radio Recorder Mobile App (Windows)
REM Supports iOS and Android builds with Capacitor

setlocal enabledelayedexpansion

set BUILD_TYPE=%1
if "%BUILD_TYPE%"=="" set BUILD_TYPE=web

set ENVIRONMENT=%2
if "%ENVIRONMENT%"=="" set ENVIRONMENT=development

REM Get version from package.json
for /f "tokens=2 delims=:" %%A in ('findstr /C:"version" package.json') do (
    set VERSION=%%A
    set VERSION=!VERSION:"=!
    set VERSION=!VERSION:,=!
    set VERSION=!VERSION: =!
)

echo.
echo ========================================
echo Radio Recorder Mobile Build Script
echo ========================================
echo Build Type: %BUILD_TYPE%
echo Environment: %ENVIRONMENT%
echo Version: %VERSION%
echo ========================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed
    exit /b 1
)

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)

REM Load environment file if exists
if exist ".env.%ENVIRONMENT%" (
    echo Loading environment: .env.%ENVIRONMENT%
    for /f "delims== tokens=1,*" %%A in (.env.%ENVIRONMENT%) do (
        if not "%%A"=="" (
            if not "%%A:~0,1%%" == "#" (
                set "%%A=%%B"
            )
        )
    )
)

REM Build web assets
echo.
echo Building web assets...
call npm run build
if %errorlevel% neq 0 (
    echo Error: Build failed
    exit /b 1
)

if "%BUILD_TYPE%"=="web" (
    echo.
    echo Web build completed successfully
    echo Output directory: .\dist
    goto :end
)

if "%BUILD_TYPE%"=="ios" (
    echo.
    echo Syncing with Capacitor iOS...
    call npx cap sync ios

    if exist "ios\App" (
        echo Opening Xcode...
        call npx cap open ios
        echo iOS project synced and opened in Xcode
        echo.
        echo Next steps:
        echo   1. Open ios/App/App.xcworkspace in Xcode
        echo   2. Select your team in Signing ^& Capabilities
        echo   3. Build and run on device or simulator
    ) else (
        echo Error: iOS project not found
        exit /b 1
    )
    goto :end
)

if "%BUILD_TYPE%"=="android" (
    echo.
    echo Syncing with Capacitor Android...
    call npx cap sync android

    if exist "android" (
        echo Opening Android Studio...
        call npx cap open android
        echo Android project synced and opened in Android Studio
        echo.
        echo Next steps:
        echo   1. Open android folder in Android Studio
        echo   2. Wait for Gradle sync to complete
        echo   3. Build and run on device or emulator
    ) else (
        echo Error: Android project not found
        exit /b 1
    )
    goto :end
)

echo Error: Invalid build type '%BUILD_TYPE%'
echo Usage: build.bat [web^|ios^|android] [development^|production]
exit /b 1

:end
echo.
echo Build process completed!
echo.

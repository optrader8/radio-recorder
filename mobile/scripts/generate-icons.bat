@echo off
REM Generate icons script for Radio Recorder Mobile App (Windows)
REM This script requires ImageMagick to be installed

setlocal enabledelayedexpansion

REM Check if ImageMagick convert is available
where convert >nul 2>nul
if errorlevel 1 (
    echo Error: ImageMagick is not installed or not in PATH
    echo Download from: https://imagemagick.org/script/download.php
    exit /b 1
)

echo.
echo Creating directories...
if not exist "ios\App\Assets.xcassets\AppIcon.appiconset" mkdir "ios\App\Assets.xcassets\AppIcon.appiconset"
if not exist "ios\App\Assets.xcassets\Splash.imageset" mkdir "ios\App\Assets.xcassets\Splash.imageset"

if not exist "android\app\src\main\res\mipmap-mdpi" mkdir "android\app\src\main\res\mipmap-mdpi"
if not exist "android\app\src\main\res\mipmap-hdpi" mkdir "android\app\src\main\res\mipmap-hdpi"
if not exist "android\app\src\main\res\mipmap-xhdpi" mkdir "android\app\src\main\res\mipmap-xhdpi"
if not exist "android\app\src\main\res\mipmap-xxhdpi" mkdir "android\app\src\main\res\mipmap-xxhdpi"
if not exist "android\app\src\main\res\mipmap-xxxhdpi" mkdir "android\app\src\main\res\mipmap-xxxhdpi"
if not exist "android\app\src\main\res\drawable" mkdir "android\app\src\main\res\drawable"
if not exist "android\app\src\main\res\drawable-land" mkdir "android\app\src\main\res\drawable-land"

echo.
echo Generating iOS icons...

REM iOS icons
convert assets\icon.svg -background none -resize "40x40!" "ios\App\Assets.xcassets\AppIcon.appiconset\notification-icon-iphone.png"
echo   + notification-icon-iphone (40x40)

convert assets\icon.svg -background none -resize "58x58!" "ios\App\Assets.xcassets\AppIcon.appiconset\settings-icon-iphone.png"
echo   + settings-icon-iphone (58x58)

convert assets\icon.svg -background none -resize "80x80!" "ios\App\Assets.xcassets\AppIcon.appiconset\spotlight-icon-iphone.png"
echo   + spotlight-icon-iphone (80x80)

convert assets\icon.svg -background none -resize "120x120!" "ios\App\Assets.xcassets\AppIcon.appiconset\app-icon-iphone.png"
echo   + app-icon-iphone (120x120)

convert assets\icon.svg -background none -resize "152x152!" "ios\App\Assets.xcassets\AppIcon.appiconset\ipad-icon.png"
echo   + ipad-icon (152x152)

convert assets\icon.svg -background none -resize "167x167!" "ios\App\Assets.xcassets\AppIcon.appiconset\ipad-pro-icon.png"
echo   + ipad-pro-icon (167x167)

convert assets\icon.svg -background none -resize "240x240!" "ios\App\Assets.xcassets\AppIcon.appiconset\app-icon-iphone-retina.png"
echo   + app-icon-iphone-retina (240x240)

convert assets\icon.svg -background none -resize "334x334!" "ios\App\Assets.xcassets\AppIcon.appiconset\ipad-pro-retina-icon.png"
echo   + ipad-pro-retina-icon (334x334)

convert assets\icon.svg -background none -resize "360x360!" "ios\App\Assets.xcassets\AppIcon.appiconset\app-icon-iphone-6-plus.png"
echo   + app-icon-iphone-6-plus (360x360)

convert assets\icon.svg -background none -resize "1024x1024!" "ios\App\Assets.xcassets\AppIcon.appiconset\app-store-icon.png"
echo   + app-store-icon (1024x1024)

echo.
echo Generating Android icons...

convert assets\icon.svg -background none -resize "72x72!" "android\app\src\main\res\mipmap-mdpi\ic_launcher.png"
echo   + mdpi (72x72)

convert assets\icon.svg -background none -resize "96x96!" "android\app\src\main\res\mipmap-hdpi\ic_launcher.png"
echo   + hdpi (96x96)

convert assets\icon.svg -background none -resize "144x144!" "android\app\src\main\res\mipmap-xhdpi\ic_launcher.png"
echo   + xhdpi (144x144)

convert assets\icon.svg -background none -resize "192x192!" "android\app\src\main\res\mipmap-xxhdpi\ic_launcher.png"
echo   + xxhdpi (192x192)

convert assets\icon.svg -background none -resize "512x512!" "android\app\src\main\res\mipmap-xxxhdpi\ic_launcher.png"
echo   + xxxhdpi (512x512)

echo.
echo Generating splash screens...

convert assets\splash.svg -background none -extent "640x1136!" "ios\App\Assets.xcassets\Splash.imageset\splash-iphone-5.png"
echo   + iOS splash-iphone-5 (640x1136)

convert assets\splash.svg -background none -extent "750x1334!" "ios\App\Assets.xcassets\Splash.imageset\splash-iphone-6.png"
echo   + iOS splash-iphone-6 (750x1334)

convert assets\splash.svg -background none -extent "1242x2208!" "ios\App\Assets.xcassets\Splash.imageset\splash-iphone-6-plus.png"
echo   + iOS splash-iphone-6-plus (1242x2208)

convert assets\splash.svg -background none -extent "1125x2436!" "ios\App\Assets.xcassets\Splash.imageset\splash-iphone-x.png"
echo   + iOS splash-iphone-x (1125x2436)

REM Android splash screens (portrait)
convert assets\splash.svg -background none -extent "320x426!" "android\app\src\main\res\drawable\splash.png"
echo   + Android splash (320x426)

REM Android splash screens (landscape)
convert assets\splash.svg -background none -extent "426x320!" "android\app\src\main\res\drawable-land\splash.png"
echo   + Android splash-land (426x320)

echo.
echo [SUCCESS] Icon and splash screen generation complete!
echo.
echo Next steps:
echo   1. Review the generated images in the directories above
echo   2. Customize icon colors and splash screen text as needed
echo   3. For iOS: Update LaunchScreen.storyboard in Xcode
echo   4. For Android: Update styles.xml and AndroidManifest.xml
echo.

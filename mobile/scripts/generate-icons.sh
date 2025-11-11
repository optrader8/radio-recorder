#!/bin/bash

# Generate icons script for Radio Recorder Mobile App
# This script uses ImageMagick to convert SVG icons to PNG at different sizes

set -e

# Check if ImageMagick is installed
if ! command -v convert &> /dev/null; then
    echo "Error: ImageMagick is not installed"
    echo "Install with: brew install imagemagick (macOS) or apt-get install imagemagick (Linux)"
    exit 1
fi

# Create directories if they don't exist
mkdir -p ios/App/Assets.xcassets/AppIcon.appiconset
mkdir -p android/app/src/main/res/mipmap-{hdpi,mdpi,xhdpi,xxhdpi,xxxhdpi}

echo "Generating iOS icons..."

# iOS App Icon sizes
declare -a ios_sizes=(
  "20:notification-icon-iphone"
  "29:settings-icon-iphone"
  "40:spotlight-icon-iphone"
  "60:app-icon-iphone"
  "76:ipad-icon"
  "83.5:ipad-pro-icon"
  "120:app-icon-iphone-retina"
  "167:ipad-pro-retina-icon"
  "180:app-icon-iphone-6-plus"
  "1024:app-store-icon"
)

for size_config in "${ios_sizes[@]}"; do
  size="${size_config%%:*}"
  name="${size_config##*:}"

  # Convert to points (iOS uses points, not pixels)
  pixels=$((${size%.*} * 2))

  convert assets/icon.svg -background none -resize "${pixels}x${pixels}!" \
    "ios/App/Assets.xcassets/AppIcon.appiconset/${name}.png"
  echo "  ✓ Generated iOS icon: ${name} (${pixels}x${pixels}px)"
done

echo ""
echo "Generating Android icons..."

# Android icon sizes (dpi)
declare -a android_sizes=(
  "72:mdpi"
  "96:hdpi"
  "144:xhdpi"
  "192:xxhdpi"
  "512:xxxhdpi"
)

for size_config in "${android_sizes[@]}"; do
  size="${size_config%%:*}"
  dpi="${size_config##*:}"

  convert assets/icon.svg -background none -resize "${size}x${size}!" \
    "android/app/src/main/res/mipmap-${dpi}/ic_launcher.png"
  echo "  ✓ Generated Android icon: ${dpi} (${size}x${size}px)"
done

echo ""
echo "Generating splash screens..."

# iOS Splash screens
declare -a ios_splash=(
  "640x1136:iphone-5"
  "750x1334:iphone-6"
  "1242x2208:iphone-6-plus"
  "1125x2436:iphone-x"
  "1170x2532:iphone-12"
  "768x1024:ipad"
  "1536x2048:ipad-retina"
  "2048x2732:ipad-pro"
)

for size_config in "${ios_splash[@]}"; do
  dimensions="${size_config%%:*}"
  name="${size_config##*:}"

  convert assets/splash.svg -background none -extent "${dimensions}!" \
    "ios/App/Assets.xcassets/Splash.imageset/splash-${name}.png"
  echo "  ✓ Generated iOS splash: ${name} (${dimensions})"
done

# Android Splash screens
declare -a android_splash=(
  "320x470:ldpi"
  "470x320:ldpi-land"
  "320x426:mdpi"
  "426x320:mdpi-land"
  "480x640:hdpi"
  "640x480:hdpi-land"
  "720x960:xhdpi"
  "960x720:xhdpi-land"
  "1080x1920:xxhdpi"
  "1920x1080:xxhdpi-land"
  "1440x2560:xxxhdpi"
  "2560x1440:xxxhdpi-land"
)

mkdir -p android/app/src/main/res/{drawable,drawable-land}

for size_config in "${android_splash[@]}"; do
  dimensions="${size_config%%:*}"
  name="${size_config##*:}"

  if [[ $name == *"-land" ]]; then
    output_dir="android/app/src/main/res/drawable-land"
    output_name="splash"
  else
    output_dir="android/app/src/main/res/drawable"
    output_name="splash"
  fi

  convert assets/splash.svg -background none -extent "${dimensions}!" \
    "${output_dir}/${output_name}.png"
  echo "  ✓ Generated Android splash: ${name} (${dimensions})"
done

echo ""
echo "✅ Icon and splash screen generation complete!"
echo ""
echo "Next steps:"
echo "1. Review the generated images in the directories above"
echo "2. Customize icon colors and splash screen text as needed"
echo "3. For iOS: Update LaunchScreen.storyboard in Xcode"
echo "4. For Android: Update styles.xml and AndroidManifest.xml"

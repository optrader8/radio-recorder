#!/bin/bash

# Build script for Radio Recorder Mobile App
# Supports iOS and Android builds with Capacitor

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BUILD_TYPE="${1:-web}"
ENVIRONMENT="${2:-development}"
VERSION=$(grep '"version"' package.json | sed 's/.*"version": "\([^"]*\)".*/\1/')

echo -e "${YELLOW}========================================${NC}"
echo -e "${YELLOW}Radio Recorder Mobile Build Script${NC}"
echo -e "${YELLOW}========================================${NC}"
echo -e "Build Type: ${BUILD_TYPE}"
echo -e "Environment: ${ENVIRONMENT}"
echo -e "Version: ${VERSION}"
echo -e "${YELLOW}========================================${NC}\n"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}Error: Node.js is not installed${NC}"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${GREEN}Installing dependencies...${NC}"
    npm install
fi

# Load environment variables
if [ -f ".env.$ENVIRONMENT" ]; then
    export $(cat .env.$ENVIRONMENT | grep -v '^#' | xargs)
    echo -e "${GREEN}Loaded environment: .env.$ENVIRONMENT${NC}"
else
    echo -e "${YELLOW}Warning: .env.$ENVIRONMENT not found, using defaults${NC}"
fi

# Build web assets
echo -e "\n${GREEN}Building web assets...${NC}"
npm run build

case $BUILD_TYPE in
    web)
        echo -e "${GREEN}✓ Web build completed successfully${NC}"
        echo -e "Output directory: ./dist"
        ;;

    ios)
        echo -e "\n${GREEN}Syncing with Capacitor iOS...${NC}"
        npx cap sync ios

        if [ -d "ios/App" ]; then
            echo -e "${GREEN}Opening Xcode...${NC}"
            npx cap open ios
            echo -e "${GREEN}✓ iOS project synced and opened in Xcode${NC}"
            echo -e "Next steps:"
            echo -e "  1. Open ios/App/App.xcworkspace in Xcode"
            echo -e "  2. Select your team in Signing & Capabilities"
            echo -e "  3. Build and run on device or simulator"
        else
            echo -e "${RED}Error: iOS project not found${NC}"
            exit 1
        fi
        ;;

    android)
        echo -e "\n${GREEN}Syncing with Capacitor Android...${NC}"
        npx cap sync android

        if [ -d "android" ]; then
            echo -e "${GREEN}Opening Android Studio...${NC}"
            npx cap open android
            echo -e "${GREEN}✓ Android project synced and opened in Android Studio${NC}"
            echo -e "Next steps:"
            echo -e "  1. Open android folder in Android Studio"
            echo -e "  2. Wait for Gradle sync to complete"
            echo -e "  3. Build and run on device or emulator"
        else
            echo -e "${RED}Error: Android project not found${NC}"
            exit 1
        fi
        ;;

    *)
        echo -e "${RED}Error: Invalid build type '$BUILD_TYPE'${NC}"
        echo -e "Usage: ./scripts/build.sh [web|ios|android] [development|production]"
        exit 1
        ;;
esac

echo -e "\n${GREEN}Build process completed!${NC}\n"

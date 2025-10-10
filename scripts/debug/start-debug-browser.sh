#!/bin/bash

# Browser Debug Starter
# This script starts Chrome with debugging enabled for VS Code debugging

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEBUG_PROFILE_DIR="$HOME/.chrome-debug-profile"
CHROME_DEBUG_PORT=9222
CHROME_DEBUG_URL="http://localhost:3000"

echo -e "${BLUE}🚀 Starting Chrome with debugging enabled...${NC}"

# Check if debug profile exists
if [ ! -d "$DEBUG_PROFILE_DIR" ]; then
    echo -e "${RED}❌ Debug profile not found. Please run prepare-chrome-debug.sh first.${NC}"
    exit 1
fi

# Kill any existing Chrome processes
echo -e "${YELLOW}🔄 Closing existing Chrome processes...${NC}"
pkill -f "Google Chrome" || true
sleep 2

# Start Chrome with debugging
echo -e "${GREEN}🔧 Starting Chrome with debug profile...${NC}"
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
    --user-data-dir="$DEBUG_PROFILE_DIR" \
    --remote-debugging-port=$CHROME_DEBUG_PORT \
    --disable-web-security \
    --disable-features=VizDisplayCompositor \
    --enable-logging \
    --v=1 \
    --no-first-run \
    --no-default-browser-check \
    --disable-background-timer-throttling \
    --disable-backgrounding-occluded-windows \
    --disable-renderer-backgrounding \
    --disable-features=TranslateUI \
    --disable-ipc-flooding-protection \
    --enable-automation \
    --disable-extensions \
    --disable-plugins \
    --disable-images \
    --disable-javascript-harmony-shipping \
    --disable-background-networking \
    --disable-sync \
    --metrics-recording-only \
    --no-report-upload \
    --disable-default-apps \
    --mute-audio \
    --no-sandbox \
    --disable-gpu \
    --disable-dev-shm-usage \
    --remote-allow-origins=* \
    "$CHROME_DEBUG_URL" &

# Wait for Chrome to start
echo -e "${YELLOW}⏳ Waiting for Chrome to start...${NC}"
sleep 3

# Check if Chrome is running
if pgrep -f "Google Chrome" > /dev/null; then
    echo -e "${GREEN}✅ Chrome started successfully with debugging enabled${NC}"
    echo -e "${BLUE}🌐 Debug URL: http://localhost:$CHROME_DEBUG_PORT${NC}"
    echo -e "${BLUE}🎯 Target URL: $CHROME_DEBUG_URL${NC}"
    echo -e "${YELLOW}💡 You can now attach VS Code debugger to this Chrome instance${NC}"
else
    echo -e "${RED}❌ Failed to start Chrome${NC}"
    exit 1
fi

#!/bin/bash
# Safe Chrome Debug Starter
# This script safely starts Chrome with debugging, handling conflicts and crashes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DEBUG_PROFILE_DIR="$HOME/.chrome-debug-profile-safe"
CHROME_DEBUG_PORT=9222
CHROME_DEBUG_URL="http://localhost:3000"

echo -e "${BLUE}🚀 Starting Chrome with safe debugging configuration...${NC}"

# Find Chrome binary
CHROME_BINARY=""
if [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
    CHROME_BINARY="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif [ -f "/Applications/Chromium.app/Contents/MacOS/Chromium" ]; then
    CHROME_BINARY="/Applications/Chromium.app/Contents/MacOS/Chromium"
else
    echo -e "${RED}❌ Chrome not found. Please install Google Chrome or Chromium.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Found Chrome: $CHROME_BINARY${NC}"

# Clean up any existing Chrome processes
echo -e "${YELLOW}🔄 Cleaning up existing Chrome processes...${NC}"
pkill -f "Google Chrome.*remote-debugging-port" 2>/dev/null || true
pkill -f "Google Chrome.*user-data-dir.*debug" 2>/dev/null || true
pkill -f "chrome.*remote-debugging-port" 2>/dev/null || true
pkill -f "chrome.*user-data-dir.*debug" 2>/dev/null || true

# Wait for processes to terminate
sleep 3

# Create debug profile directory
echo -e "${YELLOW}📁 Setting up debug profile...${NC}"
rm -rf "$DEBUG_PROFILE_DIR"
mkdir -p "$DEBUG_PROFILE_DIR"

# Find available port
while lsof -Pi :$CHROME_DEBUG_PORT -sTCP:LISTEN -t >/dev/null 2>&1; do
    CHROME_DEBUG_PORT=$((CHROME_DEBUG_PORT + 1))
done

echo -e "${GREEN}✅ Using debug port: $CHROME_DEBUG_PORT${NC}"

# Start Chrome with safe debugging configuration
echo -e "${GREEN}🔧 Starting Chrome with safe debug profile...${NC}"
"$CHROME_BINARY" \
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
    --disable-background-mode \
    --disable-component-extensions-with-background-pages \
    --disable-translate \
    --hide-scrollbars \
    --no-pings \
    --no-zygote \
    --single-process \
    --disable-setuid-sandbox \
    --disable-features=TranslateUI \
    --disable-ipc-flooding-protection \
    --disable-background-networking \
    --disable-sync \
    --disable-default-apps \
    --disable-extensions \
    --disable-plugins \
    --disable-translate \
    --hide-scrollbars \
    --mute-audio \
    --no-first-run \
    --no-pings \
    --no-zygote \
    --single-process \
    "$CHROME_DEBUG_URL" &

CHROME_PID=$!

# Wait for Chrome to start
echo -e "${YELLOW}⏳ Waiting for Chrome to start...${NC}"
sleep 5

# Verify Chrome started successfully
if ps -p $CHROME_PID > /dev/null; then
    echo -e "${GREEN}✅ Chrome started successfully with debugging enabled${NC}"
    echo -e "${BLUE}🌐 Debug URL: http://localhost:$CHROME_DEBUG_PORT${NC}"
    echo -e "${BLUE}🎯 Target URL: $CHROME_DEBUG_URL${NC}"
    echo -e "${YELLOW}💡 You can now attach VS Code debugger to this Chrome instance${NC}"
    
    # Test debug port availability
    echo -e "${YELLOW}🧪 Testing debug port...${NC}"
    if curl -s "http://localhost:$CHROME_DEBUG_PORT/json" > /dev/null; then
        echo -e "${GREEN}✅ Debug port is responding correctly${NC}"
    else
        echo -e "${YELLOW}⚠️ Debug port may not be ready yet, please wait...${NC}"
    fi
    
    # Keep script running and handle cleanup
    echo -e "${BLUE}🔄 Chrome is running. Press Ctrl+C to stop...${NC}"
    trap "echo -e '${YELLOW}🛑 Stopping Chrome...${NC}'; kill $CHROME_PID 2>/dev/null; rm -rf '$DEBUG_PROFILE_DIR'; exit" INT TERM
    
    # Wait for Chrome process
    wait $CHROME_PID
else
    echo -e "${RED}❌ Failed to start Chrome${NC}"
    echo -e "${YELLOW}💡 Try running: ./cleanup-debug-profiles.sh${NC}"
    exit 1
fi
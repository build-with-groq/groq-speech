#!/bin/bash

# Safe Chrome Debug Starter (Alternative)
# This script provides an alternative way to start Chrome with debugging

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

echo -e "${BLUE}🚀 Starting Chrome with debugging enabled (Alternative Safe Mode)...${NC}"

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        echo -e "${YELLOW}⚠️ Port $port is in use, attempting to free it...${NC}"
        lsof -ti:$port | xargs kill -9 || true
        sleep 2
    fi
}

# Function to ensure Chrome is completely closed
ensure_chrome_closed() {
    echo -e "${YELLOW}🔄 Ensuring Chrome is completely closed...${NC}"
    
    # Kill Chrome processes
    pkill -f "Google Chrome" || true
    sleep 2
    
    # Force kill if still running
    if pgrep -f "Google Chrome" > /dev/null; then
        echo -e "${YELLOW}⚠️ Force killing Chrome processes...${NC}"
        pkill -9 -f "Google Chrome" || true
        sleep 2
    fi
    
    # Verify Chrome is closed
    if pgrep -f "Google Chrome" > /dev/null; then
        echo -e "${RED}❌ Chrome processes still running after force kill${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Chrome is completely closed${NC}"
}

# Check prerequisites
if [ ! -d "$DEBUG_PROFILE_DIR" ]; then
    echo -e "${RED}❌ Debug profile not found. Please run prepare-chrome-debug.sh first.${NC}"
    exit 1
fi

# Check and free debug port
check_port $CHROME_DEBUG_PORT

# Ensure Chrome is completely closed
ensure_chrome_closed

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
    --disable-background-mode \
    --disable-component-extensions-with-background-pages \
    --disable-translate \
    --hide-scrollbars \
    --no-pings \
    --no-zygote \
    --single-process \
    "$CHROME_DEBUG_URL" &

# Wait for Chrome to start
echo -e "${YELLOW}⏳ Waiting for Chrome to start...${NC}"
sleep 5

# Verify Chrome started successfully
if pgrep -f "Google Chrome" > /dev/null; then
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
else
    echo -e "${RED}❌ Failed to start Chrome${NC}"
    exit 1
fi

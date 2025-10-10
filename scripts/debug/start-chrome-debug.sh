#!/bin/bash
# Script to start Chrome with debugging, handling existing instances

echo "🚀 Starting Chrome with debugging..."

# Kill existing Chrome processes with debugging
echo "Cleaning up existing Chrome processes..."
pkill -f "chrome.*remote-debugging-port" 2>/dev/null || true
pkill -f "chrome.*user-data-dir.*debug" 2>/dev/null || true

# Wait for processes to terminate
sleep 2

# Generate unique profile name
PROFILE_NAME="chrome-debug-$(date +%s)"
PROFILE_DIR="$(pwd)/.vscode/$PROFILE_NAME"

echo "Using profile: $PROFILE_DIR"

# Create profile directory
mkdir -p "$PROFILE_DIR"

# Find available port
PORT=9222
while lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; do
    PORT=$((PORT + 1))
done

echo "Using debugging port: $PORT"

# Launch Chrome with unique profile and debugging
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --user-data-dir="$PROFILE_DIR" \
  --remote-debugging-port=$PORT \
  --no-first-run \
  --no-default-browser-check \
  --disable-web-security \
  --disable-features=VizDisplayCompositor \
  --disable-background-timer-throttling \
  --disable-backgrounding-occluded-windows \
  --disable-renderer-backgrounding \
  --disable-extensions \
  --disable-plugins \
  --disable-default-apps \
  --new-window \
  --force-new-window \
  --no-sandbox \
  --disable-setuid-sandbox \
  http://localhost:3000 &

CHROME_PID=$!

echo "✅ Chrome launched with PID: $CHROME_PID"
echo "🌐 URL: http://localhost:3000"
echo "🔧 Debug port: $PORT"
echo "📁 Profile: $PROFILE_DIR"
echo ""
echo "You can now use 'Debug Frontend (Manual Browser)' to attach to this Chrome instance."
echo "Press Ctrl+C to stop Chrome when done."

# Wait for Chrome to start
sleep 3

# Check if Chrome is running
if ps -p $CHROME_PID > /dev/null; then
    echo "✅ Chrome is running successfully!"
else
    echo "❌ Chrome failed to start"
    exit 1
fi

# Keep script running until Ctrl+C
trap "echo '🛑 Stopping Chrome...'; kill $CHROME_PID 2>/dev/null; exit" INT TERM
wait $CHROME_PID
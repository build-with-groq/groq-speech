#!/bin/bash
# Script to prepare Chrome debugging environment by killing existing instances

echo "🧹 Preparing Chrome debugging environment..."

# Kill all existing Chrome processes with debugging
echo "Killing existing Chrome processes..."
pkill -f "chrome.*remote-debugging-port" 2>/dev/null || true
pkill -f "chrome.*user-data-dir.*debug" 2>/dev/null || true
pkill -f "chrome.*--new-window" 2>/dev/null || true

# Kill all existing Edge processes with debugging
echo "Killing existing Edge processes..."
pkill -f "msedge.*remote-debugging-port" 2>/dev/null || true
pkill -f "msedge.*user-data-dir.*debug" 2>/dev/null || true

# Wait a moment for processes to terminate
sleep 2

# Clean up old debug profiles
echo "Cleaning up old debug profiles..."
rm -rf .vscode/chrome-debug-* 2>/dev/null || true
rm -rf .vscode/edge-debug-* 2>/dev/null || true

# Create fresh debug profile directory
echo "Creating fresh debug profile directory..."
mkdir -p .vscode/chrome-debug-fresh-$(date +%s) 2>/dev/null || true

echo "✅ Chrome debugging environment prepared!"
echo ""
echo "Now you can use these debug configurations:"
echo "1. 'Next.js: debug client-side' - Chrome debugging"
echo "2. 'Debug Frontend (Browser)' - Chrome debugging"
echo "3. 'Debug Frontend (Edge)' - Edge debugging"
echo "4. 'Debug Full Stack (API + Next.js)' - Full stack with Chrome"
echo ""
echo "Each will create a new Chrome instance with a unique profile."

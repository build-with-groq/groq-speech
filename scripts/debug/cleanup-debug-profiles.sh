#!/bin/bash
# Script to clean up Chrome debug profiles that might be causing conflicts

echo "🧹 Cleaning up Chrome debug profiles..."

# Remove existing debug profiles
if [ -d ".vscode/chrome-debug-profile" ]; then
    echo "Removing .vscode/chrome-debug-profile..."
    rm -rf .vscode/chrome-debug-profile
fi

if [ -d ".vscode/chrome-debug-profile-groq-speech" ]; then
    echo "Removing .vscode/chrome-debug-profile-groq-speech..."
    rm -rf .vscode/chrome-debug-profile-groq-speech
fi

if [ -d ".vscode/edge-debug-profile" ]; then
    echo "Removing .vscode/edge-debug-profile..."
    rm -rf .vscode/edge-debug-profile
fi

if [ -d ".vscode/edge-debug-profile-groq-speech" ]; then
    echo "Removing .vscode/edge-debug-profile-groq-speech..."
    rm -rf .vscode/edge-debug-profile-groq-speech
fi

# Kill any existing Chrome processes with debugging enabled
echo "Killing existing Chrome processes with debugging..."
pkill -f "chrome.*remote-debugging-port" || true
pkill -f "chrome.*user-data-dir.*debug" || true

# Kill any existing Edge processes with debugging enabled
echo "Killing existing Edge processes with debugging..."
pkill -f "msedge.*remote-debugging-port" || true
pkill -f "msedge.*user-data-dir.*debug" || true

echo "✅ Cleanup complete!"
echo ""
echo "Now you can try these debug configurations in order:"
echo "1. 'Debug Full Stack (API + Next.js - No Chrome)' - Safest option"
echo "2. 'Next.js: debug server-only (No Chrome)' - Next.js only"
echo "3. 'Debug API Server' - Python API only"
echo "4. 'Next.js: debug client-side' - Chrome debugging (if needed)"
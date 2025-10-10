#!/bin/bash
# Chrome Debug Cleanup Script
# This script safely cleans up Chrome debugging processes and profiles

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧹 Cleaning up Chrome debugging processes and profiles...${NC}"

# Kill Chrome debugging processes
echo -e "${YELLOW}🔄 Stopping Chrome debugging processes...${NC}"

# Kill processes with various patterns
pkill -f "Google Chrome.*remote-debugging-port" 2>/dev/null || true
pkill -f "Google Chrome.*user-data-dir.*debug" 2>/dev/null || true
pkill -f "chrome.*remote-debugging-port" 2>/dev/null || true
pkill -f "chrome.*user-data-dir.*debug" 2>/dev/null || true
pkill -f "chrome.*--remote-debugging-port" 2>/dev/null || true
pkill -f "chrome.*--user-data-dir.*debug" 2>/dev/null || true

# Wait for processes to terminate
sleep 2

# Check if any Chrome processes are still running
if pgrep -f "Google Chrome.*debug" > /dev/null; then
    echo -e "${YELLOW}⚠️ Some Chrome debugging processes are still running, forcing termination...${NC}"
    pkill -9 -f "Google Chrome.*debug" 2>/dev/null || true
    sleep 1
fi

# Clean up debug profile directories
echo -e "${YELLOW}📁 Cleaning up debug profile directories...${NC}"

# Remove common debug profile directories
rm -rf "$HOME/.chrome-debug-profile" 2>/dev/null || true
rm -rf "$HOME/.chrome-debug-profile-safe" 2>/dev/null || true
rm -rf "$HOME/.chrome-debug-profile-*" 2>/dev/null || true
rm -rf "$HOME/.vscode/chrome-debug-*" 2>/dev/null || true
rm -rf ".vscode/chrome-debug-*" 2>/dev/null || true

# Remove any remaining Chrome debug directories
find "$HOME" -name "chrome-debug-*" -type d -exec rm -rf {} + 2>/dev/null || true
find ".vscode" -name "chrome-debug-*" -type d -exec rm -rf {} + 2>/dev/null || true

# Clean up any Chrome crash dumps
echo -e "${YELLOW}🗑️ Cleaning up Chrome crash dumps...${NC}"
rm -rf "$HOME/Library/Application Support/Google/Chrome/Crashpad" 2>/dev/null || true
rm -rf "$HOME/Library/Logs/Google Chrome" 2>/dev/null || true

# Check for any remaining Chrome processes
echo -e "${YELLOW}🔍 Checking for remaining Chrome processes...${NC}"
if pgrep -f "Google Chrome" > /dev/null; then
    echo -e "${YELLOW}⚠️ Some Chrome processes are still running:${NC}"
    ps aux | grep -i chrome | grep -v grep || true
    echo -e "${YELLOW}💡 You may need to manually close Chrome or restart your system${NC}"
else
    echo -e "${GREEN}✅ All Chrome debugging processes have been stopped${NC}"
fi

# Check for any remaining debug ports
echo -e "${YELLOW}🔍 Checking for remaining debug ports...${NC}"
for port in 9222 9223 9224 9225 9226 9227 9228 9229; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️ Port $port is still in use${NC}"
        lsof -Pi :$port -sTCP:LISTEN || true
    fi
done

echo -e "${GREEN}✅ Chrome debugging cleanup completed${NC}"
echo -e "${BLUE}💡 You can now safely start Chrome debugging again${NC}"

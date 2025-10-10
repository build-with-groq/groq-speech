#!/bin/bash

echo "🚀 Debug Script - Testing Frontend Startup"
echo "=========================================="

# Set verbose mode
VERBOSE=true
LOG_FILE="logs/debug-$(date +%Y%m%d-%H%M%S).log"
mkdir -p logs

echo "📝 Debug log will be saved to: $LOG_FILE"

# Test frontend startup
echo "🔍 Testing frontend startup..."
cd examples/groq-speech-ui

echo "📁 Current directory: $(pwd)"
echo "📦 Checking if package.json exists: $(ls -la package.json 2>/dev/null || echo 'NOT FOUND')"

echo "🚀 Starting frontend with verbose logging..."
NEXT_PUBLIC_VERBOSE=true NEXT_PUBLIC_DEBUG=true NEXT_PUBLIC_LOG_LEVEL=DEBUG npm run dev:https 2>&1 | while IFS= read -r line; do
    echo -e "${GREEN}[FRONTEND]${NC} $line"
    echo "[FRONTEND] $line" >> "$LOG_FILE"
done &
FRONTEND_PID=$!

echo "🆔 Frontend PID: $FRONTEND_PID"

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -s -k https://localhost:3443 > /dev/null 2>&1; then
        echo "✅ Frontend ready at https://localhost:3443"
        break
    fi
    echo "⏳ Attempt $i/30 - waiting..."
    sleep 1
done

echo "🔍 Frontend process status:"
ps aux | grep -E "(npm.*dev|node.*https)" | grep -v grep

echo "📄 Debug log content:"
cat "$LOG_FILE"

echo "🧹 Cleaning up..."
kill $FRONTEND_PID 2>/dev/null || true
cd ../..

echo "✅ Debug script completed"

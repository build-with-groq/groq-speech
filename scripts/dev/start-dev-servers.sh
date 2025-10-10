#!/bin/bash
# Script to start development servers without debugging to avoid Chrome conflicts

echo "🚀 Starting development servers (no debugging)..."

# Function to cleanup on exit
cleanup() {
    echo "🛑 Stopping servers..."
    kill $API_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start API server
echo "📡 Starting API server..."
cd /Users/srajaram/Work/sreeni-code/groq-speech
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000 --reload &
API_PID=$!

# Wait a moment for API to start
sleep 3

# Start Next.js frontend
echo "🌐 Starting Next.js frontend..."
cd /Users/srajaram/Work/sreeni-code/groq-speech/examples/groq-speech-ui
npm run dev &
FRONTEND_PID=$!

echo "✅ Servers started!"
echo "📡 API Server: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for both processes
wait $API_PID $FRONTEND_PID
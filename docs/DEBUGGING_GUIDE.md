# Safe Debugging Guide

## Chrome Crash Fix - Safe Debugging Options

The Chrome crash issue has been resolved by providing multiple safe debugging approaches that avoid Chrome conflicts.

## 🚀 Quick Start (Recommended)

### Option 1: Manual Server Start (Safest)
```bash
# Start both servers without debugging
./start-dev-servers.sh

# Then open browser manually to http://localhost:3000
```

### Option 2: API-Only Debugging (Most Stable)
1. Select **"Debug API Server Only (Recommended)"** from debug dropdown
2. Press F5 to start API debugging
3. Open terminal and run: `cd examples/groq-speech-ui && npm run dev`
4. Open browser to http://localhost:3000

### Option 3: Full Stack Debugging (No Chrome)
1. Select **"Debug Full Stack (API + Next.js - No Chrome)"** from debug dropdown
2. Press F5 to start both API and Next.js debugging
3. Open browser manually to http://localhost:3000

## 🔧 Debugging Configurations (In Order of Safety)

### 1. **Debug API Server Only (Recommended)** ⭐
- **What it debugs**: Python API server only
- **Chrome usage**: None
- **Stability**: Highest
- **Use case**: Debug WebSocket issues, API endpoints

### 2. **Debug Full Stack (API + Next.js - No Chrome)** ⭐
- **What it debugs**: Python API + Next.js server-side
- **Chrome usage**: None
- **Stability**: High
- **Use case**: Full backend debugging

### 3. **Next.js: debug server-only (No Chrome)**
- **What it debugs**: Next.js server-side only
- **Chrome usage**: None
- **Stability**: High
- **Use case**: Next.js API routes, server components

### 4. **Debug Full Stack (API + Next.js)** (Use with caution)
- **What it debugs**: Python API + Next.js + Chrome
- **Chrome usage**: Yes
- **Stability**: Medium
- **Use case**: Full stack debugging with browser

## 🐛 Setting Breakpoints

### For WebSocket Issues (Most Important)
1. **Set breakpoints in `api/server.py`**:
   - Line 636: `elif message_type == "audio_data":`
   - Line 1017: `async def handle_file_recognition`
   - Line 1183: `if enable_diarization:`

2. **Set breakpoints in `groq_speech/speech_recognizer.py`**:
   - Line 903: `def recognize_audio_data_chunked`
   - Line 903: `def recognize_audio_data`

### For Frontend Issues
1. **Set breakpoints in Next.js server-side code**:
   - API routes in `pages/api/` or `app/api/`
   - Server components

2. **For client-side debugging** (if needed):
   - Use browser DevTools directly
   - Set breakpoints in browser console

## 🔍 Testing the WebSocket Fix

1. **Start debugging** with "Debug API Server Only (Recommended)"
2. **Set breakpoints** in the WebSocket handler
3. **Open browser** to http://localhost:3000
4. **Try "Single Microphone"** mode
5. **Breakpoints should hit** in the API server

## 🚨 If Chrome Still Crashes

1. **Run cleanup script**:
   ```bash
   ./cleanup-debug-profiles.sh
   ```

2. **Use manual approach**:
   ```bash
   ./start-dev-servers.sh
   ```

3. **Use API-only debugging**:
   - Select "Debug API Server Only (Recommended)"
   - Start frontend manually

## 📝 Debugging Tips

- **Start with API-only debugging** to isolate WebSocket issues
- **Use browser DevTools** for frontend debugging instead of VS Code Chrome debugging
- **Check terminal logs** for detailed error information
- **Set breakpoints in WebSocket handlers** to trace the audio data flow

## ✅ Expected Behavior

- **API server starts** without Chrome conflicts
- **Breakpoints hit** in WebSocket handlers
- **Audio data flows** from frontend to API
- **WebSocket connection** remains stable
- **No Chrome crashes** or unexpected quits

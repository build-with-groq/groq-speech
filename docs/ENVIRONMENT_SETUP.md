# Environment Setup Guide

> **⚠️ Note**: This setup guide is for demonstrative and development purposes.

This document explains the environment variable configuration for the Groq Speech Solution project.

## 📋 Overview

The project uses **two separate environment files** for better isolation and security:

### **`.env.api` - Python/API Configuration**
- **Location**: Project root (`/groq-speech/.env.api`)
- **Used by**: 
  - Core Solution (`groq_speech/`)
  - CLI Demo (`examples/speech_demo.py`)
  - API Server (`api/server.py`)
- **Purpose**: Backend configuration, API keys, processing settings

### **`.env.ui` - Next.js UI Configuration**  
- **Location**: Project root (`/groq-speech/.env.ui`)
- **Used by**: 
  - Web UI (`examples/groq-speech-ui/`)
- **Purpose**: Frontend configuration, API connection, UI settings

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
# Run setup script from project root
./setup.sh
```

This automatically:
1. Creates `.env.api` from `.env.api.template`
2. Creates `.env.ui` from `.env.ui.template`
3. Sets up Python virtual environment
4. Installs all dependencies

### Option 2: Manual Setup

```bash
# Copy templates
cp .env.api.template .env.api
cp .env.ui.template .env.ui

# Edit with your keys
nano .env.api  # Add GROQ_API_KEY and HF_TOKEN
```

## 📝 Configuration Files

### `.env.api` - Backend Configuration

```bash
# ============================================
# REQUIRED: API Credentials
# ============================================
GROQ_API_KEY=your_groq_api_key_here          # Get from: https://console.groq.com/keys
HF_TOKEN=your_huggingface_token_here         # Get from: https://huggingface.co/settings/tokens

# ============================================
# OPTIONAL: API Configuration
# ============================================
GROQ_API_BASE=https://api.groq.com/openai/v1
GROQ_MODEL_ID=whisper-large-v3
GROQ_TEMPERATURE=0.0
GROQ_RESPONSE_FORMAT=verbose_json

# Logging
GROQ_VERBOSE=false
GROQ_LOG_LEVEL=INFO

# ============================================
# OPTIONAL: Audio Processing
# ============================================
AUDIO_SAMPLE_RATE=16000
AUDIO_CHANNELS=1
MAX_AUDIO_FILE_SIZE=25000000

# ============================================
# OPTIONAL: Diarization Settings
# ============================================
DIARIZATION_MIN_SEGMENT_DURATION=2.0
DIARIZATION_SILENCE_THRESHOLD=0.8
DIARIZATION_MAX_SEGMENTS_PER_CHUNK=8
DIARIZATION_CHUNK_STRATEGY=adaptive
DIARIZATION_MAX_SPEAKERS=5

# ============================================
# OPTIONAL: Server Configuration
# ============================================
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=1
API_LOG_LEVEL=info
LOG_LEVEL=INFO
ENVIRONMENT=development
```

### `.env.ui` - Frontend Configuration

```bash
# ============================================
# REQUIRED: API Connection
# ============================================
NEXT_PUBLIC_API_URL=http://localhost:8000

# ============================================
# OPTIONAL: UI Configuration
# ============================================
NEXT_PUBLIC_FRONTEND_URL=http://localhost:3000

# Debugging
NEXT_PUBLIC_VERBOSE=false
NEXT_PUBLIC_DEBUG=false

# Next.js Configuration
NODE_ENV=development
NEXT_TELEMETRY_DISABLED=1
```

## 🐳 Docker Deployment

For Docker deployments, environment files are copied to `deployment/docker/`:

```bash
# Automated setup
./deployment/docker/setup-env.sh

# Manual setup
cp .env.api.template deployment/docker/.env.api
cp .env.ui.template deployment/docker/.env.ui

# Edit deployment files
nano deployment/docker/.env.api
nano deployment/docker/.env.ui
```

Docker Compose mounts these files:
- API container: `deployment/docker/.env.api`
- UI container: `deployment/docker/.env.ui`

## 🔐 Security Best Practices

### ✅ DO:
- ✅ Keep `.env.api` and `.env.ui` in `.gitignore`
- ✅ Use `.env.api.template` and `.env.ui.template` as examples (tracked in git)
- ✅ Store actual API keys only in `.env.api` (never in UI files)
- ✅ Use environment-specific files for different deployments

### ❌ DON'T:
- ❌ Never commit actual `.env.api` or `.env.ui` files to git
- ❌ Never put API keys in frontend environment files
- ❌ Never share `.env.api` files publicly
- ❌ Never hardcode API keys in code

## 📍 File Locations

### Local Development
```
groq-speech/
├── .env.api              # Python/API (gitignored)
├── .env.api.template     # Template (in git)
├── .env.ui               # Next.js UI (gitignored)
├── .env.ui.template      # Template (in git)
├── .venv/                # Python virtual environment
├── groq_speech/          # Uses .env.api
├── api/                  # Uses .env.api
└── examples/
    ├── speech_demo.py    # Uses .env.api
    └── groq-speech-ui/   # Uses .env.ui (via next.config.ts)
```

### Docker Deployment
```
groq-speech/
├── deployment/docker/
│   ├── .env.api          # Copied from root template (gitignored)
│   ├── .env.ui           # Copied from root template (gitignored)
│   └── docker-compose.yml  # Mounts these files
```

## 🔄 Migration from Old Structure

If you have an old `.env` file:

```bash
# Your old .env is backed up as .env.backup
# Keys are already in .env.api (renamed from .env)

# If you need to migrate manually:
# 1. Copy API-related variables to .env.api
# 2. Copy UI-related variables to .env.ui
# 3. Delete old .env file
```

## 🆘 Troubleshooting

### Issue: "GROQ_API_KEY not found"
```bash
# Check file exists
ls -la .env.api

# Verify content
cat .env.api | grep GROQ_API_KEY

# Ensure not using placeholder
grep "your_groq_api_key_here" .env.api  # Should return nothing
```

### Issue: "Module not found" in Python
```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Verify environment is loaded
python -c "import os; print('GROQ_API_KEY:', 'SET' if os.getenv('GROQ_API_KEY') else 'NOT SET')"
```

### Issue: UI can't connect to API
```bash
# Check .env.ui has correct API URL
cat .env.ui | grep NEXT_PUBLIC_API_URL

# For local development, should be:
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📚 Related Documentation

- [Main README](README.md) - Quick start guide
- [QUICKSTART.md](QUICKSTART.md) - Step-by-step setup
- [Deployment Guide](deployment/README.md) - Production deployment
- [Docker README](deployment/docker/README.md) - Docker-specific setup

---

**Last Updated:** October 2025  
**Version:** 2.0 (Separate .env.api and .env.ui structure)

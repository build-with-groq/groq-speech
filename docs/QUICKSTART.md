# Quick Start Guide

> **⚠️ Disclaimer**: This is a **demonstrative solution** for educational purposes. Not intended for production use without additional hardening and testing.

This guide will help you get the Groq Speech Solution up and running in minutes.

## 📋 Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed ([Download](https://www.python.org/downloads/))
- **Node.js 18+** installed ([Download](https://nodejs.org/))
- **Groq API Key** ([Get one here](https://console.groq.com/keys))
- **Hugging Face Token** (optional, for speaker diarization - [Get one here](https://huggingface.co/settings/tokens))

## ⚡ Quick Setup (2 Steps)

### Step 1: Run Setup Script

```bash
# Clone and navigate to the repository
git clone <repository-url>
cd groq-speech

# Run the automated setup script
./setup.sh
```

This will automatically:
- ✅ Create Python virtual environment (`.venv/`)
- ✅ Install all Python dependencies
- ✅ Install Node.js dependencies
- ✅ Create `.env.api` and `.env.ui` configuration files

### Step 2: Configure API Keys

Edit the `.env.api` file that was created:

```bash
# Open .env.api in your favorite editor
nano .env.api  # or vim, code, etc.
```

Add your API keys:
```env
GROQ_API_KEY=your_actual_groq_api_key_here
HF_TOKEN=your_huggingface_token_here  # Optional, for diarization
```

**Note:** `.env.ui` defaults should work for local development.

## 🚀 Usage Examples

### 1. CLI Demo (Speech Recognition)

```bash
# Activate virtual environment
source venv/bin/activate

# Transcribe an audio file
python examples/speech_demo.py --file examples/test_audio.wav

# With speaker diarization
python examples/speech_demo.py --file examples/test_audio.wav --diarize

# Live microphone input
python examples/speech_demo.py --microphone-mode single
```

### 2. Web Interface

**Terminal 1 - Start API Server:**
```bash
source venv/bin/activate
cd api
python server.py
```

**Terminal 2 - Start Web UI:**
```bash
cd examples/groq-speech-ui
npm run dev
```

Then open [http://localhost:3000](http://localhost:3000) in your browser.

## 📁 Project Structure

```
groq-speech/
├── venv/                    # Python virtual environment
├── groq_speech/             # Core Solution
├── api/                     # FastAPI server
├── examples/
│   ├── speech_demo.py      # CLI demo
│   └── groq-speech-ui/     # Web UI
├── .env                     # Your API keys (create this)
├── env.example             # Environment template
├── setup.sh                # Automated setup script
└── README.md               # Full documentation
```

## 🔧 Common Commands

### Python Environment

```bash
# Activate virtual environment
source .venv/bin/activate

# Deactivate when done
deactivate

# Install new Python packages
pip install package_name
```

### Web UI

```bash
cd examples/groq-speech-ui

# Development mode
npm run dev

# Production build
npm run build
npm start
```

## 🆘 Troubleshooting

### Issue: "Module not found" error

**Solution:** Make sure you've activated the virtual environment:
```bash
source .venv/bin/activate
```

### Issue: "GROQ_API_KEY not found"

**Solution:** Check that `.env.api` file exists and contains your API key:
```bash
cat .env.api  # Should show GROQ_API_KEY=...
```

### Issue: Node.js packages not found

**Solution:** Reinstall Node.js dependencies:
```bash
cd examples/groq-speech-ui
npm install
```

### Issue: PyAudio installation fails

**Solution:** Install system dependencies first:

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**Ubuntu/Debian:**
```bash
sudo apt-get install portaudio19-dev
pip install pyaudio
```

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

## 📚 Next Steps

- Read the [Full Documentation](README.md)
- Explore [API Reference](groq_speech/API_REFERENCE.md)
- Check [Architecture Guide](docs/ARCHITECTURE.md)
- Review [Examples](examples/)

## 💡 Tips

1. **Always activate the virtual environment** before running Python commands
2. **Keep your `.env` file secure** - never commit it to version control
3. **For diarization features**, you must configure `HF_TOKEN` and accept the Pyannote.audio license
4. **Use `--verbose` flag** for debugging: `python examples/speech_demo.py --file audio.wav --verbose`

---

**Need help?** Check the [README.md](README.md) or create an issue on GitHub.

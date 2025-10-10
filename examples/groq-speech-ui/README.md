# Groq Speech Recognition Demo

A comprehensive Next.js application that demonstrates real-time speech transcription and translation using the Groq Speech API. This application provides both single-shot and continuous recognition modes with detailed performance metrics and visualizations.

## Features

### 🎤 Speech Recognition
- **Single Shot Mode**: Record audio and get immediate transcription/translation
- **Continuous Mode**: Real-time streaming recognition with WebSocket support
- **Multiple Languages**: Support for 10+ languages including English, German, French, Spanish, etc.
- **Translation**: Convert speech to English text from any supported language

### 📊 Performance Metrics
- **Real-time Timing**: Track microphone capture, API call, and response processing times
- **Visual Charts**: Interactive charts showing performance breakdown and trends
- **Success Rates**: Monitor recognition success and failure rates
- **Historical Data**: View performance metrics over time

### 🎨 User Interface
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Modern UI**: Clean, intuitive interface with Tailwind CSS styling
- **Real-time Feedback**: Visual indicators for recording, processing, and results
- **Export Functionality**: Download results as JSON files

### 🔧 Configuration
- **API Key Management**: Secure storage and management of Groq API keys
- **Mock Mode**: Demo mode for testing without real API calls
- **Environment Variables**: Configurable API endpoints and settings

## Technology Stack

- **Frontend**: Next.js 14, React 18, TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **Audio Processing**: Web Audio API, MediaRecorder API
- **Backend Integration**: Groq Speech API

## Getting Started

### Prerequisites

- Node.js 20+ or 22
- npm or yarn
- Groq API key (optional for mock mode)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/build-with-groq/groq-speech
   cd groq-speech/examples/groq-speech-ui
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start the development server**
   ```bash
   npm run dev
   ```

4. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

### Configuration

#### Using Real Groq API

1. Get your API key from the [Groq Console](https://console.groq.com/)
2. Click the "Settings" button in the app
3. Enter your API key and save
4. Disable "Use Mock API" option

#### Using Mock API (Demo Mode)

1. Enable "Use Mock API" in the settings
2. No API key required
3. Simulates real API responses for demonstration

## Usage

### Single Shot Recognition

1. Select "Single Shot" mode
2. Choose operation type (Transcription or Translation)
3. Select your language
4. Click "Start Recording"
5. Speak into your microphone
6. Click "Stop Recording" when done
7. View results and performance metrics

### Continuous Recognition

1. Select "Continuous" mode
2. Choose operation type and language
3. Click "Start Recording"
4. Speak continuously - the system will:
   - Detect silence periods automatically (3-second threshold)
   - Process and display results when silence is detected
   - Continue listening for new audio after processing
   - Show real-time audio level and status indicators
5. Click "Stop Recording" to end (processes any remaining audio)

### Performance Metrics

1. Click "Show Metrics" to view detailed performance data
2. View timing breakdown charts
3. Monitor success rates and response times
4. Export data for analysis

## API Integration

The application integrates with the Groq Speech API backend through REST endpoints:

- **REST API**: For all recognition and translation operations
- **Audio Processing**: Converts audio to appropriate formats for API transmission
- **Client-Side VAD**: Voice Activity Detection runs in the browser for real-time performance

### API Endpoints

- `POST /api/v1/recognize` - File transcription (base64-encoded audio)
- `POST /api/v1/translate` - File translation (base64-encoded audio)
- `POST /api/v1/recognize-microphone` - Single microphone recording (Float32Array)
- `POST /api/v1/recognize-microphone-continuous` - Continuous microphone with chunking (Float32Array)
- `GET /api/v1/device-info` - CPU/GPU device information for diarization
- `GET /health` - Backend health check
- `GET /api/v1/models` - Available Groq models
- `GET /api/v1/languages` - Supported languages

## Performance Features

### Timing Metrics
- **Microphone Capture**: Time to capture audio from microphone
- **API Call**: Time for Groq API to process and respond
- **Response Processing**: Time to parse and display results
- **Total Time**: End-to-end processing time

### Visualizations
- **Pie Charts**: Timing breakdown percentages
- **Bar Charts**: Success/failure distribution
- **Line Charts**: Performance trends over time
- **Real-time Updates**: Live metric updates during recognition

## Voice Activity Detection (VAD)

The continuous mode uses client-side Voice Activity Detection for optimal performance:

### Key Features
- **3-Second Silence Threshold**: Processes audio chunks after detecting 3 seconds of silence
- **Real-Time Audio Level Monitoring**: Visual feedback shows current audio levels
- **Intelligent Silence Detection**: Distinguishes between conversation pauses (<3s) and actual silence
- **Background Noise Filtering**: Uses adaptive thresholds to prevent false triggers
- **Automatic Buffer Management**: Clears processed audio to prevent duplicates

### Silence Detection Thresholds
- **Normal Recording**: RMS > 0.003, Max > 0.01 (sensitive for speech detection)
- **Silence Mode**: RMS > 0.02, Max > 0.05 (higher threshold to filter background noise)
- **Audio Content Validation**: RMS ≥ 0.015 (minimum for actual speech content)

### Continuous Mode Behavior
1. **Start Recording** → Begin accumulating audio
2. **Detect Audio** → Monitor RMS levels and display status
3. **Detect Silence** → Wait for 3 seconds of continuous silence
4. **Process Chunk** → Send audio to API, clear buffer, enter silence mode
5. **Wait for New Audio** → Stay in silence mode until real audio detected
6. **Repeat** → Continue cycle until "Stop Recording"

## File Structure

```
src/
├── app/                    # Next.js app directory
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Main page component
│   └── globals.css        # Global styles
├── components/             # React components
│   ├── EnhancedSpeechDemo.tsx  # Main demo component
│   ├── PerformanceMetrics.tsx  # Performance charts
│   └── DebugPanel.tsx         # Debug information
├── lib/                   # Utility libraries
│   ├── audio-recorder.ts        # Standard audio recording
│   ├── continuous-audio-recorder.ts  # VAD-based continuous recording
│   ├── client-vad-service.ts   # Client-side VAD implementation
│   ├── audio-converter.ts      # Audio format conversion
│   ├── groq-api.ts            # API client
│   └── frontend-logger.ts     # Logging utilities
└── types/                 # TypeScript type definitions
    └── index.ts           # Application types
```

## Development

### Running in Development Mode

```bash
npm run dev
```

### Building for Production

```bash
npm run build
npm start
```

### Code Quality

```bash
npm run lint
npm run type-check
```

## Environment Variables

The UI uses the root `.env.ui` file for configuration. For local development overrides, create a `.env.local` file:

```env
# API Connection (required)
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Debugging
NEXT_PUBLIC_VERBOSE=true
NEXT_PUBLIC_DEBUG=true
```

**Note:** API keys are configured in the backend (root `.env.api`), not in the UI.

## Troubleshooting

### Microphone Access Issues

1. Ensure your browser has microphone permissions
2. Check that your microphone is working in other applications
3. Try refreshing the page and granting permissions again

### API Connection Issues

1. Verify your Groq API key is correct
2. Check your internet connection
3. Ensure the API endpoint is accessible
4. Try using mock mode for testing

### Performance Issues

1. Check browser console for errors
2. Ensure you have sufficient system resources
3. Try closing other applications using microphone
4. Check network latency to Groq API

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the Groq API documentation
- Open an issue on GitHub

## Acknowledgments

- Groq for providing the Speech API
- Next.js team for the excellent framework
- Recharts for the charting library
- Lucide for the beautiful icons

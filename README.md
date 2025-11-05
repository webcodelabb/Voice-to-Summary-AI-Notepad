---
title: Voice-to-Summary AI Notepad
emoji: 🎙️
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.1.1
app_file: app.py
pinned: false
license: mit

Upload audio or record with your microphone to get transcriptions and concise summaries.

Set the API_URL environment variable in your Space settings if you want this frontend
to call a remote FastAPI backend for transcription/summarization. If `API_URL` is empty,
the app will use a local dummy summarizer for testing.

Check the Spaces docs: https://huggingface.co/docs/hub/spaces
# Voice-to-Summary AI Notepad Backend

A production-ready FastAPI backend for audio transcription and AI summarization. Upload audio files, get transcriptions, and receive intelligent summaries.

##  Features

- **Audio Transcription**: Support for MP3, WAV, and raw audio files
- **AI Summarization**: Intelligent text summarization using OpenAI GPT or Hugging Face models
- **Modular Architecture**: Easy to extend and customize
- **Production Ready**: Async FastAPI with proper error handling
- **Flexible Model Support**: Switch between OpenAI API and local models via environment variables

##  Project Structure

```
/voice-summary-api/
├── app/
│   ├── main.py                  # FastAPI entry point
│   ├── routes/
│   │   ├── transcribe.py        # POST /transcribe - accepts audio file
│   │   └── summarize.py         # POST /summarize - accepts transcript
│   ├── services/
│   │   ├── whisper_service.py   # Handles transcription (local or API)
│   │   └── llm_service.py       # Handles LLM summarization
│   ├── schemas/
│   │   └── summary.py           # Request/response Pydantic schemas
│   └── utils/
│       └── audio_utils.py       # Validate and preprocess audio
├── requirements.txt
├── README.md
└── .env.example
```

##  Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/webcodelabb/Voice-to-Summary-AI-Notepad.git
   cd Voice-to-Summary-AI-Notepad
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Run the server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

##  Configuration

Create a `.env` file with the following variables:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Whisper Configuration
WHISPER_MODEL=base  # Options: tiny, base, small, medium, large
USE_OPENAI_WHISPER=false  # Set to true to use OpenAI Whisper API instead of local

# LLM Configuration
LLM_PROVIDER=openai  # Options: openai, huggingface
HUGGINGFACE_MODEL=facebook/bart-large-cnn

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

##  API Endpoints

### 1. Transcribe Audio
**POST** `/transcribe`

Upload an audio file to get its transcription.

**Request:**
- Content-Type: `multipart/form-data`
- Body: Audio file (MP3, WAV, or raw audio)

**Response:**
```json
{
  "transcript": "This is the transcribed text from the audio file.",
  "confidence": 0.95,
  "language": "en"
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/transcribe" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@audio.mp3"
```

### 2. Summarize Text
**POST** `/summarize`

Send transcribed text to get an AI-generated summary.

**Request:**
```json
{
  "text": "Your transcribed text here...",
  "max_length": 150,
  "style": "bullet_points"
}
```

**Response:**
```json
{
  "summary": "• Key point 1\n• Key point 2\n• Action items",
  "word_count": 45,
  "original_length": 250
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Your transcribed text here...",
    "max_length": 150,
    "style": "bullet_points"
  }'
```

##  Complete Workflow

1. **Upload audio file** → Get transcription
2. **Send transcription** → Get AI summary
3. **Use summary** → Integrate with your frontend

## 🧠 Model Options

### Transcription Models
- **Local Whisper**: Free, runs offline, good quality
- **OpenAI Whisper API**: Higher accuracy, requires API key

### Summarization Models
- **OpenAI GPT-4**: Best quality, requires API key
- **Hugging Face BART**: Free, runs locally, good quality

## Authentication

This backend is designed to be easily extended with authentication. The `/auth/` module is left as a placeholder for future JWT or OAuth implementation.

## 🚀 Production Deployment

1. **Environment Setup**
   ```bash
   export OPENAI_API_KEY=your_key
   export WHISPER_MODEL=base
   export LLM_PROVIDER=openai
   ```

2. **Run with Gunicorn**
   ```bash
   gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
   ```

3. **Docker Deployment**
   ```bash
   docker build -t voice-summary-api .
   docker run -p 8000:8000 voice-summary-api
   ```

## 🧪 Testing

Test the API endpoints:

```bash
# Test transcription
curl -X POST "http://localhost:8000/transcribe" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_audio.mp3"

# Test summarization
curl -X POST "http://localhost:8000/summarize" \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test transcript for summarization.", "max_length": 50}'
```

## 🔧 Customization

### Adding New Models
1. Extend `WhisperService` in `app/services/whisper_service.py`
2. Extend `LLMService` in `app/services/llm_service.py`
3. Add new environment variables for configuration

### Adding Authentication
1. Create `app/auth/` directory
2. Implement JWT or OAuth middleware
3. Add authentication decorators to routes

### Frontend Integration
This backend is designed to work with any frontend:
- React/Vue/Svelte web apps
- Mobile apps (React Native, Flutter)
- Desktop applications

## 📝 License

MIT License - feel free to use this as a starting point for your projects!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---
**Built with ❤️ for developers who want to build amazing voice-to-text applications!** Fixing coauthor format


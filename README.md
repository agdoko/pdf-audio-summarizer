# PDF Audio Summarizer 🎧

Convert scientific PDFs into professional audio summaries using Claude AI and ElevenLabs text-to-speech.

## 🚀 Quick Start (5 minutes)

### 1. Clone and Setup
```bash
git clone https://github.com/agdoko/pdf-audio-summarizer.git
cd pdf-audio-summarizer

# Set Python version (resolves uv environment conflicts)
echo "3.12.3" > .python-version

# Install dependencies with uv (faster than pip)
uv sync
```

### 2. Configure API Keys
```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API keys:
# ANTHROPIC_API_KEY=your_claude_api_key
# ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

### 3. Run Application
```bash
# Start Streamlit app
uv run streamlit run streamlit_app.py

# App opens at http://localhost:8501
```

## 🎯 Core Features

- **PDF Processing**: Extract text from scientific papers with fallback methods
- **AI Summarization**: Claude Sonnet 4 generates 6-minute spoken summaries  
- **Professional TTS**: ElevenLabs Rachel voice for clear, engaging narration
- **Streamlit UI**: Clean, responsive web interface with progress tracking
- **Error Handling**: Comprehensive error recovery and user feedback

## 🏗️ Architecture Overview

```
PDF Upload → Text Extraction → Claude Summarization → ElevenLabs TTS → Audio Download
     ↓              ↓                    ↓                  ↓              ↓
  Streamlit    pdfplumber/PyPDF2    Claude Sonnet 4    ElevenLabs API   MP3 File
```

### Key Design Patterns

**API Integration**: Async/await patterns with proper error handling and retry logic
**File Processing**: Multiple extraction methods with graceful fallback
**User Experience**: Real-time progress tracking and clear status indicators
**Cost Optimization**: Token management and intelligent content truncation

## 🔧 Technical Details

### Dependencies Management
- **Package Manager**: `uv` for fast, reliable dependency resolution
- **Python Version**: 3.12+ for optimal performance and type hints
- **Core Libraries**: Streamlit, Anthropic, ElevenLabs, pdfplumber

### API Integration Patterns
```python
# Async API calls with error handling
async def generate_summary(self, text: str) -> str:
    try:
        response = await asyncio.to_thread(self._make_sync_api_call, prompt)
        return response.content[0].text.strip()
    except anthropic.APIError as e:
        logger.error(f"Claude API error: {e}")
        raise
```

### Configuration Management
- **Environment Variables**: Secure API key storage
- **Type Safety**: Pydantic validation for all settings
- **Fallback Values**: Sensible defaults for all configuration options

## 📊 Performance & Costs

| Component | Processing Time | Estimated Cost |
|-----------|----------------|----------------|
| PDF Text Extraction | ~5 seconds | Free |
| Claude Sonnet 4 | ~30-60 seconds | $0.15-0.30 |
| ElevenLabs TTS | ~30-45 seconds | $0.30 |
| **Total Pipeline** | **~2-3 minutes** | **~$0.45-0.60** |

## 🚀 Deployment Options

### Streamlit Community Cloud (Recommended)
1. Push code to GitHub repository
2. Connect repository to [share.streamlit.io](https://share.streamlit.io)
3. Add API keys in Streamlit Cloud secrets
4. Deploy automatically on every push

### Local Development
```bash
# Development mode with auto-reload
uv run streamlit run streamlit_app.py --reload

# Production mode
uv run streamlit run streamlit_app.py --server.port 8080
```

### Docker Deployment
```bash
# Build image
docker build -t pdf-audio-summarizer .

# Run container
docker run -p 8501:8501 --env-file .env pdf-audio-summarizer
```

## 🧪 Testing & Quality

```bash
# Run tests
uv run pytest

# Code formatting
uv run black .
uv run isort .

# Type checking
uv run mypy utils/ streamlit_app.py
```

## 🔐 Security & Best Practices

- **API Keys**: Never commit to repository, use environment variables
- **Input Validation**: File size limits, content validation, error boundaries
- **Logging**: Structured logging for monitoring and debugging
- **Resource Management**: Proper cleanup of temporary files and memory

## 💡 Interview Discussion Points

### System Design
- **Scalability**: How would you handle 1000+ concurrent users?
- **Reliability**: What happens when external APIs fail?
- **Cost Optimization**: How to reduce per-request costs?

### Technical Implementation
- **Async Patterns**: Why use asyncio for API calls?
- **Error Handling**: Strategy for graceful degradation
- **File Processing**: Multiple extraction methods and fallback logic

### Production Readiness
- **Monitoring**: What metrics would you track?
- **Deployment**: CI/CD pipeline and environment management
- **Security**: API key rotation and input sanitization

## 📈 Extension Ideas

- **Batch Processing**: Multiple PDFs in parallel
- **Voice Options**: Multiple TTS voices and languages
- **Content Types**: Support for research papers, reports, books
- **Integration**: Slack/Discord bots, API endpoints
- **Analytics**: Usage tracking and performance metrics

## 🛠️ Development Setup

### Environment Resolution
If you see uv environment warnings:
```bash
# Set explicit Python version
echo "3.12.3" > .python-version

# Clear any existing environments
uv clean

# Reinstall with correct Python
uv sync
```

### API Setup
1. **Claude API**: Get key from [console.anthropic.com](https://console.anthropic.com)
2. **ElevenLabs**: Get key from [elevenlabs.io](https://elevenlabs.io)
3. **Voice ID**: Default uses Rachel (clear, professional)

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

**Built for technical interviews and portfolio demonstration**  
*Showcasing production-ready API integration, async programming, and user experience design*
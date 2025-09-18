# Google Cloud Text-to-Speech Application

A comprehensive Text-to-Speech application built using the VIPER architecture pattern and Google Cloud Platform services. This application converts text and SSML to natural-sounding speech using Google's advanced AI models.

## 🏗️ Architecture

This application follows the **VIPER (View, Interactor, Presenter, Entity, Router)** architecture pattern for clean, testable, and maintainable code:

- **View**: Web interface and UI components
- **Interactor**: Business logic and AI service integrations
- **Presenter**: Data formatting and validation
- **Entity**: Data models and repositories
- **Router**: API endpoints and routing logic

## ✨ Features

- **Multiple Voice Types**: Standard, WaveNet, Neural2, News, and Studio voices
- **40+ Languages**: Support for major world languages
- **SSML Support**: Advanced speech control with Speech Synthesis Markup Language
- **Multiple Audio Formats**: MP3, WAV, OGG Opus support
- **Voice Customization**: Adjust pitch, speed, and gender
- **Cloud Storage**: Automatic audio file storage and retrieval
- **RESTful API**: Complete REST API with OpenAPI documentation
- **Web Interface**: Modern, responsive web interface
- **Real-time Processing**: Fast speech synthesis with Google Cloud Text-to-Speech
- **History Tracking**: User synthesis history and analytics

## 🚀 Quick Start

### Prerequisites

- Google Cloud Platform account
- Docker and Docker Compose
- gcloud CLI tool
- Python 3.11+

### CLI Installation (Recommended)

The fastest way to get started is using the command-line interface:

```bash
# Install CLI tool
./scripts/install-cli.sh

# Quick test
gcp-tts synthesize "Hello, world!" --output hello.mp3

# Get help
gcp-tts --help
```

### Local Development

1. **Clone the repository**
```bash
git clone <repository-url>
cd presentation
```

2. **Set up environment configuration**
```bash
# Copy and edit environment file
cp .env.example .env
nano .env

# The .env file is pre-configured with project credentials:
# - Staging Project: qwiklabs-gcp-01-59ed30a122ce
# - Production Project: qwiklabs-gcp-04-240a2b7a2b9f
# You can switch between environments as needed
```

3. **Set up Google Cloud credentials** (if needed)
```bash
# Authenticate with Google Cloud
gcloud auth login

# Set your project ID
export GOOGLE_CLOUD_PROJECT="qwiklabs-gcp-04-240a2b7a2b9f"

# Create and download service account key (if needed)
gcloud iam service-accounts create tts-api --display-name="TTS API Service Account"
gcloud iam service-accounts keys create ./credentials/service-account.json \
  --iam-account=tts-api@qwiklabs-gcp-04-240a2b7a2b9f.iam.gserviceaccount.com
```

4. **Run with Docker Compose**
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f tts-api

# Run tests
docker-compose --profile testing run test-runner

# Stop services
docker-compose down
```

5. **Access the application**
- Web Interface: http://localhost:8080
- API Documentation: http://localhost:8080/docs (if Swagger is enabled)
- Health Check: http://localhost:8080/health

### Cloud Deployment

1. **Make the deployment script executable**
```bash
chmod +x scripts/deploy.sh
```

2. **Deploy to Google Cloud**
```bash
# Set environment variables
export GOOGLE_CLOUD_PROJECT="your-project-id"
export VERTEX_AI_LOCATION="us-central1"

# Run deployment script
./scripts/deploy.sh
```

3. **Set up CI/CD with Cloud Build**
```bash
# Submit the build
gcloud builds submit --config infrastructure/cloudbuild/cloudbuild.yaml
```

## 📁 Project Structure

```
presentation/
├── src/                              # Source code following VIPER pattern
│   ├── view/                         # View Layer (UI)
│   │   ├── components/
│   │   └── web/
│   ├── interactor/                   # Interactor Layer (Business Logic)
│   │   ├── ai_services/
│   │   └── business_logic/
│   ├── presenter/                    # Presenter Layer (Data Formatting)
│   │   ├── formatters/
│   │   └── middleware/
│   ├── entity/                       # Entity Layer (Data Models)
│   │   ├── models/
│   │   └── repositories/
│   ├── router/                       # Router Layer (API Routing)
│   │   └── api_gateway/
│   └── shared/                       # Shared Components
│       ├── config/
│       └── utils/
├── docs/                             # Documentation
│   └── api/
├── config/                           # Configuration files
├── scripts/                          # Deployment and utility scripts
├── infrastructure/                   # Infrastructure as Code
│   ├── terraform/
│   └── cloudbuild/
├── tests/                            # Test suites
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── requirements.txt                  # Python dependencies
├── Dockerfile                        # Container definition
├── docker-compose.yaml              # Local development setup
└── README.md                         # This file
```

## 🔧 Usage Options

### Command Line Interface (CLI)

The `gcp-tts` CLI provides the easiest way to use the service:

```bash
# Basic text-to-speech
gcp-tts synthesize "Hello, world!"

# Custom voice and language
gcp-tts synthesize "Hola, mundo!" --language es-ES --voice es-ES-Neural2-A

# Process files
gcp-tts synthesize --file input.txt --output speech.mp3

# Batch processing
gcp-tts batch texts.csv --output-dir ./audio

# List available voices
gcp-tts voices --language en-US --type neural2
```

See [CLI Usage Guide](docs/CLI_USAGE.md) for complete documentation.

### REST API Endpoints

- `POST /api/v1/tts/synthesize` - Convert text to speech
- `POST /api/v1/tts/synthesize-ssml` - Convert SSML to speech
- `GET /api/v1/tts/voices` - Get available voices
- `GET /api/v1/tts/languages` - Get supported languages
- `GET /api/v1/tts/history/{user_id}` - Get user synthesis history
- `GET /health` - Health check endpoint

### Web Interface

Access the web interface at `http://localhost:8080` for a user-friendly GUI.

## 🔄 Development Workflow

### Running Tests
```bash
# Unit tests
python -m pytest tests/unit/ -v

# Integration tests
python -m pytest tests/integration/ -v

# End-to-end tests
python -m pytest tests/e2e/ -v

# All tests with coverage
python -m pytest tests/ --cov=src --cov-report=html
```

### Code Quality
```bash
# Format code
black src/
isort src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

### Local Development Server
```bash
# Install dependencies
pip install -r requirements.txt

# Run development server
python src/view/components/web_app.py
```

## 🌐 Environment Variables

### Required
- `GOOGLE_CLOUD_PROJECT` - Google Cloud Project ID
- `TTS_BUCKET_NAME` - Cloud Storage bucket for audio files
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to service account JSON

### Optional
- `VERTEX_AI_LOCATION` - GCP region (default: us-central1)
- `PORT` - Server port (default: 8080)
- `ENVIRONMENT` - Environment name (development/production)
- `REDIS_PASSWORD` - Redis password for caching

## 📊 Monitoring and Observability

The application includes comprehensive monitoring:

- **Health Checks**: Built-in health endpoints
- **Logging**: Structured logging with Google Cloud Logging
- **Metrics**: Prometheus metrics collection
- **Tracing**: Distributed tracing with Jaeger
- **Dashboards**: Grafana dashboards for visualization

## 🔒 Security

- **IAM**: Fine-grained Google Cloud IAM permissions
- **Service Accounts**: Dedicated service accounts for each component
- **Input Validation**: Comprehensive request validation
- **Rate Limiting**: API rate limiting and throttling
- **CORS**: Configurable CORS policies
- **Container Security**: Non-root container execution

## 🎨 Voice Customization

### Supported Parameters
- **Language**: 40+ languages and dialects
- **Voice Types**: Standard, WaveNet, Neural2, News, Studio
- **Gender**: Male, Female, Neutral
- **Speaking Rate**: 0.25x to 4.0x speed
- **Pitch**: -20 to +20 semitones
- **Audio Formats**: MP3, WAV, OGG Opus

### SSML Features
- Pauses and breaks
- Emphasis and prosody
- Phoneme pronunciation
- Audio insertion
- Voice switching

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:

1. Check the [API documentation](docs/api/openapi.yaml)
2. Review the [troubleshooting guide](docs/troubleshooting.md)
3. Open an issue on GitHub
4. Contact the development team

## 🔄 Version History

- **v1.0.0** - Initial release with VIPER architecture
- Features: Basic TTS, SSML support, multiple voices
- Cloud deployment with Google Cloud Platform
- Comprehensive API with OpenAPI documentation

---

Built with ❤️ using Google Cloud Platform and the VIPER architecture pattern.
# Google Cloud Text-to-Speech CLI Usage Guide

The `gcp-tts` CLI tool provides a command-line interface for Google Cloud Text-to-Speech services, built with the VIPER architecture pattern.

## Installation

### Quick Install
```bash
# Install from source
./scripts/install-cli.sh

# Or with virtual environment
./scripts/install-cli.sh --venv

# Or manually with pip
pip install -e .
```

### Requirements
- Python 3.8+
- Google Cloud Project with Text-to-Speech API enabled
- Valid Google Cloud credentials

## Configuration

### Environment Variables (.env file)

The CLI supports loading configuration from a `.env` file. Create a `.env` file in your project root:

```bash
# Copy the example file
cp .env.example .env

# Edit with your values
nano .env
```

Example `.env` file:
```bash
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=qwiklabs-gcp-04-240a2b7a2b9f
VERTEX_AI_LOCATION=us-central1
TTS_BUCKET_NAME=qwiklabs-gcp-04-240a2b7a2b9f-tts-audio

# Default TTS Settings
DEFAULT_LANGUAGE=en-US
DEFAULT_VOICE_GENDER=NEUTRAL
DEFAULT_AUDIO_ENCODING=MP3

# CLI Settings
CLI_VERBOSE=false
CLI_OUTPUT_DIR=./tts-output
CLI_WORKERS=3

# Environment Mode
ENVIRONMENT=production
```

### Multiple Environments

You can manage multiple environments using different .env files:

```bash
# Development
gcp-tts --env-file .env.dev synthesize "Development test"

# Staging
gcp-tts --env-file .env.staging synthesize "Staging test"

# Production
gcp-tts --env-file .env.prod synthesize "Production test"

# Or use environment flag
gcp-tts --environment staging synthesize "Auto-select staging project"
```

### Manual Environment Variables
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export TTS_BUCKET_NAME="your-project-tts-audio"
export VERTEX_AI_LOCATION="us-central1"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/credentials.json"
```

## Basic Usage

### Quick Start
```bash
# Basic text-to-speech
gcp-tts synthesize "Hello, world!"

# Check configuration
gcp-tts config

# Get help
gcp-tts --help
```

## Commands

### `synthesize` - Convert Text to Speech

Convert text or SSML to natural-sounding speech.

#### Basic Examples
```bash
# Simple text
gcp-tts synthesize "Hello, world!"

# Custom output file
gcp-tts synthesize "Hello, world!" --output greeting.mp3

# Different language and voice
gcp-tts synthesize "Hola, mundo!" --language es-ES --voice es-ES-Neural2-A

# Adjust speech parameters
gcp-tts synthesize "Fast speech" --speed 1.5 --pitch 2.0

# Process file
gcp-tts synthesize --file input.txt --output speech.mp3
```

#### SSML Examples
```bash
# Basic SSML
gcp-tts synthesize "<speak>Hello <break time='1s'/> World!</speak>" --ssml

# Advanced SSML with emphasis
gcp-tts synthesize --ssml --file advanced.ssml --voice en-US-Neural2-A
```

#### Audio Format Options
```bash
# High-quality WAV
gcp-tts synthesize "Test" --format LINEAR16 --output test.wav

# Compressed OGG
gcp-tts synthesize "Test" --format OGG_OPUS --output test.ogg

# Standard MP3 (default)
gcp-tts synthesize "Test" --format MP3 --output test.mp3
```

#### Full Syntax
```bash
gcp-tts synthesize [TEXT|--file FILE] [OPTIONS]

Options:
  --file, -f PATH           Read text from file
  --output, -o PATH         Output audio file path
  --language, -l TEXT       Language code (default: en-US)
  --voice TEXT              Specific voice name
  --gender [NEUTRAL|MALE|FEMALE]  Voice gender (default: NEUTRAL)
  --format [MP3|LINEAR16|OGG_OPUS]  Audio format (default: MP3)
  --speed FLOAT             Speaking rate 0.25-4.0 (default: 1.0)
  --pitch FLOAT             Pitch adjustment -20.0 to 20.0 (default: 0.0)
  --ssml                    Treat input as SSML
  --play                    Play audio after generation
  --verbose, -v             Enable verbose output
```

### `voices` - List Available Voices

Discover and filter available voices.

#### Examples
```bash
# List all voices
gcp-tts voices

# Filter by language
gcp-tts voices --language en-US

# Filter by voice type
gcp-tts voices --type neural2

# Filter by gender
gcp-tts voices --gender FEMALE

# JSON output
gcp-tts voices --language en-US --output-format json

# CSV output
gcp-tts voices --type wavenet --output-format csv
```

#### Voice Types
- **standard**: Basic quality voices
- **wavenet**: High-quality DeepMind voices
- **neural2**: Premium natural voices
- **news**: Broadcast-style voices
- **studio**: Ultra-premium voices

### `languages` - Supported Languages

List supported languages and regions.

```bash
# Table format (default)
gcp-tts languages

# JSON format
gcp-tts languages --output-format json
```

### `history` - User History

View synthesis history for a user.

```bash
# View history
gcp-tts history cli-user

# Limit results
gcp-tts history user123 --limit 5

# JSON output
gcp-tts history user123 --output-format json
```

### `batch` - Batch Processing

Process multiple texts efficiently.

#### Input Formats

**Text File (`.txt`)** - One text per line:
```
Hello, world!
This is the second line.
Another text to convert.
```

**CSV File (`.csv`)** - Structured data:
```csv
text,language,voice,output_name
"Hello, world!",en-US,en-US-Neural2-A,greeting
"Hola, mundo!",es-ES,es-ES-Neural2-B,spanish_greeting
```

**JSON File (`.json`)** - Full control:
```json
[
  {
    "text": "Hello, world!",
    "language": "en-US",
    "voice": "en-US-Neural2-A",
    "output_name": "greeting"
  },
  {
    "text": "Bonjour, monde!",
    "language": "fr-FR",
    "voice": "fr-FR-Neural2-A",
    "output_name": "french_greeting"
  }
]
```

#### Batch Examples
```bash
# Process text file
gcp-tts batch texts.txt

# Process CSV with custom settings
gcp-tts batch data.csv --output-dir ./audio --workers 5

# Process JSON with continue-on-error
gcp-tts batch batch.json --continue-on-error

# Auto-detect format
gcp-tts batch input.csv --language en-US --voice en-US-Neural2-A
```

### `convert-files` - Directory Processing

Convert all text files in a directory.

```bash
# Convert all .txt files
gcp-tts convert-files ./documents/

# Custom pattern and recursive
gcp-tts convert-files ./docs/ --pattern "*.md" --recursive

# Different language
gcp-tts convert-files ./spanish/ --language es-ES --voice es-ES-Neural2-A
```

### `process-text-file` - Long Document Processing

Process long text files with automatic chunking for documents over 5000 characters.

```bash
# Process long document
gcp-tts process-text-file book.txt

# Custom chunk size and voice
gcp-tts process-text-file document.txt --chunk-size 3000 --voice en-US-Neural2-A

# Combine chunks into single file
gcp-tts process-text-file article.md --combine-output --output-dir ./audio

# Preview chunks without processing
gcp-tts process-text-file large-doc.txt --preview

# Parallel processing with workers
gcp-tts process-text-file book.txt --workers 5 --output-dir ./audiobook
```

### `read-aloud` - Simple File Conversion

Quick conversion for files under 5000 characters.

```bash
# Simple file reading
gcp-tts read-aloud document.txt

# Custom voice and output
gcp-tts read-aloud article.md --voice en-US-Neural2-A --output article.mp3

# Adjust speech parameters
gcp-tts read-aloud text.txt --speed 1.2 --pitch 2.0
```

## Advanced Usage

### Voice Selection

#### List Neural2 voices for English (US)
```bash
gcp-tts voices --language en-US --type neural2
```

#### Use specific premium voice
```bash
gcp-tts synthesize "Premium quality speech" --voice en-US-Neural2-A
```

### SSML (Speech Synthesis Markup Language)

#### Basic SSML
```bash
gcp-tts synthesize '<speak>Hello <break time="1s"/> World!</speak>' --ssml
```

#### Advanced SSML file
Create `advanced.ssml`:
```xml
<speak>
  <prosody rate="slow" pitch="+2st">
    Welcome to our
    <emphasis level="strong">amazing</emphasis>
    text-to-speech service.
  </prosody>
  <break time="2s"/>
  <prosody rate="fast">
    This sentence is spoken quickly.
  </prosody>
</speak>
```

```bash
gcp-tts synthesize --file advanced.ssml --ssml --voice en-US-Neural2-A
```

### Batch Processing Workflows

#### 1. Prepare CSV data
```csv
text,language,voice,output_name
"Chapter 1: Introduction",en-US,en-US-Neural2-A,chapter1
"Chapter 2: Getting Started",en-US,en-US-Neural2-A,chapter2
"Capítulo 3: Configuración",es-ES,es-ES-Neural2-B,capitulo3
```

#### 2. Process with monitoring
```bash
gcp-tts batch chapters.csv --output-dir ./audiobook --workers 3 --verbose
```

#### 3. Check results
```bash
ls -la ./audiobook/
cat ./audiobook/batch_results.json
```

### Pipeline Integration

#### Shell scripting
```bash
#!/bin/bash
# Convert documentation to audio

echo "Converting README to speech..."
gcp-tts synthesize --file README.md --output readme.mp3 --verbose

echo "Converting all markdown files..."
gcp-tts convert-files ./docs/ --pattern "*.md" --output-dir ./audio-docs/

echo "Completed audio generation"
```

#### Python integration
```python
import subprocess
import json

# Generate speech via CLI
result = subprocess.run([
    'gcp-tts', 'synthesize', 'Hello from Python!',
    '--output', 'python_output.mp3',
    '--voice', 'en-US-Neural2-A'
], capture_output=True, text=True)

if result.returncode == 0:
    print("Speech generated successfully!")
else:
    print(f"Error: {result.stderr}")
```

## Output Management

### File Naming
- Default: `tts_output_{request_id}.{format}`
- Custom: Use `--output filename.ext`
- Batch: Use `output_name` field or auto-generated

### Directory Structure
```
./tts-output/           # Default output directory
├── tts_output_abc123.mp3
├── greeting.mp3        # Custom named
└── batch_output/       # Batch processing
    ├── chapter1.mp3
    ├── chapter2.mp3
    └── batch_results.json  # Processing log
```

## Error Handling

### Common Issues

#### Authentication
```bash
# Error: Authentication required
gcloud auth login
gcloud auth application-default login
```

#### Project Configuration
```bash
# Error: Project not set
export GOOGLE_CLOUD_PROJECT="your-project-id"
```

#### API Not Enabled
```bash
# Enable Text-to-Speech API
gcloud services enable texttospeech.googleapis.com
```

#### Quota Exceeded
```bash
# Check quotas in Cloud Console
# Wait or request quota increase
```

### Verbose Mode
```bash
# Enable detailed logging
gcp-tts synthesize "Debug mode" --verbose
```

### Batch Error Recovery
```bash
# Continue processing despite errors
gcp-tts batch problematic.csv --continue-on-error

# Check failed items
cat ./batch_output/batch_results.json | jq '.failed_items'
```

## Performance Tips

### Batch Processing
- Use 3-5 workers for optimal performance
- Enable `--continue-on-error` for large batches
- Monitor Cloud Storage quotas

### Voice Selection
- Neural2 voices: Highest quality, slower generation
- WaveNet voices: Good quality, balanced speed
- Standard voices: Fastest generation

### File Management
- Use MP3 for smaller files
- Use LINEAR16 (WAV) for highest quality
- Clean up old files regularly

## Examples Repository

### Basic Use Cases
```bash
# News article
gcp-tts synthesize --file news.txt --voice en-US-News-K --output news.mp3

# Audiobook chapter
gcp-tts synthesize --file chapter1.txt --voice en-US-Neural2-A --speed 0.9

# Multiple languages
gcp-tts synthesize "Hello" --language en-US --output en.mp3
gcp-tts synthesize "Hola" --language es-ES --output es.mp3
gcp-tts synthesize "Bonjour" --language fr-FR --output fr.mp3
```

### Production Workflows
```bash
# Podcast intro generation
gcp-tts synthesize "Welcome to Tech Talk Podcast" \
  --voice en-US-Studio-O --format LINEAR16 --output intro.wav

# Multi-language support system
gcp-tts batch multilingual.csv --workers 5 --output-dir ./localized/

# Documentation audio generation
find ./docs -name "*.md" -exec gcp-tts synthesize --file {} \
  --output "./audio-docs/{}.mp3" \;
```

## Troubleshooting

### Debug Steps
1. Check configuration: `gcp-tts config`
2. Verify authentication: `gcloud auth list`
3. Test basic synthesis: `gcp-tts synthesize "test"`
4. Enable verbose mode: `--verbose`
5. Check logs and error messages

### Getting Help
```bash
# General help
gcp-tts --help

# Command-specific help
gcp-tts synthesize --help
gcp-tts batch --help

# Version information
gcp-tts --version
```

For additional support, check the [GitHub repository](https://github.com/your-org/gcp-tts-cli) or open an issue.
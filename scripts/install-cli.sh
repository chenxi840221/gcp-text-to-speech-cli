#!/bin/bash

# Installation script for Google Cloud Text-to-Speech CLI
# Installs the CLI tool for easy command-line access

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.8+ is available
check_python() {
    log_info "Checking Python version..."

    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

        if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
            log_success "Python $PYTHON_VERSION found"
            PYTHON_CMD="python3"
        else
            log_error "Python 3.8+ is required. Found Python $PYTHON_VERSION"
            exit 1
        fi
    else
        log_error "Python 3 is not installed"
        exit 1
    fi
}

# Check if pip is available
check_pip() {
    log_info "Checking pip availability..."

    if command -v pip3 &> /dev/null; then
        log_success "pip3 found"
        PIP_CMD="pip3"
    elif $PYTHON_CMD -m pip --version &> /dev/null; then
        log_success "pip module found"
        PIP_CMD="$PYTHON_CMD -m pip"
    else
        log_error "pip is not available"
        exit 1
    fi
}

# Install the CLI application
install_cli() {
    log_info "Installing Google Cloud Text-to-Speech CLI..."

    # Create virtual environment (optional but recommended)
    if [ "$1" = "--venv" ]; then
        log_info "Creating virtual environment..."
        $PYTHON_CMD -m venv gcp-tts-env
        source gcp-tts-env/bin/activate
        PIP_CMD="pip"
        log_success "Virtual environment created and activated"
    fi

    # Install from current directory
    if [ -f "setup.py" ]; then
        log_info "Installing from source..."
        $PIP_CMD install -e .
    else
        log_error "setup.py not found. Please run this script from the project root directory."
        exit 1
    fi

    log_success "Installation completed"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."

    if command -v gcp-tts &> /dev/null; then
        log_success "gcp-tts command is available"
        gcp-tts --version
    else
        log_warning "gcp-tts command not found in PATH"
        log_info "You may need to add the installation directory to your PATH"
        log_info "Or run: export PATH=\"\$HOME/.local/bin:\$PATH\""
    fi
}

# Setup Google Cloud credentials
setup_credentials() {
    log_info "Setting up Google Cloud credentials..."

    if command -v gcloud &> /dev/null; then
        log_info "gcloud CLI found"

        # Check if authenticated
        if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
            log_success "Already authenticated with gcloud"
        else
            log_warning "Not authenticated with gcloud"
            echo "Run: gcloud auth login"
            echo "Then: gcloud auth application-default login"
        fi
    else
        log_warning "gcloud CLI not found"
        log_info "Install gcloud CLI: https://cloud.google.com/sdk/docs/install"
    fi

    # Check environment variables
    if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
        log_warning "GOOGLE_CLOUD_PROJECT environment variable not set"
        echo "Set it with: export GOOGLE_CLOUD_PROJECT=your-project-id"
    else
        log_success "GOOGLE_CLOUD_PROJECT set to: $GOOGLE_CLOUD_PROJECT"
    fi
}

# Create sample configuration
create_sample_config() {
    log_info "Creating sample configuration..."

    cat > ~/.gcp-tts-config.yaml << 'EOF'
# Google Cloud Text-to-Speech CLI Configuration
project_id: "${GOOGLE_CLOUD_PROJECT}"
bucket_name: "${GOOGLE_CLOUD_PROJECT}-tts-audio"
location: "us-central1"

# Default settings
defaults:
  language: "en-US"
  voice: null  # Use default voice
  audio_format: "MP3"
  speaking_rate: 1.0
  pitch: 0.0

# Output settings
output:
  directory: "./tts-output"
  filename_template: "tts_{timestamp}_{language}"

# CLI settings
cli:
  verbose: false
  auto_play: false
EOF

    log_success "Sample configuration created at ~/.gcp-tts-config.yaml"
}

# Show usage examples
show_examples() {
    log_info "Usage examples:"
    echo ""
    echo "Basic text-to-speech:"
    echo "  gcp-tts synthesize \"Hello, world!\""
    echo ""
    echo "Custom voice and language:"
    echo "  gcp-tts synthesize \"Hola, mundo!\" --language es-ES --voice es-ES-Neural2-A"
    echo ""
    echo "Process file:"
    echo "  gcp-tts synthesize --file input.txt --output speech.mp3"
    echo ""
    echo "List available voices:"
    echo "  gcp-tts voices --language en-US"
    echo ""
    echo "Batch processing:"
    echo "  gcp-tts batch texts.txt --output-dir ./audio"
    echo ""
    echo "Show configuration:"
    echo "  gcp-tts config"
    echo ""
}

# Main installation function
main() {
    echo "Google Cloud Text-to-Speech CLI Installer"
    echo "========================================"
    echo ""

    # Parse arguments
    USE_VENV=false
    SETUP_CREDS=false

    while [[ $# -gt 0 ]]; do
        case $1 in
            --venv)
                USE_VENV=true
                shift
                ;;
            --setup-credentials)
                SETUP_CREDS=true
                shift
                ;;
            --help|-h)
                echo "Usage: $0 [options]"
                echo ""
                echo "Options:"
                echo "  --venv                Create and use virtual environment"
                echo "  --setup-credentials   Help setup Google Cloud credentials"
                echo "  --help, -h           Show this help message"
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                exit 1
                ;;
        esac
    done

    # Run installation steps
    check_python
    check_pip

    if [ "$USE_VENV" = true ]; then
        install_cli --venv
    else
        install_cli
    fi

    verify_installation

    if [ "$SETUP_CREDS" = true ]; then
        setup_credentials
    fi

    create_sample_config
    show_examples

    log_success "Installation completed successfully!"
    echo ""
    echo "Next steps:"
    echo "1. Set up Google Cloud credentials (if not done already)"
    echo "2. Set GOOGLE_CLOUD_PROJECT environment variable"
    echo "3. Run: gcp-tts synthesize \"Hello, world!\" to test"
}

# Handle script interruption
trap 'log_error "Installation interrupted"; exit 1' INT TERM

# Run main function
main "$@"
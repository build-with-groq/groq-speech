#!/bin/bash

# Groq Speech SDK Setup Script
# This script sets up the complete development environment for the Groq Speech SDK

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_step "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8 or higher."
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "Python $PYTHON_VERSION found"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18 or higher."
        exit 1
    fi
    
    NODE_VERSION=$(node --version)
    print_success "Node.js $NODE_VERSION found"
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm."
        exit 1
    fi
    
    NPM_VERSION=$(npm --version)
    print_success "npm $NPM_VERSION found"
}

# Setup Python environment
setup_python() {
    print_step "Setting up Python environment..."
    
    # Create virtual environment
    if [ ! -d ".venv" ]; then
        print_step "Creating virtual environment..."
        python3 -m venv .venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists, skipping creation"
    fi
    
    # Activate virtual environment
    print_step "Activating virtual environment..."
    source .venv/bin/activate
    print_success "Virtual environment activated"
    
    # Upgrade pip
    print_step "Upgrading pip..."
    pip install --upgrade pip --quiet
    print_success "pip upgraded"
    
    # Install the package in editable mode
    print_step "Installing groq-speech package..."
    pip install -e . --quiet
    print_success "groq-speech package installed"
    
    # Install requirements
    print_step "Installing Python dependencies..."
    pip install -r requirements.txt --quiet
    print_success "Root requirements installed"
    
    print_step "Installing groq_speech dependencies..."
    pip install -r groq_speech/requirements.txt --quiet
    print_success "groq_speech requirements installed"
}

# Setup Node.js environment
setup_nodejs() {
    print_step "Setting up Node.js environment..."
    
    cd examples/groq-speech-ui
    
    print_step "Installing Node.js dependencies..."
    npm install --silent
    print_success "Node.js dependencies installed"
    
    cd ../..
}

# Setup environment variables
setup_env() {
    print_step "Setting up environment variables..."
    
    # Setup .env.api for Python/API
    if [ ! -f ".env.api" ]; then
        if [ -f ".env.api.template" ]; then
            cp .env.api.template .env.api
            print_warning "Created .env.api file from .env.api.template"
            print_warning "Please edit .env.api and add your API keys:"
            print_warning "  - GROQ_API_KEY: Get from https://console.groq.com/keys"
            print_warning "  - HF_TOKEN (optional): Get from https://huggingface.co/settings/tokens"
        else
            print_error ".env.api.template file not found. Cannot create .env.api file."
        fi
    else
        print_success ".env.api file already exists"
    fi
    
    # Setup .env.ui for Next.js UI
    if [ ! -f ".env.ui" ]; then
        if [ -f ".env.ui.template" ]; then
            cp .env.ui.template .env.ui
            print_success "Created .env.ui file from .env.ui.template"
        else
            print_error ".env.ui.template file not found. Cannot create .env.ui file."
        fi
    else
        print_success ".env.ui file already exists"
    fi
}

# Display next steps
display_next_steps() {
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}Setup completed successfully!${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo "Next steps:"
    echo ""
    echo "1. Configure your API keys:"
    echo "   Edit the .env.api file and add your keys:"
    echo "   - GROQ_API_KEY (required)"
    echo "   - HF_TOKEN (optional, for speaker diarization)"
    echo ""
    echo "2. Activate the Python virtual environment:"
    echo -e "   ${BLUE}source .venv/bin/activate${NC}"
    echo ""
    echo "3. Try the CLI demo:"
    echo -e "   ${BLUE}python examples/speech_demo.py --file examples/test_audio.wav${NC}"
    echo ""
    echo "4. Start the API server (in one terminal):"
    echo -e "   ${BLUE}source .venv/bin/activate${NC}"
    echo -e "   ${BLUE}cd api && python server.py${NC}"
    echo ""
    echo "5. Start the web UI (in another terminal):"
    echo -e "   ${BLUE}cd examples/groq-speech-ui && npm run dev${NC}"
    echo ""
    echo "For more information, see README.md"
    echo ""
}

# Main execution
main() {
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║   Groq Speech SDK Setup Script    ║${NC}"
    echo -e "${BLUE}╔════════════════════════════════════╗${NC}"
    echo ""
    
    check_prerequisites
    setup_python
    setup_nodejs
    setup_env
    display_next_steps
}

# Run main function
main

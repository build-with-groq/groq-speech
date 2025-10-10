#!/bin/bash

# Groq Speech SDK - Run Development Environment
# This script sets up and runs both backend and frontend
# Usage: ./run-dev.sh [--verbose] [--help]

set -e  # Exit on any error

# Default values
VERBOSE=false
HELP=false
LOG_FILE=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --help|-h)
            HELP=true
            shift
            ;;
        --clean|-c)
            echo "🧹 Cleaning up existing processes..."
            pkill -f "python.*api" 2>/dev/null || true
            pkill -f "uvicorn" 2>/dev/null || true
            pkill -f "npm.*dev" 2>/dev/null || true
            pkill -f "node.*https" 2>/dev/null || true
            lsof -ti:8000 | xargs kill -9 2>/dev/null || true
            lsof -ti:3443 | xargs kill -9 2>/dev/null || true
            lsof -ti:3000 | xargs kill -9 2>/dev/null || true
            echo "✅ All processes cleaned up"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Show help if requested
if [ "$HELP" = true ]; then
    echo "Groq Speech SDK - Development Environment Runner"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --verbose, -v    Enable verbose logging for all components"
    echo "  --help, -h       Show this help message"
    echo "  --clean, -c      Clean up existing processes and exit"
    echo ""
    echo "Examples:"
    echo "  $0                # Run in normal mode (HTTPS for microphone access)"
    echo "  $0 --verbose      # Run with verbose logging"
    echo "  $0 --clean        # Clean up existing processes"
    echo ""
    echo "Note: Frontend runs on HTTPS (https://localhost:3443) to enable microphone access."
    echo "      Your browser will show a security warning for the self-signed certificate."
    echo "      Click 'Advanced' and 'Proceed to localhost' to continue."
    exit 0
fi


echo "🚀 Starting Groq Speech SDK Development Environment..."
if [ "$VERBOSE" = true ]; then
    echo "🔍 Verbose mode enabled - detailed logs will be shown"
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env.api file exists and is configured
check_env() {
    if [ ! -f .env.api ]; then
        print_warning "Creating .env.api file from template..."
        cp .env.api.template .env.api
        print_error "Please edit .env.api file with your actual API keys!"
        print_error "Required: GROQ_API_KEY and HF_TOKEN"
        print_error "Then run this script again."
        exit 1
    fi

    if grep -q "GROQ_API_KEY=your_groq_api_key_here" .env.api; then
        print_error "Please set your actual GROQ_API_KEY in .env.api file"
        exit 1
    fi

    if grep -q "HF_TOKEN=your_huggingface_token_here" .env.api; then
        print_error "Please set your actual HF_TOKEN in .env.api file"
        exit 1
    fi

    print_success ".env.api file configured"
}

# Install Python dependencies in dependency order
install_python_deps() {
    print_status "Installing Python dependencies in dependency order..."
    
    # 1. Install core SDK dependencies
    print_status "Installing core SDK dependencies..."
    pip install -r groq_speech/requirements.txt
    
    # 2. Install core SDK in editable mode
    print_status "Installing core SDK in editable mode..."
    pip install -e .
    
    # 3. Install API server dependencies
    print_status "Installing API server dependencies..."
    pip install -r api/requirements.txt
    
    # 4. Install examples dependencies (if any)
    print_status "Installing examples dependencies..."
    if [ -f "examples/requirements.txt" ]; then
        pip install -r examples/requirements.txt
    fi
    
    # 5. Install development dependencies
    print_status "Installing development dependencies..."
    pip install -r requirements-dev.txt
    
    print_success "Python dependencies installed"
}

# Install Node.js dependencies
install_node_deps() {
    print_status "Installing Node.js dependencies..."
    cd examples/groq-speech-ui
    if [ ! -d "node_modules" ]; then
        npm install
        print_success "Node.js dependencies installed"
    else
        print_status "Node.js dependencies already installed"
    fi
    cd ../..
}

# Start backend server
start_backend() {
    print_status "Starting backend server..."
    
    # Set verbose environment variable if verbose mode is enabled
    if [ "$VERBOSE" = true ]; then
        export GROQ_VERBOSE=true
        export GROQ_LOG_LEVEL=DEBUG
        print_status "Backend verbose logging enabled"
        
        # Create log file with timestamp for both backend and frontend
        LOG_FILE="logs/verbose-$(date +%Y%m%d-%H%M%S).log"
        mkdir -p logs
        touch "$LOG_FILE"  # Create the file immediately
        echo "📝 Verbose logs will be saved to: $LOG_FILE"
    fi
    
    # Start backend in background with appropriate logging
    if [ "$VERBOSE" = true ]; then
        print_status "Starting backend with verbose logging..."
        python -m api.server 2>&1 | while IFS= read -r line; do
            echo -e "${BLUE}[BACKEND]${NC} $line"
            echo "[BACKEND] $line" >> "$LOG_FILE"
        done &
        BACKEND_PID=$!
    else
        python -m api.server > backend.log 2>&1 &
        BACKEND_PID=$!
    fi
    
    # Wait for backend to be ready
    print_status "Waiting for backend to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "Backend server ready at http://localhost:8000"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Backend server failed to start"
            if [ "$VERBOSE" = false ]; then
                print_error "Check backend.log for details"
            fi
            kill $BACKEND_PID 2>/dev/null || true
            exit 1
        fi
        sleep 1
    done
}

# Start frontend
start_frontend() {
    print_status "Starting frontend with HTTPS support for microphone access..."
    cd examples/groq-speech-ui
    
    # Set verbose environment variable if verbose mode is enabled
    if [ "$VERBOSE" = true ]; then
        export NEXT_PUBLIC_VERBOSE=true
        export NEXT_PUBLIC_DEBUG=true
        export NEXT_PUBLIC_LOG_LEVEL=DEBUG
        print_status "Frontend verbose logging enabled"
    fi
    
    # Start frontend with HTTPS support for microphone access
    if [ "$VERBOSE" = true ]; then
        print_status "Starting frontend with HTTPS and verbose logging..."
        # Ensure logs directory and log file exist before writing to it
        if [ -n "$LOG_FILE" ]; then
            mkdir -p "$(dirname "$LOG_FILE")"
            touch "$LOG_FILE"
        fi
        NEXT_PUBLIC_VERBOSE=true NEXT_PUBLIC_DEBUG=true NEXT_PUBLIC_LOG_LEVEL=DEBUG npm run dev:https 2>&1 | while IFS= read -r line; do
            echo -e "${GREEN}[FRONTEND]${NC} $line"
            if [ -n "$LOG_FILE" ]; then
                echo "[FRONTEND] $line" >> "$LOG_FILE"
            fi
        done &
        FRONTEND_PID=$!
    else
        npm run dev:https > frontend.log 2>&1 &
        FRONTEND_PID=$!
    fi
    
    cd ../..
    
    # Wait for frontend to be ready (HTTPS on port 3443)
    print_status "Waiting for frontend to be ready..."
    for i in {1..30}; do
        if curl -s -k https://localhost:3443 > /dev/null 2>&1; then
            print_success "Frontend ready at https://localhost:3443"
            print_success "🎤 Microphone access is now enabled!"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Frontend failed to start"
            if [ "$VERBOSE" = false ]; then
                print_error "Check frontend.log for details"
            fi
            kill $FRONTEND_PID 2>/dev/null || true
            exit 1
        fi
        sleep 1
    done
}

# Setup signal handlers for cleanup
cleanup() {
    print_status "Shutting down services..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    print_success "Services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Kill existing processes
kill_existing_processes() {
    print_status "Cleaning up existing processes..."
    
    # Kill existing backend processes
    pkill -f "python.*api" 2>/dev/null || true
    pkill -f "uvicorn" 2>/dev/null || true
    
    # Kill existing frontend processes
    pkill -f "npm.*dev" 2>/dev/null || true
    pkill -f "node.*https" 2>/dev/null || true
    
    # Kill processes on specific ports
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    lsof -ti:3443 | xargs kill -9 2>/dev/null || true
    lsof -ti:3000 | xargs kill -9 2>/dev/null || true
    
    # Wait a moment for processes to fully terminate
    sleep 2
    
    print_success "Existing processes cleaned up"
}

# Main execution
main() {
    print_status "Checking environment..."
    check_env
    
    print_status "Installing dependencies..."
    install_python_deps
    install_node_deps
    
    print_status "Cleaning up existing processes..."
    kill_existing_processes
    
    print_status "Starting services..."
    start_backend
    start_frontend
    
    print_success "🎉 Development environment is ready!"
    echo ""
    echo "🌐 Frontend: https://localhost:3443 (HTTPS - Microphone enabled!)"
    echo "🔧 Backend: http://localhost:8000"
    echo "📖 API Docs: http://localhost:8000/docs"
    echo ""
    if [ "$VERBOSE" = true ]; then
        echo "🔍 Verbose logging enabled - all component logs are shown above"
        echo "📝 Logs are prefixed with [BACKEND] and [FRONTEND] for easy identification"
        echo "📄 Complete verbose log saved to: $LOG_FILE"
        echo "💡 To share logs for analysis, send the file: $LOG_FILE"
    else
        echo "📝 Logs are saved to backend.log and frontend.log"
        echo "💡 Use --verbose flag to see real-time logs: ./run-dev.sh --verbose"
    fi
    echo ""
    echo "Press Ctrl+C to stop all services"
    echo ""
    
    # Keep script running
    wait
}

# Run main function
main "$@"

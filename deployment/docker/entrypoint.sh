#!/bin/bash
set -e

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to wait for dependencies
wait_for_dependency() {
    local host=$1
    local port=$2
    local max_attempts=${3:-30}
    local attempt=1
    
    log "Waiting for $host:$port..."
    
    while [ $attempt -le $max_attempts ]; do
        if nc -z "$host" "$port" 2>/dev/null; then
            log "$host:$port is available"
            return 0
        fi
        
        log "Attempt $attempt/$max_attempts: $host:$port not available yet"
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log "ERROR: $host:$port is not available after $max_attempts attempts"
    return 1
}

# Function to validate environment variables
validate_env() {
    local required_vars=("GROQ_API_KEY")
    local missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        log "ERROR: Missing required environment variables: ${missing_vars[*]}"
        log "Please set these variables in your .env file or environment"
        exit 1
    fi
    
    log "Environment validation passed"
}

# Function to check Python dependencies
check_dependencies() {
    log "Checking Python dependencies..."
    
    if ! python -c "import groq" 2>/dev/null; then
        log "ERROR: groq package not found"
        exit 1
    fi
    
    if ! python -c "import fastapi" 2>/dev/null; then
        log "ERROR: fastapi package not found"
        exit 1
    fi
    
    if ! python -c "import uvicorn" 2>/dev/null; then
        log "ERROR: uvicorn package not found"
        exit 1
    fi
    
    log "Python dependencies check passed"
}

# Function to test GPU support
test_gpu_support() {
    if [ -f "test_gpu_support.py" ]; then
        log "Testing GPU support..."
        python test_gpu_support.py
        if [ $? -eq 0 ]; then
            log "GPU support test passed"
        else
            log "WARNING: GPU support test failed, continuing with CPU fallback"
        fi
    else
        log "GPU test script not found, skipping GPU test"
    fi
}

# Function to run database migrations (if applicable)
run_migrations() {
    if [ -f "alembic.ini" ]; then
        log "Running database migrations..."
        alembic upgrade head
    fi
}

# Function to create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p /app/logs
    mkdir -p /app/temp
    mkdir -p /app/uploads
    
    # Set proper permissions
    chmod 755 /app/logs
    chmod 755 /app/temp
    chmod 755 /app/uploads
}

# Function to start the application
start_app() {
    local cmd="$1"
    local args="${@:2}"
    
    log "Starting application with command: $cmd $args"
    
    # Execute the command
    exec "$cmd" "$args"
}

# Main execution
main() {
    log "Starting Groq Speech SDK API Server..."
    
    # Validate environment
    validate_env
    
    # Check dependencies
    check_dependencies
    
    # Test GPU support
    test_gpu_support
    
    # Create directories
    create_directories
    
    # Run migrations if needed
    run_migrations
    
    # Start the application
    start_app "$@"
}

# Handle signals
trap 'log "Received signal, shutting down..."; exit 0' SIGTERM SIGINT

# Run main function with all arguments
main "$@" 
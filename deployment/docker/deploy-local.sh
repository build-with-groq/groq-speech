#!/bin/bash

# Groq Speech Local Docker Deployment Script
# This script builds and runs both API and UI containers locally

set -e

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

# Check if environment files exist in deployment/docker/
if [ ! -f "deployment/docker/.env.api" ]; then
    print_warning "No deployment/docker/.env.api file found. Creating from root template..."
    if [ -f ".env.api.template" ]; then
        cp .env.api.template deployment/docker/.env.api
        print_warning "Please edit deployment/docker/.env.api file with your actual API keys before continuing."
        print_warning "Required: GROQ_API_KEY and HF_TOKEN"
        exit 1
    else
        print_error "No .env.api.template found in root. Please create it manually."
        exit 1
    fi
fi

if [ ! -f "deployment/docker/.env.ui" ]; then
    print_warning "No deployment/docker/.env.ui file found. Creating from root template..."
    if [ -f ".env.ui.template" ]; then
        cp .env.ui.template deployment/docker/.env.ui
        print_success "Created deployment/docker/.env.ui file with default values"
    else
        print_error "No .env.ui.template found in root. Please create it manually."
        exit 1
    fi
fi

# Check for required API environment variables
if ! grep -q "GROQ_API_KEY=" deployment/docker/.env.api || grep -q "GROQ_API_KEY=your_groq_api_key_here" deployment/docker/.env.api; then
    print_error "GROQ_API_KEY is not set or is still the placeholder in deployment/docker/.env.api file."
    print_error "Please edit deployment/docker/.env.api with your actual Groq API key."
    exit 1
fi

if ! grep -q "HF_TOKEN=" deployment/docker/.env.api || grep -q "HF_TOKEN=your_huggingface_token_here" deployment/docker/.env.api; then
    print_error "HF_TOKEN is not set or is still the placeholder in deployment/docker/.env.api file."
    print_error "Please edit deployment/docker/.env.api with your actual Hugging Face token."
    exit 1
fi

print_status "Starting Groq Speech local deployment..."

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f deployment/docker/docker-compose.yml down 2>/dev/null || true

# Build and start services
print_status "Building and starting services..."
docker-compose -f deployment/docker/docker-compose.yml up --build -d

# Wait for services to be healthy
print_status "Waiting for services to be healthy..."
sleep 10

# Check API health
print_status "Checking API health..."
if curl -f http://localhost:8000/health >/dev/null 2>&1; then
    print_success "API is healthy"
else
    print_error "API health check failed"
    docker-compose -f deployment/docker/docker-compose.yml logs groq-speech-api
    exit 1
fi

# Check UI health (HTTPS)
print_status "Checking UI health..."
if curl -f -k https://localhost:3443 >/dev/null 2>&1; then
    print_success "UI is healthy"
else
    print_error "UI health check failed"
    docker-compose -f deployment/docker/docker-compose.yml logs groq-speech-ui
    exit 1
fi

print_success "Deployment completed successfully!"
echo ""
echo "🌐 Services are running:"
echo "   API: http://localhost:8000"
echo "   UI:  https://localhost:3443"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🔒 Note: The UI uses HTTPS for microphone access."
echo "   Your browser will show a security warning for the self-signed certificate."
echo "   Click 'Advanced' and 'Proceed to localhost' to continue."
echo ""
echo "📋 Useful commands:"
echo "   View logs: docker-compose -f deployment/docker/docker-compose.yml logs -f"
echo "   Stop services: docker-compose -f deployment/docker/docker-compose.yml down"
echo "   Restart: docker-compose -f deployment/docker/docker-compose.yml restart"

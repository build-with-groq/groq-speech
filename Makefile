# Groq Speech SDK Makefile
# Professional build automation and development workflows

.PHONY: help install install-dev test test-unit test-integration test-e2e test-coverage lint format type-check clean build docker-build docker-run docker-stop docs serve-docs release

# Variables
PYTHON := python3
PIP := pip3
PYTEST := pytest
COVERAGE := coverage
BLACK := black
FLAKE8 := flake8
MYPY := mypy
ISORT := isort

# Project information
PROJECT_NAME := groq-speech-sdk
VERSION := $(shell python -c "import groq_speech; print(groq_speech.__version__)")
PYTHON_VERSION := $(shell python --version)

# Directories
SRC_DIR := groq_speech
API_DIR := api
TESTS_DIR := tests
DOCS_DIR := docs
BUILD_DIR := build
DIST_DIR := dist
COVERAGE_DIR := htmlcov

# Files
REQUIREMENTS := requirements.txt
REQUIREMENTS_DEV := requirements-dev.txt
SETUP_PY := setup.py
README := README.md
DOCKERFILE := deployment/docker/Dockerfile
DOCKER_COMPOSE := deployment/docker/docker-compose.yml

# Default target
help: ## Show this help message
	@echo "Groq Speech SDK - Development Commands"
	@echo "======================================"
	@echo ""
	@echo "Available commands:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'
	@echo ""
	@echo "Environment:"
	@echo "  Python: $(PYTHON_VERSION)"
	@echo "  Version: $(VERSION)"
	@echo ""

# Installation
install: ## Install production dependencies
	@echo "Installing production dependencies..."
	$(PIP) install -r $(REQUIREMENTS)
	@echo "✅ Production dependencies installed"

install-dev: ## Install development dependencies
	@echo "Installing development dependencies..."
	$(PIP) install -r $(REQUIREMENTS)
	$(PIP) install -r $(REQUIREMENTS_DEV)
	@echo "✅ Development dependencies installed"

install-editable: ## Install package in editable mode
	@echo "Installing package in editable mode..."
	$(PIP) install -e .
	@echo "✅ Package installed in editable mode"

# Testing
test: ## Run all tests
	@echo "Running all tests..."
	$(PYTHON) run_tests.py --verbose
	@echo "✅ All tests completed"

test-unit: ## Run unit tests only
	@echo "Running unit tests..."
	$(PYTHON) run_tests.py --unit --verbose
	@echo "✅ Unit tests completed"

test-integration: ## Run integration tests only
	@echo "Running integration tests..."
	$(PYTHON) run_tests.py --e2e --verbose
	@echo "✅ Integration tests completed"

test-e2e: ## Run end-to-end tests only
	@echo "Running end-to-end tests..."
	$(PYTHON) run_tests.py --e2e --verbose
	@echo "✅ End-to-end tests completed"

test-cli: ## Run CLI tests only
	@echo "Running CLI tests..."
	$(PYTHON) run_tests.py --cli --verbose
	@echo "✅ CLI tests completed"

test-api: ## Run API tests only
	@echo "Running API tests..."
	$(PYTHON) -m pytest tests/test_e2e_api.py -v --tb=short
	@echo "✅ API tests completed"

test-quick: ## Run quick tests (unit tests only)
	@echo "Running quick tests..."
	$(PYTHON) run_tests.py --unit
	@echo "✅ Quick tests completed"

test-performance: ## Run performance tests
	@echo "Running performance tests..."
	$(PYTEST) $(TESTS_DIR)/performance/ -v
	@echo "✅ Performance tests completed"

test-coverage: ## Run tests with coverage report
	@echo "Running tests with coverage..."
	$(PYTEST) $(TESTS_DIR) --cov=$(SRC_DIR) --cov=$(API_DIR) --cov-report=html --cov-report=term
	@echo "✅ Coverage report generated in $(COVERAGE_DIR)/"

test-watch: ## Run tests in watch mode
	@echo "Running tests in watch mode..."
	$(PYTEST) $(TESTS_DIR) -f -v

# Code Quality
lint: ## Run linting checks
	@echo "Running linting checks..."
	$(FLAKE8) $(SRC_DIR) $(API_DIR) $(TESTS_DIR)
	@echo "✅ Linting completed"

format: ## Format code with black and isort
	@echo "Formatting code..."
	$(BLACK) $(SRC_DIR) $(API_DIR) $(TESTS_DIR)
	$(ISORT) $(SRC_DIR) $(API_DIR) $(TESTS_DIR)
	@echo "✅ Code formatting completed"

format-check: ## Check code formatting without making changes
	@echo "Checking code formatting..."
	$(BLACK) --check $(SRC_DIR) $(API_DIR) $(TESTS_DIR)
	$(ISORT) --check-only $(SRC_DIR) $(API_DIR) $(TESTS_DIR)
	@echo "✅ Code formatting check completed"

type-check: ## Run type checking with mypy
	@echo "Running type checking..."
	$(MYPY) $(SRC_DIR) $(API_DIR)
	@echo "✅ Type checking completed"

quality: lint format-check type-check ## Run all code quality checks
	@echo "✅ All code quality checks completed"

# Building
build: clean ## Build the package
	@echo "Building package..."
	$(PYTHON) setup.py sdist bdist_wheel
	@echo "✅ Package built in $(DIST_DIR)/"

clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	rm -rf $(BUILD_DIR) $(DIST_DIR) $(COVERAGE_DIR)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	@echo "✅ Build artifacts cleaned"

# Docker
docker-build: ## Build Docker image
	@echo "Building Docker image..."
	docker build -f $(DOCKERFILE) -t $(PROJECT_NAME):latest .
	@echo "✅ Docker image built"

docker-run: ## Run Docker container
	@echo "Running Docker container..."
	docker run -d --name $(PROJECT_NAME)-container -p 8000:8000 $(PROJECT_NAME):latest
	@echo "✅ Docker container running on http://localhost:8000"

docker-stop: ## Stop Docker container
	@echo "Stopping Docker container..."
	docker stop $(PROJECT_NAME)-container || true
	docker rm $(PROJECT_NAME)-container || true
	@echo "✅ Docker container stopped"

docker-compose-up: ## Start services with Docker Compose
	@echo "Starting services with Docker Compose..."
	docker-compose -f $(DOCKER_COMPOSE) up -d
	@echo "✅ Services started"

docker-compose-down: ## Stop services with Docker Compose
	@echo "Stopping services with Docker Compose..."
	docker-compose -f $(DOCKER_COMPOSE) down
	@echo "✅ Services stopped"

docker-compose-logs: ## View Docker Compose logs
	docker-compose -f $(DOCKER_COMPOSE) logs -f

# Documentation
docs: ## Build documentation
	@echo "Building documentation..."
	cd $(DOCS_DIR) && make html
	@echo "✅ Documentation built"

serve-docs: ## Serve documentation locally
	@echo "Serving documentation on http://localhost:8001..."
	cd $(DOCS_DIR)/_build/html && python -m http.server 8001

# Development
dev-install: install-dev install-editable ## Install for development
	@echo "✅ Development environment ready"

dev-setup: dev-install ## Complete development setup
	@echo "Setting up pre-commit hooks..."
	pre-commit install
	@echo "✅ Development setup completed"

dev-test: quality test-coverage ## Run all development checks
	@echo "✅ All development checks completed"

# Examples
examples: ## Run example scripts
	@echo "Running examples..."
	$(PYTHON) examples/basic_recognition.py
	$(PYTHON) examples/continuous_recognition.py
	@echo "✅ Examples completed"

demo: ## Run interactive demo
	@echo "Running interactive demo..."
	$(PYTHON) demo.py
	@echo "✅ Demo completed"

# Configuration
config-test: ## Test configuration
	@echo "Testing configuration..."
	$(PYTHON) test_config.py
	@echo "✅ Configuration test completed"

# Security
security-check: ## Run security checks
	@echo "Running security checks..."
	bandit -r $(SRC_DIR) $(API_DIR)
	safety check
	@echo "✅ Security checks completed"

# Performance
benchmark: ## Run performance benchmarks
	@echo "Running performance benchmarks..."
	$(PYTHON) -m pytest tests/performance/ -v --benchmark-only
	@echo "✅ Performance benchmarks completed"

# Release
release: clean build test quality ## Prepare for release
	@echo "Preparing release..."
	@echo "Version: $(VERSION)"
	@echo "✅ Release preparation completed"

release-publish: release ## Publish to PyPI
	@echo "Publishing to PyPI..."
	twine upload $(DIST_DIR)/*
	@echo "✅ Package published to PyPI"

# Monitoring
monitor: ## Start monitoring services
	@echo "Starting monitoring services..."
	docker-compose -f $(DOCKER_COMPOSE) up -d prometheus grafana
	@echo "✅ Monitoring services started"
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3000"

# Database
db-migrate: ## Run database migrations
	@echo "Running database migrations..."
	alembic upgrade head
	@echo "✅ Database migrations completed"

db-rollback: ## Rollback database migrations
	@echo "Rolling back database migrations..."
	alembic downgrade -1
	@echo "✅ Database rollback completed"

# Utilities
check-deps: ## Check for outdated dependencies
	@echo "Checking for outdated dependencies..."
	$(PIP) list --outdated
	@echo "✅ Dependency check completed"

update-deps: ## Update dependencies
	@echo "Updating dependencies..."
	$(PIP) install --upgrade -r $(REQUIREMENTS)
	$(PIP) install --upgrade -r $(REQUIREMENTS_DEV)
	@echo "✅ Dependencies updated"

# Environment
env-create: ## Create virtual environment
	@echo "Creating virtual environment..."
	$(PYTHON) -m venv .venv
	@echo "✅ Virtual environment created"
	@echo "Activate with: source .venv/bin/activate"

env-activate: ## Activate virtual environment
	@echo "Activating virtual environment..."
	source .venv/bin/activate

# CI/CD
ci-test: lint format-check type-check test-coverage ## Run CI tests
	@echo "✅ CI tests completed"

ci-build: ci-test build ## Run CI build
	@echo "✅ CI build completed"

# Helpers
version: ## Show version information
	@echo "Project: $(PROJECT_NAME)"
	@echo "Version: $(VERSION)"
	@echo "Python: $(PYTHON_VERSION)"

status: ## Show project status
	@echo "Project Status"
	@echo "=============="
	@echo "Project: $(PROJECT_NAME)"
	@echo "Version: $(VERSION)"
	@echo "Python: $(PYTHON_VERSION)"
	@echo ""
	@echo "Directories:"
	@ls -la | grep "^d"
	@echo ""
	@echo "Recent files:"
	@ls -la --time-style=long-iso | head -10

# Default target
.DEFAULT_GOAL := help 
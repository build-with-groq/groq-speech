# Scripts Documentation

> **⚠️ Note**: These scripts are part of a demonstrative solution for development and testing purposes.

This document provides a comprehensive guide to all scripts in the Groq Speech Solution project.

> **📁 NEW:** Scripts are now organized in subdirectories under `scripts/` for better maintainability.  
> A symlink `run-dev.sh` exists in root for convenience.

## 📂 Directory Structure

```
scripts/
├── debug/      # Chrome debugging and browser automation scripts (8 scripts)
├── dev/        # Development environment scripts (2 scripts)
└── utils/      # Utility and helper scripts (1 script)
```

## 📁 Root Directory Scripts

### 🚀 Setup & Installation

#### `setup.sh` - Main Setup Script
**Location:** `/setup.sh` (Root)  
**Purpose:** Automated setup for the entire development environment

**Usage:**
```bash
./setup.sh
```

**What it does:**
- ✅ Checks Python 3.8+ and Node.js 18+ prerequisites
- ✅ Creates Python virtual environment (`.venv/`)
- ✅ Installs all Python dependencies (Solution, API, examples)
- ✅ Installs Node.js dependencies for web UI
- ✅ Creates `.env.api` and `.env.ui` configuration files

**When to use:** First-time setup or fresh environment setup

---

#### `run-dev.sh` - Development Environment Runner (Symlink)
**Location:** `/run-dev.sh` → `scripts/dev/run-dev.sh`  
**Purpose:** Run complete development environment with backend and frontend

**Usage:**
```bash
./run-dev.sh [--verbose] [--help]
# or
./scripts/dev/run-dev.sh
```

**Options:**
- `--verbose` - Enable verbose output
- `--help` - Show help message

**What it does:**
- Checks and creates `.env.api` if missing
- Validates API keys are configured
- Installs Python dependencies in order
- Starts FastAPI backend server
- Starts Next.js frontend development server

**When to use:** Daily development workflow

---

## 🔧 Development Scripts (`scripts/dev/`)

### `start-dev-servers.sh`
**Location:** `scripts/dev/start-dev-servers.sh`  
**Purpose:** Start development servers without Chrome debugging

**Usage:**
```bash
./scripts/dev/start-dev-servers.sh
```

**What it does:**
- Starts API server on port 8000
- Starts UI server on port 3000
- No debugging or Chrome remote debugging

**When to use:** Quick testing without browser debugging

---

## 🐛 Chrome Debugging Scripts (`scripts/debug/`)

These scripts help with Chrome/VS Code debugging for the Next.js frontend. They handle Chrome instances, debugging profiles, and connection issues.

### `start-chrome-debug-safe.sh` - Safe Chrome Debug
**Location:** `scripts/debug/start-chrome-debug-safe.sh`  
**Purpose:** Safely start Chrome with debugging, handling conflicts

**Usage:**
```bash
./scripts/debug/start-chrome-debug-safe.sh
```

**What it does:**
- Comprehensive Chrome process cleanup
- Creates isolated debug profile
- Starts Chrome with debugging flags
- Error handling and crash recovery

**When to use:** Recommended for Chrome debugging (most reliable)

---

### `start-chrome-debug.sh` - Basic Chrome Debug
**Location:** `scripts/debug/start-chrome-debug.sh`  
**Purpose:** Start Chrome with debugging, handling existing instances

**Usage:**
```bash
./scripts/debug/start-chrome-debug.sh
```

**What it does:**
- Checks for existing Chrome processes
- Starts Chrome with remote debugging on port 9222
- Opens localhost:3000 for UI debugging

**When to use:** Basic Chrome debugging session

---

### `cleanup-chrome-debug.sh` - Chrome Cleanup
**Location:** `scripts/debug/cleanup-chrome-debug.sh`  
**Purpose:** Clean up Chrome debugging processes and profiles

**Usage:**
```bash
./scripts/debug/cleanup-chrome-debug.sh
```

**What it does:**
- Kills all Chrome processes safely
- Removes debug profiles
- Cleans up temporary debugging files

**When to use:** When Chrome debugging is stuck or crashed

---

### `cleanup-debug-profiles.sh` - Profile Cleanup
**Location:** `scripts/debug/cleanup-debug-profiles.sh`  
**Purpose:** Clean up Chrome debug profiles causing conflicts

**Usage:**
```bash
./scripts/debug/cleanup-debug-profiles.sh
```

**What it does:**
- Removes Chrome debug user data directories
- Clears debugging session data

**When to use:** When Chrome reports profile conflicts

---

### `prepare-chrome-debug.sh` - Debug Environment Preparation
**Location:** `scripts/debug/prepare-chrome-debug.sh`  
**Purpose:** Prepare Chrome debugging environment

**Usage:**
```bash
./scripts/debug/prepare-chrome-debug.sh
```

**What it does:**
- Kills existing Chrome instances
- Prepares fresh debugging environment

**When to use:** Before starting a new debug session

---

### `start-debug-browser.sh` - Browser Debug for VS Code
**Location:** `scripts/debug/start-debug-browser.sh`  
**Purpose:** Start Chrome with debugging enabled for VS Code

**Usage:**
```bash
./scripts/debug/start-debug-browser.sh
```

**What it does:**
- Configures Chrome for VS Code debugging
- Sets up remote debugging port
- Prepares browser for attach

**When to use:** VS Code debugging configuration

---

### `start-debug-chrome-safe.sh` - Alternative Safe Debug
**Location:** `scripts/debug/start-debug-chrome-safe.sh`  
**Purpose:** Alternative safe method to start Chrome debugging

**Usage:**
```bash
./scripts/debug/start-debug-chrome-safe.sh
```

**What it does:**
- Alternative Chrome debugging startup
- Different process handling approach
- Fallback option for debugging issues

**When to use:** When other debug scripts don't work

---

### `debug-script.sh` - Debug Test Script
**Location:** `scripts/debug/debug-script.sh`  
**Purpose:** Test frontend startup and debugging

**Usage:**
```bash
./scripts/debug/debug-script.sh
```

**What it does:**
- Tests frontend startup sequence
- Validates debugging configuration
- Diagnostic output for troubleshooting

**When to use:** Debugging startup issues

---

## 🛠️ Utility Scripts (`scripts/utils/`)

### `share-logs.sh` - Log Sharing Helper
**Location:** `scripts/utils/share-logs.sh`  
**Purpose:** Help share verbose logs for analysis

**Usage:**
```bash
./scripts/utils/share-logs.sh
```

**What it does:**
- Finds latest verbose log file
- Prepares log for sharing
- Formats output for bug reports

**When to use:** Sharing logs for troubleshooting

---

## 🐍 Root Python Files

### `setup.py` - Package Setup ⚠️ CRITICAL
**Location:** `/setup.py` (Root)  
**Purpose:** Python package installation configuration

**Usage:**
```bash
pip install -e .
```

**What it does:**
- Defines package metadata
- Specifies dependencies
- Configures entry points

**⚠️ IMPORTANT:** DO NOT MOVE - Required for `pip install -e .`

---

### `run_tests.py` - Test Runner
**Location:** `/run_tests.py` (Root)  
**Purpose:** Comprehensive test suite runner

**Usage:**
```bash
python run_tests.py                    # Run all tests
python run_tests.py --unit            # Run only unit tests
python run_tests.py --integration     # Run only integration tests
python run_tests.py --e2e             # Run only e2e tests
python run_tests.py --coverage        # Run with coverage report
```

**What it does:**
- Runs all test suites in correct order
- Generates coverage reports
- Validates all components

**When to use:** Before commits, CI/CD pipeline

---

### `test_gpu_support.py` - GPU Validation
**Location:** `/test_gpu_support.py` (Root)  
**Purpose:** Test GPU support for Pyannote.audio diarization

**Usage:**
```bash
python test_gpu_support.py
```

**What it does:**
- Detects GPU availability
- Tests Pyannote.audio with GPU
- Validates CUDA support
- Shows device and memory info

**When to use:** Deployment validation, GPU troubleshooting

---

## 📂 Other Script Locations

### `deployment/docker/`
- `setup-env.sh` - Docker environment setup (copies root `.env.*.template` files)
- `deploy-local.sh` - Local Docker deployment
- `entrypoint.sh` - Container entrypoint

### `deployment/gcp/`
- `deploy.sh` - GCP Cloud Run deployment
- `deploy-simple-gke.sh` - GKE deployment
- `deploy-cloudrun-simple.sh` - Simple Cloud Run deploy

### `examples/groq-speech-ui/scripts/`
- `https-dev-server.js` - HTTPS development server

---

## 🔄 Common Workflows

### First-Time Setup
```bash
./setup.sh
# Edit .env.api with your keys
source .venv/bin/activate
```

### Daily Development
```bash
source .venv/bin/activate
./run-dev.sh
```

### Debugging Frontend Issues
```bash
./scripts/debug/cleanup-chrome-debug.sh
./scripts/debug/start-chrome-debug-safe.sh
```

### Running Tests
```bash
source .venv/bin/activate
python run_tests.py --coverage
```

### Deployment Validation
```bash
python test_gpu_support.py  # Check GPU support
./deployment/docker/deploy-local.sh  # Test Docker deployment
```

---

## 🆘 Troubleshooting

### Chrome Debugging Issues
1. Try `./scripts/debug/cleanup-chrome-debug.sh`
2. Then `./scripts/debug/start-chrome-debug-safe.sh`
3. If still failing, try `./scripts/debug/start-debug-chrome-safe.sh`
4. Last resort: `./scripts/debug/cleanup-debug-profiles.sh` + restart

### Environment Issues
1. Re-run `./setup.sh`
2. Check `.env.api` has correct keys
3. Verify virtual environment: `source .venv/bin/activate`

### Test Failures
1. Run `python run_tests.py --verbose`
2. Check individual test suites
3. Validate GPU if using diarization: `python test_gpu_support.py`

---

## 📝 Script Maintenance Notes

### Script Organization
- **Root:** `setup.sh` + symlink `run-dev.sh` for frequently-used scripts
- **scripts/dev/:** Development workflow scripts
- **scripts/debug/:** Chrome debugging and browser automation
- **scripts/utils/:** Utility and helper scripts

### Adding New Scripts
- Place in appropriate subdirectory: `dev/`, `debug/`, or `utils/`
- Create symlink in root only for very frequently-used scripts
- Document in this file

### Script Naming Convention
- Use lowercase with hyphens: `my-script.sh`
- Prefix with purpose: `setup-`, `start-`, `cleanup-`, `test-`
- Be descriptive but concise

### Dependencies
- Always check prerequisites at script start
- Provide clear error messages
- Exit gracefully on failures

---

**Last Updated:** October 2025  
**Maintained By:** Groq Speech Solution Team

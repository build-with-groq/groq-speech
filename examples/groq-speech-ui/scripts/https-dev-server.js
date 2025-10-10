#!/usr/bin/env node

/**
 * HTTPS Development Server for Groq Speech UI
 * 
 * This script creates an HTTPS development server to enable microphone access
 * in browsers, which requires secure contexts for getUserMedia() API.
 * 
 * Features:
 * - Self-signed SSL certificates for local development
 * - Automatic certificate generation if not present
 * - Proxy to Next.js development server
 * - Microphone access enabled
 */

const https = require('https');
const http = require('http');
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const HTTPS_PORT = 3443; // HTTPS port for frontend
const NEXT_PORT = 3000;  // Next.js dev server port
const API_PORT = 8000;   // Backend API port

// Colors for console output
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m'
};

function log(message, color = 'reset') {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function createSelfSignedCert() {
  const certDir = path.join(__dirname, '..', 'certs');
  const keyPath = path.join(certDir, 'localhost-key.pem');
  const certPath = path.join(certDir, 'localhost.pem');

  // Create certs directory if it doesn't exist
  if (!fs.existsSync(certDir)) {
    fs.mkdirSync(certDir, { recursive: true });
  }

  // Check if certificates already exist
  if (fs.existsSync(keyPath) && fs.existsSync(certPath)) {
    log('✅ SSL certificates already exist', 'green');
    return { keyPath, certPath };
  }

  log('🔐 Generating self-signed SSL certificates...', 'yellow');
  
  try {
    // Generate private key
    execSync(`openssl genrsa -out "${keyPath}" 2048`, { stdio: 'pipe' });
    
    // Generate certificate
    execSync(`openssl req -new -x509 -key "${keyPath}" -out "${certPath}" -days 365 -subj "/C=US/ST=CA/L=San Francisco/O=Groq Speech/OU=Development/CN=localhost"`, { stdio: 'pipe' });
    
    log('✅ SSL certificates generated successfully', 'green');
    return { keyPath, certPath };
  } catch (error) {
    log('❌ Failed to generate SSL certificates. Make sure OpenSSL is installed.', 'red');
    log('   You can install OpenSSL with: brew install openssl (macOS) or apt-get install openssl (Ubuntu)', 'yellow');
    process.exit(1);
  }
}

function startNextDevServer() {
  log('🚀 Starting Next.js development server...', 'blue');
  
  // Kill any existing Next.js processes on port 3000
  try {
    execSync(`lsof -ti:${NEXT_PORT} | xargs kill -9 2>/dev/null || true`, { stdio: 'pipe' });
    log('🧹 Cleaned up existing processes on port 3000', 'yellow');
  } catch (error) {
    // Ignore errors - port might not be in use
  }
  
  // Wait a moment for processes to fully terminate
  setTimeout(() => {
    const nextProcess = spawn('npm', ['run', 'dev'], {
      cwd: path.join(__dirname, '..'),
      stdio: 'pipe',
      shell: true,
      env: { 
        ...process.env, 
        PORT: NEXT_PORT.toString(),
        NEXT_PUBLIC_FRONTEND_URL: `https://localhost:${HTTPS_PORT}`,
        NODE_OPTIONS: '--max-old-space-size=4096' // Increase memory limit
      }
    });

    let serverStarted = false;

    nextProcess.stdout.on('data', (data) => {
      const output = data.toString();
      if (output.includes('ready - started server on') && !serverStarted) {
        serverStarted = true;
        log('✅ Next.js development server is ready', 'green');
      }
      // Don't log all Next.js output to keep console clean
    });

    nextProcess.stderr.on('data', (data) => {
      const output = data.toString();
      if (output.includes('error') || output.includes('Error')) {
        log(`Next.js Error: ${output}`, 'red');
      }
    });

    nextProcess.on('close', (code) => {
      if (code !== 0) {
        log(`❌ Next.js development server exited with code ${code}`, 'red');
      }
    });

    nextProcess.on('error', (error) => {
      log(`❌ Failed to start Next.js development server: ${error.message}`, 'red');
    });

    // Store the process globally so we can access it
    global.nextProcess = nextProcess;
  }, 1000); // Wait 1 second before starting
}

function createHttpsProxy() {
  const { keyPath, certPath } = createSelfSignedCert();
  
  const options = {
    key: fs.readFileSync(keyPath),
    cert: fs.readFileSync(certPath)
  };

  const server = https.createServer(options, (req, res) => {
    // Set CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    
    if (req.method === 'OPTIONS') {
      res.writeHead(200);
      res.end();
      return;
    }

    // Proxy to Next.js development server
    const proxyReq = http.request({
      hostname: 'localhost',
      port: NEXT_PORT,
      path: req.url,
      method: req.method,
      headers: {
        ...req.headers,
        'host': `localhost:${NEXT_PORT}`
      },
      timeout: 10000 // 10 second timeout
    }, (proxyRes) => {
      // Copy response headers
      Object.keys(proxyRes.headers).forEach(key => {
        res.setHeader(key, proxyRes.headers[key]);
      });
      
      res.writeHead(proxyRes.statusCode);
      proxyRes.pipe(res);
    });

    proxyReq.on('error', (err) => {
      log(`❌ Proxy error: ${err.message}`, 'red');
      if (!res.headersSent) {
        res.writeHead(502, { 'Content-Type': 'text/plain' });
        res.end('Bad Gateway: Next.js server not available');
      }
    });

    proxyReq.on('timeout', () => {
      log(`❌ Proxy timeout for ${req.url}`, 'red');
      if (!res.headersSent) {
        res.writeHead(504, { 'Content-Type': 'text/plain' });
        res.end('Gateway Timeout');
      }
      proxyReq.destroy();
    });

    req.pipe(proxyReq);
  });

  server.listen(HTTPS_PORT, () => {
    log('🔒 HTTPS Development Server started', 'green');
    log(`   Frontend: https://localhost:${HTTPS_PORT}`, 'cyan');
    log(`   Backend:  http://localhost:${API_PORT}`, 'cyan');
    log('   Microphone access is now enabled!', 'green');
    log('', 'reset');
    log('📝 Note: Your browser will show a security warning for the self-signed certificate.', 'yellow');
    log('   Click "Advanced" and "Proceed to localhost" to continue.', 'yellow');
    log('', 'reset');
    log('Press Ctrl+C to stop the server', 'blue');
  });

  return server;
}

function checkBackendServer() {
  return new Promise((resolve) => {
    const req = http.request({
      hostname: 'localhost',
      port: API_PORT,
      path: '/health',
      method: 'GET'
    }, (res) => {
      resolve(res.statusCode === 200);
    });

    req.on('error', () => {
      resolve(false);
    });

    req.setTimeout(1000, () => {
      req.destroy();
      resolve(false);
    });

    req.end();
  });
}

function waitForNextJsServer() {
  return new Promise((resolve) => {
    const maxAttempts = 30;
    let attempts = 0;
    let serverReady = false;
    
    const checkServer = () => {
      if (serverReady) {
        return; // Don't check again if already ready
      }
      
      attempts++;
      const req = http.request({
        hostname: 'localhost',
        port: NEXT_PORT,
        path: '/',
        method: 'GET',
        timeout: 3000 // 3 second timeout
      }, (res) => {
        if (!serverReady) {
          serverReady = true;
          log('✅ Next.js server is ready', 'green');
          resolve();
        }
      });

      req.on('error', (err) => {
        if (serverReady) {
          return; // Don't retry if already ready
        }
        
        if (attempts < maxAttempts) {
          log(`⏳ Attempt ${attempts}/${maxAttempts}: Waiting for Next.js server...`, 'yellow');
          setTimeout(checkServer, 2000); // Wait 2 seconds between attempts
        } else {
          log('❌ Next.js server failed to start within 60 seconds', 'red');
          log('   The HTTPS server will start anyway, but Next.js may not be ready', 'yellow');
          resolve(); // Continue anyway
        }
      });

      req.on('timeout', () => {
        req.destroy();
        if (serverReady) {
          return; // Don't retry if already ready
        }
        
        if (attempts < maxAttempts) {
          log(`⏳ Attempt ${attempts}/${maxAttempts}: Next.js server timeout, retrying...`, 'yellow');
          setTimeout(checkServer, 2000); // Wait 2 seconds between attempts
        } else {
          log('❌ Next.js server failed to start within 60 seconds', 'red');
          log('   The HTTPS server will start anyway, but Next.js may not be ready', 'yellow');
          resolve(); // Continue anyway
        }
      });

      req.end();
    };
    
    checkServer();
  });
}

async function main() {
  log('🎤 Groq Speech UI - HTTPS Development Server', 'bright');
  log('===============================================', 'bright');
  
  // Check if backend is running
  log('🔍 Checking backend server...', 'blue');
  const backendRunning = await checkBackendServer();
  
  if (!backendRunning) {
    log('⚠️  Backend server is not running on port 8000', 'yellow');
    log('   Please start the backend server first:', 'yellow');
    log('   python -m api.server', 'cyan');
    log('', 'reset');
  } else {
    log('✅ Backend server is running', 'green');
  }
  
  // Start Next.js development server
  startNextDevServer();
  
  // Wait for Next.js to be ready
  log('⏳ Waiting for Next.js server to be ready...', 'blue');
  await waitForNextJsServer();
  
  // Start HTTPS proxy
  const httpsServer = createHttpsProxy();
  
  // Graceful shutdown
  process.on('SIGINT', () => {
    log('\n🛑 Shutting down servers...', 'yellow');
    if (global.nextProcess) {
      global.nextProcess.kill();
    }
    httpsServer.close();
    process.exit(0);
  });
}

// Run the server
main().catch((error) => {
  log(`❌ Error starting HTTPS development server: ${error.message}`, 'red');
  process.exit(1);
});

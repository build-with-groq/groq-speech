#!/usr/bin/env node

/**
 * HTTPS Production Server for Groq Speech UI (Docker)
 * 
 * This script creates an HTTPS production server for the Docker container
 * to enable microphone access in browsers.
 * 
 * Features:
 * - Self-signed SSL certificates for local development
 * - Proxies to Next.js standalone server
 * - Microphone access enabled
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');

const HTTPS_PORT = 3443;
const NEXT_PORT = 3000;

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
  const certDir = path.join(__dirname, 'certs');
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

  log('🔐 Generating self-signed SSL certificate...', 'yellow');
  
  try {
    // Generate private key
    execSync(`openssl genrsa -out "${keyPath}" 2048`, { stdio: 'pipe' });
    
    // Generate certificate
    execSync(`openssl req -new -x509 -key "${keyPath}" -out "${certPath}" -days 365 -subj "/C=US/ST=CA/L=San Francisco/O=Groq Speech/OU=Development/CN=localhost"`, { stdio: 'pipe' });
    
    log('✅ SSL certificate generated successfully', 'green');
    return { keyPath, certPath };
  } catch (error) {
    log('❌ Failed to generate SSL certificates. Make sure OpenSSL is installed.', 'red');
    process.exit(1);
  }
}

function checkNextServerHealth() {
  return new Promise((resolve) => {
    // Try both localhost and 127.0.0.1
    const hosts = ['127.0.0.1', 'localhost'];
    let currentHost = 0;
    
    function tryNextHost() {
      if (currentHost >= hosts.length) {
        log('❌ Next.js server health check failed on all hosts', 'red');
        resolve(false);
        return;
      }
      
      const hostname = hosts[currentHost];
      log(`🔍 Trying health check on ${hostname}:${NEXT_PORT}...`, 'blue');
      
      const req = http.request({
        hostname: hostname,
        port: NEXT_PORT,
        path: '/',
        method: 'GET',
        timeout: 5000
      }, (res) => {
        log(`✅ Next.js server health check passed on ${hostname}`, 'green');
        resolve(true);
      });

      req.on('error', (err) => {
        log(`❌ Next.js server health check failed on ${hostname}: ${err.message}`, 'red');
        currentHost++;
        tryNextHost();
      });

      req.on('timeout', () => {
        log(`❌ Next.js server health check timeout on ${hostname}`, 'red');
        req.destroy();
        currentHost++;
        tryNextHost();
      });

      req.end();
    }
    
    tryNextHost();
  });
}

function startNextServer() {
  return new Promise((resolve, reject) => {
    log('🚀 Starting Next.js standalone server...', 'blue');
    
    const nextProcess = spawn('node', ['server.js'], {
      cwd: __dirname,
      stdio: 'pipe',
      env: { 
        ...process.env, 
        PORT: NEXT_PORT.toString(),
        HOSTNAME: '127.0.0.1',
        NODE_ENV: 'production'
      }
    });

    let serverStarted = false;

    nextProcess.stdout.on('data', (data) => {
      const output = data.toString();
      console.log(`[Next.js] ${output.trim()}`);
      if ((output.includes('Ready') || output.includes('started server on')) && !serverStarted) {
        serverStarted = true;
        log('✅ Next.js server is ready', 'green');
        resolve(nextProcess);
      }
    });

    nextProcess.stderr.on('data', (data) => {
      const output = data.toString();
      console.log(`[Next.js Error] ${output.trim()}`);
      if (output.includes('error') || output.includes('Error')) {
        log(`Next.js Error: ${output}`, 'red');
      }
    });

    nextProcess.on('close', (code) => {
      if (code !== 0) {
        log(`❌ Next.js server exited with code ${code}`, 'red');
        reject(new Error(`Next.js server exited with code ${code}`));
      }
    });

    nextProcess.on('error', (error) => {
      log(`❌ Failed to start Next.js server: ${error.message}`, 'red');
      reject(error);
    });

    // Store the process globally so we can access it
    global.nextProcess = nextProcess;
    
    // Timeout after 30 seconds
    setTimeout(() => {
      if (!serverStarted) {
        log('❌ Next.js server failed to start within 30 seconds', 'red');
        reject(new Error('Next.js server startup timeout'));
      }
    }, 30000);
  });
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

    // Proxy to Next.js server
    const proxyReq = http.request({
      hostname: '127.0.0.1',
      port: NEXT_PORT,
      path: req.url,
      method: req.method,
      headers: {
        ...req.headers,
        'host': `127.0.0.1:${NEXT_PORT}`
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

  server.listen(HTTPS_PORT, '0.0.0.0', () => {
    log('🎤 Groq Speech UI - HTTPS Production Server', 'bright');
    log('===============================================', 'bright');
    log('🔐 Generating self-signed SSL certificate...', 'yellow');
    log('✅ SSL certificate generated successfully', 'green');
    log('🚀 Starting Next.js server with HTTPS...', 'blue');
    log(`🔗 Access the UI at: https://localhost:${HTTPS_PORT}`, 'cyan');
    log('⚠️  Browser will show security warning for self-signed certificate', 'yellow');
    log('   Click "Advanced" → "Proceed to localhost" to continue', 'yellow');
    log('✅ Next.js app loaded successfully', 'green');
    log(`🚀 HTTPS server running on https://0.0.0.0:${HTTPS_PORT}`, 'green');
    log(`🔗 Access the UI at: https://localhost:${HTTPS_PORT}`, 'cyan');
    log('⚠️  Browser will show security warning for self-signed certificate', 'yellow');
    log('   Click "Advanced" → "Proceed to localhost" to continue', 'yellow');
  });

  return server;
}

async function main() {
  try {
    // Start Next.js server and wait for it to be ready
    await startNextServer();
    
    // Wait a moment for Next.js to fully initialize
    log('⏳ Waiting for Next.js to fully initialize...', 'blue');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Check if Next.js server is actually responding
    log('🔍 Checking Next.js server health...', 'blue');
    const isHealthy = await checkNextServerHealth();
    
    if (!isHealthy) {
      log('❌ Next.js server is not responding, retrying...', 'yellow');
      // Wait a bit more and try again
      await new Promise(resolve => setTimeout(resolve, 3000));
      const retryHealthy = await checkNextServerHealth();
      if (!retryHealthy) {
        throw new Error('Next.js server failed health check');
      }
    }
    
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

    process.on('SIGTERM', () => {
      log('\n🛑 Shutting down servers...', 'yellow');
      if (global.nextProcess) {
        global.nextProcess.kill();
      }
      httpsServer.close();
      process.exit(0);
    });
  } catch (error) {
    log(`❌ Failed to start servers: ${error.message}`, 'red');
    process.exit(1);
  }
}

// Run the server
main().catch((error) => {
  log(`❌ Error starting HTTPS production server: ${error.message}`, 'red');
  process.exit(1);
});
import type { NextConfig } from "next";
import { config as dotenvConfig } from 'dotenv';
import path from 'path';

// Load .env.ui from project root (two levels up from this file)
const rootDir = path.resolve(__dirname, '../..');
const envPath = path.join(rootDir, '.env.ui');
dotenvConfig({ path: envPath });

const nextConfig: NextConfig = {
  /* config options here */
  // Enable standalone output for Docker
  output: 'standalone',
  // Enable source maps for better debugging
  productionBrowserSourceMaps: false,
  // Enable webpack source maps in development
  webpack: (config, { dev, isServer }) => {
    if (dev && !isServer) {
      config.devtool = 'eval-source-map';
    }
    return config;
  },
  // Expose environment variables to the client
  env: {
    NEXT_PUBLIC_VERBOSE: process.env.NEXT_PUBLIC_VERBOSE,
    NEXT_PUBLIC_DEBUG: process.env.NEXT_PUBLIC_DEBUG,
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_FRONTEND_URL: process.env.NEXT_PUBLIC_FRONTEND_URL,
    NEXT_DEV_MODE: process.env.NEXT_DEV_MODE,
    NEXT_HOT_RELOAD: process.env.NEXT_HOT_RELOAD,
  },
  // Enable debugging
  experimental: {
    // Enable better debugging support
  },
  // Ensure proper source map generation
  typescript: {
    // Don't ignore TypeScript errors during build for debugging
    ignoreBuildErrors: false,
  },
  eslint: {
    // Don't ignore ESLint errors during build for debugging
    ignoreDuringBuilds: false,
  },
};

export default nextConfig;

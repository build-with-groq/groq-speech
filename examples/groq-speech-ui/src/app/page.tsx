'use client';

import { ClientOnly } from '@/components/ClientOnly';
import { DebugPanel } from '@/components/DebugPanel';
import { EnhancedSpeechDemo } from '@/components/EnhancedSpeechDemo';
import { uiLogger } from '@/lib/frontend-logger';
import { GroqAPIClient } from '@/lib/groq-api';
import { AlertCircle, CheckCircle, Info, Server } from 'lucide-react';
import { useEffect, useState } from 'react';

export default function Home() {
    const [useMockApi, setUseMockApi] = useState(false);
    const [isConfigured, setIsConfigured] = useState(false);
    const [showBackendConfig, setShowBackendConfig] = useState(false);
    const [backendStatus, setBackendStatus] = useState<'checking' | 'configured' | 'not-configured' | 'error'>('checking');
    const [errorMessage, setErrorMessage] = useState<string | null>(null);
    const [isClient, setIsClient] = useState(false);
    const [apiClient, setApiClient] = useState<GroqAPIClient | null>(null);

    useEffect(() => {
        setIsClient(true);
        
        // Test frontend logger explicitly
        uiLogger.info('Home page loaded - testing frontend logger', {
            timestamp: new Date().toISOString(),
            location: 'page.tsx',
            test: 'frontend-logger-test'
        });
        
        // Also test direct fetch to backend for debugging
        console.log('Testing direct fetch to backend logging endpoint...');
        fetch('http://localhost:8000/api/log', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                component: 'DIRECT_TEST',
                level: 'INFO',
                message: 'Direct fetch test from page.tsx',
                context: { test: 'direct-fetch', timestamp: new Date().toISOString() },
                timestamp: new Date().toISOString()
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log('Direct fetch response:', data);
        })
        .catch(error => {
            console.error('Direct fetch error:', error);
        });
        
        checkBackendConfiguration();
        
        // Check logging status after a delay
        setTimeout(() => {
            console.log('=== FRONTEND LOGGING STATUS ===');
        }, 3000);
    }, []);

    const checkBackendConfiguration = async () => {
        try {
            console.log('Starting backend configuration check...');
            setBackendStatus('checking');
            setErrorMessage(null);

            const client = new GroqAPIClient();
            setApiClient(client);

            // Check if backend is running and API key is configured
            console.log('Calling checkApiKeyConfigured...');
            const isConfigured = await client.checkApiKeyConfigured();
            console.log('checkApiKeyConfigured result:', isConfigured);

            if (isConfigured) {
                console.log('Backend is configured, setting status to configured');
                setBackendStatus('configured');
                setIsConfigured(true);
            } else {
                console.log('Backend is not configured, setting status to not-configured');
                setBackendStatus('not-configured');
                setIsConfigured(false);
            }
        } catch (error) {
            console.error('Backend configuration check failed:', error);
            setBackendStatus('error');
            setIsConfigured(false);
            setErrorMessage(error instanceof Error ? error.message : 'Unknown error occurred');
        }
    };

    const handleUseMockApi = () => {
        console.log('Toggling mock API, current state:', useMockApi);
        const newMockState = !useMockApi;
        setUseMockApi(newMockState);

        if (newMockState) {
            // When switching to mock API, don't require backend
            console.log('Enabling mock mode, setting isConfigured to true');
            setIsConfigured(true);
            setBackendStatus('configured');
        } else {
            // When switching back to real API, check backend
            console.log('Disabling mock mode, checking backend configuration');
            checkBackendConfiguration();
        }
    };

    const getBackendStatusMessage = () => {
        switch (backendStatus) {
            case 'checking':
                return 'Checking backend configuration...';
            case 'configured':
                return 'Backend API key is configured and ready';
            case 'not-configured':
                return 'Backend API key not configured';
            case 'error':
                return errorMessage || 'Cannot connect to backend server';
            default:
                return 'Unknown status';
        }
    };

    const getBackendStatusIcon = () => {
        switch (backendStatus) {
            case 'checking':
                return <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>;
            case 'configured':
                return <CheckCircle className="h-5 w-5 text-green-600" />;
            case 'not-configured':
                return <AlertCircle className="h-5 w-5 text-yellow-600" />;
            case 'error':
                return <AlertCircle className="h-5 w-5 text-red-600" />;
            default:
                return <AlertCircle className="h-5 w-5 text-gray-600" />;
        }
    };

    // Don't render anything until client-side hydration is complete
    if (!isClient) {
        return (
            <div className="min-h-screen bg-gray-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50">
            {/* Header */}
            <header className="bg-white shadow-sm border-b">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center py-6">
                        <div className="flex items-center">
                            <div className="flex-shrink-0">
                                <h1 className="text-2xl font-bold text-gray-900">
                                    Groq Speech Recognition Demo
                                </h1>
                            </div>
                        </div>

                        <div className="flex items-center space-x-4">
                            {/* Backend Status */}
                            <div className="flex items-center space-x-2">
                                {getBackendStatusIcon()}
                                <span className="text-sm font-medium">
                                    {getBackendStatusMessage()}
                                </span>
                            </div>

                            {/* Mock API Toggle */}
                            <label className="flex items-center space-x-2">
                                <input
                                    type="checkbox"
                                    checked={useMockApi}
                                    onChange={handleUseMockApi}
                                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                />
                                <span className="text-sm text-gray-700">Use Mock API</span>
                            </label>


                            {/* Backend Config Button */}
                            <button
                                onClick={() => setShowBackendConfig(!showBackendConfig)}
                                className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
                            >
                                <Server className="h-4 w-4 mr-1" />
                                Backend Config
                            </button>

                            {/* Refresh Button */}
                            <button
                                onClick={checkBackendConfiguration}
                                disabled={backendStatus === 'checking'}
                                className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                <div className={`h-4 w-4 mr-1 ${backendStatus === 'checking' ? 'animate-spin' : ''}`}>
                                    {backendStatus === 'checking' ? (
                                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                                    ) : (
                                        <div className="h-4 w-4 border-2 border-gray-400 rounded-full"></div>
                                    )}
                                </div>
                                Refresh
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Backend Configuration Instructions */}
            {showBackendConfig && (
                <div className="max-w-4xl mx-auto mt-8 px-4">
                    <div className="bg-white rounded-lg shadow-md border p-6">
                        <div className="flex items-center mb-4">
                            <Server className="h-6 w-6 text-blue-600 mr-2" />
                            <h2 className="text-xl font-semibold text-gray-900">
                                Backend Configuration
                            </h2>
                        </div>

                        {useMockApi ? (
                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                                <div className="flex items-start">
                                    <Info className="h-5 w-5 text-blue-600 mr-2 mt-0.5" />
                                    <div>
                                        <h3 className="text-sm font-medium text-blue-800">
                                            Mock API Mode
                                        </h3>
                                        <p className="text-sm text-blue-700 mt-1">
                                            You&apos;re currently using the mock API for demonstration purposes.
                                            This mode simulates speech recognition without requiring a backend server.
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                                    <div className="flex items-start">
                                        <AlertCircle className="h-5 w-5 text-yellow-600 mr-2 mt-0.5" />
                                        <div>
                                            <h3 className="text-sm font-medium text-yellow-800">
                                                Backend API Key Configuration
                                            </h3>
                                            <p className="text-sm text-yellow-700 mt-1">
                                                The Groq API key should be configured in the backend, not in the UI.
                                                This provides better security and easier management.
                                            </p>
                                        </div>
                                    </div>
                                </div>

                                <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
                                    <h3 className="text-sm font-medium text-gray-800 mb-2">
                                        How to Configure Backend API Key:
                                    </h3>
                                    <ol className="text-sm text-gray-700 space-y-2 list-decimal list-inside">
                                        <li>
                                            <strong>Create a .env file</strong> in the root directory of the groq-speech project:
                                            <pre className="bg-gray-100 p-2 rounded mt-1 text-xs">
                                                GROQ_API_KEY=your_actual_groq_api_key_here
                                            </pre>
                                        </li>
                                        <li>
                                            <strong>Start the backend server</strong>:
                                            <pre className="bg-gray-100 p-2 rounded mt-1 text-xs">
                                                cd groq-speech
                                                python -m api.server
                                            </pre>
                                        </li>
                                        <li>
                                            <strong>Verify the backend is running</strong> at http://localhost:8000
                                        </li>
                                        <li>
                                            <strong>Check the health endpoint</strong> to confirm API key is configured
                                        </li>
                                    </ol>
                                </div>

                                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                                    <div className="flex items-start">
                                        <CheckCircle className="h-5 w-5 text-green-600 mr-2 mt-0.5" />
                                        <div>
                                            <h3 className="text-sm font-medium text-green-800">
                                                Benefits of Backend Configuration
                                            </h3>
                                            <ul className="text-sm text-green-700 mt-1 space-y-1">
                                                <li>• API key is never exposed to the frontend</li>
                                                <li>• Centralized configuration management</li>
                                                <li>• Better security practices</li>
                                                <li>• Easier deployment and environment management</li>
                                            </ul>
                                        </div>
                                    </div>
                                </div>

                                <div className="flex justify-between">
                                    <button
                                        onClick={checkBackendConfiguration}
                                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                    >
                                        Check Backend Status
                                    </button>
                                    <button
                                        onClick={() => setShowBackendConfig(false)}
                                        className="px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
                                    >
                                        Close
                                    </button>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Main Content */}
            {isConfigured && (
                <main className="py-8">
                    <ClientOnly fallback={
                        <div className="max-w-6xl mx-auto p-6">
                            <div className="bg-white rounded-lg shadow-md border p-6">
                                <div className="animate-pulse">
                                    <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
                                    <div className="h-4 bg-gray-200 rounded w-1/2 mb-6"></div>
                                    <div className="h-12 bg-gray-200 rounded w-32 mx-auto"></div>
                                </div>
                            </div>
                        </div>
                    }>
                        <EnhancedSpeechDemo />
                    </ClientOnly>
                </main>
            )}

            {/* Instructions */}
            {!isConfigured && !showBackendConfig && (
                <div className="max-w-2xl mx-auto mt-8 px-4">
                    <div className="bg-white rounded-lg shadow-md border p-6">
                        <div className="text-center">
                            <Server className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                            <h2 className="text-xl font-semibold text-gray-900 mb-2">
                                Backend Configuration Required
                            </h2>
                            <p className="text-gray-600 mb-4">
                                Please configure the backend API key or enable mock mode to start using the speech recognition demo.
                            </p>
                            <div className="flex justify-center space-x-4">
                                <button
                                    onClick={() => setShowBackendConfig(true)}
                                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                                >
                                    Configure Backend
                                </button>
                                <button
                                    onClick={handleUseMockApi}
                                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500"
                                >
                                    Use Mock Mode
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Footer */}
            <footer className="bg-white border-t mt-12">
                <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                    <div className="text-center text-sm text-gray-500">
                        <p>
                            Groq Speech Recognition Demo - Built with Next.js and React
                        </p>
                        <p className="mt-1">
                            Features real-time transcription, translation, and performance metrics
                        </p>
                    </div>
                </div>
            </footer>

            {/* Debug Panel */}
            <DebugPanel
                backendStatus={backendStatus}
                useMockApi={useMockApi}
                isConfigured={isConfigured}
                errorMessage={errorMessage}
            />
        </div>
    );
}

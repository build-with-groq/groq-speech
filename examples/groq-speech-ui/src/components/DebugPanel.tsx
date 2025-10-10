'use client';

import { useState } from 'react';

interface DebugPanelProps {
    backendStatus: 'checking' | 'configured' | 'not-configured' | 'error';
    useMockApi: boolean;
    isConfigured: boolean;
    errorMessage: string | null;
}

export function DebugPanel({ backendStatus, useMockApi, isConfigured, errorMessage }: DebugPanelProps) {
    const [isVisible, setIsVisible] = useState(false);
    const [testResult, setTestResult] = useState<string>('');

    const testBackendConnection = async () => {
        setTestResult('Testing...');
        try {
            const response = await fetch('http://localhost:8000/health', {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                signal: AbortSignal.timeout(5000),
            });

            if (response.ok) {
                const data = await response.json();
                setTestResult(`✅ Success! Status: ${response.status}\nData: ${JSON.stringify(data, null, 2)}`);
            } else {
                setTestResult(`❌ Error! Status: ${response.status} ${response.statusText}`);
            }
        } catch (error) {
            setTestResult(`❌ Connection failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
        }
    };

    if (!isVisible) {
        return (
            <button
                onClick={() => setIsVisible(true)}
                className="fixed bottom-4 right-4 bg-gray-800 text-white px-3 py-2 rounded-md text-sm"
            >
                Debug
            </button>
        );
    }

    return (
        <div className="fixed bottom-4 right-4 bg-white border border-gray-300 rounded-lg shadow-lg p-4 max-w-md">
            <div className="flex justify-between items-center mb-3">
                <h3 className="text-sm font-semibold">Debug Panel</h3>
                <button
                    onClick={() => setIsVisible(false)}
                    className="text-gray-500 hover:text-gray-700"
                >
                    ✕
                </button>
            </div>

            <div className="space-y-2 text-xs">
                <div><strong>Backend Status:</strong> {backendStatus}</div>
                <div><strong>Mock API:</strong> {useMockApi ? 'Enabled' : 'Disabled'}</div>
                <div><strong>Is Configured:</strong> {isConfigured ? 'Yes' : 'No'}</div>
                {errorMessage && (
                    <div><strong>Error:</strong> {errorMessage}</div>
                )}
            </div>

            <div className="mt-3">
                <button
                    onClick={testBackendConnection}
                    className="bg-blue-600 text-white px-2 py-1 rounded text-xs"
                >
                    Test Backend
                </button>
            </div>

            {testResult && (
                <pre className="mt-2 text-xs bg-gray-100 p-2 rounded max-h-32 overflow-auto">
                    {testResult}
                </pre>
            )}
        </div>
    );
} 
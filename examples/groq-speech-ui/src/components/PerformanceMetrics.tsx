'use client';

import { PerformanceMetrics, TimingMetrics } from '@/types';
import { Activity, Clock, TrendingUp, Zap } from 'lucide-react';
import React from 'react';
import {
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    Legend,
    Line,
    LineChart,
    Pie,
    PieChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from 'recharts';

interface PerformanceMetricsProps {
    timingMetrics: TimingMetrics;
    performanceMetrics: PerformanceMetrics;
    recentResults: Array<{ timestamp: string; timing_metrics?: TimingMetrics }>;
}



export const PerformanceMetricsComponent: React.FC<PerformanceMetricsProps> = ({
    timingMetrics,
    performanceMetrics,
    recentResults,
}) => {
    const timingData = [
        {
            name: 'Microphone Capture',
            value: timingMetrics.microphone_capture || 0,
            color: '#0088FE',
        },
        {
            name: 'API Call',
            value: timingMetrics.api_call || 0,
            color: '#00C49F',
        },
        {
            name: 'Response Processing',
            value: timingMetrics.response_processing || 0,
            color: '#FFBB28',
        },
    ].filter(item => item.value > 0);

    const performanceData = [
        {
            name: 'Successful',
            value: performanceMetrics.successful_recognitions,
            color: '#00C49F',
        },
        {
            name: 'Failed',
            value: performanceMetrics.failed_recognitions,
            color: '#FF8042',
        },
    ];

    const recentTimingData = recentResults
        .filter(result => result.timing_metrics)
        .map((result, index) => ({
            name: `Result ${index + 1}`,
            total: result.timing_metrics?.total_time || 0,
            api: result.timing_metrics?.api_call || 0,
            processing: result.timing_metrics?.response_processing || 0,
        }))
        .slice(-10); // Last 10 results

    const formatTime = (ms: number) => {
        if (ms < 1000) return `${ms.toFixed(0)}ms`;
        return `${(ms / 1000).toFixed(2)}s`;
    };

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Total Time */}
                <div className="bg-white p-4 rounded-lg shadow-md border">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Total Time</p>
                            <p className="text-2xl font-bold text-blue-600">
                                {formatTime(timingMetrics.total_time || 0)}
                            </p>
                        </div>
                        <Clock className="h-8 w-8 text-blue-500" />
                    </div>
                </div>

                {/* API Call Time */}
                <div className="bg-white p-4 rounded-lg shadow-md border">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">API Call</p>
                            <p className="text-2xl font-bold text-green-600">
                                {formatTime(timingMetrics.api_call || 0)}
                            </p>
                        </div>
                        <Zap className="h-8 w-8 text-green-500" />
                    </div>
                </div>

                {/* Processing Time */}
                <div className="bg-white p-4 rounded-lg shadow-md border">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Processing</p>
                            <p className="text-2xl font-bold text-yellow-600">
                                {formatTime(timingMetrics.response_processing || 0)}
                            </p>
                        </div>
                        <Activity className="h-8 w-8 text-yellow-500" />
                    </div>
                </div>

                {/* Success Rate */}
                <div className="bg-white p-4 rounded-lg shadow-md border">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-sm font-medium text-gray-600">Success Rate</p>
                            <p className="text-2xl font-bold text-purple-600">
                                {performanceMetrics.total_requests > 0
                                    ? `${((performanceMetrics.successful_recognitions / performanceMetrics.total_requests) * 100).toFixed(1)}%`
                                    : '0%'}
                            </p>
                        </div>
                        <TrendingUp className="h-8 w-8 text-purple-500" />
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Timing Breakdown Chart */}
                <div className="bg-white p-6 rounded-lg shadow-md border">
                    <h3 className="text-lg font-semibold mb-4">Timing Breakdown</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                            <Pie
                                data={timingData}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={({ name, value }) => `${name}: ${formatTime(typeof value === 'number' ? value : 0)}`}
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey="value"
                            >
                                {timingData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                            <Tooltip formatter={(value) => formatTime(value as number)} />
                        </PieChart>
                    </ResponsiveContainer>
                </div>

                {/* Performance Distribution */}
                <div className="bg-white p-6 rounded-lg shadow-md border">
                    <h3 className="text-lg font-semibold mb-4">Recognition Results</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={performanceData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="value" fill="#8884d8" />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Recent Results Timeline */}
            {recentTimingData.length > 0 && (
                <div className="bg-white p-6 rounded-lg shadow-md border">
                    <h3 className="text-lg font-semibold mb-4">Recent Results Timeline</h3>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={recentTimingData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip formatter={(value) => formatTime(value as number)} />
                            <Legend />
                            <Line
                                type="monotone"
                                dataKey="total"
                                stroke="#8884d8"
                                name="Total Time"
                            />
                            <Line
                                type="monotone"
                                dataKey="api"
                                stroke="#82ca9d"
                                name="API Call"
                            />
                            <Line
                                type="monotone"
                                dataKey="processing"
                                stroke="#ffc658"
                                name="Processing"
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            )}

            {/* Detailed Statistics */}
            <div className="bg-white p-6 rounded-lg shadow-md border">
                <h3 className="text-lg font-semibold mb-4">Detailed Statistics</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                        <p className="text-gray-600">Total Requests</p>
                        <p className="font-semibold">{performanceMetrics.total_requests}</p>
                    </div>
                    <div>
                        <p className="text-gray-600">Successful</p>
                        <p className="font-semibold text-green-600">
                            {performanceMetrics.successful_recognitions}
                        </p>
                    </div>
                    <div>
                        <p className="text-gray-600">Failed</p>
                        <p className="font-semibold text-red-600">
                            {performanceMetrics.failed_recognitions}
                        </p>
                    </div>
                    <div>
                        <p className="text-gray-600">Avg Response Time</p>
                        <p className="font-semibold">
                            {formatTime(performanceMetrics.avg_response_time)}
                        </p>
                    </div>
                    <div>
                        <p className="text-gray-600">Audio Processing Time</p>
                        <p className="font-semibold">
                            {formatTime(performanceMetrics.audio_processing.avg_processing_time)}
                        </p>
                    </div>
                    <div>
                        <p className="text-gray-600">Total Chunks</p>
                        <p className="font-semibold">
                            {performanceMetrics.audio_processing.total_chunks}
                        </p>
                    </div>
                    <div>
                        <p className="text-gray-600">Buffer Size</p>
                        <p className="font-semibold">
                            {performanceMetrics.audio_processing.buffer_size}
                        </p>
                    </div>
                    <div>
                        <p className="text-gray-600">Success Rate</p>
                        <p className="font-semibold text-blue-600">
                            {performanceMetrics.total_requests > 0
                                ? `${((performanceMetrics.successful_recognitions / performanceMetrics.total_requests) * 100).toFixed(1)}%`
                                : '0%'}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}; 
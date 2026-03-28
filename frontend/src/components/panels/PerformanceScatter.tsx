"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { Zap, Activity } from "lucide-react";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

const mockScatterData = [
  { symbol: "RELIANCE", volume: 150000000, return: 3.24 },
  { symbol: "TCS", volume: 80000000, return: 1.88 },
  { symbol: "HDFCBANK", volume: 120000000, return: 0.85 },
  { symbol: "INFY", volume: 90000000, return: 2.10 },
  { symbol: "SBIN", volume: 110000000, return: 2.50 },
  { symbol: "WIPRO", volume: 45000000, return: -4.32 },
  { symbol: "ICICIBANK", volume: 70000000, return: -1.15 },
  { symbol: "TATAMOTORS", volume: 200000000, return: 5.42 },
  { symbol: "ASIANPAINT", volume: 30000000, return: -0.25 },
  { symbol: "ITC", volume: 60000000, return: 0.42 },
];

export const PerformanceScatter: React.FC<{ theme?: 'light' | 'dark' }> = ({ theme = "dark" }) => {
    const [isClient, setIsClient] = useState(false);
    useEffect(() => setIsClient(true), []);

    if (!isClient) return <div className="h-full flex items-center justify-center text-secondary-text">Plotting Neural Signal Array...</div>;

    const x = mockScatterData.map(d => d.volume);
    const y = mockScatterData.map(d => d.return);
    const size = mockScatterData.map(d => d.volume / 1000000); // Scale for size
    const labels = mockScatterData.map(d => d.symbol);
    const colors = mockScatterData.map(d => d.return >= 0 ? '#3D9970' : '#FF4136');

    const isLight = theme === 'light';

    return (
        <div className={`h-full w-full p-5 flex flex-col font-sans transition-colors ${isLight ? 'bg-white' : 'bg-[#050505]'}`}>
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <Activity size={18} className="text-secondary-text opacity-40" />
                    <h2 className={`text-[12px] font-black uppercase tracking-[0.3em] ${isLight ? 'text-primary-text' : 'text-[#f5f5f5]'}`}>Performance vs Volume</h2>
                </div>
            </div>

            <div className="flex-1">
                <Plot
                    data={[
                        {
                            x: x,
                            y: y,
                            mode: 'markers+text' as any,
                            text: labels,
                            textposition: 'top center',
                            marker: {
                                size: size,
                                color: colors,
                                opacity: 0.5,
                                line: { width: 1, color: isLight ? '#fff' : '#050505' }
                            },
                            hovertemplate: "<b>%{text}</b><br>Volume: ₹%{x:,.0f}<br>Return: %{y:.2f}%<extra></extra>",
                        }
                    ]}
                    layout={{
                        autosize: true,
                        paper_bgcolor: 'transparent',
                        plot_bgcolor: 'transparent',
                        margin: { t: 40, l: 60, r: 40, b: 60 },
                        showlegend: false,
                        font: { family: 'var(--font-sans)', size: 10, color: isLight ? '#1a1a1a' : '#fff' },
                        xaxis: { 
                            title: { text: "Trading Volume (Cr)", font: { size: 10 } }, 
                            gridcolor: isLight ? 'rgba(0,0,0,0.05)' : 'rgba(255,255,255,0.05)',
                            linecolor: isLight ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.1)',
                            type: 'log',
                            tickfont: { size: 9 }
                        },
                        yaxis: { 
                            title: { text: "Return %", font: { size: 10 } }, 
                            gridcolor: isLight ? 'rgba(0,0,0,0.05)' : 'rgba(255,255,255,0.05)',
                            linecolor: isLight ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.1)',
                            tickfont: { size: 9 }
                        },
                    }}
                    useResizeHandler={true}
                    className="w-full h-full"
                    style={{ width: '100%', height: '100%' }}
                    config={{ displayModeBar: false }}
                />
            </div>
        </div>
    );
};

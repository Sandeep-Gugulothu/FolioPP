"use client";

import React, { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import { TrendingUp, TrendingDown } from "lucide-react";

const Plot = dynamic(() => import("react-plotly.js"), { ssr: false });

const mockMovers = {
    date: "2026-03-28",
    gainers: [
        { symbol: "TATAMOTORS", change: 5.42 },
        { symbol: "RELIANCE", change: 3.24 },
        { symbol: "INFY", change: 2.85 },
        { symbol: "SBIN", change: 2.10 },
        { symbol: "TCS", change: 1.88 },
    ],
    losers: [
        { symbol: "WIPRO", change: -4.32 },
        { symbol: "ICICIBANK", change: -3.15 },
        { symbol: "HDFCBANK", change: -2.45 },
        { symbol: "AXISBANK", change: -1.90 },
        { symbol: "ITC", change: -1.20 },
    ]
};

export const MoversDashboard: React.FC<{ theme?: 'light' | 'dark' }> = ({ theme = "dark" }) => {
    const [isClient, setIsClient] = useState(false);
    useEffect(() => setIsClient(true), []);

    if (!isClient) return <div className="h-full flex items-center justify-center text-secondary-text">Loading Market Movers...</div>;

    const gLabels = mockMovers.gainers.map(d => d.symbol);
    const gValues = mockMovers.gainers.map(d => d.change);
    const lLabels = mockMovers.losers.map(d => d.symbol);
    const lValues = mockMovers.losers.map(d => d.change);

    const isLight = theme === 'light';

    return (
        <div className={`h-full w-full p-4 flex flex-col font-sans transition-colors ${isLight ? 'bg-white' : 'bg-[#050505]'}`}>
            <div className="flex items-center justify-between mb-4 px-2">
                <div className="flex items-center gap-2">
                    <TrendingUp size={16} className="text-emerald-500" />
                    <span className={`text-[11px] font-black uppercase tracking-[0.2em] ${isLight ? 'text-primary-text' : 'text-[#f5f5f5]'}`}>Top Movers</span>
                </div>
                <span className="text-[10px] font-bold text-secondary-text opacity-40 uppercase tracking-widest">{mockMovers.date}</span>
            </div>
            
            <div className="flex-1">
                <Plot
                    data={[
                        {
                            x: [...gLabels, ...lLabels],
                            y: [...gValues, ...lValues],
                            type: 'bar',
                            marker: { 
                                color: [...gValues.map(() => '#3D9970'), ...lValues.map(() => '#FF4136')],
                                opacity: 0.8 
                            },
                            hovertemplate: "%{x}: %{y}%<extra></extra>",
                        }
                    ]}
                    layout={{
                        autosize: true,
                        paper_bgcolor: 'transparent',
                        plot_bgcolor: 'transparent',
                        margin: { t: 40, l: 40, r: 20, b: 60 },
                        showlegend: false,
                        font: { family: 'var(--font-sans)', size: 10, color: isLight ? '#1a1a1a' : '#fff' },
                        xaxis: { 
                          tickfont: { size: 9 }, 
                          gridcolor: isLight ? 'rgba(0,0,0,0.05)' : 'rgba(255,255,255,0.05)',
                          linecolor: isLight ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.1)'
                        },
                        yaxis: { 
                          title: { text: "Return %", font: { size: 10 } }, 
                          gridcolor: isLight ? 'rgba(0,0,0,0.05)' : 'rgba(255,255,255,0.05)',
                          linecolor: isLight ? 'rgba(0,0,0,0.1)' : 'rgba(255,255,255,0.1)'
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

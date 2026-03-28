"use client";

import React from "react";
import { Zap, Activity } from "lucide-react";

const mockPulse = [
    { symbol: "RELIANCE", change: "+1.24%" },
    { symbol: "SBIN", change: "+0.85%" },
    { symbol: "HDFCBANK", change: "-0.32%" },
    { symbol: "TCS", change: "+2.10%" },
    { symbol: "AAPL", change: "+1.15%" },
    { symbol: "NVDA", change: "+4.20%" },
    { symbol: "TSLA", change: "-1.50%" },
    { symbol: "^NSEI", change: "+0.95%" },
    { symbol: "^BSESN", change: "+0.88%" },
    { symbol: "BTC-USD", change: "+2.45%" },
    { symbol: "INFY", change: "+0.55%" },
    { symbol: "ALPH", change: "+1.20%" },
    { symbol: "MSFT", change: "+0.75%" },
    { symbol: "TATAMOTORS", change: "+1.80%" },
];

export const PulseMonitor: React.FC<{ theme?: 'light' | 'dark' }> = ({ theme = "dark" }) => {
    const isLight = theme === 'light';

    return (
        <div className={`h-full w-full flex items-center overflow-hidden border-b border-primary-border relative group transition-colors ${isLight ? 'bg-white' : 'bg-[#050505]'}`}>
            <div className="flex-1 flex items-center whitespace-nowrap animate-pulse-scroll">
                {[...mockPulse, ...mockPulse].map((item, i) => (
                    <div key={i} className="flex items-center gap-6 px-10 border-r border-primary-border/10 group/item hover:bg-primary-text/[0.04] transition-colors cursor-crosshair">
                        <div className="flex items-center gap-2">
                             <span className={`text-[11px] font-black tracking-widest transition-colors uppercase ${isLight ? 'text-primary-text/80' : 'text-white/80'} group-hover/item:text-primary-text`}>
                                ${item.symbol}
                             </span>
                             <span className={`text-[10px] font-black p-1 rounded-sm ${item.change.startsWith('+') ? 'text-emerald-500' : 'text-rose-500'}`}>
                                {item.change}
                             </span>
                        </div>
                        <div className="w-[1px] h-3 bg-primary-border/20 rotate-12" />
                    </div>
                ))}
            </div>

            <style jsx global>{`
                @keyframes pulse-scroll {
                    0% { transform: translateX(0); }
                    100% { transform: translateX(-50%); }
                }
                .animate-pulse-scroll {
                    animation: pulse-scroll 60s linear infinite;
                }
                .animate-pulse-scroll:hover {
                    animation-play-state: paused;
                }
            `}</style>
        </div>
    );
};

"use client";

import React, { useState, useEffect } from "react";
import { Zap, ShieldCheck, Activity, ChevronRight } from "lucide-react";

interface Signal {
    id: string;
    ticker: string;
    type: 'LONG' | 'SHORT' | 'NEUTRAL';
    reasoning: string;
    confidence: number;
    volume: string;
    source: string;
    timestamp: string;
}

const generateMockSignal = (): Signal => {
    const tickers = ["RELIANCE", "TCS", "HDFCBANK", "INFY", "SBIN", "TATAMOTORS", "ITC", "WIPRO", "HCLTECH", "ICICIBANK"];
    const types: ('LONG' | 'SHORT' | 'NEUTRAL')[] = ['LONG', 'SHORT', 'NEUTRAL'];
    const reasons = [
        "Strong volume breakout on 15m timeframe.",
        "Institutional buying pressure increasing.",
        "Resistance level tested at previous day high.",
        "Consolidation pattern breaking to the upside.",
        "MACD signal line crossover detected.",
        "Heavy distribution observed at current levels.",
        "VSA signal: No Supply detected on retest.",
        "Oversold bounce expected from supply zone."
    ];
    
    return {
        id: Math.random().toString(36).substr(2, 9),
        ticker: tickers[Math.floor(Math.random() * tickers.length)],
        type: types[Math.floor(Math.random() * types.length)],
        reasoning: reasons[Math.floor(Math.random() * reasons.length)],
        confidence: 0.6 + Math.random() * 0.35,
        volume: `+${(Math.random() * 3).toFixed(1)}Cr`,
        source: "TELEMETRY-X",
        timestamp: "JUST NOW"
    };
};

export const SignalStream: React.FC<{ theme?: 'light' | 'dark' }> = ({ theme = "dark" }) => {
    const [signals, setSignals] = useState<Signal[]>([
        { id: '1', ticker: 'NIFTY 50', type: 'LONG', reasoning: 'Strong support at 24,000, indicators oversold.', confidence: 0.88, volume: '+1.2B', source: 'NSE-TEL', timestamp: '1m ago' },
        { id: '2', ticker: 'RELIANCE', type: 'NEUTRAL', reasoning: 'Sideways consolidation near 1,350.', confidence: 0.65, volume: '-0.3B', source: 'BSE-TEL', timestamp: '3m ago' },
        { id: '3', ticker: 'HDFCBANK', type: 'SHORT', reasoning: 'Failed breakout above overhead supply.', confidence: 0.72, volume: '+0.8B', source: 'NSE-TEL', timestamp: '5m ago' },
    ]);

    useEffect(() => {
        const interval = setInterval(() => {
            setSignals(prev => [generateMockSignal(), ...prev.slice(0, 19)]);
        }, 5000);
        return () => clearInterval(interval);
    }, []);

    const isLight = theme === 'light';

    return (
        <div className={`h-full font-sans flex items-center overflow-x-auto no-scrollbar gap-4 px-6 py-2 transition-colors ${isLight ? 'bg-white' : 'bg-[#050505]'}`}>
           {signals.map((sig) => (
               <div key={sig.id} className={`min-w-[400px] h-[180px] relative border flex flex-col p-5 group transition-all shrink-0 rounded-lg ${isLight ? 'bg-black/[0.02] border-black/5 hover:border-black/20' : 'bg-primary-bg border-white/5 hover:border-white/20'}`}>
                   {/* Corner Accents */}
                   <div className="absolute top-0 left-0 w-2 h-2 border-t border-l border-primary-text/20" />
                   <div className="absolute top-0 right-0 w-2 h-2 border-t border-r border-primary-text/20" />
                   <div className="absolute bottom-0 left-0 w-2 h-2 border-b border-l border-primary-text/20" />
                   <div className="absolute bottom-0 right-0 w-2 h-2 border-b border-r border-primary-text/20" />

                   <div className="flex items-center justify-between mb-4 border-b border-primary-text/5 pb-3">
                       <div className="flex items-center gap-3">
                           <div className={`w-1 h-6 ${
                               sig.type === 'LONG' ? 'bg-emerald-500' : 
                               sig.type === 'SHORT' ? 'bg-rose-500' : 'bg-primary-text/20'
                           } shadow-[0_0_10px_rgba(16,185,129,0.3)]`} />
                           <span className="text-[18px] font-black tracking-tighter text-primary-text uppercase italic">
                              {sig.ticker}
                           </span>
                       </div>
                       <div className="flex flex-col items-end">
                           <span className="text-[8px] font-black text-secondary-text uppercase tracking-[0.3em] opacity-40">Status</span>
                           <span className={`text-[10px] font-black ${
                               sig.type === 'LONG' ? 'text-emerald-500' : 
                               sig.type === 'SHORT' ? 'text-rose-500' : 'text-secondary-text'
                           }`}>
                              {sig.type}
                            </span>
                       </div>
                   </div>

                   <p className="flex-1 text-[11px] text-primary-text/60 leading-snug tracking-tight italic line-clamp-2 pr-4">
                       "{sig.reasoning}"
                   </p>

                   <div className="flex items-center justify-between mt-4">
                       <div className="flex gap-4">
                            <div className="flex flex-col">
                                <span className="text-[7px] font-black uppercase text-secondary-text tracking-widest opacity-40">Confidence</span>
                                <span className="text-[11px] font-black text-primary-text/80 tabular-nums">{Math.round(sig.confidence * 100)}%</span>
                            </div>
                            <div className="flex flex-col border-l border-primary-text/10 pl-4">
                                <span className="text-[7px] font-black uppercase text-secondary-text tracking-widest opacity-40">Institutional Delta</span>
                                <span className="text-[11px] font-black text-primary-text/80 tabular-nums">{sig.volume}</span>
                            </div>
                       </div>
                       <button className="p-2 border border-primary-text/10 hover:border-primary-text/40 transition-all opacity-20 hover:opacity-100">
                           <ChevronRight size={14} className="text-primary-text" />
                       </button>
                   </div>
               </div>
           ))}
        </div>
    );
};

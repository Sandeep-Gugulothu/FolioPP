"use client";

import React, { useState, useEffect } from "react";
import { TrendingUp, TrendingDown } from "lucide-react";

interface WatchlistItem {
  symbol: string;
  name: string;
  price?: number;
  change?: number;
  newsTitle?: string;
  newsUrl?: string;
}

export const Watchlist: React.FC<{ theme?: 'light' | 'dark' }> = ({ theme = "dark" }) => {
  const [items, setItems] = useState<WatchlistItem[]>([
    { symbol: "RELIANCE.NS", name: "Reliance Industries" },
    { symbol: "SBIN.NS", name: "State Bank of India" },
    { symbol: "HDFCBANK.NS", name: "HDFC Bank" },
    { symbol: "TCS.NS", name: "TATA Consultancy" },
    { symbol: "AAPL", name: "Apple Inc." },
    { symbol: "NVDA", name: "NVIDIA Corp" },
    { symbol: "TSLA", name: "Tesla, Inc." },
    { symbol: "^NSEI", name: "NIFTY 50" },
    { symbol: "^BSESN", name: "SENSEX" },
    { symbol: "BTC-USD", name: "Bitcoin" },
  ]);

  const isLight = theme === 'light';

  return (
    <div className={`h-full flex flex-col overflow-hidden animate-in fade-in duration-500 font-sans transition-colors ${isLight ? 'bg-white' : 'bg-[#050505]'}`}>
        <div className="flex-1 flex flex-col overflow-hidden bg-primary-bg transition-colors">
            {/* Table Header */}
            <div className={`grid grid-cols-4 px-8 py-3 border-b border-primary-border transition-colors ${isLight ? 'bg-black/[0.02]' : 'bg-white/[0.02]'}`}>
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-secondary-text">Instrument</span>
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-secondary-text text-right">LTP (₹/$)</span>
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-secondary-text text-right">Change %</span>
                <span className="text-[10px] font-black uppercase tracking-[0.2em] text-secondary-text text-right">Volume</span>
            </div>

            <div className="flex-1 overflow-y-auto no-scrollbar divide-y divide-primary-border/20">
               {items.map((item, i) => (
                 <div key={i} className={`grid grid-cols-4 px-8 py-4 transition-all group cursor-crosshair items-center border-l-2 border-transparent hover:border-l-primary-text/40 ${isLight ? 'hover:bg-black/[0.02]' : 'hover:bg-white/[0.03]'}`}>
                    <div className="flex flex-col">
                       <span className="text-[12px] font-black uppercase tracking-widest text-primary-text group-hover:opacity-100 opacity-80 transition-opacity">{item.symbol.split('.')[0]}</span>
                       <span className="text-[9px] font-bold truncate lowercase text-secondary-text opacity-40 tracking-tighter">{item.name}</span>
                    </div>
                    <div className="text-right font-black text-[13px] text-primary-text opacity-80 font-mono tabular-nums">1,240.50</div>
                    <div className="text-right text-[13px] font-black text-emerald-500 font-mono tabular-nums">+1.24%</div>
                    <div className="text-right text-[11px] font-bold text-secondary-text opacity-40 italic uppercase">2.4M</div>
                 </div>
               ))}
            </div>
        </div>
    </div>
  );
};

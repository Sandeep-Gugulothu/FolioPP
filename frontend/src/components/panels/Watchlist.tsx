"use client";

import React, { useState, useEffect } from "react";
import { Globe, TrendingUp, TrendingDown, Newspaper, ExternalLink, Zap, Activity } from "lucide-react";

interface WatchlistItem {
  symbol: string;
  name: string;
  price?: number;
  change?: number;
  newsTitle?: string;
  newsUrl?: string;
}

export const Watchlist: React.FC = () => {
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

  const [globalNews, setGlobalNews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // 1. Fetch Global News
        const newsRes = await fetch("http://localhost:8000/market/news");
        if (newsRes.ok) {
          const newsData = await newsRes.json();
          setGlobalNews(newsData);
        }

        // 2. Fetch Prices (Mock/Simulated or use existing quote endpoint)
        // In a real app, we'd hit /equity/quote for each or a batch
      } catch (err) {
        console.error("Watchlist fetch error", err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 60000); // Update every minute
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="h-full flex flex-col bg-primary-bg overflow-hidden animate-in fade-in duration-500">
      
      {/* 1. Market Heat Ticker (Top Bar) */}
      <div className="h-16 px-8 border-b border-primary-border flex items-center gap-10 overflow-x-auto no-scrollbar shrink-0 bg-primary-text/[0.01]">
         <div className="flex items-center gap-2 shrink-0">
            <Zap size={14} className="text-sky-400" />
            <span className="terminal-label">Market pulse</span>
         </div>
         {items.map((item, i) => (
           <div key={i} className="flex items-center gap-3 shrink-0 group cursor-pointer">
              <span className="text-[12px] font-black tracking-widest text-primary-text group-hover:text-sky-400 transition-colors uppercase">${item.symbol.split('.')[0]}</span>
              <span className="text-[11px] font-bold text-emerald-400 opacity-80">+1.24%</span>
           </div>
         ))}
      </div>

      <div className="flex-1 flex overflow-hidden">
        
        {/* 2. Global News Stream (Left Side) */}
        <div className="w-[50%] border-r border-primary-border flex flex-col h-full">
           <div className="px-6 py-4 border-b border-primary-border flex items-center justify-between">
              <div className="flex items-center gap-3">
                 <Newspaper size={16} className="text-secondary-text" />
                 <h3 className="terminal-h2">Global Feed</h3>
              </div>
              <span className="text-[9px] font-black bg-emerald-500/10 text-emerald-500 px-2 py-0.5 rounded-full border border-emerald-500/20">LIVE</span>
           </div>
           
           <div className="flex-1 overflow-y-auto no-scrollbar p-6 space-y-1.5">
              {globalNews.map((news, i) => (
                <div key={i} className="group cursor-pointer border-b border-primary-border pb-3 last:border-0 last:pb-0">
                   <div className="flex items-center gap-3 mb-1">
                      <span className="terminal-label text-emerald-500 opacity-100">
                        ${news.source_ticker?.split('.')[0] || 'GLOBAL'}
                      </span>
                      <span className="terminal-label opacity-20">/</span>
                      <span className="terminal-label">{news.source || 'REUTERS'}</span>
                   </div>
                   <h4 className="terminal-h3 leading-tight group-hover:text-blue-400 transition-colors">
                      {news.title}
                   </h4>
                   <p className="text-[12px] text-primary-text/40 leading-relaxed line-clamp-2 mt-1 italic font-medium">
                      {news.summary || "Institutional analysis pending for this signal..."}
                   </p>
                </div>
              ))}
           </div>
        </div>

        {/* 3. Ticker Details Grid (Right Side) - Professional Table */}
        <div className="flex-1 flex flex-col overflow-hidden bg-primary-bg">
            <div className="px-6 py-4 border-b border-primary-border flex items-center justify-between">
               <div className="flex items-center gap-3">
                  <Activity size={16} className="text-secondary-text" />
                  <h3 className="terminal-h2">PORTFOLIO OBSERVATION</h3>
               </div>
               <span className="terminal-label">{items.length} ASSETS</span>
            </div>

            {/* Table Header */}
            <div className="grid grid-cols-4 px-6 py-3 bg-primary-text/[0.02] border-b border-primary-border">
                <span className="terminal-label">Symbol / Name</span>
                <span className="terminal-label text-right">Price</span>
                <span className="terminal-label text-right">Change</span>
                <span className="terminal-label text-right">Volume</span>
            </div>

            <div className="flex-1 overflow-y-auto no-scrollbar divide-y divide-primary-border">
               {items.map((item, i) => (
                 <div key={i} className="grid grid-cols-4 px-6 py-4 hover:bg-primary-text/[0.03] transition-colors group cursor-pointer items-center">
                    <div className="flex flex-col">
                       <span className="terminal-h3 group-hover:text-blue-400 transition-colors uppercase">{item.symbol.split('.')[0]}</span>
                       <span className="text-[10px] terminal-label truncate lowercase opacity-20">{item.name}</span>
                    </div>
                    <div className="terminal-data text-right">₹1,240.50</div>
                    <div className="terminal-data text-right text-emerald-500">+1.24%</div>
                    <div className="terminal-data text-right opacity-40 italic">2.4M</div>
                 </div>
               ))}
            </div>
        </div>
      </div>
    </div>
  );
};

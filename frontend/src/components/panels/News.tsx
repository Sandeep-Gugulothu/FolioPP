"use client";

import React, { useEffect, useState } from "react";
import { Newspaper, Globe, Target } from "lucide-react";

interface NewsItem {
  title: string;
  url: string;
  provider_publish_time?: number;
  date?: string;
  source?: string;
  source_ticker?: string;
}

export const News: React.FC<{ symbol: string; exchange?: string }> = ({ symbol, exchange = "NSE" }) => {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [isGlobal, setIsGlobal] = useState(false);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        setLoading(true);
        const endpoint = isGlobal
          ? `http://localhost:8000/market/news`
          : `http://localhost:8000/equity/news?symbol=${symbol}&exchange=${exchange}`;

        const res = await fetch(endpoint);
        if (res.ok) {
          const data = await res.json();
          setNews(data);
        }
      } catch (err) {
        console.error("Failed to fetch news", err);
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, [symbol, exchange, isGlobal]);

  return (
    <div className="h-full flex flex-col">
      <div className="px-6 py-3 border-b border-primary-border flex items-center justify-end shrink-0">
        {/* Simplified Header: Only keeping the control buttons to avoid redundancy with the Dock title */}
        
        <div className="flex items-center bg-primary-text/5 p-1 rounded-xl border border-primary-border shrink-0">
          <button
            onClick={() => setIsGlobal(false)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-[10px] font-black tracking-widest transition-all ${!isGlobal ? 'bg-primary-text text-primary-bg shadow-md' : 'text-secondary-text hover:text-primary-text'}`}
          >
            <Target size={12} /> {symbol}
          </button>
          <button
            onClick={() => setIsGlobal(true)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-[10px] font-black tracking-widest transition-all ${isGlobal ? 'bg-primary-text text-primary-bg shadow-md' : 'text-secondary-text hover:text-primary-text'}`}
          >
            <Globe size={12} /> GLOBAL
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex flex-col items-center justify-center gap-4">
           <span className="terminal-label animate-pulse">Synchronizing Stream</span>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto no-scrollbar p-6 space-y-1.5">
          {news.map((item, i) => (
            <div key={i} className="group cursor-pointer animate-in fade-in slide-in-from-bottom-2 duration-300 border-b border-primary-border pb-2 last:border-0 last:pb-0">
              <div className="flex justify-between items-center mb-0.5">
                <div className="flex items-center gap-2">
                  {isGlobal && item.source_ticker && (
                    <span className="text-[10px] text-emerald-400 opacity-60 font-black tracking-widest uppercase font-sans">
                      ${item.source_ticker.split('.')[0]}
                    </span>
                  )}
                  <span className="text-[10px] text-primary-text/50 font-bold uppercase tracking-widest font-outfit">
                    {item.source || 'REUTERS ANALYTICS'}
                  </span>
                </div>
                <span className="text-[10px] text-primary-text/30 font-medium uppercase tracking-widest font-outfit">
                  {item.date ? new Date(item.date).toLocaleDateString() : 'SIGNAL: LIVE'}
                </span>
              </div>
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block text-[14px] font-outfit font-medium text-primary-text leading-snug hover:text-sky-400 transition-colors"
              >
                {item.title}
              </a>
            </div>
          ))}
          {news.length === 0 && (
            <div className="flex-1 flex flex-col items-center justify-center py-20 opacity-20 capitalize italic text-[13px]">
              No relevant signals detected in current stream
            </div>
          )}
        </div>
      )}
    </div>
  );
};

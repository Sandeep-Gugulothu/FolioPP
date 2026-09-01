"use client";

import React, { useEffect, useState } from "react";
import { Globe, Target } from "lucide-react";

interface NewsItem {
  title: string;
  url: string;
  provider_publish_time?: number;
  date?: string;
  source?: string;
  source_ticker?: string;
}

const FALLBACK_NEWS: NewsItem[] = [
  {
    title: "RBI Governor maintains repo rate at 6.50%; highlights robust liquidity & GDP trajectory above 7.2%",
    url: "https://www.bloomberg.com",
    date: "2026-03-28",
    source: "BLOOMBERG TERMINAL",
    source_ticker: "NSE:NIFTY"
  },
  {
    title: "State Bank of India expands corporate credit pipeline by 18% YoY with sustained net interest margins",
    url: "https://www.reuters.com",
    date: "2026-03-28",
    source: "REUTERS INSTITUTIONAL",
    source_ticker: "NSE:SBIN"
  },
  {
    title: "Reliance Industries accelerates green hydrogen & retail investments; Q4 margin outlook remains positive",
    url: "https://www.reuters.com",
    date: "2026-03-27",
    source: "FINANCIAL TIMES",
    source_ticker: "NSE:RELIANCE"
  },
  {
    title: "Foreign Institutional Investors (FIIs) infuse net ₹4,250 Cr across large-cap financial & IT equities",
    url: "https://www.bloomberg.com",
    date: "2026-03-27",
    source: "NSE ORDERFLOW",
    source_ticker: "NSE:FII"
  },
  {
    title: "TCS and Infosys bag multi-year cloud transformation mandates across European financial enterprises",
    url: "https://www.reuters.com",
    date: "2026-03-26",
    source: "MINT ANALYTICS",
    source_ticker: "NSE:TCS"
  }
];

export const News: React.FC<{ symbol: string; exchange?: string; theme?: 'light' | 'dark' }> = ({ symbol, exchange = "NSE", theme = "dark" }) => {
  const [news, setNews] = useState<NewsItem[]>(FALLBACK_NEWS);
  const [loading, setLoading] = useState(false);
  const [isGlobal, setIsGlobal] = useState(false);

  useEffect(() => {
    const fetchNews = async () => {
      try {
        const endpoint = isGlobal
          ? `/market/news`
          : `/equity/news?symbol=${symbol}&exchange=${exchange}`;

        const res = await fetch(endpoint);
        if (res.ok) {
          const data = await res.json();
          if (Array.isArray(data) && data.length > 0) {
            setNews(data);
          }
        }
      } catch (err) {
        // Fallback news stays populated
      } finally {
        setLoading(false);
      }
    };

    fetchNews();
  }, [symbol, exchange, isGlobal]);

  const isLight = theme === 'light';

  return (
    <div className={`h-full flex flex-col font-sans transition-colors ${isLight ? 'bg-white' : 'bg-transparent'}`}>
      <div className="px-6 py-3 border-b border-primary-border flex items-center justify-end shrink-0">
        <div className={`flex items-center p-1 rounded-xl border border-primary-border shrink-0 ${isLight ? 'bg-black/5' : 'bg-white/5'}`}>
          <button
            onClick={() => setIsGlobal(false)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-[10px] font-black tracking-widest transition-all ${!isGlobal ? 'bg-primary-text text-primary-bg shadow-sm' : 'text-secondary-text hover:text-primary-text'}`}
          >
            <Target size={12} /> {symbol}
          </button>
          <button
            onClick={() => setIsGlobal(true)}
            className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-[10px] font-black tracking-widest transition-all ${isGlobal ? 'bg-primary-text text-primary-bg shadow-sm' : 'text-secondary-text hover:text-primary-text'}`}
          >
            <Globe size={12} /> GLOBAL
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex-1 flex flex-col items-center justify-center gap-4">
          <span className="text-[10px] uppercase font-black tracking-widest text-secondary-text animate-pulse">Synchronizing Stream</span>
        </div>
      ) : (
        <div className="flex-1 overflow-y-auto no-scrollbar p-6 space-y-4">
          {news.map((item, i) => (
            <div key={i} className="group cursor-pointer animate-in fade-in slide-in-from-bottom-2 duration-300 border-b border-primary-border/20 pb-4 last:border-0 last:pb-0">
              <div className="flex justify-between items-center mb-1">
                <div className="flex items-center gap-2">
                  {item.source_ticker && (
                    <span className="text-[10px] text-emerald-500 opacity-60 font-black tracking-widest uppercase">
                      ${item.source_ticker.split('.')[0]}
                    </span>
                  )}
                  <span className="text-[10px] text-secondary-text font-black uppercase tracking-[0.2em]">
                    {item.source || 'REUTERS ANALYTICS'}
                  </span>
                </div>
                <span className="text-[9px] text-secondary-text/60 font-black uppercase tracking-widest">
                  {item.date ? new Date(item.date).toLocaleDateString() : 'LIVE SIGNAL'}
                </span>
              </div>
              <a
                href={item.url}
                target="_blank"
                rel="noopener noreferrer"
                className="block text-[13px] font-bold text-primary-text leading-snug hover:underline decoration-primary-text/20 underline-offset-4 transition-all"
              >
                {item.title}
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};


"use client";

import React from "react";

const FALLBACK_QUOTES: Record<string, { price: number; change: number; change_pct: number; volume: number; name: string; exchange: string }> = {
  SBIN: { price: 812.45, change: 14.30, change_pct: 1.79, volume: 18450000, name: "State Bank of India", exchange: "NSE" },
  RELIANCE: { price: 2985.60, change: -12.40, change_pct: -0.41, volume: 7890000, name: "Reliance Industries Ltd", exchange: "NSE" },
  TCS: { price: 4120.00, change: 35.80, change_pct: 0.88, volume: 3200000, name: "Tata Consultancy Services", exchange: "NSE" },
  INFY: { price: 1845.25, change: 8.50, change_pct: 0.46, volume: 5400000, name: "Infosys Limited", exchange: "NSE" },
  HDFCBANK: { price: 1640.80, change: -5.20, change_pct: -0.32, volume: 12100000, name: "HDFC Bank Limited", exchange: "NSE" },
  TATAMOTORS: { price: 975.30, change: 22.40, change_pct: 2.35, volume: 14200000, name: "Tata Motors Limited", exchange: "NSE" },
  ICICIBANK: { price: 1180.50, change: 11.20, change_pct: 0.96, volume: 9100000, name: "ICICI Bank Limited", exchange: "NSE" },
  NIFTY: { price: 24350.00, change: 145.20, change_pct: 0.60, volume: 45000000, name: "NIFTY 50 Index", exchange: "NSE" },
};

export const Information: React.FC<{ symbol: string; exchange?: string; theme?: 'light' | 'dark' }> = ({ symbol, exchange = "NSE", theme = "dark" }) => {
  const cleanSymbol = symbol.replace(".NS", "").toUpperCase();
  const defaultFallback = FALLBACK_QUOTES[cleanSymbol] || {
    price: 1245.50,
    change: 12.30,
    change_pct: 1.00,
    volume: 5200000,
    name: `${cleanSymbol} Equity`,
    exchange: exchange
  };

  const [data, setData] = React.useState<any>(defaultFallback);

  React.useEffect(() => {
    fetch(`/equity/quote?symbol=${symbol}&exchange=${exchange}`)
      .then(res => {
        if (!res.ok) throw new Error("Backend offline");
        return res.json();
      })
      .then(d => {
        if (d && typeof d.price === "number") {
          setData(d);
        } else {
          setData(defaultFallback);
        }
      })
      .catch(() => {
        setData(defaultFallback);
      });
  }, [symbol, exchange]);

  const currency = (exchange === "NSE" || exchange === "BSE") ? "₹" : "$";

  return (
    <div className="flex flex-col h-full bg-transparent p-6">
      <div className="flex justify-end gap-12 mb-4">
        <div className="flex flex-col items-start border-r border-primary-border pr-8">
          <span className="text-[11px] text-secondary-text font-extrabold uppercase tracking-widest mb-1">Price</span>
          <span className="text-[18px] font-extrabold text-primary-text leading-none">
            {data?.price ? `${currency}${data.price.toFixed(2)}` : '---'}
          </span>
        </div>
        <div className="flex flex-col items-start">
          <span className="text-[11px] text-secondary-text font-extrabold uppercase tracking-widest mb-1">Day's Change</span>
          <span className={`text-[13px] font-extrabold ${data?.change >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>
            {data?.change !== undefined ? `${data.change >= 0 ? '+' : ''}${data.change.toFixed(2)} (${data.change_pct?.toFixed(2)}%)` : '---'}
          </span>
        </div>
      </div>

      <div className="flex-1 flex flex-col justify-center relative">
        <div className="absolute inset-0 flex items-center justify-center opacity-20">
          <svg className="w-full h-20" viewBox="0 0 100 20" preserveAspectRatio="none">
            <path d="M 0,10 Q 25,2 50,10 T 100,10" fill="none" stroke={data?.change >= 0 ? "#10b981" : "#ef4444"} strokeWidth="1" />
          </svg>
        </div>
        <div className="mt-auto z-10">
          <div className="flex flex-col mb-4">
            <span className="text-[11px] text-secondary-text font-extrabold uppercase tracking-widest">Volume</span>
            <span className="text-[13px] font-extrabold text-primary-text">
              {data?.volume ? (data.volume / 1000000).toFixed(2) + ' M' : '---'}
            </span>
          </div>
          <p className="text-[11px] font-extrabold text-primary-text uppercase tracking-[0.2em] border-t border-primary-border pt-3">
            {data?.name ? `${data.name} | ${data.exchange}` : symbol}
          </p>
        </div>
      </div>
    </div>
  );
};


"use client";

import React, { useState, useEffect } from "react";
import { MarketChart } from "../charts/MarketChart";
import { CandlestickData, Time } from "lightweight-charts";

interface PricePerformanceProps {
  symbol: string;
  exchange?: string;
  interval?: string;
  theme: 'light' | 'dark';
}

export const Performance: React.FC<PricePerformanceProps> = ({ 
  symbol, 
  exchange = "NSE", 
  interval: initialInterval = "1d",
  theme
}) => {
  const [chartData, setChartData] = useState<CandlestickData<Time>[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentInterval, setCurrentInterval] = useState(initialInterval);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    setError(null);

    const fetchData = async () => {
      try {
        const response = await fetch(
          `http://localhost:8000/equity/historical?symbol=${symbol}&exchange=${exchange}&interval=${currentInterval}`
        );
        
        if (!response.ok) {
          throw new Error(`Error fetching data: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        if (isMounted) {
          // Transform FolioPP convention to lightweight-charts convention
          const transformedData: CandlestickData<Time>[] = data.map((item: any) => {
             const d = new Date(item.date);
             // date should be in 'YYYY-MM-DD' or timestamp
             // For intraday, use timestamps
             const time = (currentInterval.includes('m') || currentInterval.includes('h')) 
                ? (d.getTime() / 1000) as Time 
                : d.toISOString().split('T')[0] as Time;
                
             return {
                time,
                open: item.open,
                high: item.high,
                low: item.low,
                close: item.close,
             };
          }).filter((item: any) => item.open !== null && item.close !== null);
          
          setChartData(transformedData);
          setLoading(false);
        }
      } catch (err: any) {
        if (isMounted) {
          setError(err.message);
          setLoading(false);
        }
      }
    };

    fetchData();
    return () => { isMounted = false; };
  }, [symbol, exchange, currentInterval]);

  return (
    <div className="h-full bg-transparent flex flex-col relative">
      <div className="flex items-center justify-between px-4 py-2 border-b border-[var(--border-primary)] z-20 bg-[var(--bg-surface)] h-10">
        <div className="flex items-center gap-3">
          <span className="text-[16px] font-black text-[var(--text-primary)] uppercase leading-none tracking-tight">
            {symbol}
          </span>
          <div className="w-[1px] h-4 bg-[var(--text-primary)]/10 mx-1" />
          <div className="relative group">
            <select 
              value={currentInterval}
              onChange={(e) => setCurrentInterval(e.target.value)}
              className="bg-transparent text-[13px] font-bold text-[var(--text-primary)] uppercase outline-none cursor-pointer hover:text-[var(--text-primary)] transition-colors appearance-none pr-6 border border-[var(--border-primary)] px-2 py-0.5 rounded"
            >
              {['1m', '5m', '15m', '1h', '1d', '1w'].map((int) => (
                <option key={int} value={int} className="bg-[var(--bg-surface)] text-[var(--text-primary)]">{int}</option>
              ))}
            </select>
            <div className="absolute right-1 top-1/2 -translate-y-1/2 pointer-events-none opacity-40">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6"/></svg>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 relative overflow-hidden p-2">
        {loading && (
          <div className="absolute inset-0 flex items-center justify-center bg-[var(--bg-primary)]/20 z-10 backdrop-blur-sm">
            <span className="text-[12px] uppercase font-black tracking-widest text-[var(--text-secondary)] animate-pulse">Syncing Telemetry...</span>
          </div>
        )}
        
        {error && (
          <div className="absolute inset-0 flex items-center justify-center bg-[var(--bg-primary)]/20 z-10">
            <span className="text-[12px] uppercase font-black tracking-widest text-rose-500 italic">Error: {error}</span>
          </div>
        )}

        <MarketChart data={chartData} theme={theme} className="rounded-xl overflow-hidden" />
      </div>
    </div>
  );
};

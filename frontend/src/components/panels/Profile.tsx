"use client";

import React, { useState, useEffect } from "react";

export const Profile: React.FC<{ symbol: string; exchange?: string }> = ({ symbol, exchange = "NSE" }) => {
  const [data, setData] = useState<any>(null);
  const [metrics, setMetrics] = useState<any>(null);

  useEffect(() => {
    fetch(`http://localhost:8000/equity/profile?symbol=${symbol}&exchange=${exchange}`)
      .then(res => res.json())
      .then(setData)
      .catch(console.error);

    fetch(`http://localhost:8000/equity/key-metrics?symbol=${symbol}&exchange=${exchange}`)
      .then(res => res.json())
      .then(setMetrics)
      .catch(console.error);
  }, [symbol, exchange]);

  if (!data) return <div className="p-6 text-secondary-text text-[12px] animate-pulse uppercase tracking-widest">Synchronizing Profile...</div>;

  return (
    <div className="h-full p-6 overflow-y-auto no-scrollbar">
      <div className="space-y-6 mb-8">
        <div className="space-y-1 mb-4">
          <h3 className="terminal-h1">{data.name || symbol}</h3>
          <p className="terminal-body opacity-60">{data.address}, {data.city}</p>
          <p className="terminal-body opacity-60 underline underline-offset-4 cursor-pointer">{data.phone}, {data.website}</p>
        </div>

        <div className="grid grid-cols-2 gap-y-4 gap-x-8 mb-6">
          <div className="space-y-2">
            <p><span className="terminal-label">Sector:</span> <span className="terminal-data">{data.sector || 'N/A'}</span></p>
            <p><span className="terminal-label">Industry:</span> <span className="terminal-data">{data.industry || 'N/A'}</span></p>
            <p><span className="terminal-label">Employees:</span> <span className="terminal-data">{data.employees?.toLocaleString('en-IN') || 'N/A'}</span></p>
          </div>

          <div className="space-y-2 border-l border-primary-border pl-8">
            <p><span className="terminal-label">Market Cap:</span> <span className="terminal-data">{formatValue(metrics?.market_cap)}</span></p>
            <p><span className="terminal-label">P/E Ratio:</span> <span className="terminal-data">{metrics?.pe_ratio?.toFixed(2) || 'N/A'}</span></p>
            <p><span className="terminal-label">52W Return:</span> <span className={`terminal-data ${metrics?.price_return_1y >= 0 ? 'text-emerald-500' : 'text-rose-500'}`}>{metrics?.price_return_1y ? (metrics.price_return_1y * 100).toFixed(2) + '%' : 'N/A'}</span></p>
          </div>
        </div>
      </div>

      <div className="border-t border-primary-border pt-6">
        <h4 className="terminal-h2 mb-4">About Company</h4>
        <p className="terminal-body">
          {data.description || 'No summary available.'}
        </p>
      </div>
    </div>
  );
};

const formatValue = (val: number | null) => {
  if (val == null) return "N/A";
  if (val >= 1e12) return "₹" + (val / 1e12).toFixed(2) + " T";
  if (val >= 1e7) return "₹" + (val / 1e7).toFixed(2) + " Cr";
  return "₹" + val.toLocaleString();
};

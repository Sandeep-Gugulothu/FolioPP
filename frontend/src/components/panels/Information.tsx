"use client";

import React from "react";

export const Information: React.FC<{ symbol: string; exchange?: string }> = ({ symbol, exchange = "NSE" }) => {
  const [data, setData] = React.useState<any>(null);

  React.useEffect(() => {
    fetch(`http://localhost:8000/equity/quote?symbol=${symbol}&exchange=${exchange}`)
      .then(res => res.json())
      .then(setData)
      .catch(console.error);
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

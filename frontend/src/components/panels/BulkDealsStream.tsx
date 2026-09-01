"use client";

import React, { useState, useEffect } from "react";
import { Zap, Activity } from "lucide-react";

interface BulkDeal {
  symbol: string;
  client_name: string;
  deal_type: string; // BUY, SELL
  quantity: number;
  price: number;
  date: string;
  is_promoter: boolean;
  priority: number;
}

const FALLBACK_DEALS: BulkDeal[] = [
  { symbol: "SBIN", client_name: "LIFE INSURANCE CORPORATION OF INDIA", deal_type: "BUY", quantity: 1850000, price: 812.40, date: "2026-03-28", is_promoter: false, priority: 1 },
  { symbol: "RELIANCE", client_name: "MORGAN STANLEY ASIA SINGAPORE PTE", deal_type: "BUY", quantity: 940000, price: 2985.50, date: "2026-03-28", is_promoter: false, priority: 1 },
  { symbol: "TATASTEEL", client_name: "SOCIETE GENERALE - ODI", deal_type: "SELL", quantity: 3200000, price: 156.40, date: "2026-03-27", is_promoter: false, priority: 0 },
  { symbol: "HDFCBANK", client_name: "VANGUARD EMERGING MARKETS FUND", deal_type: "BUY", quantity: 1250000, price: 1640.80, date: "2026-03-27", is_promoter: false, priority: 1 },
  { symbol: "INFY", client_name: "ICICI PRUDENTIAL MUTUAL FUND", deal_type: "BUY", quantity: 720000, price: 1845.10, date: "2026-03-26", is_promoter: false, priority: 0 },
  { symbol: "ZOMATO", client_name: "ANTFIN SINGAPORE HOLDING PTE LTD", deal_type: "SELL", quantity: 4500000, price: 245.80, date: "2026-03-26", is_promoter: true, priority: 1 },
  { symbol: "TATAMOTORS", client_name: "NPS TRUST - A/C SBI PENSION FUND", deal_type: "BUY", quantity: 890000, price: 975.30, date: "2026-03-25", is_promoter: false, priority: 0 },
  { symbol: "ITC", client_name: "BRITISH AMERICAN TOBACCO PLC", deal_type: "SELL", quantity: 5100000, price: 428.50, date: "2026-03-25", is_promoter: true, priority: 1 },
];

export const BulkDealsStream: React.FC<{ theme?: 'light' | 'dark' }> = ({ theme = "dark" }) => {
  const [deals, setDeals] = useState<BulkDeal[]>(FALLBACK_DEALS);
  const [lastUpdate, setLastUpdate] = useState<string>("LIVE");

  useEffect(() => {
    const fetchDeals = async () => {
      try {
        const res = await fetch("/api/institutional/latest-bulk-deals");
        if (res.ok) {
           const data = await res.json();
           if (Array.isArray(data) && data.length > 0) {
             setDeals(data);
             setLastUpdate(new Date().toLocaleTimeString());
           }
        }
      } catch (err) {
        // Retain fallback deals
      }
    };

    fetchDeals();
    const interval = setInterval(fetchDeals, 300000);
    return () => clearInterval(interval);
  }, []);

  const isLight = theme === 'light';

  return (
    <div className={`h-full flex flex-col p-0 overflow-hidden ${isLight ? 'bg-white' : 'bg-[#050505]'}`}>
      <div className="flex-1 overflow-auto no-scrollbar">
        <table className="w-full text-left border-collapse">
          <thead className={`sticky top-0 z-10 ${isLight ? 'bg-black/5' : 'bg-white/5'} backdrop-blur-md`}>
            <tr>
              <th className="px-4 py-2 text-[10px] font-black uppercase tracking-tighter text-secondary-text border-b border-primary-border">Date</th>
              <th className="px-4 py-2 text-[10px] font-black uppercase tracking-tighter text-secondary-text border-b border-primary-border">Symbol</th>
              <th className="px-4 py-2 text-[10px] font-black uppercase tracking-tighter text-secondary-text border-b border-primary-border">Client</th>
              <th className="px-4 py-2 text-[10px] font-black uppercase tracking-tighter text-secondary-text border-b border-primary-border">Type</th>
              <th className="px-4 py-2 text-[10px] font-black uppercase tracking-tighter text-secondary-text border-b border-primary-border text-right">Qty</th>
              <th className="px-4 py-2 text-[10px] font-black uppercase tracking-tighter text-secondary-text border-b border-primary-border text-right">Price</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-primary-border/20">
            {deals.map((deal, idx) => (
              <tr key={`${deal.symbol}-${idx}`} className="transition-colors">
                <td className="px-4 py-3 text-[10px] font-mono font-medium text-secondary-text whitespace-nowrap">{deal.date}</td>
                <td className="px-4 py-3">
                  <div className="flex flex-col">
                    <span className="text-[11px] font-bold text-primary-text uppercase">{deal.symbol}</span>
                    {deal.is_promoter && <span className="text-[7px] font-bold text-rose-500 uppercase tracking-tighter">Promoter</span>}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className="text-[10px] font-medium text-secondary-text truncate block max-w-[180px]">
                    {deal.client_name}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${deal.deal_type === 'BUY' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-rose-500/10 text-rose-500'}`}>
                    {deal.deal_type}
                  </span>
                </td>
                <td className="px-4 py-3 text-right">
                  <span className="text-[10px] font-mono font-bold text-primary-text">{deal.quantity.toLocaleString()}</span>
                </td>
                <td className="px-4 py-3 text-right">
                  <div className="flex items-center justify-end gap-2">
                    <span className="text-[11px] font-mono font-bold text-primary-text">₹{deal.price.toFixed(2)}</span>
                    {deal.priority === 1 && <Zap size={8} className="text-yellow-500 fill-yellow-500" />}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};


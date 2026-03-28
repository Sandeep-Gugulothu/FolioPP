"use client";

import React, { useState, useEffect } from "react";
import { Server, Users, Database, Activity, ShieldCheck, Database as DBIcon, Clock, Zap } from "lucide-react";

export function AdminDashboard() {
  const [stats, setStats] = useState<any>(null);
  const [rawTickers, setRawTickers] = useState<any[]>([]);
  const [rawDeals, setRawDeals] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchAllData = async () => {
      try {
        const [statsRes, tickersRes, dealsRes] = await Promise.all([
          fetch("/api/admin/stats"),
          fetch("/api/admin/raw/tickers?limit=20"),
          fetch("/api/admin/raw/deals?limit=20")
        ]);
        
        setStats(await statsRes.json());
        setRawTickers(await tickersRes.json());
        setRawDeals(await dealsRes.json());
      } catch (err) {
        console.error("Admin data fetch failed:", err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAllData();
    const interval = setInterval(fetchAllData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading || !stats) {
    return (
      <div className="flex items-center justify-center h-full text-[#ffffff] bg-[#09090b]">
        <Activity className="animate-pulse mr-2" /> 
        <span className="font-black uppercase tracking-widest text-[10px]">Accessing System Interior...</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-[#09090b] p-8 overflow-auto no-scrollbar font-sans text-white selection:bg-[#fcd34d] selection:text-black">
      
      {/* 🔮 Hero Status */}
      <div className="flex items-center justify-between mb-12">
        <div>
          <h1 className="text-3xl font-black text-white tracking-tighter uppercase mb-1">Neural Backend Console</h1>
          <p className="text-[10px] font-bold text-white/40 uppercase tracking-widest">PostgreSQL Instance: localhost:5432/etdb</p>
        </div>
        <div className="flex items-center gap-4">
           <div className="flex items-center gap-2 bg-green-500/10 border border-green-500/20 px-4 py-2 rounded-xl">
              <Zap size={14} className="text-green-500" />
              <span className="text-[10px] font-black text-green-500 uppercase tracking-widest">{stats.api_status}</span>
           </div>
           <div className="bg-white/5 border border-white/10 px-4 py-2 rounded-xl">
              <span className="text-[10px] font-black text-white/40 uppercase tracking-widest">Latency: {stats.latency}</span>
           </div>
        </div>
      </div>

      {/* 📊 High-Density Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        {[
          { icon: Users, label: "Platform Users", value: stats.users, color: "text-blue-500" },
          { icon: Database, label: "Portfolios Tracked", value: stats.portfolio, color: "text-amber-500" },
          { icon: Zap, label: "Market Tickers", value: stats.tickers, color: "text-purple-500" },
          { icon: Activity, label: "System Audit Logs", value: stats.audit_logs, color: "text-emerald-500" }
        ].map((item, idx) => (
          <div key={idx} className="bg-white/5 border border-white/10 p-6 rounded-3xl hover:bg-white/10 transition-all group">
            <div className="flex items-center justify-between mb-4">
               <item.icon size={20} className={item.color} />
               <div className="w-1.5 h-1.5 bg-white/20 rounded-full" />
            </div>
            <div className="text-3xl font-black text-white mb-1 tracking-tighter">{(item.value ?? 0).toLocaleString()}</div>
            <div className="text-[10px] font-bold text-white/40 uppercase tracking-widest">{item.label}</div>
          </div>
        ))}
      </div>

      {/* 🔎 Raw Storage Audit Sections */}
      <div className="grid grid-cols-1 gap-8 mb-12">
        {/* Tickers Table */}
        <div className="bg-[#121212]/50 border border-white/10 rounded-3xl p-8 backdrop-blur-sm">
             <div className="flex items-center gap-6">
                <div className="flex items-center gap-3">
                  <Database size={18} className="text-[#fcd34d]" />
                  <h3 className="text-[12px] font-black uppercase tracking-widest text-white">Neural Ticker Metadata (Raw Storage)</h3>
                </div>
                <a 
                   href="/api/admin/raw/tickers/all" 
                   target="_blank"
                   className="text-[9px] font-black px-3 py-1 bg-white/5 border border-white/10 rounded-lg hover:bg-white/10 transition-colors uppercase tracking-widest text-white/60"
                >
                  Download Full Dump ({stats.tickers})
                </a>
             </div>
           
           <div className="overflow-x-auto">
             <table className="w-full text-left border-collapse">
               <thead>
                 <tr className="border-b border-white/5">
                   <th className="pb-4 text-[10px] font-black text-white/40 uppercase tracking-widest">Symbol</th>
                   <th className="pb-4 text-[10px] font-black text-white/40 uppercase tracking-widest">Name</th>
                   <th className="pb-4 text-[10px] font-black text-white/40 uppercase tracking-widest">Sector</th>
                   <th className="pb-4 text-[10px] font-black text-white/40 uppercase tracking-widest text-right">Market Cap</th>
                   <th className="pb-4 text-[10px] font-black text-white/40 uppercase tracking-widest text-right">Bucket</th>
                 </tr>
               </thead>
               <tbody>
                 {Array.isArray(rawTickers) ? rawTickers.map((ticker, idx) => (
                   <tr key={idx} className="border-b border-white/5 group hover:bg-white/[0.02]">
                     <td className="py-4 text-xs font-black text-white tracking-wider">{ticker.symbol}</td>
                     <td className="py-4 text-[11px] font-bold text-white/60">{ticker.name}</td>
                     <td className="py-4 text-[11px] font-bold text-white/60">{ticker.sector}</td>
                     <td className="py-4 text-[11px] font-mono text-white/40 text-right">₹{(ticker.market_cap / 10000000).toLocaleString(undefined, {maximumFractionDigits: 0})} Cr</td>
                     <td className="py-4 text-right">
                        <span className={`text-[9px] font-black px-2 py-1 rounded-full uppercase tracking-tighter ${
                          ticker.market_cap_bucket === 'Large Cap' ? 'bg-blue-500/10 text-blue-400' :
                          ticker.market_cap_bucket === 'Mid Cap' ? 'bg-amber-500/10 text-amber-400' :
                          'bg-white/5 text-white/40'
                        }`}>
                          {ticker.market_cap_bucket}
                        </span>
                     </td>
                   </tr>
                 )) : (
                   <tr>
                     <td colSpan={5} className="py-12 text-center text-[10px] font-bold text-white/20 uppercase tracking-widest">
                       Failed to load ticker metadata
                     </td>
                   </tr>
                 )}
               </tbody>
             </table>
           </div>
        </div>

        {/* Bulk Deals Table */}
        <div className="bg-[#121212]/50 border border-white/10 rounded-3xl p-8 backdrop-blur-sm">
           <div className="flex items-center justify-between mb-8">
             <div className="flex items-center gap-3">
               <Zap size={18} className="text-[#fcd34d]" />
               <h3 className="text-[12px] font-black uppercase tracking-widest text-white">NSE Institutional Flow (Raw Deals)</h3>
             </div>
             <span className="text-[9px] font-bold text-white/20 uppercase tracking-widest">Live Harvest Scan</span>
           </div>
           
           <div className="overflow-x-auto">
             <table className="w-full text-left border-collapse">
               <thead>
                 <tr className="border-b border-white/5">
                   <th className="pb-4 text-[10px] font-black text-white/40 uppercase tracking-widest">Symbol</th>
                   <th className="pb-4 text-[10px] font-black text-white/40 uppercase tracking-widest">Client Name</th>
                   <th className="pb-4 text-[10px] font-black text-white/40 uppercase tracking-widest">Type</th>
                   <th className="pb-4 text-[10px] font-black text-white/40 uppercase tracking-widest text-right">Price</th>
                   <th className="pb-4 text-[10px] font-black text-white/40 uppercase tracking-widest text-right">Qty</th>
                 </tr>
               </thead>
               <tbody>
                 {Array.isArray(rawDeals) && rawDeals.length > 0 ? rawDeals.map((deal, idx) => (
                   <tr key={idx} className="border-b border-white/5 hover:bg-white/[0.02]">
                     <td className="py-4 text-xs font-black text-white tracking-wider">{deal.symbol}</td>
                     <td className="py-4 text-[10px] font-bold text-white/60 truncate max-w-[200px]">{deal.client_name}</td>
                     <td className="py-4">
                        <span className={`text-[9px] font-black px-2 py-1 rounded-md uppercase tracking-tighter ${
                          deal.deal_type === 'BUY' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
                        }`}>
                          {deal.deal_type}
                        </span>
                     </td>
                     <td className="py-4 text-[11px] font-mono text-white/40 text-right">₹{deal.price.toLocaleString()}</td>
                     <td className="py-4 text-[11px] font-mono text-white/40 text-right">{deal.quantity.toLocaleString()}</td>
                   </tr>
                 )) : (
                   <tr>
                     <td colSpan={5} className="py-12 text-center text-[10px] font-bold text-white/20 uppercase tracking-widest">
                       {Array.isArray(rawDeals) ? "No live institutional deals harvested in current session" : "Failed to load deal flow data"}
                     </td>
                   </tr>
                 )}
               </tbody>
             </table>
           </div>
        </div>
      </div>

    </div>
  );
}

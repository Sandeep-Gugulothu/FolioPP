"use client";

import React, { useState, useEffect, useRef } from "react";
import { Briefcase, TrendingUp, TrendingDown, DollarSign, PieChart, Plus, MoreVertical, X, Loader2, Search, Trash2 } from "lucide-react";

interface Investment {
  symbol: string;
  name?: string;
  units: number;
  avg_price?: number;
  current_price?: number;
  pnl: number;
  pnl_pct: number;
  sector: string;
}

interface TickerSuggestion {
  symbol: string;
  name: string;
}

const FALLBACK_HOLDINGS: Investment[] = [
  { symbol: "SBIN.NS", name: "State Bank of India", units: 250, avg_price: 745.20, current_price: 812.45, pnl: 16812.50, pnl_pct: 9.02, sector: "Banking" },
  { symbol: "RELIANCE.NS", name: "Reliance Industries", units: 100, avg_price: 2850.00, current_price: 2985.60, pnl: 13560.00, pnl_pct: 4.76, sector: "Energy" },
  { symbol: "TCS.NS", name: "Tata Consultancy Services", units: 80, avg_price: 3920.50, current_price: 4120.00, pnl: 15960.00, pnl_pct: 5.09, sector: "Technology" },
  { symbol: "HDFCBANK.NS", name: "HDFC Bank", units: 150, avg_price: 1680.00, current_price: 1640.80, pnl: -5880.00, pnl_pct: -2.33, sector: "Banking" },
  { symbol: "TATAMOTORS.NS", name: "Tata Motors Ltd", units: 300, avg_price: 880.00, current_price: 975.30, pnl: 28590.00, pnl_pct: 10.83, sector: "Automobile" }
];

export function Portfolio() {
  const [investments, setInvestments] = useState<Investment[]>(FALLBACK_HOLDINGS);
  const [isLoading, setIsLoading] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [openMenu, setOpenMenu] = useState<string | null>(null);

  // Form State
  const [newTicker, setNewTicker] = useState("");
  const [newQty, setNewQty] = useState("");
  const [newPrice, setNewPrice] = useState("");
  const [suggestions, setSuggestions] = useState<TickerSuggestion[]>([]);

  // 📡 Initial Fetch from PostgreSQL
  const fetchHoldings = async () => {
    try {
      const resp = await fetch("/api/portfolio");
      if (!resp.ok) throw new Error("Backend unreachable");
      const data = await resp.json();
      if (Array.isArray(data) && data.length > 0) {
        setInvestments(data);
      }
    } catch (err) {
      // Keep fallback holdings
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHoldings();
  }, []);

  // 🔍 Autocomplete logic
  useEffect(() => {
    const searchTickers = async () => {
      if (newTicker.length < 2) {
        setSuggestions([]);
        return;
      }
      try {
        const resp = await fetch(`/api/tickers/search?q=${newTicker}`);
        if (!resp.ok) return;
        const data = await resp.json();
        setSuggestions(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error("Search failed:", err);
      }
    };

    const debounce = setTimeout(searchTickers, 300);
    return () => clearTimeout(debounce);
  }, [newTicker]);

  const addInvestment = async () => {
    if (!newTicker || !newQty) return;
    
    const payload = {
      symbol: newTicker.toUpperCase(),
      units: parseInt(newQty),
      avg_price: newPrice ? parseFloat(newPrice) : null,
      sector: "Various"
    };
    
    try {
      await fetch("/api/portfolio", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      fetchHoldings();
      setNewTicker(""); setNewQty(""); setNewPrice("");
      setIsAddModalOpen(false);
    } catch (err) {
      console.error("Add failed:", err);
    }
  };

  const removeInvestment = async (symbol: string) => {
    try {
      await fetch(`/api/portfolio/${symbol}`, { method: "DELETE" });
      fetchHoldings();
      setOpenMenu(null);
    } catch (err) {
      console.error("Delete failed:", err);
    }
  };

  const totalInvestment = Array.isArray(investments) ? investments.reduce((acc, stock) => {
    const costBasis = stock.avg_price ?? stock.current_price ?? 0;
    return acc + (stock.units * costBasis);
  }, 0) : 0;

  const currentValuation = Array.isArray(investments) ? investments.reduce((acc, stock) => {
    const mktValue = stock.current_price ?? stock.avg_price ?? 0;
    return acc + (stock.units * mktValue);
  }, 0) : 0;

  const totalPnL = currentValuation - totalInvestment;
  const totalPnLPct = totalInvestment > 0 ? (totalPnL / totalInvestment) * 100 : 0;

  return (
    <div className="flex flex-col h-full bg-surface-bg border border-primary-border rounded-3xl overflow-hidden shadow-2xl animate-in fade-in zoom-in-95 duration-500 relative font-sans">
      
      {/* 🚀 Header Stats */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-6 p-8 border-b border-primary-border bg-background/10 relative z-10">
        <div className="flex-1 w-full grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-primary-text/5 p-5 rounded-2xl border border-primary-border hover:bg-primary-text/[0.07] transition-all group">
            <div className="flex items-center gap-2 mb-2 text-secondary-text">
              <DollarSign size={13} className="opacity-50 group-hover:opacity-100 transition-opacity" />
              <span className="text-[10px] font-black uppercase tracking-widest opacity-60">Live Valuation</span>
            </div>
            <div className="text-2xl font-black text-primary-text tracking-tighter">
              ₹{currentValuation.toLocaleString(undefined, { minimumFractionDigits: 2 })}
            </div>
          </div>

          <div className="bg-primary-text/5 p-5 rounded-2xl border border-primary-border hover:bg-primary-text/[0.07] transition-all group">
            <div className="flex items-center gap-2 mb-2 text-secondary-text">
              <TrendingUp size={13} className="opacity-50 group-hover:opacity-100 transition-opacity" />
              <span className="text-[10px] font-black uppercase tracking-widest opacity-60">Total P&L</span>
            </div>
            <div className={`text-2xl font-black tracking-tighter ${totalPnL >= 0 ? 'text-[#10b981]' : 'text-[#f43f5e]'}`}>
              {totalPnL >= 0 ? '+' : ''}₹{totalPnL.toLocaleString(undefined, { minimumFractionDigits: 2 })}
              <span className="text-xs ml-2 opacity-60">({totalPnLPct.toFixed(2)}%)</span>
            </div>
          </div>

          <div className="bg-primary-text/5 p-5 rounded-2xl border border-primary-border hover:bg-primary-text/[0.07] transition-all group">
            <div className="flex items-center gap-2 mb-2 text-secondary-text">
              <PieChart size={13} className="opacity-50 group-hover:opacity-100 transition-opacity" />
              <span className="text-[10px] font-black uppercase tracking-widest opacity-60">Active Holdings</span>
            </div>
            <div className="text-2xl font-black text-primary-text tracking-tighter">
              {investments.length} <span className="text-[10px] font-bold text-secondary-text uppercase ml-1">Stocks</span>
            </div>
          </div>
        </div>

        <button 
          onClick={() => setIsAddModalOpen(true)}
          className="w-full md:w-auto flex items-center justify-center gap-2.5 bg-[#fcd34d] text-black hover:bg-[#fbbf24] hover:scale-[1.02] active:scale-[0.98] transition-all rounded-xl font-black text-[11px] uppercase tracking-[0.1em] px-8 py-4 shadow-xl shadow-[#fcd34d]/5"
        >
          <Plus size={16} /> Add Investment
        </button>
      </div>

      {/* 📊 Holdings Table */}
      <div className="flex-1 overflow-auto no-scrollbar relative z-10">
        {isLoading ? (
          <div className="w-full h-full flex flex-col items-center justify-center text-secondary-text animate-pulse">
            <Loader2 size={32} className="animate-spin mb-4" />
            <span className="text-[10px] font-black uppercase tracking-[0.2em]">Syncing with Portfolio Engine...</span>
          </div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead className="sticky top-0 bg-surface-bg/95 backdrop-blur-md z-20">
              <tr className="border-b border-primary-border">
                <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-secondary-text">Instrument</th>
                <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-secondary-text text-right">Quantity</th>
                <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-secondary-text text-right">Avg Price</th>
                <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-secondary-text text-right">Net Value</th>
                <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-secondary-text text-right">Returns</th>
                <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-secondary-text text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              {investments.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-8 py-20 text-center text-secondary-text opacity-40">
                    <span className="text-[11px] font-black uppercase tracking-widest">No Active Investments Detected.</span>
                  </td>
                </tr>
              ) : (
                investments.map((stock, idx) => (
                  <tr key={idx} className="border-b border-primary-border/10 hover:bg-primary-text/5 transition-all group relative">
                    <td className="px-8 py-5">
                      <div className="font-black text-[14px] text-primary-text tracking-widest">{stock.symbol}</div>
                      <div className="text-[9px] font-bold text-secondary-text uppercase tracking-widest opacity-60 tracking-tighter">{stock.sector}</div>
                    </td>
                    <td className="px-8 py-5 text-right font-bold text-[13px]">{stock.units}</td>
                    <td className="px-8 py-5 text-right font-mono text-[12px] opacity-40">₹{(stock.avg_price ?? stock.current_price ?? 0).toFixed(2)}</td>
                    <td className="px-8 py-5 text-right font-black text-[13px]">₹{(stock.units * (stock.current_price ?? stock.avg_price ?? 0)).toLocaleString()}</td>
                    <td className={`px-8 py-5 text-right`}>
                       <div className={`text-[13px] font-black ${stock.pnl >= 0 ? 'text-[#10b981]' : 'text-[#f43f5e]'}`}>
                        {stock.pnl >= 0 ? '+' : ''}{stock.pnl_pct.toFixed(2)}%
                      </div>
                      <div className="text-[10px] font-bold opacity-30 uppercase">₹{Math.abs(stock.pnl).toLocaleString()}</div>
                    </td>
                    <td className="px-8 py-5 text-center relative overflow-visible">
                       <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          setOpenMenu(openMenu === stock.symbol ? null : stock.symbol);
                        }}
                        className="p-2 text-secondary-text hover:text-primary-text transition-all bg-primary-text/5 rounded-lg border border-primary-border/20"
                       >
                         <MoreVertical size={16} />
                       </button>

                       {openMenu === stock.symbol && (
                         <div className="absolute right-0 top-[80%] w-48 bg-[#121212] border border-primary-border rounded-xl shadow-[0_20px_50px_rgba(0,0,0,0.8)] z-[100] p-1.5 animate-in zoom-in-95 duration-200">
                           <button 
                            onClick={(e) => { e.stopPropagation(); removeInvestment(stock.symbol); }}
                            className="w-full flex items-center justify-between px-3 py-2.5 text-left text-[#f43f5e] hover:bg-[#f43f5e]/10 rounded-lg transition-all group/del"
                           >
                              <span className="text-[10px] font-black uppercase tracking-widest">Remove Tracking</span>
                              <Trash2 size={12} className="opacity-40 group-hover/del:opacity-100" />
                           </button>
                         </div>
                       )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* 🧩 Add Investment Modal (Fixed logic) */}
      {isAddModalOpen && (
        <div 
          className="fixed inset-0 z-[10000] flex items-center justify-center p-8 bg-black/70 backdrop-blur-lg animate-in fade-in duration-300"
          onClick={() => {setIsAddModalOpen(false); setSuggestions([]);}}
        >
          <div 
            className="w-full max-w-md bg-surface-bg border border-primary-border rounded-3xl p-8 shadow-2xl relative animate-in zoom-in-95 duration-500 overflow-visible"
            onClick={e => e.stopPropagation()}
          >
             <button onClick={() => setIsAddModalOpen(false)} className="absolute top-6 right-6 text-secondary-text hover:text-primary-text transition-colors">
               <X size={20} />
             </button>
             <h2 className="text-xl font-black text-primary-text uppercase tracking-tighter mb-8">Commit New Position</h2>
             
             <div className="space-y-6 overflow-visible">
                <div className="space-y-2 relative">
                   <label className="text-[10px] font-black uppercase tracking-widest text-secondary-text">Ticker Symbol (NSE/NASDAQ)</label>
                   <div className="relative group/search">
                     <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-secondary-text group-hover/search:text-primary-text transition-colors" />
                     <input 
                      value={newTicker} 
                      onChange={e => setNewTicker(e.target.value)}
                      className="w-full bg-primary-text/5 border border-primary-border rounded-xl pl-12 pr-4 py-3 outline-none focus:border-primary-text/30 transition-all font-black uppercase text-[14px]"
                      placeholder="Search Tickers..."
                      autoComplete="off"
                     />
                   </div>

                   {/* ⚡ Autocomplete Suggestions (Fixed Double Click) */}
                   {suggestions.length > 0 && (
                     <div className="absolute top-[100%] left-0 w-full mt-2 bg-[#121212] border-2 border-[#fcd34d]/30 rounded-2xl shadow-[0_20px_80px_rgba(0,0,0,0.8)] z-[20000] p-1.5 animate-in slide-in-from-top-2 duration-300">
                        {suggestions.map((s, idx) => (
                          <div 
                            key={idx} 
                            // Using onMouseDown to prevent blur/double-click issues
                            onMouseDown={(e) => {
                              e.preventDefault(); 
                              setNewTicker(s.symbol); 
                              setSuggestions([]);
                            }}
                            className="flex items-center justify-between px-5 py-4 hover:bg-[#fcd34d]/10 rounded-xl cursor-pointer group transition-all"
                          >
                             <div>
                               <div className="text-[13px] font-black uppercase tracking-widest text-[#ffffff] group-hover:text-[#fcd34d]">{s.symbol}</div>
                               <div className="text-[9px] font-bold text-[#a1a1aa] uppercase tracking-tighter">{s.name}</div>
                             </div>
                             <div className="text-[9px] font-black bg-[#fcd34d]/10 px-3 py-1 rounded-lg text-[#fcd34d]">CHOOSE</div>
                          </div>
                        ))}
                     </div>
                   )}
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-[10px] font-black uppercase tracking-widest text-secondary-text">Quantity</label>
                    <input 
                      type="number" value={newQty} onChange={e => setNewQty(e.target.value)}
                      className="w-full bg-primary-text/5 border border-primary-border rounded-xl px-4 py-3 outline-none focus:border-primary-text/30 transition-all font-black text-[14px]"
                      placeholder="Shares"
                    />
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] font-black uppercase tracking-widest text-secondary-text">Buy Price (Optional)</label>
                    <input 
                      type="number" value={newPrice} onChange={e => setNewPrice(e.target.value)}
                      className="w-full bg-primary-text/5 border border-primary-border rounded-xl px-4 py-3 outline-none focus:border-primary-text/30 transition-all font-black text-[14px]"
                      placeholder="LTP used if empty"
                    />
                  </div>
                </div>

                <button 
                  onClick={addInvestment}
                  className="w-full bg-[#fcd34d] text-black py-4 rounded-xl font-black uppercase tracking-widest text-[13px] hover:opacity-90 shadow-xl transition-all h-14"
                >
                  Verify & Store
                </button>
             </div>
          </div>
        </div>
      )}
    </div>
  );
}

"use client";

import React from "react";
import { BarChart3 } from "lucide-react";

export const PricePerformance: React.FC<{ symbol: string }> = ({ symbol }) => (
  <div className="h-full bg-[#0c0c0c] p-6 font-mono flex flex-col">
    <div className="flex items-center gap-2 mb-6">
      <span className="text-[9px] text-slate-500 font-black uppercase tracking-widest">Outstanding Shares:</span>
      <span className="text-[9px] text-white font-black">410.500 M</span>
    </div>
    
    <div className="flex-1 rounded-xl bg-black border border-white/5 relative flex flex-col p-6 overflow-hidden">
       <div className="flex items-center justify-between mb-4 z-10">
          <div className="flex items-center gap-3">
            <span className="text-[9px] font-mono font-black text-slate-100 italic tracking-tighter">{symbol} - 1D - NASDAQ</span>
          </div>
          <span className="text-[9px] font-mono text-slate-500 font-extrabold uppercase tracking-widest">07:37:41 (UTC-4)</span>
       </div>
       <div className="flex-1 flex items-center justify-center opacity-5">
          <BarChart3 size={120} className="text-emerald-500" />
       </div>
       <div className="mt-auto border-t border-white/5 pt-4 z-10">
          <div className="flex gap-6 text-[9px] font-mono font-extrabold uppercase tracking-widest text-slate-500">
             <span className="text-white underline decoration-rose-500 underline-offset-4">5yr</span> <span>1yr</span> <span>1mo</span> <span>1wk</span>
          </div>
       </div>
    </div>
  </div>
);

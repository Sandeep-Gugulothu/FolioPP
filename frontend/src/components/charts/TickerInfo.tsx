"use client";

import React from "react";

export const TickerInfo: React.FC<{ symbol: string }> = ({ symbol }) => (
  <div className="flex flex-col h-full bg-[#0c0c0c] p-6 font-mono">
    <div className="flex justify-end gap-12 mb-4">
      <div className="flex flex-col items-start border-r border-white/5 pr-8">
         <span className="text-[9px] text-slate-500 font-extrabold uppercase tracking-widest mb-1">Price</span>
         <span className="text-[16px] font-mono font-extrabold text-white leading-none">$246.00</span>
      </div>
      <div className="flex flex-col items-start font-mono">
         <span className="text-[9px] text-slate-500 font-extrabold uppercase tracking-widest mb-1">Day's Change</span>
         <span className="text-[11px] font-mono font-extrabold text-rose-500">-8.20 (-3.23%)</span>
      </div>
    </div>
    
    <div className="flex-1 flex flex-col justify-center relative">
       <div className="absolute inset-0 flex items-center justify-center opacity-20">
         <svg className="w-full h-20" viewBox="0 0 100 40">
           <path d="M0 40 Q 20 10, 40 30 T 80 10 L 100 40 Z" fill="#ef4444" opacity="0.4" />
           <path d="M0 40 Q 20 10, 40 30 T 80 10" stroke="#ef4444" strokeWidth="2" fill="none" />
         </svg>
       </div>
       <div className="mt-auto z-10">
         <div className="flex flex-col mb-4">
            <span className="text-[9px] text-slate-500 font-extrabold uppercase tracking-widest">Volume</span>
            <span className="text-[11px] font-mono font-extrabold text-white">7.306 M</span>
         </div>
         <p className="text-[9px] font-extrabold text-slate-500 uppercase tracking-[0.2em] border-t border-white/5 pt-3">
           Software - Infrastructure | US | NASDAQ
         </p>
       </div>
    </div>
  </div>
);

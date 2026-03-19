"use client";

import React, { useState } from "react";
import { 
  X, Sparkles, Send, BrainCircuit, Globe, Zap, 
  Settings, Share2, Database, Paperclip, Lightbulb,
  Maximize2, Trash2, ChevronDown, MessageSquare
} from "lucide-react";

interface MarketChatProps {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
}

export const MarketChat: React.FC<MarketChatProps> = ({ isOpen, setIsOpen }) => {

  const prompts = [
    "Analyze the trend in dividend payouts and dividend yield.",
    "Using the financial statements, assess the trend in revenue growth.",
    "Analyze the gross and net profit margin trend."
  ];

  if (!isOpen) {
    return (
      <button 
        onClick={() => setIsOpen(true)}
        className="fixed bottom-12 right-12 w-14 h-14 bg-white/10 border border-white/20 rounded-2xl flex items-center justify-center hover:bg-white/20 hover:scale-110 transition-all z-[900] shadow-2xl backdrop-blur-xl"
      >
        <div className="relative">
          <BrainCircuit size={28} className="text-white" />
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full border-2 border-black" />
        </div>
      </button>
    );
  }

  return (
    <div className="fixed top-16 right-0 bottom-0 w-[500px] bg-black border-l border-white/5 flex flex-col font-mono z-[1000] animate-in slide-in-from-right duration-300">
      {/* Precision Header (Flat/Full Width) */}
      <div className="h-14 px-6 flex items-center justify-between border-b border-white/5 bg-white/[0.01]">
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-slate-500 font-bold tracking-widest uppercase">New chat</span>
          <ChevronDown size={10} className="text-slate-500" />
        </div>
        <div className="flex items-center gap-4 text-slate-500">
          <button className="p-1.5 hover:text-white transition-colors"><PlusSquare size={16} /></button>
          <button className="p-1.5 hover:text-white transition-colors"><Trash2 size={16} /></button>
          <button onClick={() => setIsOpen(false)} className="p-1.5 hover:text-white transition-colors ml-2"><X size={18} /></button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto no-scrollbar py-12 px-8 flex flex-col items-center">
        {/* Central Identity (High Resolution) */}
        <div className="flex flex-col items-center mb-10 w-full">
          <div className="w-12 h-12 bg-sky-500 rounded-xl flex items-center justify-center shadow-[0_0_30px_rgba(14,165,233,0.3)] mb-6">
            <Sparkles size={24} className="text-white" />
          </div>
          <h2 className="text-[16px] font-black text-white tracking-[0.2em] uppercase mb-2">Copilot</h2>
          <p className="text-[11px] text-slate-500 text-center leading-relaxed max-w-[280px]">
            Get started with these suggested prompts:
          </p>
        </div>

        {/* Tactical Suggestions (Full Sidebar Alignment) */}
        <div className="space-y-4 w-full">
          {prompts.map((p, i) => (
            <button 
              key={i} 
              className="p-5 w-full bg-white/[0.03] border border-white/5 rounded-2xl hover:bg-white/[0.06] hover:border-white/10 transition-all text-left group"
            >
              <p className="text-[11px] text-slate-400 group-hover:text-white leading-relaxed">
                {p}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Full-Width Persistent Input Terminal */}
      <div className="px-6 pb-10 pt-4 border-t border-white/5 bg-black">
        <div className="bg-[#141414] border border-white/10 rounded-2xl overflow-hidden shadow-2xl">
          <div className="h-10 px-4 border-b border-white/5 flex items-center gap-4 text-slate-500">
            <div className="flex items-center gap-1.5 opacity-60">
              <Settings size={14} />
              <div className="w-px h-3 bg-white/10 mx-1" />
              <Share2 size={14} />
              <span className="text-[10px] font-bold">0</span>
            </div>
            <div className="w-px h-3 bg-white/10" />
            <div className="flex items-center gap-1.5">
              <span className="text-[11px] uppercase font-bold tracking-widest text-slate-500 italic"> Using widgets</span>
            </div>
          </div>
          
          <div className="p-4">
            <textarea 
              rows={3}
              className="w-full bg-transparent border-none outline-none text-[11px] text-white placeholder:text-slate-600 resize-none font-medium leading-relaxed"
              placeholder="Inquire..."
            />
          </div>

          <div className="h-12 px-4 bg-white/[0.02] border-t border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-3">
               <button className="flex items-center gap-2 px-2.5 py-1.5 rounded-lg border border-white/5 text-[10px] text-slate-400 hover:text-white hover:bg-white/5 transition-all">
                 <Sparkles size={12} /> Copilot <ChevronDown size={10} />
               </button>
            </div>
            <div className="flex items-center gap-3">
               <button className="p-1.5 text-slate-500 hover:text-white transition-colors"><Lightbulb size={16} /></button>
               <button className="p-1.5 text-slate-500 hover:text-white transition-colors"><Paperclip size={16} /></button>
               <button className="p-1.5 text-slate-500 hover:text-white transition-colors"><Database size={16} /></button>
               <button className="w-9 h-9 flex items-center justify-center bg-white/10 text-slate-500 rounded-lg">
                 <Send size={15} />
               </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const PlusSquare = ({ size }: { size: number }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><line x1="12" x2="12" y1="8" y2="16"/><line x1="8" x2="16" y1="12" y2="12"/></svg>
);

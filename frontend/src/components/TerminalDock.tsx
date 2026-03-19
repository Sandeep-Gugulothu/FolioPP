import React, { useState } from "react";
import Image from "next/image";
import LogoImage from "../../public/images/logo-foliopp.png";
import {
  History,
  Info,
  TrendingUp,
  LayoutDashboard,
  BarChart3,
  Search,
  Plus,
  Settings,
  Clock,
  ArrowRight
} from "lucide-react";

import { useLayoutManager, PanelState } from "@/hooks/useLayoutManager";
import { DockPanel } from "./layout/DockPanel";
import { TickerInfo } from "./charts/TickerInfo";
import { TickerProfile } from "./signals/TickerProfile";
import { PricePerformance } from "./charts/PricePerformance";
import { MarketChat } from "./chat/MarketChat";

import "@/assets/styles/globals.css";


const initialPanels: PanelState[] = [
  { id: 'info', title: 'Information', symbol: 'ADBE', icon: History, x: 20, y: 15, w: 520, h: 320 },
  { id: 'profile', title: 'Profile', symbol: 'ADBE', icon: Info, x: 20, y: 350, w: 520, h: 520 },
  { id: 'performance', title: 'Performance', symbol: 'ADBE', icon: TrendingUp, x: 560, y: 15, w: 920, h: 855 },
];

export function TerminalDock() {
  const {
    panels,
    activePanelId,
    setActivePanelId,
    startDrag,
    handleClose,
    handleMaximize,
    handleMinimize,
    updateSymbols
  } = useLayoutManager(initialPanels);

  const [tickerQuery, setTickerQuery] = useState("ADBE");
  const [isAiOpen, setIsAiOpen] = useState(false);

  const handleUpdate = (val: string) => {
    setTickerQuery(val.toUpperCase());
    updateSymbols(val);
  };

  return (
    <div className="flex h-screen w-full bg-black overflow-hidden font-outfit text-slate-300">

      {/* 1. Sidebar (Elite Compact) */}
      <aside className="w-16 h-full border-r border-white/5 flex flex-col items-center py-6 gap-8 bg-[#080808] shrink-0 z-50">
        <div className="w-9 h-9 relative mb-4 cursor-pointer hover:scale-110 transition-transform">
          <Image src={LogoImage} alt="FolioPP Logo" fill className="object-contain" priority />
        </div>
        <SidebarItem icon={LayoutDashboard} active />
        <SidebarItem icon={BarChart3} />
        <SidebarItem icon={Search} />
        <div className="mt-auto flex flex-col mb-4 gap-6">
          <SidebarItem icon={Plus} />
          <SidebarItem icon={Settings} />
        </div>
      </aside>

      {/* 2. Intelligent High-Resolution Surface */}
      <div className="flex-1 flex flex-col bg-[#050505] relative overflow-auto no-scrollbar scroll-smooth">

        {/* Top Neural Breadcrumbs (Ticket + Search) */}
        <header className="h-16 border-b border-white/5 px-8 flex items-center justify-between shrink-0 bg-black/95 backdrop-blur-2xl z-[100] sticky top-0">
          <div className="flex items-center gap-3">
            {/* The First Tab: TICKET with Search */}
            <div className="flex items-center bg-white/5 rounded-xl border border-white/10 p-1.5 pl-4 group focus-within:border-white/20 transition-all shadow-lg">
               <span className="text-[11px] font-black uppercase tracking-[0.2em] text-white">Ticker</span>
               <div className="w-px h-4 bg-white/10 mx-5" />
               <input 
                 value={tickerQuery}
                 onChange={(e) => handleUpdate(e.target.value)}
                 className="bg-transparent border-none outline-none text-[12px] font-black text-white w-24 uppercase tracking-widest placeholder:text-slate-700"
                 placeholder="Search..."
               />
               <div className="flex items-center bg-white/10 hover:bg-white/20 p-2 rounded-lg cursor-pointer transition-colors ml-2">
                 <ArrowRight size={14} className="text-white" />
               </div>
            </div>

            <div className="w-px h-6 bg-white/5 mx-3" />
            
            {['Overview', 'Financials', 'Technical Analysis', 'Comparison Analysis', 'Calendar'].map((tab) => (
               <button key={tab} className={`px-5 py-2 text-[10px] font-black uppercase tracking-widest ${tab === 'Overview' ? 'text-white underline decoration-blue-500 underline-offset-8' : 'text-slate-600 hover:text-slate-300'} transition-all`}>{tab}</button>
            ))}
          </div>
          <div className="flex items-center gap-4 text-[10px] font-mono font-bold text-slate-700 uppercase tracking-widest">
             <Clock size={14} className="opacity-40" /> 17:09:39
          </div>
        </header>

        {/* The Compacting Stage */}
        <div className={`relative flex-1 p-4 min-h-[1500px] transition-all duration-300 ${isAiOpen ? 'mr-[500px]' : ''}`}>
          {panels.map((p) => {
            return (
              <DockPanel
                key={p.id}
                panel={p}
                isActive={activePanelId === p.id}
                onStartDrag={startDrag}
                onClose={handleClose}
                onMaximize={handleMaximize}
                onMinimize={handleMinimize}
                onClick={() => setActivePanelId(p.id)}
              >
                {p.id === 'info' && <TickerInfo symbol={p.symbol} />}
                {p.id === 'profile' && <TickerProfile symbol={p.symbol} />}
                {p.id === 'performance' && <PricePerformance symbol={p.symbol} />}
              </DockPanel>
            );
          })}
        </div>
        <MarketChat isOpen={isAiOpen} setIsOpen={setIsAiOpen} />
      </div>

    </div>
  );
}

// --- Sidebar Helper ---

const SidebarItem = ({ icon: Icon, active = false }: any) => (
  <div className={`p-2.5 cursor-pointer transition-all rounded-lg group ${active ? 'bg-white/10 text-white shadow-inner' : 'text-slate-700 hover:text-slate-300 hover:bg-white/5'}`}>
    <Icon size={20} className={active ? '' : 'transition-transform group-hover:scale-110'} />
  </div>
);

import React, { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Image from "next/image";
import LogoImage from "../../public/images/logo-foliopp.png";
import {
  History,
  Info,
  TrendingUp,
  LayoutDashboard,
  BarChart3,
  Search,
  Newspaper,
  Plus,
  Settings,
  Clock,
  ArrowRight,
  Sun,
  Moon,
  Globe,
  LayoutList,
  Activity,
  DollarSign,
  TrendingDown,
  CandlestickChart
} from "lucide-react";

import { useLayoutManager, PanelState } from "@/hooks/useLayoutManager";
import { DockPanel } from "./layout/DockPanel";
import { Information } from "./panels/Information";
import { Profile } from "./panels/Profile";
import { Performance } from "./panels/Performance";
import { News } from "./panels/News";
import { Watchlist } from "./panels/Watchlist";
import { MarketChat } from "./chat/MarketChat";
import { Financials } from "./charts/Financials";
import { RevenueChart } from "./charts/RevenueChart";
import { ExpenseChart } from "./charts/ExpenseChart";
import { ProfitabilityChart } from "./charts/ProfitabilityChart";
import { ValuationChart } from "./charts/ValuationChart";
import { TechnicalChart } from "./charts/TechnicalChart";
import { ResearchChart } from "./panels/ResearchChart";

import "@/assets/styles/globals.css";


const initialOverviewPanels: PanelState[] = [
  { id: 'info', title: 'Information', symbol: 'SBIN', icon: 'History', x: 20, y: 15, w: 520, h: 320 },
  { id: 'signals', title: 'News', symbol: 'SBIN', icon: 'Newspaper', x: 20, y: 350, w: 520, h: 420 },
  { id: 'profile', title: 'Profile', symbol: 'SBIN', icon: 'Info', x: 20, y: 785, w: 520, h: 520 },
  { id: 'performance', title: 'Performance', symbol: 'SBIN', icon: 'TrendingUp', x: 560, y: 15, w: 920, h: 700 },
];

const initialFinancialsPanels: PanelState[] = [
  { id: 'financials', title: 'Income Statement', symbol: 'SBIN', icon: 'LayoutList', x: 20, y: 15, w: 730, h: 580 },
  { id: 'rev_chart', title: 'Revenue Breakdown', symbol: 'SBIN', icon: 'BarChart3', x: 770, y: 15, w: 730, h: 580 },
  { id: 'exp_chart', title: 'Expense Analysis', symbol: 'SBIN', icon: 'TrendingDown', x: 20, y: 615, w: 730, h: 530 },
  { id: 'profit_chart', title: 'Profitability Flux', symbol: 'SBIN', icon: 'Activity', x: 770, y: 615, w: 730, h: 530 },
];

const initialWatchlistPanels: PanelState[] = [
  { id: 'watchlist', title: 'Institutional Watchlist', symbol: 'ALL', icon: 'Globe', x: 20, y: 15, w: 1460, h: 1210 },
];

const initialTechnicalPanels: PanelState[] = [
  { id: 'tech_chart', title: 'Technical Research Surface', symbol: 'SBIN', icon: 'CandlestickChart', x: 20, y: 15, w: 920, h: 700 },
];

export function TerminalDock() {
  const overviewManager = useLayoutManager(initialOverviewPanels, "overview");
  const financialsManager = useLayoutManager(initialFinancialsPanels, "financials");
  const watchlistManager = useLayoutManager(initialWatchlistPanels, "watchlist");
  const technicalManager = useLayoutManager(initialTechnicalPanels, "technical");

  const [tickerQuery, setTickerQuery] = useState("SBIN");
  const [isAiOpen, setIsAiOpen] = useState(false);
  const [pendingMessage, setPendingMessage] = useState<string | null>(null);
  const [exchange, setExchange] = useState("NSE");
  const router = useRouter();
  const searchParams = useSearchParams();
  const [activeTab, setActiveTabRaw] = useState(searchParams.get("tab") || 'Overview');
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  const [researchPlots, setResearchPlots] = useState<Record<string, string>>({});
  const [isAddMenuOpen, setIsAddMenuOpen] = useState(false);

  // Choose active manager
  const activeManager =
    activeTab === 'Financials' ? financialsManager :
      activeTab === 'Watchlist' ? watchlistManager :
        activeTab === 'Technical Analysis' ? technicalManager :
          overviewManager;

  // Keep in sync with URL
  const setActiveTab = (tab: string) => {
    setActiveTabRaw(tab);
    const params = new URLSearchParams(searchParams.toString());
    params.set("tab", tab);
    router.push(`?${params.toString()}`);
  };

  useEffect(() => {
    const tabFromUrl = searchParams.get("tab");
    if (tabFromUrl && tabFromUrl !== activeTab) {
      setActiveTabRaw(tabFromUrl);
    }
  }, [searchParams]);

  React.useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === 'dark' ? 'light' : 'dark');

  const addNewPanel = (type: string, title: string, iconKey: string) => {
    const id = `${type}-${Date.now()}`;
    activeManager.addPanel({
      id,
      title: title,
      symbol: tickerQuery,
      icon: iconKey,
      x: 100 + (activeManager.panels.length * 30),
      y: 100 + (activeManager.panels.length * 30),
      w: type === 'performance' ? 800 : 520,
      h: type === 'performance' ? 500 : 320
    });
    setIsAddMenuOpen(false);
  };

  const handleUpdate = (val: string) => {
    const uppercase = val.toUpperCase();
    setTickerQuery(uppercase);
    const isUS = ["ADBE", "AAPL", "MSFT", "TSLA", "GOOG", "NVDA", "META"].includes(uppercase);
    const newExchange = isUS ? "NASDAQ" : "NSE";
    setExchange(newExchange);
    // Removed automatic global synchronization to restore symbol individuality
  };

  const handleAskAI = (id: string, title: string) => {
    // Construct deep context prompt
    const contextPrompt = `I am analyzing the ${title} module for ${tickerQuery}. Please perform a deep neural pattern analysis on this chart. Identify any technical indicators, trends, or anomalies and provide a professional institutional summary.`;
    setPendingMessage(contextPrompt);
    setIsAiOpen(true);
  };

  const handlePopout = (imageSrc: string) => {
    const id = `research-${Date.now()}`;
    const timestamp = new Date().toLocaleTimeString();

    // Store the plot data
    setResearchPlots(prev => ({ ...prev, [id]: imageSrc }));

    // Add a new panel to the active manager
    activeManager.addPanel({
      id,
      title: `Neural Analysis (${timestamp})`,
      symbol: tickerQuery,
      icon: Activity,
      x: 100, y: 150, w: 800, h: 550
    });
  };

  return (
    <div className="flex h-screen w-full bg-primary-bg overflow-hidden font-outfit text-primary-text">

      {/* 1. Sidebar (Elite Compact) */}
      <aside className="w-16 h-full border-r border-primary-border flex flex-col items-center py-6 gap-8 bg-sidebar-bg shrink-0 z-50 transition-colors">
        <div className="w-9 h-9 relative mb-4 cursor-pointer transition-transform">
          <Image src={LogoImage} alt="FolioPP Logo" fill className="object-contain" priority />
        </div>
        <SidebarItem icon={LayoutDashboard} active={activeTab === 'Overview'} onClick={() => setActiveTab('Overview')} />
        <SidebarItem icon={Globe} active={activeTab === 'Watchlist'} onClick={() => setActiveTab('Watchlist')} />
        <SidebarItem icon={Search} />
        <div className="mt-auto flex flex-col mb-4 gap-6 relative">
          <SidebarItem icon={theme === 'dark' ? Sun : Moon} onClick={toggleTheme} />

          <div className="relative">
            <SidebarItem icon={Plus} onClick={() => setIsAddMenuOpen(!isAddMenuOpen)} active={isAddMenuOpen} />
            {isAddMenuOpen && (
              <div className="absolute left-16 bottom-0 w-56 bg-surface-bg border border-primary-border rounded-xl shadow-2xl z-[1000] p-2 animate-in slide-in-from-left-2 fade-in duration-200">
                <div className="px-3 py-2 border-b border-primary-border mb-1">
                  <span className="text-[10px] font-bold uppercase tracking-widest text-secondary-text">Add Terminal Module</span>
                </div>
                <div className="max-h-[300px] overflow-y-auto no-scrollbar">
                  <div className="px-3 py-1.5 opacity-30 select-none"><span className="text-[8px] font-black uppercase tracking-tighter">Market Overview</span></div>
                  <AddMenuItem icon={History} label="Information" onClick={() => addNewPanel('info', 'Information', 'History')} />
                  <AddMenuItem icon={TrendingUp} label="Performance" onClick={() => addNewPanel('performance', 'Performance', 'TrendingUp')} />
                  <AddMenuItem icon={Newspaper} label="News Stream" onClick={() => addNewPanel('signals', 'News Stream', 'Newspaper')} />
                  <AddMenuItem icon={Info} label="Institutional Profile" onClick={() => addNewPanel('profile', 'Institutional Profile', 'Info')} />

                  <div className="px-3 py-1.5 opacity-30 select-none mt-2 border-t border-primary-border/20 pt-2"><span className="text-[8px] font-black uppercase tracking-tighter">Financial Analysis</span></div>
                  <AddMenuItem icon={LayoutList} label="Income Statement" onClick={() => addNewPanel('financials', 'Income Statement', 'LayoutList')} />
                  <AddMenuItem icon={BarChart3} label="Revenue Breakdown" onClick={() => addNewPanel('rev_chart', 'Revenue Breakdown', 'BarChart3')} />
                  <AddMenuItem icon={TrendingDown} label="Expense Analysis" onClick={() => addNewPanel('exp_chart', 'Expense Analysis', 'TrendingDown')} />
                  <AddMenuItem icon={Activity} label="Profitability Flux" onClick={() => addNewPanel('profit_chart', 'Profitability Flux', 'Activity')} />
                </div>
              </div>
            )}
          </div>

          <SidebarItem icon={Settings} />
        </div>
      </aside>

      {/* 2. Intelligent High-Resolution Surface */}
      <div className="flex-1 flex flex-col bg-primary-bg relative overflow-auto no-scrollbar scroll-smooth transition-colors">

        {/* Top Neural Breadcrumbs (Ticket + Search) */}
        <header className="h-16 border-b border-primary-border px-8 flex items-center justify-between shrink-0 bg-background/80 backdrop-blur-md z-[1000] sticky top-0 transition-colors">
          <div className="flex items-center gap-3">
            <div className="flex items-center bg-primary-text/5 rounded-xl border border-primary-border p-1.5 pl-4 transition-all shadow-lg">
              <span className="text-[13px] font-black uppercase tracking-[0.2em] text-primary-text">Ticker</span>
              <div className="w-px h-4 bg-primary-text/10 mx-5" />
              <input
                value={tickerQuery}
                onChange={(e) => handleUpdate(e.target.value)}
                className="bg-transparent border-none outline-none text-[14px] font-black text-primary-text w-24 uppercase tracking-widest placeholder:text-primary-text"
                placeholder="Search..."
              />
              <div className="flex items-center bg-primary-text/10 p-2 rounded-lg cursor-pointer transition-colors ml-2 hover:bg-primary-text/20">
                <ArrowRight size={14} className="text-primary-text" />
              </div>
            </div>

            <div className="w-px h-6 bg-primary-border mx-3" />

            {['Overview', 'Financials', 'Technical Analysis', 'Calendar'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-1.5 text-[12px] font-bold uppercase tracking-wider rounded-lg transition-all ${tab === activeTab ? 'bg-primary-text/10 text-primary-text shadow-xl' : 'text-secondary-text hover:text-primary-text hover:bg-primary-text/5'}`}
              >
                {tab}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-4 text-[12px] font-mono font-bold text-primary-text uppercase tracking-widest">
            <Clock size={14} className="opacity-40" /> 17:09:39
          </div>
        </header>

        {/* The Compacting Stage */}
        <div className={`relative flex-1 p-4 pr-12 min-h-[1500px] transition-all duration-300 ${isAiOpen ? 'mr-[500px]' : ''}`}>
          {activeManager.panels.map((p) => {
            return (
              <DockPanel
                key={p.id}
                panel={p}
                isActive={activeManager.activePanelId === p.id}
                onStartDrag={activeManager.startDrag}
                onClose={activeManager.handleClose}
                onMaximize={activeManager.handleMaximize}
                onMinimize={activeManager.handleMinimize}
                onAskAI={handleAskAI}
                onClick={() => activeManager.setActivePanelId(p.id)}
                theme={theme}
              >
                {(() => {
                  switch (p.id) {
                    case 'profile': return <Profile symbol={p.symbol} exchange={exchange} />;
                    case 'performance': return <Performance symbol={p.symbol} exchange={exchange} theme={theme} />;
                    case 'financials': return <Financials symbol={p.symbol} exchange={exchange} />;
                    case 'rev_chart': return <RevenueChart symbol={p.symbol} exchange={exchange} />;
                    case 'exp_chart': return <ExpenseChart symbol={p.symbol} exchange={exchange} />;
                    case 'profit_chart': return <ProfitabilityChart symbol={p.symbol} exchange={exchange} />;
                    case 'watchlist': return <Watchlist />;
                    case 'signals': return <News symbol={p.symbol} exchange={exchange} />;
                    case 'tech_chart': return <TechnicalChart symbol={p.symbol} exchange={exchange} />;
                    default:
                      if (p.id.startsWith('info') || p.id.startsWith('extra-')) {
                        return <Information symbol={p.symbol} exchange={exchange} />;
                      }
                      if (p.id.startsWith('performance-') || p.id === 'performance') {
                        return <Performance symbol={p.symbol} exchange={exchange} theme={theme} />;
                      }
                      if (p.id.startsWith('signals-') || p.id === 'signals') {
                        return <News symbol={p.symbol} exchange={exchange} />;
                      }
                      if (p.id.startsWith('profile-') || p.id === 'profile') {
                        return <Profile symbol={p.symbol} exchange={exchange} />;
                      }
                      if (p.id.startsWith('financials-') || p.id === 'financials') {
                        return <Financials symbol={p.symbol} exchange={exchange} />;
                      }
                      if (p.id.startsWith('rev_chart-') || p.id === 'rev_chart') {
                        return <RevenueChart symbol={p.symbol} exchange={exchange} />;
                      }
                      if (p.id.startsWith('exp_chart-') || p.id === 'exp_chart') {
                        return <ExpenseChart symbol={p.symbol} exchange={exchange} />;
                      }
                      if (p.id.startsWith('profit_chart-') || p.id === 'profit_chart') {
                        return <ProfitabilityChart symbol={p.symbol} exchange={exchange} />;
                      }
                      if (p.id.startsWith('research-')) {
                        return <ResearchChart imageSrc={researchPlots[p.id]} />;
                      }
                      return <div>Dashboard Module: {p.id}</div>;
                  }
                })()}
              </DockPanel>
            );
          })}
        </div>
        <MarketChat
          isOpen={isAiOpen}
          setIsOpen={setIsAiOpen}
          theme={theme}
          symbol={tickerQuery}
          pendingMessage={pendingMessage}
          onPlotPopout={handlePopout}
          onMessageConsumed={() => setPendingMessage(null)}
        />
      </div>

    </div>
  );
}

// --- Sidebar Helper ---

const SidebarItem = ({ icon: Icon, active = false, onClick }: any) => (
  <div
    onClick={onClick}
    className={`p-2.5 cursor-pointer transition-all rounded-lg group ${active ? 'bg-primary-text/10 text-primary-text shadow-inner' : 'text-secondary-text hover:text-primary-text hover:bg-primary-text/5'}`}
  >
    <Icon size={20} className={active ? '' : 'transition-transform'} />
  </div>
);

const AddMenuItem = ({ icon: Icon, label, onClick }: any) => (
  <div
    onClick={onClick}
    className="flex items-center gap-3 px-3 py-2.5 rounded-lg hover:bg-primary-text/5 cursor-pointer group transition-all"
  >
    <Icon size={14} className="text-secondary-text group-hover:text-primary-text transition-colors" />
    <span style={{ fontFamily: 'var(--outfit-font)' }} className="text-[11px] font-bold uppercase tracking-widest text-secondary-text group-hover:text-primary-text transition-colors">
      {label}
    </span>
  </div>
);

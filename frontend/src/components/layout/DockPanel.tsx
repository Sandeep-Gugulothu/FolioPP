"use client";

import React, { useState, useRef, useEffect } from "react";
import { ChevronDown, X, Maximize2, Minimize2, MoreVertical, Sparkles, BrainCircuit, History, Newspaper, Info, TrendingUp, Globe, LayoutList, BarChart3, TrendingDown, Activity } from "lucide-react";
import { PanelState, ICON_REGISTRY } from "@/hooks/useLayoutManager";

interface DockPanelProps {
  panel: PanelState;
  children: React.ReactNode;
  isActive: boolean;
  isDragging: boolean;
  onStartDrag: (id: string, e: React.MouseEvent, type: 'move' | 'resize') => void;
  onClose: (id: string) => void;
  onMaximize: (id: string) => void;
  onMinimize: (id: string) => void;
  onAskAI?: (id: string, title: string) => void;
  onClick: () => void;
  theme: 'light' | 'dark';
}

export const DockPanel: React.FC<DockPanelProps> = ({
  panel: p,
  children,
  isActive,
  isDragging,
  onStartDrag,
  onClose,
  onMaximize,
  onMinimize,
  onAskAI,
  onClick,
  theme
}) => {
  const isMinimized = p.minimized;
  const isMaximized = p.maximized;

  let IconComponent = ICON_REGISTRY[p.icon];
  
  if (!IconComponent || p.icon === 'Sparkles') {
     if (p.id === 'info') IconComponent = History;
     else if (p.id === 'signals' || p.id.startsWith('signals-')) IconComponent = Newspaper;
     else if (p.id === 'profile' || p.id.startsWith('profile-')) IconComponent = Info;
     else if (p.id === 'performance' || p.id.startsWith('performance-')) IconComponent = TrendingUp;
     else if (p.id === 'watchlist') IconComponent = Globe;
     else if (p.id.startsWith('financials')) IconComponent = LayoutList;
     else if (p.id.startsWith('rev_chart')) IconComponent = BarChart3;
     else if (p.id.startsWith('exp_chart')) IconComponent = TrendingDown;
     else if (p.id.startsWith('profit_chart')) IconComponent = Activity;
     else IconComponent = History;
  }

  const isLight = theme === 'light';

  return (
    <div
      onClick={onClick}
      style={{
        position: isMaximized ? 'fixed' : 'absolute',
        top: isMaximized ? '74px' : `${p.y}px`,
        left: isMaximized ? '74px' : `${p.x}px`,
        width: isMaximized ? 'calc(100% - 84px)' : `${p.w}px`,
        height: isMaximized ? 'calc(100% - 84px)' : (isMinimized ? '40px' : `${p.h}px`),
        zIndex: isMaximized ? 400 : (isActive ? 100 : 10),
      }}
      className={`
        bg-surface-bg border border-primary-border rounded-2xl flex flex-col overflow-hidden
        ${!isDragging ? 'transition-all duration-300' : ''}
        ring-1 ring-primary-text/[0.02] font-sans
      `}
    >
      {/* 🔹 Institutional Header */}
      <div
        onMouseDown={(e) => onStartDrag(p.id, e, 'move')}
        className={`
          h-12 px-5 flex items-center justify-between cursor-move select-none shrink-0 border-b border-primary-border/40 bg-primary-text/[0.01]
        `}
      >
        <div className="flex items-center gap-3">
          <IconComponent size={14} className="text-secondary-text opacity-50" />
          <span className="text-[11px] font-bold text-primary-text uppercase tracking-[0.15em] opacity-90">{p.title}</span>
        </div>

        <div className="flex items-center gap-1" onMouseDown={e => e.stopPropagation()}>
          <button 
            onClick={() => onAskAI?.(p.id, p.title)}
            className="p-2 hover:bg-primary-text/5 text-secondary-text transition-all rounded-lg group"
            title="Neural Insights"
          >
            <BrainCircuit size={14} className="group-hover:text-accent-color transition-colors" />
          </button>

          <div className="w-px h-3 bg-primary-border/60 mx-1.5" />

          <button onClick={() => onMinimize(p.id)} className="p-2 hover:bg-primary-text/5 text-secondary-text transition-colors rounded-lg"><ChevronDown size={14} /></button>
          <button onClick={() => onMaximize(p.id)} className={`p-2 transition-all rounded-lg ${isMaximized ? 'bg-accent-color/10 text-accent-color' : 'text-secondary-text hover:bg-primary-text/5'}`}><Maximize2 size={14} /></button>
          <button onClick={() => onClose(p.id)} className="p-2 hover:bg-rose-500/10 hover:text-rose-500 text-secondary-text transition-all rounded-lg"><X size={14} /></button>
        </div>
      </div>

      {/* 🔹 Dynamic Data Surface */}
      {!isMinimized && (
        <div className="flex-1 relative overflow-auto no-scrollbar bg-primary-text/[0.005]">
          {children}
        </div>
      )}

      {/* 🔹 Resize Grip */}
      {!isMinimized && !isMaximized && (
        <div
          onMouseDown={(e) => onStartDrag(p.id, e, 'resize')}
          className="absolute bottom-1 right-1 w-4 h-4 cursor-nwse-resize flex items-end justify-end p-0.5 opacity-20 hover:opacity-100 transition-opacity"
        >
          <div className="w-1.5 h-1.5 border-r border-b border-primary-text" />
        </div>
      )}
    </div>
  );
};

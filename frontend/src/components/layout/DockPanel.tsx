"use client";

import React from "react";
import { ChevronDown, X, Maximize2, MoreVertical, PlusSquare } from "lucide-react";
import { PanelState } from "@/hooks/useLayoutManager";

interface DockPanelProps {
  panel: PanelState;
  isActive: boolean;
  onStartDrag: (id: string, e: React.MouseEvent, type: 'move' | 'resize') => void;
  onClose: (id: string) => void;
  onMaximize: (id: string) => void;
  onMinimize: (id: string) => void;
  onClick: () => void;
  children: React.ReactNode;
}

export const DockPanel: React.FC<DockPanelProps> = ({ 
  panel: p, 
  isActive, 
  onStartDrag, 
  onClose, 
  onMaximize, 
  onMinimize,
  onClick,
  children 
}) => {
  const isMaximized = p.maximized;
  const isMinimized = p.minimized;
  
  const dynamicStyle = isMaximized ? {
     left: 10, top: 74, width: 'calc(100% - 20px)', height: 'calc(100vh - 94px)', zIndex: 300, position: 'fixed' as const
  } : {
     left: p.x, top: p.y, width: p.w, height: isMinimized ? 40 : p.h, zIndex: isActive ? 40 : 10, position: 'absolute' as const
  };

  return (
    <div 
      className={`flex flex-col rounded-xl border border-white/5 transition-all overflow-hidden bg-black shadow-2xl ${isActive ? 'ring-1 ring-white/10' : ''}`}
      style={dynamicStyle}
      onMouseDown={onClick}
    >
      <div 
        className={`h-11 px-5 flex items-center justify-between shrink-0 hover:bg-white/[0.03] transition-colors border-b border-white/5 ${isMaximized ? 'cursor-default' : 'cursor-grab active:cursor-grabbing'}`}
        onMouseDown={(e) => onStartDrag(p.id, e, 'move')}
      >
        <div className="flex items-center gap-3 select-none">
          <p.icon size={13} className="text-slate-500" />
          <span className="text-[10px] font-black text-white uppercase tracking-widest">{p.title}</span>
        </div>

        <div className="flex items-center gap-1 opacity-20 hover:opacity-100 transition-opacity">
          <button onClick={(e) => { e.stopPropagation(); onMinimize(p.id); }} className="p-1.5 hover:bg-white/10 rounded-md transition-all text-slate-100">
            <ChevronDown size={14} className={`transition-transform duration-300 ${isMinimized ? 'rotate-[-90deg]' : ''}`} />
          </button>
          <button onClick={(e) => { e.stopPropagation(); onMaximize(p.id); }} className="p-1.5 hover:bg-white/10 rounded-md transition-all text-slate-100">
            {isMaximized ? <X size={14} /> : <PlusSquare size={14} />}
          </button>
          <button className="p-1.5 hover:bg-white/10 rounded-md transition-all text-slate-100">
            <MoreVertical size={14} />
          </button>
          <div className="w-px h-3 bg-white/10 mx-1" />
          <button onClick={(e) => { e.stopPropagation(); onClose(p.id); }} className="p-1.5 hover:bg-white/10 rounded-md transition-all text-rose-500/80 hover:text-rose-500">
            <X size={14} />
          </button>
        </div>
      </div>

      <div className={`flex-1 overflow-hidden relative ${isMaximized ? 'bg-[#0c0c0c]' : ''} ${isMinimized ? 'hidden' : 'block'}`}>
        {children}

        {!isMaximized && !isMinimized && (
          <div 
            className="absolute bottom-1 right-1 w-5 h-5 cursor-nwse-resize flex items-center justify-center opacity-10 hover:opacity-100 transition-opacity"
            onMouseDown={(e) => onStartDrag(p.id, e, 'resize')}
          >
            <div className="w-1.5 h-1.5 border-r border-b border-white/40" />
          </div>
        )}
      </div>
    </div>
  );
};

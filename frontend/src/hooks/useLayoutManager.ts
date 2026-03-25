"use client";

import { useState, useRef, useCallback, useEffect } from "react";
import {
  History, TrendingUp, Newspaper, Info, LayoutList,
  BarChart3, TrendingDown, Activity, Globe, LayoutDashboard,
  CandlestickChart
} from "lucide-react";

// The Registry: Resolves strings to actual React components
export const ICON_REGISTRY: Record<string, any> = {
  History: History,
  TrendingUp: TrendingUp,
  Newspaper: Newspaper,
  Info: Info,
  LayoutList: LayoutList,
  BarChart3: BarChart3,
  TrendingDown: TrendingDown,
  Activity: Activity,
  Globe: Globe,
  LayoutDashboard: LayoutDashboard,
  CandlestickChart: CandlestickChart
};

export interface PanelState {
  id: string;
  title: string;
  symbol: string;
  icon: string | any;
  x: number;
  y: number;
  w: number;
  h: number;
  minimized?: boolean;
  maximized?: boolean;
}

export function useLayoutManager(initialPanels: PanelState[], storageKey?: string) {
  const [panels, setPanels] = useState<PanelState[]>(initialPanels);
  const [activePanelId, setActivePanelId] = useState<string | null>(null);
  const dragRef = useRef<{ id: string, startX: number, startY: number, startWidth: number, startHeight: number, panelStartX: number, panelStartY: number, type: 'move' | 'resize' } | null>(null);

  const isInitialized = useRef(false);

  // 1. Load from Neural Memory (LocalStorage) on mount
  useEffect(() => {
    if (typeof window === "undefined" || !storageKey) return;
    const saved = localStorage.getItem(`foliopp_layout_${storageKey}`);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        // FORCE HEAL: Ensure icon strings match the expected IDs for restoration
        const sanitized = parsed.map((p: any) => {
          let healedIcon = p.icon;
          // Aggressive healing based on ID mapping
          if (p.id === 'info') healedIcon = 'History';
          else if (p.id === 'signals' || p.id.startsWith('signals-')) healedIcon = 'Newspaper';
          else if (p.id === 'profile' || p.id.startsWith('profile-')) healedIcon = 'Info';
          else if (p.id === 'performance' || p.id.startsWith('performance-')) healedIcon = 'TrendingUp';
          else if (p.id.startsWith('financials')) healedIcon = 'LayoutList';
          else if (p.id.startsWith('rev_chart')) healedIcon = 'BarChart3';
          else if (p.id.startsWith('exp_chart')) healedIcon = 'TrendingDown';
          else if (p.id.startsWith('profit_chart')) healedIcon = 'Activity';
          else if (p.id === 'watchlist') healedIcon = 'Globe';
          else if (p.id === 'tech_chart') healedIcon = 'CandlestickChart';

          return { ...p, icon: healedIcon };
        });
        setPanels(sanitized);
      } catch (e) {
        console.error("Failed to restore layout memory:", e);
      }
    }
    isInitialized.current = true;
  }, [storageKey]);

  // 2. Mirror into Neural Memory whenever layout shifts
  useEffect(() => {
    if (typeof window === "undefined" || !storageKey || !isInitialized.current) return;
    localStorage.setItem(`foliopp_layout_${storageKey}`, JSON.stringify(panels));
  }, [panels, storageKey]);

  // --- Hybrid Collision & Pull-Up Logic ---

  const resolveLayout = useCallback((currentPanels: PanelState[], activeId: string, isDragging: boolean = false) => {
    let adjusted = [...currentPanels];
    const active = adjusted.find(p => p.id === activeId);
    if (!active || active.maximized) return currentPanels;

    let changed = true;
    while (changed) {
      changed = false;
      for (let i = 0; i < adjusted.length; i++) {
        const p = adjusted[i];
        if (p.id === activeId || p.maximized) continue;
        const pEffectiveH = p.minimized ? 40 : p.h;
        const activeEffectiveH = active.minimized ? 40 : active.h;
        const overlapX = active.x < p.x + p.w && active.x + active.w > p.x;
        const overlapY = active.y < p.y + pEffectiveH && active.y + active.h > p.y;
        if (overlapX && overlapY) {
          const buffer = 15;
          if (p.y < (active.y + activeEffectiveH + buffer)) {
            adjusted[i] = { ...p, y: active.y + activeEffectiveH + buffer };
            changed = true;
          }
        }
      }
    }

    if (isDragging) return adjusted;

    const sorted = [...adjusted].sort((a, b) => a.y - b.y);
    let finalLayout: PanelState[] = [];
    for (const p of sorted) {
      if (p.id === activeId || p.maximized) { finalLayout.push(p); continue; }
      let currentY = 15;
      let foundY = false;
      const pEffectiveH = p.minimized ? 40 : p.h;
      while (!foundY) {
        const collision = finalLayout.find(other => {
          const otherEffectiveH = other.minimized ? 40 : other.h;
          const overlapX = p.x < other.x + other.w && p.x + p.w > other.x;
          const overlapY = currentY < other.y + otherEffectiveH && currentY + pEffectiveH > other.y;
          return overlapX && overlapY;
        });
        if (!collision) { finalLayout.push({ ...p, y: currentY }); foundY = true; }
        else {
          const collisionEffectiveH = collision.minimized ? 40 : collision.h;
          currentY = collision.y + collisionEffectiveH + 15;
        }
      }
    }
    return finalLayout;
  }, []);

  const onMouseMove = useCallback((e: MouseEvent) => {
    if (!dragRef.current) return;
    const { id, startX, startY, startWidth, startHeight, panelStartX, panelStartY, type } = dragRef.current;
    const deltaX = e.clientX - startX;
    const deltaY = e.clientY - startY;

    setPanels(prev => {
      let nextPanels = prev.map(p => {
        if (p.id !== id) return p;
        if (type === 'resize') return { ...p, w: Math.max(200, startWidth + deltaX), h: Math.max(100, startHeight + deltaY) };
        return { ...p, x: Math.max(0, panelStartX + deltaX), y: Math.max(15, panelStartY + deltaY) };
      });
      return resolveLayout(nextPanels, id, true);
    });
  }, [resolveLayout]);

  const onMouseUp = useCallback(() => {
    if (dragRef.current) {
      const id = dragRef.current.id;
      setPanels(prev => resolveLayout(prev, id, false));
    }
    dragRef.current = null;
    document.removeEventListener('mousemove', onMouseMove);
    document.removeEventListener('mouseup', onMouseUp);
  }, [onMouseMove, resolveLayout]);

  const startDrag = useCallback((id: string, e: React.MouseEvent, type: 'move' | 'resize') => {
    const panel = panels.find(p => p.id === id);
    if (!panel || panel.maximized) return;
    e.preventDefault();
    dragRef.current = { id, startX: e.clientX, startY: e.clientY, startWidth: panel.w, startHeight: panel.h, panelStartX: panel.x, panelStartY: panel.y, type };
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
    setActivePanelId(id);
  }, [panels, onMouseMove, onMouseUp]);

  const handleClose = useCallback((id: string) => setPanels(prev => prev.filter(p => p.id !== id)), []);
  const handleMaximize = useCallback((id: string) => setPanels(prev => {
    const next = prev.map(p => p.id === id ? { ...p, maximized: !p.maximized } : p);
    return resolveLayout(next, id);
  }), [resolveLayout]);

  const handleMinimize = useCallback((id: string) => setPanels(prev => {
    const next = prev.map(p => p.id === id ? { ...p, minimized: !p.minimized } : p);
    return resolveLayout(next, id);
  }), [resolveLayout]);

  const updateSymbols = useCallback((newSymbol: string) => {
    setPanels(prev => prev.map(p => ({ ...p, symbol: newSymbol.toUpperCase() })));
  }, []);

  const addPanel = useCallback((panel: PanelState) => {
    setPanels(prev => [...prev, panel]);
  }, []);

  return {
    panels,
    activePanelId,
    setActivePanelId,
    startDrag,
    handleClose,
    handleMaximize,
    handleMinimize,
    updateSymbols,
    addPanel
  };
}

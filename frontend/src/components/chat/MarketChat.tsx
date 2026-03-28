"use client";

import React, { useState, useRef, useEffect } from "react";
import dynamic from 'next/dynamic';
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

import {
  X, Sparkles, Send, BrainCircuit, Globe, Zap,
  Settings, Share2, Database, Paperclip, Lightbulb,
  Maximize2, Trash2, ChevronDown, User, Bot, Loader2, MessageSquare,
  FileText, TrendingUp, AlertCircle, History, Plus, RefreshCw
} from "lucide-react";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  thoughts?: string[];
}

interface MarketChatProps {
  isOpen: boolean;
  setIsOpen: (open: boolean) => void;
  theme: 'light' | 'dark';
  pendingMessage?: string | null;
  onMessageConsumed?: () => void;
  onPlotPopout?: (imageSrc: string) => void;
  symbol: string;
}

export const MarketChat: React.FC<MarketChatProps> = ({ isOpen, setIsOpen, theme, pendingMessage, onMessageConsumed, onPlotPopout, symbol }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState("default");
  const [sessions, setSessions] = useState<any[]>([]);
  const [showSessions, setShowSessions] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);
  const sessionMenuRef = useRef<HTMLDivElement>(null);

  const prompts = [
    "Analyze the trend in dividend payouts and dividend yield.",
    "Using the financial statements, assess the trend in revenue growth.",
    "Analyze the gross and net profit margin trend."
  ];

  const loadHistory = async () => {
    setIsTyping(true);
    try {
      // Add t parameter for cache-busting to bypass browser caches
      const res = await fetch(`/intelligence/history?session_id=${sessionId}&t=${Date.now()}`);
      if (res.ok) {
        const history = await res.json();
        const mapped = history.map((m: any) => ({
          role: m.role,
          content: m.content,
          thoughts: Array.isArray(m.thoughts) ? m.thoughts : []
        }));
        setMessages(mapped);
        console.log(`Loaded ${mapped.length} messages for session ${sessionId}`);
      } else {
        console.error("History fetch failed with status:", res.status);
      }
    } catch (e) {
      console.error("Failed to load chat history:", e);
    } finally {
      setIsTyping(false);
      setHistoryLoaded(true);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setSessionId(`session_${Date.now()}`);
  };

  const loadSessions = async () => {
    try {
      const res = await fetch(`/intelligence/sessions`);
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
      }
    } catch (e) {
      console.error("Failed to load sessions:", e);
    }
  };

  const switchSession = (id: string) => {
    setSessionId(id);
    setShowSessions(false);
    // Use the id directly because state might not have updated yet
    const refresh = async () => {
        setIsTyping(true);
        try {
          const res = await fetch(`/intelligence/history?session_id=${id}&t=${Date.now()}`);
          if (res.ok) {
            const history = await res.json();
            setMessages(history.map((m: any) => ({
              role: m.role,
              content: m.content,
              thoughts: Array.isArray(m.thoughts) ? m.thoughts : []
            })));
          }
        } finally {
          setIsTyping(false);
        }
    }
    refresh();
  };

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (sessionMenuRef.current && !sessionMenuRef.current.contains(event.target as Node)) {
        setShowSessions(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  useEffect(() => {
    if (historyLoaded) return;
    loadHistory();
  }, [historyLoaded]);


  useEffect(() => {
    if (isOpen && pendingMessage) {
      setInput(pendingMessage); // Load into terminal input instead of auto-sending
      onMessageConsumed?.();
    }
  }, [isOpen, pendingMessage]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSend = async (text: string) => {
    if (!text.trim() || isTyping) return;

    const userMsg: Message = { role: 'user', content: text };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setIsTyping(true);

    try {
      const response = await fetch(`/intelligence/chat?query=${encodeURIComponent(text)}&session_id=${sessionId}`);
      if (!response.ok) throw new Error("Failed to connect to agent");

      const reader = response.body?.getReader();
      if (!reader) throw new Error("No reader available");

      const assistantMsg: Message = { role: 'assistant', content: "" };
      setMessages(prev => [...prev, assistantMsg]);

      let fullContent = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        fullContent += chunk;

        // Extract Thoughts
        const thoughts: string[] = [];
        let cleanContent = fullContent;
        const thoughtRegex = /\[THOUGHT\]([\s\S]*?)\[\/THOUGHT\]/g;
        let match;

        while ((match = thoughtRegex.exec(fullContent)) !== null) {
          thoughts.push(match[1].trim());
          cleanContent = cleanContent.replace(match[0], "");
        }

        // Check for Research Plots
        if (cleanContent.includes("[RESEARCH_PLOT]")) {
          const plotMatch = cleanContent.match(/\[RESEARCH_PLOT\]([\s\S]*?)\[\/RESEARCH_PLOT\]/);
          if (plotMatch && plotMatch[1]) {
            onPlotPopout?.(plotMatch[1].trim());
            cleanContent = cleanContent.replace(/\[RESEARCH_PLOT\][\s\S]*?\[\/RESEARCH_PLOT\]/, "\n\n*Institutional visualization generated. Popping out research window...*\n");
          }
        }

        setMessages(prev => {
          const newMsgs = [...prev];
          newMsgs[newMsgs.length - 1] = {
            ...assistantMsg,
            content: cleanContent.trim(),
            thoughts: thoughts.length > 0 ? thoughts : undefined
          };
          return newMsgs;
        });
      }
    } catch (error) {
      console.error("Chat Error:", error);
      setMessages(prev => [...prev, { role: 'assistant', content: "Error: Could not connect to the intelligence layer." }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend(input);
    }
  };

  const isLight = theme === 'light';

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-10 right-10 w-12 h-12 rounded-xl flex items-center justify-center transition-all z-[900] shadow-2xl backdrop-blur-md group hover:scale-110 active:scale-95 ${isLight ? 'bg-white border border-black/10 text-black shadow-black/5 hover:bg-white/90' : 'bg-black border border-white/10 text-white hover:bg-black/90'}`}
      >
        <div className="relative">
          <BrainCircuit size={22} className="transition-colors" />
        </div>
      </button>
    );
  }

  const textColorClass = isLight ? 'text-black' : 'text-white';
  const secondaryTextColorClass = isLight ? 'text-black/60' : 'text-white/60';
  const tertiaryTextColorClass = isLight ? 'text-black/30' : 'text-white/30';
  const accentBorderClass = isLight ? 'border-black/5' : 'border-white/5';
  const accentBgClass = isLight ? 'bg-black/[0.02]' : 'bg-white/[0.02]';

  return (
    <div className={`fixed top-[74px] right-[10px] bottom-[10px] ${isExpanded ? 'w-[75%] left-auto' : 'w-[500px]'} ${isLight ? 'bg-white' : 'bg-surface-bg'} border ${isLight ? 'border-black/10' : 'border-primary-border'} rounded-xl flex flex-col z-[1000] transition-all duration-500 ease-in-out shadow-2xl overflow-hidden font-sans`}>
      {/* Header - Styled like DockPanels */}
      <div className={`h-11 px-6 flex items-center justify-between border-b ${isLight ? 'border-black/5 bg-black/[0.02]' : 'border-primary-border bg-primary-text/[0.01]'} select-none`}>
        <div className="flex items-center gap-3">
          <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(16,185,129,0.3)]" />
          <span
            className={`text-[11px] font-extrabold uppercase tracking-[0.2em] ${isLight ? 'text-black/90' : 'text-white/80'}`}
          >
            Intelligence Terminal
          </span>
        </div>
        <div className="flex items-center gap-2">
          <div className="relative" ref={sessionMenuRef}>
            <button
              onClick={() => {
                if (!showSessions) loadSessions();
                setShowSessions(!showSessions);
              }}
              disabled={isTyping}
              title="Research Registry"
              className={`p-1.5 transition-all ${showSessions ? 'bg-emerald-500/10 text-emerald-500' : (isLight ? 'text-black/60 hover:text-emerald-600' : 'text-primary-text hover:text-emerald-400')}`}
            >
              <History size={13} />
            </button>
            
            {showSessions && (
              <div className={`absolute top-full right-0 mt-2 w-72 max-h-[400px] overflow-y-auto ${isLight ? 'bg-white border-black/10' : 'bg-surface-bg border-primary-border'} border rounded-xl shadow-2xl z-[1100] p-2 animate-in fade-in slide-in-from-top-2 duration-200`}>
                <div className={`px-3 py-2 border-b mb-1 ${isLight ? 'border-black/5' : 'border-white/5'}`}>
                  <span className={`text-[10px] font-black uppercase tracking-[0.2em] ${isLight ? 'text-black/40' : 'text-white/20'}`}>Institutional Registry</span>
                </div>
                {sessions.length === 0 ? (
                  <div className="p-4 text-center">
                    <span className={`text-[10px] uppercase tracking-widest ${isLight ? 'text-black/30' : 'text-white/10'}`}>No Active Sessions</span>
                  </div>
                ) : (
                  sessions.map((s) => (
                    <button
                      key={s.session_id}
                      onClick={() => switchSession(s.session_id)}
                      className={`w-full text-left p-3 rounded-lg transition-all group mb-1 ${sessionId === s.session_id ? (isLight ? 'bg-black/5' : 'bg-white/5') : 'hover:bg-emerald-500/5'}`}
                    >
                      <div className="flex flex-col gap-1">
                        <div className="flex items-center justify-between">
                          <span className={`text-[11px] font-bold truncate max-w-[180px] ${sessionId === s.session_id ? 'text-emerald-500' : textColorClass}`}>
                            {s.title || "Untitled Research"}
                          </span>
                          <span className={`text-[9px] opacity-30 ${textColorClass}`}>{new Date(s.last_active).toLocaleDateString()}</span>
                        </div>
                        <span className={`text-[9px] font-mono opacity-20 truncate ${textColorClass}`}>{s.session_id}</span>
                      </div>
                    </button>
                  ))
                )}
              </div>
            )}
          </div>
          <button
            onClick={() => handleNewChat()}
            title="New Research Session"
            className={`p-1.5 transition-colors ${isLight ? 'text-black/60 hover:text-black' : 'text-primary-text hover:text-white'}`}
          >
            <Plus size={13} />
          </button>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className={`p-1.5 transition-all rounded-md ${isExpanded ? (isLight ? 'bg-black/10 text-black' : 'bg-white/10 text-white') : (isLight ? 'text-black/60 hover:bg-black/5' : 'text-primary-text hover:bg-white/5')}`}
          >
            <Maximize2 size={13} />
          </button>
          <button onClick={() => setIsOpen(false)} className={`p-1.5 transition-colors ${isLight ? 'text-black/60 hover:bg-rose-500/10' : 'text-primary-text hover:bg-rose-500/10'}`}><X size={13} /></button>
        </div>
      </div>

      {/* Chat Messages */}
      <div
        ref={scrollRef}
        className={`flex-1 overflow-y-auto no-scrollbar p-6 space-y-8 ${isLight ? 'bg-white' : 'bg-surface-bg'}`}
      >
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center space-y-12">
            <div className="flex flex-col items-center gap-6">
              <div className="w-16 h-16 bg-white/5 rounded-2xl flex items-center justify-center border border-white/10">
                <Sparkles size={28} className="text-white/40 animate-pulse" />
              </div>
              <div className="text-center">
                <h2 className="text-[12px] font-semibold text-primary-text/80 tracking-[0.3em] uppercase mb-2">Institutional Suite</h2>
                <p className="text-[10px] text-secondary-text tracking-[0.2em] uppercase opacity-40 leading-relaxed max-w-[200px] mx-auto">
                  Awaiting directives for {symbol}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 gap-2 w-full max-w-[320px]">
              {prompts.map((p, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(p)}
                  className={`p-3.5 w-full border rounded-lg transition-all text-left group ${isLight ? 'bg-black/[0.03] border-black/5 hover:bg-black/5' : 'bg-white/[0.03] border-white/5 hover:bg-white/5'}`}
                >
                  <div className="flex items-center gap-3">
                    <MessageSquare size={12} className={`${isLight ? 'text-black/40' : 'text-white/30'} group-hover:text-amber-500 transition-colors opacity-100`} />
                    <p
                      className={`text-[11px] font-bold uppercase tracking-widest ${isLight ? 'text-black/60 group-hover:text-black' : 'text-white/40 group-hover:text-white'}`}
                    >
                      {p}
                    </p>
                  </div>
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((m, i) => (
            <div key={i} className={`flex flex-col gap-3 ${m.role === 'user' ? 'items-end' : 'items-start'} animate-in fade-in slide-in-from-bottom-2 duration-300`}>
              <div className="flex gap-4 items-start w-full">
                {m.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex-shrink-0 flex items-center justify-center shadow-lg">
                    <Bot size={18} className="text-white/40" />
                  </div>
                )}

                <div className="flex-1 space-y-4">
                  {/* Step-by-step Reasoning Accordion */}
                  {m.thoughts && m.thoughts.length > 0 && (
                    <div className={`${isLight ? 'bg-black/[0.02]' : 'bg-primary-text/[0.02]'} border ${isLight ? 'border-black/5' : 'border-primary-border'} rounded-xl overflow-hidden mb-4`}>
                      <details className="group" open={i === messages.length - 1}>
                        <summary className={`flex items-center justify-between p-3 cursor-pointer ${isLight ? 'hover:bg-black/[0.04]' : 'hover:bg-primary-text/[0.04]'} transition-colors list-none`}>
                          <div className="flex items-center gap-2">
                            <div className={`w-1.5 h-1.5 ${isLight ? 'bg-black/20' : 'bg-white/20'} rounded-full animate-pulse`} />
                            <span
                              className={`text-[10px] font-extrabold uppercase tracking-widest ${isLight ? 'text-black' : 'text-secondary-text'}`}
                            >
                              Research Reasoning History ({m.thoughts.length} steps)
                            </span>
                          </div>
                          <ChevronDown size={14} className={`${isLight ? 'text-black/20' : 'text-secondary-text'} transition-transform group-open:rotate-180`} />
                        </summary>
                        <div className={`px-4 pb-4 space-y-3 pt-1 border-t ${isLight ? 'border-black/5' : 'border-primary-border/10'}`}>
                          {m.thoughts.map((thought, idx) => (
                            <div key={idx} className="flex gap-3 items-start border-l border-primary-border/20 pl-4 py-1">
                              <p
                                className="text-[11px] leading-relaxed text-primary-text/60 italic"
                              >
                                {thought}
                              </p>
                            </div>
                          ))}
                        </div>
                      </details>
                    </div>
                  )}

                  {m.content && (
                    <div
                      className={`max-w-[85%] p-4 rounded-xl text-[13px] leading-relaxed font-medium tracking-tight overflow-hidden ${m.role === 'user'
                        ? (isLight ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-900 ml-auto' : 'bg-white/5 border border-white/10 text-white/90 ml-auto')
                        : (isLight ? 'bg-black/[0.03] border-black/10 text-black/90 shadow-sm' : 'bg-primary-text/[0.04] border border-primary-border text-primary-text/90 shadow-sm')
                        }`}>
                      {m.role === 'user' ? (
                        m.content
                      ) : (
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            h1: ({ children }) => <h1 className={`text-[14px] font-black uppercase tracking-[0.2em] mb-4 mt-2 border-b pb-2 ${textColorClass} ${isLight ? 'border-black/10' : 'border-white/10'}`}>{children}</h1>,
                            h2: ({ children }) => <h2 className={`text-[13px] font-black uppercase tracking-widest mb-3 mt-5 flex items-center gap-2 ${secondaryTextColorClass}`}><div className={`w-1 h-3 rounded-full ${isLight ? 'bg-black/20' : 'bg-white/20'}`}/>{children}</h2>,
                            h3: ({ children }) => <h3 className={`text-[12px] font-bold uppercase tracking-widest mb-3 mt-4 ${tertiaryTextColorClass}`}>{children}</h3>,
                            p: ({ children }) => <p className="mb-3 opacity-90 leading-relaxed last:mb-0">{children}</p>,
                            ul: ({ children }) => <ul className="space-y-2 mb-4 ml-2">{children}</ul>,
                            li: ({ children }) => (
                              <li className="flex gap-3 items-start group">
                                <div className={`w-1 h-1 rounded-full mt-2 flex-shrink-0 transition-colors ${isLight ? 'bg-black/20 group-hover:bg-black/60' : 'bg-white/20 group-hover:bg-white/40'}`} />
                                <span className="flex-1 opacity-80 group-hover:opacity-100 transition-opacity">{children}</span>
                              </li>
                            ),
                            strong: ({ children }) => <strong className={`font-black ${textColorClass}`}>{children}</strong>,
                            table: ({ children }) => (
                              <div className={`overflow-x-auto my-6 rounded-xl border backdrop-blur-sm ${isLight ? 'border-black/5 bg-black/5' : 'border-white/5 bg-white/5'}`}>
                                <table className="w-full text-left border-collapse">{children}</table>
                              </div>
                            ),
                            thead: ({ children }) => <thead className={`border-b font-black uppercase text-[10px] tracking-widest ${isLight ? 'bg-black/5 border-black/10 text-black/40' : 'bg-white/5 border-white/10 text-white/40'}`}>{children}</thead>,
                            th: ({ children }) => <th className="p-3">{children}</th>,
                            td: ({ children }) => <td className={`p-3 border-t text-[11px] ${isLight ? 'border-black/5 text-black/60' : 'border-white/5 text-white/60'}`}>{children}</td>,
                            code: ({ children }) => <code className={`px-1.5 py-0.5 rounded-md font-mono text-[11px] ${isLight ? 'bg-black/5 text-black' : 'bg-white/5 text-white'}`}>{children}</code>,
                            blockquote: ({ children }) => <blockquote className={`border-l-2 pl-4 py-1 italic opacity-60 my-4 ${isLight ? 'border-black/10 bg-black/5' : 'border-white/10 bg-white/5'}`}>{children}</blockquote>,
                          }}
                        >
                          {m.content}
                        </ReactMarkdown>
                      )}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
        {isTyping && (
          <div className="flex gap-4 justify-start animate-pulse">
            <div className={`p-4 rounded-xl border w-16 h-12 flex items-center justify-center ${isLight ? 'bg-black/[0.02] border-black/5' : 'bg-primary-text/[0.01] border-primary-border'}`}>
              <div className="flex gap-1">
                <div className={`w-1 h-1 rounded-full animate-bounce ${isLight ? 'bg-black/20' : 'bg-white/20'}`} />
                <div className={`w-1 h-1 rounded-full animate-bounce [animation-delay:0.2s] ${isLight ? 'bg-black/20' : 'bg-white/20'}`} />
                <div className={`w-1 h-1 rounded-full animate-bounce [animation-delay:0.4s] ${isLight ? 'bg-black/20' : 'bg-white/20'}`} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Terminal */}
      <div className={`p-6 border-t ${isLight ? 'bg-white border-black/5' : 'bg-surface-bg border-primary-border'}`}>
        <div className={`${isLight ? 'bg-black/[0.02] border-black/10' : 'bg-primary-text/[0.02] border-primary-border'} border rounded-xl p-4 transition-all focus-within:border-emerald-500/30`}>
          <div className="flex items-center justify-between mb-3 select-none">
            <span
              className={`text-[10px] font-black uppercase tracking-[0.2em] ${isLight ? 'text-black/80' : 'text-white/40'}`}
            >
              Research Input Pipeline
            </span>
            <div className="flex gap-3">
              <Settings size={12} className={`cursor-pointer transition-colors ${isLight ? 'text-black/30 hover:text-black' : 'hover:text-white'}`} />
              <Database size={12} className={`cursor-pointer transition-colors ${isLight ? 'text-black/30 hover:text-black' : 'hover:text-white'}`} />
            </div>
          </div>

          <textarea
            rows={3}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            className={`w-full bg-transparent border-none outline-none text-[13px] font-medium ${isLight ? 'text-black' : 'text-white/70'} placeholder:${isLight ? 'placeholder-black/30' : 'placeholder-secondary-text/20'} resize-none leading-relaxed`}
            placeholder={`Identify patterns in ${symbol || 'SBIN'}...`}
          />

          <div className="flex items-center justify-between mt-3 pt-3 border-t border-primary-text/5">
            <div className="flex gap-2">
              <div className="w-1.5 h-1.5 bg-white/10 rounded-full" />
              <div className="w-1.5 h-1.5 bg-emerald-500/20 rounded-full" />
            </div>
            <button
              onClick={() => handleSend(input)}
              disabled={!input.trim() || isTyping}
              className={`px-4 py-1.5 rounded-lg flex items-center gap-2 transition-all ${input.trim() && !isTyping
                  ? 'bg-white/10 text-white border border-white/20 hover:bg-white/20 shadow-sm'
                  : 'bg-primary-text/5 text-secondary-text opacity-40 cursor-not-allowed'
                }`}
            >
              <span
                className="text-[10px] font-bold uppercase tracking-widest"
              >
                Execute
              </span>
              <Send size={12} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

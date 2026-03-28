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
  const [isTyping, setIsTyping] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const prompts = [
    "Analyze the trend in dividend payouts and dividend yield.",
    "Using the financial statements, assess the trend in revenue growth.",
    "Analyze the gross and net profit margin trend."
  ];

  const loadHistory = async () => {
    try {
      const res = await fetch(`/intelligence/history?session_id=${sessionId}`);
      if (res.ok) {
        const history = await res.json();
        setMessages(history.map((m: any) => ({
          role: m.role,
          content: m.content,
          thoughts: m.thoughts
        })));
      }
      setHistoryLoaded(true);
    } catch (e) {
      console.error("Failed to load chat history:", e);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setSessionId(`session_${Date.now()}`);
  };

  useEffect(() => {
    if (historyLoaded) return;
    loadHistory();
  }, [historyLoaded]);


  useEffect(() => {
    if (isOpen && pendingMessage) {
      handleSend(pendingMessage);
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

  if (!isOpen) {
    const isLight = theme === 'light';
    return (
      <button
        onClick={() => setIsOpen(true)}
        className={`fixed bottom-10 right-10 w-12 h-12 rounded-xl flex items-center justify-center transition-all z-[900] shadow-2xl backdrop-blur-md group hover:scale-110 active:scale-95 ${isLight ? 'bg-black border border-black text-white hover:bg-black/90' : 'bg-white border border-white text-black hover:bg-white/90'}`}
      >
        <div className="relative">
          <BrainCircuit size={22} className="transition-colors" />
        </div>
      </button>
    );
  }

  return (
    <div className={`fixed top-[74px] right-[10px] bottom-[10px] ${isExpanded ? 'w-[75%] left-auto' : 'w-[500px]'} bg-surface-bg border border-primary-border rounded-xl flex flex-col z-[1000] transition-all duration-500 ease-in-out shadow-2xl overflow-hidden font-sans`}>
      {/* Header - Styled like DockPanels */}
      <div className="h-11 px-6 flex items-center justify-between border-b border-primary-border bg-primary-text/[0.01] select-none">
        <div className="flex items-center gap-3">
          <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(16,185,129,0.3)]" />
          <span
            className="text-[11px] font-bold text-primary-text uppercase tracking-widest opacity-80"
          >
            Intelligence Terminal
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => loadHistory()}
            title="Refresh History"
            className="p-1.5 text-primary-text hover:text-emerald-400 transition-colors"
          >
            <History size={13} />
          </button>
          <button
            onClick={() => handleNewChat()}
            title="New Research Session"
            className="p-1.5 text-primary-text hover:text-white transition-colors"
          >
            <Plus size={13} />
          </button>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className={`p-1.5 transition-all rounded-md ${isExpanded ? 'bg-white/10 text-white' : 'text-primary-text hover:bg-white/5'}`}
          >
            <Maximize2 size={13} />
          </button>
          <button onClick={() => setIsOpen(false)} className="p-1.5 text-primary-text hover:bg-rose-500/10 transition-colors"><X size={13} /></button>
        </div>
      </div>

      {/* Chat Messages */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto no-scrollbar p-6 space-y-8 bg-surface-bg"
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
                  className="p-3.5 w-full bg-primary-text/[0.02] border border-primary-border rounded-lg transition-all text-left hover:bg-white/5 group"
                >
                  <div className="flex items-center gap-3">
                    <MessageSquare size={12} className="text-secondary-text group-hover:text-white transition-colors opacity-40" />
                    <p
                      className="text-[11px] text-primary-text font-medium uppercase tracking-widest opacity-40 group-hover:opacity-100"
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
                    <div className="bg-primary-text/[0.02] border border-primary-border rounded-xl overflow-hidden mb-4">
                      <details className="group" open={i === messages.length - 1}>
                        <summary className="flex items-center justify-between p-3 cursor-pointer hover:bg-primary-text/[0.04] transition-colors list-none">
                          <div className="flex items-center gap-2">
                            <div className="w-1.5 h-1.5 bg-white/20 rounded-full animate-pulse" />
                            <span
                              className="text-[10px] font-bold uppercase tracking-widest text-secondary-text"
                            >
                              Research Reasoning History ({m.thoughts.length} steps)
                            </span>
                          </div>
                          <ChevronDown size={14} className="text-secondary-text transition-transform group-open:rotate-180" />
                        </summary>
                        <div className="px-4 pb-4 space-y-3 pt-1 border-t border-primary-border/10">
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
                        ? 'bg-white/5 border border-white/10 text-white/90 ml-auto'
                        : 'bg-primary-text/[0.04] border border-primary-border text-primary-text/90 shadow-sm'
                        }`}>
                      {m.role === 'user' ? (
                        m.content
                      ) : (
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            h1: ({ children }) => <h1 className="text-[14px] font-black uppercase tracking-[0.2em] text-white/90 mb-4 mt-2 border-b border-white/10 pb-2">{children}</h1>,
                            h2: ({ children }) => <h2 className="text-[13px] font-black uppercase tracking-widest text-white/70 mb-3 mt-5 flex items-center gap-2"><div className="w-1 h-3 bg-white/20 rounded-full"/>{children}</h2>,
                            h3: ({ children }) => <h3 className="text-[12px] font-bold uppercase tracking-widest text-white/60 mb-3 mt-4">{children}</h3>,
                            h4: ({ children }) => <h4 className="text-[11px] font-bold uppercase tracking-widest text-secondary-text/60 mb-2 mt-4">{children}</h4>,
                            p: ({ children }) => <p className="mb-3 opacity-90 leading-relaxed last:mb-0">{children}</p>,
                            ul: ({ children }) => <ul className="space-y-2 mb-4 ml-2">{children}</ul>,
                            ol: ({ children }) => <ol className="space-y-2 mb-4 ml-6 list-decimal">{children}</ol>,
                            li: ({ children }) => (
                              <li className="flex gap-3 items-start group">
                                <div className="w-1 h-1 rounded-full bg-primary-text/20 mt-2 flex-shrink-0 group-hover:bg-white/40 transition-colors" />
                                <span className="flex-1 opacity-80 group-hover:opacity-100 transition-opacity">{children}</span>
                              </li>
                            ),
                            strong: ({ children }) => <strong className="font-black text-white">{children}</strong>,
                            table: ({ children }) => (
                              <div className="overflow-x-auto my-6 rounded-xl border border-primary-border/20 bg-[#050505]/50 backdrop-blur-sm">
                                <table className="w-full text-left border-collapse">{children}</table>
                              </div>
                            ),
                            thead: ({ children }) => <thead className="bg-white/5 border-b border-white/10 font-black uppercase text-[10px] tracking-widest text-secondary-text">{children}</thead>,
                            th: ({ children }) => <th className="p-3 font-black text-white/40">{children}</th>,
                            td: ({ children }) => <td className="p-3 border-t border-primary-border/5 text-[11px] text-white/60">{children}</td>,
                            code: ({ children }) => <code className="bg-white/5 text-white/80 px-1.5 py-0.5 rounded-md font-mono text-[11px]">{children}</code>,
                            blockquote: ({ children }) => <blockquote className="border-l-2 border-white/10 pl-4 py-1 italic opacity-60 my-4 bg-white/5">{children}</blockquote>,
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
            <div className="p-4 rounded-xl bg-primary-text/[0.01] border border-primary-border w-16 h-12 flex items-center justify-center">
              <div className="flex gap-1">
                <div className="w-1 h-1 bg-white/20 rounded-full animate-bounce" />
                <div className="w-1 h-1 bg-white/20 rounded-full animate-bounce [animation-delay:0.2s]" />
                <div className="w-1 h-1 bg-white/20 rounded-full animate-bounce [animation-delay:0.4s]" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Terminal */}
      <div className="p-6 bg-surface-bg border-t border-primary-border">
        <div className="bg-primary-text/[0.02] border border-primary-border rounded-xl p-4 transition-all focus-within:border-white/20">
          <div className="flex items-center justify-between mb-3 opacity-40 select-none">
            <span
              className="text-[10px] font-bold uppercase tracking-[0.2em]"
            >
              Research Input Pipeline
            </span>
            <div className="flex gap-3">
              <Settings size={12} className="cursor-pointer hover:text-white transition-colors" />
              <Database size={12} className="cursor-pointer hover:text-white transition-colors" />
            </div>
          </div>

          <textarea
            rows={3}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            className="w-full bg-transparent border-none outline-none text-[13px] font-medium text-primary-text/70 placeholder:text-secondary-text placeholder:opacity-20 resize-none leading-relaxed"
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

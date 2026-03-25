"use client";

import React, { useState, useRef, useEffect } from "react";
import dynamic from 'next/dynamic';
const Plot = dynamic(() => import('react-plotly.js'), { ssr: false });

import {
  X, Sparkles, Send, BrainCircuit, Globe, Zap,
  Settings, Share2, Database, Paperclip, Lightbulb,
  Maximize2, Trash2, ChevronDown, User, Bot, Loader2, MessageSquare
} from "lucide-react";

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
  const [isTyping, setIsTyping] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const prompts = [
    "Analyze the trend in dividend payouts and dividend yield.",
    "Using the financial statements, assess the trend in revenue growth.",
    "Analyze the gross and net profit margin trend."
  ];

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
      const response = await fetch(`http://localhost:8000/intelligence/chat?query=${encodeURIComponent(text)}`);
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
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-10 right-10 w-12 h-12 bg-primary-text/10 border border-primary-border rounded-xl flex items-center justify-center transition-all z-[900] shadow-2xl backdrop-blur-md group hover:scale-110 active:scale-95"
      >
        <div className="relative">
          <BrainCircuit size={22} className="text-sky-400 group-hover:text-emerald-400 transition-colors" />
        </div>
      </button>
    );
  }

  return (
    <div className={`fixed top-[74px] right-[10px] bottom-[10px] ${isExpanded ? 'w-[75%] left-auto' : 'w-[500px]'} bg-surface-bg border border-primary-border rounded-xl flex flex-col z-[1000] transition-all duration-500 ease-in-out shadow-2xl overflow-hidden`}>
      {/* Header - Styled like DockPanels */}
      <div className="h-11 px-6 flex items-center justify-between border-b border-primary-border bg-primary-text/[0.01] select-none">
        <div className="flex items-center gap-3">
          <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse shadow-[0_0_10px_rgba(16,185,129,0.5)]" />
          <span 
            style={{ fontFamily: 'var(--outfit-font)' }}
            className="text-[11px] font-bold text-primary-text uppercase tracking-widest opacity-80"
          >
            Neural Intelligence Terminal
          </span>
        </div>
        <div className="flex items-center gap-2">
          <button 
            onClick={() => setIsExpanded(!isExpanded)} 
            className={`p-1.5 transition-all rounded-md ${isExpanded ? 'bg-sky-500/10 text-sky-400' : 'text-primary-text hover:bg-primary-text/5'}`}
          >
            <Maximize2 size={13} />
          </button>
          <button onClick={() => setMessages([])} className="p-1.5 text-primary-text hover:text-rose-500 transition-colors"><Trash2 size={13} /></button>
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
                <div className="w-16 h-16 bg-gradient-to-br from-sky-500/20 to-emerald-500/20 rounded-2xl flex items-center justify-center border border-sky-500/30">
                  <Sparkles size={28} className="text-sky-400 animate-pulse" />
                </div>
                <div className="text-center">
                   <h2 style={{ fontFamily: 'var(--outfit-font)' }} className="text-[12px] font-semibold text-primary-text/80 tracking-[0.3em] uppercase mb-2">Institutional Cog-Suite</h2>
                   <p style={{ fontFamily: 'var(--outfit-font)' }} className="text-[10px] text-secondary-text tracking-[0.2em] uppercase opacity-40 leading-relaxed max-w-[200px] mx-auto">
                     Awaiting directives for {symbol}
                   </p>
                </div>
            </div>

            <div className="grid grid-cols-1 gap-2 w-full max-w-[320px]">
              {prompts.map((p, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(p)}
                  className="p-3.5 w-full bg-primary-text/[0.02] border border-primary-border rounded-lg transition-all text-left hover:bg-primary-text/[0.05] group"
                >
                  <div className="flex items-center gap-3">
                    <MessageSquare size={12} className="text-secondary-text group-hover:text-sky-400 transition-colors opacity-40" />
                    <p 
                      style={{ fontFamily: 'var(--outfit-font)' }}
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
                  <div className="w-8 h-8 rounded-lg bg-sky-500/10 border border-sky-500/30 flex-shrink-0 flex items-center justify-center shadow-lg">
                    <Bot size={18} className="text-sky-400" />
                  </div>
                )}
                
                <div className="flex-1 space-y-4">
                  {/* Step-by-step Reasoning Accordion */}
                  {m.thoughts && m.thoughts.length > 0 && (
                    <div className="bg-primary-text/[0.02] border border-primary-border rounded-xl overflow-hidden mb-4">
                       <details className="group" open={i === messages.length - 1}>
                         <summary className="flex items-center justify-between p-3 cursor-pointer hover:bg-primary-text/[0.04] transition-colors list-none">
                            <div className="flex items-center gap-2">
                               <div className="w-1.5 h-1.5 bg-sky-400 rounded-full animate-pulse" />
                               <span 
                                 style={{ fontFamily: 'var(--outfit-font)' }}
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
                                    style={{ fontFamily: 'var(--outfit-font)' }}
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
                      style={{ fontFamily: "'Outfit', sans-serif" }}
                      className={`max-w-[85%] p-4 rounded-xl text-[13px] leading-relaxed font-medium tracking-tight ${
                      m.role === 'user' 
                        ? 'bg-sky-500/10 border border-sky-500/30 text-sky-400 ml-auto' 
                        : 'bg-primary-text/[0.04] border border-primary-border text-primary-text/90 shadow-sm'
                    }`}>
                      {m.content}
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
                <div className="w-1 h-1 bg-sky-500 rounded-full animate-bounce" />
                <div className="w-1 h-1 bg-sky-500 rounded-full animate-bounce [animation-delay:0.2s]" />
                <div className="w-1 h-1 bg-sky-500 rounded-full animate-bounce [animation-delay:0.4s]" />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Input Terminal */}
      <div className="p-6 bg-surface-bg border-t border-primary-border">
        <div className="bg-primary-text/[0.02] border border-primary-border rounded-xl p-4 transition-all focus-within:border-sky-500/50">
           <div className="flex items-center justify-between mb-3 opacity-40 select-none">
              <span 
                style={{ fontFamily: 'var(--outfit-font)' }}
                className="text-[10px] font-bold uppercase tracking-[0.2em]"
              >
                Research Input Pipeline
              </span>
              <div className="flex gap-3">
                <Settings size={12} className="cursor-pointer hover:text-sky-400 transition-colors" />
                <Database size={12} className="cursor-pointer hover:text-emerald-400 transition-colors" />
              </div>
           </div>
           
           <textarea
              rows={3}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              style={{ fontFamily: "'Outfit', sans-serif" }}
              className="w-full bg-transparent border-none outline-none text-[13px] font-medium text-primary-text/70 placeholder:text-secondary-text placeholder:opacity-20 resize-none leading-relaxed"
              placeholder={`Identify patterns in ${symbol || 'SBIN'}...`}
            />

            <div className="flex items-center justify-between mt-3 pt-3 border-t border-primary-text/5">
                <div className="flex gap-2">
                   <div className="w-1.5 h-1.5 bg-sky-500/40 rounded-full" />
                   <div className="w-1.5 h-1.5 bg-emerald-500/40 rounded-full" />
                </div>
                <button 
                  onClick={() => handleSend(input)}
                  disabled={!input.trim() || isTyping}
                  className={`px-4 py-1.5 rounded-lg flex items-center gap-2 transition-all ${
                    input.trim() && !isTyping 
                      ? 'bg-sky-500/10 text-sky-400 border border-sky-500/30 hover:bg-sky-500/20 shadow-sm' 
                      : 'bg-primary-text/5 text-secondary-text opacity-40 cursor-not-allowed'
                  }`}
                >
                  <span 
                    style={{ fontFamily: 'var(--outfit-font)' }}
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

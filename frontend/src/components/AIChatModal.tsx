"use client";

import React, { useState, useRef, useEffect } from "react";
import { queryAIChat } from "@/lib/api";
import { X, Send, Bot, User, Sparkles, AlertCircle } from "lucide-react";

interface AIChatModalProps {
  isOpen: boolean;
  onClose: () => void;
  activePair: string;
  activeTimeframe: string;
}

interface Message {
  role: "user" | "assistant";
  content: string;
  citations?: string[];
}

export const AIChatModal: React.FC<AIChatModalProps> = ({
  isOpen,
  onClose,
  activePair,
  activeTimeframe,
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: `Hello! I am your **Forex AI Analyst**. I have access to real-time order blocks, multi-timeframe trends, macroeconomic surprises, and probabilistic signals for **${activePair} (${activeTimeframe})**. Ask me anything about current setups or trade risks.`,
      citations: ["Forex AI Core Engine"],
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (!isOpen) return null;

  const handleSend = async (textToSend?: string) => {
    const q = textToSend || input;
    if (!q.trim() || loading) return;

    const userMsg: Message = { role: "user", content: q };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const res = await queryAIChat(q, activePair, activeTimeframe);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.response,
          citations: res.citations,
        },
      ]);
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Error retrieving grounded market analysis: ${err.message}`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const quickQueries = [
    `Why is ${activePair} bullish or bearish?`,
    `What are the biggest risks to this trade?`,
    `What are the strongest currencies right now?`,
    `Compare EUR/USD and GBP/USD.`,
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm p-4">
      <div className="bg-surface border border-border rounded-2xl w-full max-w-2xl h-[85vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-4 border-b border-border bg-surface-raised/80">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-accent/20 border border-accent/40 flex items-center justify-center text-accent">
              <Bot className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-slate-100 flex items-center gap-2">
                Forex AI Quantitative Assistant
                <span className="text-[10px] px-2 py-0.5 rounded-full bg-emerald-500/20 text-emerald-400 font-mono">
                  Grounded
                </span>
              </h3>
              <p className="text-[11px] text-slate-400 font-mono">
                Context: {activePair} • {activeTimeframe}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-100 hover:bg-surface-raised transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Message Thread */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`flex gap-3 ${m.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {m.role === "assistant" && (
                <div className="w-7 h-7 rounded bg-accent/20 border border-accent/30 flex items-center justify-center text-accent shrink-0 mt-0.5">
                  <Bot className="w-3.5 h-3.5" />
                </div>
              )}

              <div
                className={`max-w-[85%] rounded-xl p-3.5 text-xs leading-relaxed ${
                  m.role === "user"
                    ? "bg-accent text-white"
                    : "bg-surface-raised border border-border text-slate-200"
                }`}
              >
                <div className="whitespace-pre-line font-sans">{m.content}</div>

                {m.citations && m.citations.length > 0 && (
                  <div className="mt-2.5 pt-2 border-t border-border/60 flex flex-wrap items-center gap-1.5 text-[10px] font-mono text-slate-400">
                    <span className="text-slate-500">Sources:</span>
                    {m.citations.map((c, i) => (
                      <span
                        key={i}
                        className="px-1.5 py-0.2 rounded bg-surface border border-border text-slate-300"
                      >
                        {c}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {m.role === "user" && (
                <div className="w-7 h-7 rounded bg-slate-700 flex items-center justify-center text-slate-200 shrink-0 mt-0.5">
                  <User className="w-3.5 h-3.5" />
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex gap-3 justify-start">
              <div className="w-7 h-7 rounded bg-accent/20 border border-accent/30 flex items-center justify-center text-accent shrink-0">
                <Bot className="w-3.5 h-3.5" />
              </div>
              <div className="bg-surface-raised border border-border rounded-xl p-3 text-xs text-slate-400 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-accent animate-pulse"></span>
                Evaluating market structure and quantitative probabilities...
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        {/* Quick Question Chips */}
        <div className="px-5 py-2 bg-surface-raised/40 border-t border-border/60 flex gap-2 overflow-x-auto no-scrollbar">
          {quickQueries.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(q)}
              className="px-2.5 py-1 rounded-full bg-surface border border-border hover:border-accent/50 text-[11px] text-slate-300 hover:text-white whitespace-nowrap transition"
            >
              {q}
            </button>
          ))}
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-border bg-surface-raised/60">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={`Ask Forex AI about ${activePair} or trade setup...`}
              className="flex-1 bg-surface border border-border rounded-xl px-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-accent"
            />
            <button
              type="submit"
              disabled={!input.trim() || loading}
              className="p-2.5 rounded-xl bg-accent hover:bg-accent/90 text-white disabled:opacity-40 transition shadow-md shadow-accent/20"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

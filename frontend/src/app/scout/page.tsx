"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function ScoutFinder() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hi! I am the Pitch IQ AI assistant powered by Groq. Ask me anything about football — players, teams, stats, tactics, transfers, or predictions.",
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | undefined>();

  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [messages]);

  async function sendMessage() {
    if (!input.trim() || loading) return;

    const userMessage = input.trim();

    setInput("");

    setMessages((prev) => [
      ...prev,
      {
        role: "user",
        content: userMessage,
      },
    ]);

    setLoading(true);

    try {
      const res = await api.askData(userMessage, sessionId);

      setSessionId(res.session_id);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: res.groq_available
            ? res.response
            : "AI assistant temporarily unavailable. Please try again.",
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Could not connect to backend.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  const suggestions = [
    "Who was the top scorer in La Liga 2025/26?",
    "Compare Haaland and Lewandowski stats",
    "Which team won the Bundesliga last season?",
    "Best young players under 23 in Serie A",
    "Predict who will win EPL 2026/27",
    "Mbappe stats at Barcelona",
  ];

  return (
    <main className="min-h-screen text-slate-100">
      {/* Header */}
      <div className="relative border-b border-blue-900/40 overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_50%_-20%,_#1e3a8a_0%,_transparent_60%)] opacity-70" />

        <div className="relative max-w-4xl mx-auto px-6 pt-10 pb-6">
          <Link
            href="/"
            className="text-slate-500 hover:text-blue-400 transition-colors text-xs font-bold uppercase tracking-widest mb-4 block"
          >
            &larr; Back to Dashboard
          </Link>

          <h1 className="text-3xl font-black text-white uppercase tracking-tight">
            Scout{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-indigo-300">
              AI
            </span>
          </h1>

          <p className="text-slate-500 text-xs mt-1 uppercase tracking-widest font-bold">
            Powered by Groq + Pitch IQ Database
          </p>
        </div>
      </div>

      {/* Chat */}
      <div className="max-w-4xl mx-auto px-6 py-6 flex flex-col h-[calc(100vh-200px)]">
        <div className="flex-1 bg-[#070c1a] border border-blue-900/40 flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={
                  "flex " +
                  (msg.role === "user"
                    ? "justify-end"
                    : "justify-start")
                }
              >
                <div
                  className={
                    "max-w-[80%] px-4 py-2.5 text-sm " +
                    (msg.role === "user"
                      ? "bg-blue-600 text-white rounded-2xl rounded-tr-sm"
                      : "bg-[#0a1226] border-l-2 border-blue-500 text-slate-200 rounded-2xl rounded-tl-sm")
                  }
                >
                  {msg.content}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="bg-[#0a1226] border-l-2 border-blue-500 rounded-2xl rounded-tl-sm px-4 py-2.5 text-sm text-slate-400 animate-pulse">
                  Thinking...
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="border-t border-blue-900/40 p-3 flex gap-2 bg-[#0a1226]">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter") {
                  sendMessage();
                }
              }}
              placeholder="Ask anything about football..."
              className="flex-1 bg-[#070c1a] text-white rounded-xl px-4 py-2 text-sm outline-none border border-blue-900/40 focus:border-blue-500 transition-colors placeholder:text-slate-600"
            />

            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-800 disabled:text-gray-600 text-white px-5 py-2 rounded-xl text-sm font-bold uppercase tracking-wide transition-colors"
            >
              Send
            </button>
          </div>
        </div>

        {/* Suggestions */}
        <div className="mt-3 grid grid-cols-2 md:grid-cols-3 gap-2">
          {suggestions.map((suggestion) => (
            <button
              key={suggestion}
              onClick={() => setInput(suggestion)}
              className="rounded-full bg-[#070c1a] border border-blue-900/40 hover:border-blue-500 hover:text-blue-400 text-xs px-4 py-2.5 transition-colors text-left truncate w-full text-slate-400"
            >
              {suggestion}
            </button>
          ))}
        </div>
      </div>
    </main>
  );
}
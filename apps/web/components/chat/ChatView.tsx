"use client";

import React, { useEffect, useRef, useState } from "react";
import { cn } from "@/lib/utils";
import {
  getChatLast,
  getChatSessionHistory,
  getChatStatus,
  postChatMessage,
  type ChatMessage as ApiChatMessage,
  type ChatStatus,
} from "@/lib/api";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  text: string;
  time?: string;
};

type RoomCommandPayload = {
  id: number;
  text: string;
  source: "chat";
  ts: string;
};

const parseTimestamp = (ts?: string) => {
  if (!ts) return null;
  const [datePart, timePart] = ts.split(" ");
  if (!datePart || !timePart) return null;
  const [year, month, day] = datePart.split("-").map(Number);
  const [hour, minute, second] = timePart.split(":").map(Number);
  if ([year, month, day, hour, minute].some(Number.isNaN)) return null;
  return new Date(year, month - 1, day, hour, minute, second || 0);
};

const formatTime = (ts?: string) => {
  if (!ts) return "";
  const parsed = parseTimestamp(ts);
  if (!parsed) return "";
  return parsed.toLocaleTimeString("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
  });
};

const toMessage = (msg: ApiChatMessage): ChatMessage => ({
  id: String(msg.id),
  role: msg.role,
  text: msg.text,
  time: formatTime(msg.ts),
});

export function ChatView() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [status, setStatus] = useState<ChatStatus | null>(null);
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);
  const lastMessageRef = useRef<string>("");

  const formatNow = () =>
    new Date().toLocaleTimeString("vi-VN", {
      hour: "2-digit",
      minute: "2-digit",
    });

  const appendMessage = (message: ChatMessage) => {
    setMessages((prev) => [...prev, message]);
  };

  const broadcastRoomCommand = (text: string) => {
    if (typeof window === "undefined") return;
    const payload: RoomCommandPayload = {
      id: Date.now(),
      text,
      source: "chat",
      ts: new Date().toISOString(),
    };
    try {
      const raw = window.localStorage.getItem("room_command_queue");
      const queue = raw ? JSON.parse(raw) : [];
      const next = Array.isArray(queue) ? [...queue, payload] : [payload];
      window.localStorage.setItem(
        "room_command_queue",
        JSON.stringify(next.slice(-20)),
      );
      window.localStorage.setItem("room_command_last", JSON.stringify(payload));
    } catch {
      // Ignore localStorage issues; still emit event below.
    }
    window.dispatchEvent(new CustomEvent("room-command", { detail: payload }));
  };

  useEffect(() => {
    const loadLast = async () => {
      const last = await getChatLast();
      if (last) {
        const mapped = last.messages.map(toMessage);
        const lastKey = mapped.length ? `${mapped[mapped.length - 1].id}` : "";
        if (lastKey !== lastMessageRef.current) {
          lastMessageRef.current = lastKey;
          setSessionId(last.session_id);
          setMessages(mapped);
        }
      }
    };
    loadLast();
    const interval = setInterval(loadLast, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const fetchStatus = async () => {
      const data = await getChatStatus();
      if (data) setStatus(data);
    };
    fetchStatus();
    const interval = setInterval(fetchStatus, 3000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (!listRef.current) return;
    listRef.current.scrollTo({
      top: listRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages]);

  const statusLabel = status?.recording
    ? "Listening"
    : status?.recorder_running
      ? "Ready"
      : "Offline";
  const statusTone = status?.recording
    ? "amber"
    : status?.recorder_running
      ? "emerald"
      : "rose";

  const handleLoadHistory = async () => {
    if (!sessionId) return;
    const full = await getChatSessionHistory(sessionId, 200);
    if (full) {
      setMessages(full.messages.map(toMessage));
    }
  };

  const handleSend = async () => {
    const text = input.trim();
    if (!text || isSending) return;
    setInput("");
    setIsSending(true);

    const optimistic: ChatMessage = {
      id: `local-${Date.now()}`,
      role: "user",
      text,
      time: formatNow(),
    };
    appendMessage(optimistic);
    broadcastRoomCommand(text);

    try {
      const res = await postChatMessage(text, sessionId ?? undefined, "web");
      if (!res) {
        throw new Error("No response");
      }
      if (res.session_id) setSessionId(res.session_id);
      if (res.assistant_text) {
        appendMessage({
          id: `assistant-${Date.now()}`,
          role: "assistant",
          text: res.assistant_text,
          time: formatNow(),
        });
      } else if (res.error) {
        appendMessage({
          id: `assistant-${Date.now()}`,
          role: "assistant",
          text: res.error,
          time: formatNow(),
        });
      }
    } catch (error) {
      appendMessage({
        id: `assistant-${Date.now()}`,
        role: "assistant",
        text: "Unable to send right now.",
        time: formatNow(),
      });
    } finally {
      setIsSending(false);
    }
  };

  return (
    <div className="flex h-full flex-col">
      <header className="px-6 pt-6 pb-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-[11px] uppercase tracking-[0.24em] text-slate-400">
              Assistant
            </div>
            <div className="text-2xl font-semibold text-white">Jason</div>
          </div>
          <div
            className={cn(
              "flex items-center gap-2 rounded-full px-3 py-1 text-[11px] font-semibold",
              statusTone === "emerald" && "bg-emerald-500/10 text-emerald-300",
              statusTone === "amber" && "bg-amber-500/10 text-amber-300",
              statusTone === "rose" && "bg-rose-500/10 text-rose-300",
            )}
          >
            <span
              className={cn(
                "h-2 w-2 rounded-full shadow-[0_0_12px_rgba(52,211,153,0.8)]",
                statusTone === "emerald" && "bg-emerald-400",
                statusTone === "amber" &&
                  "bg-amber-400 shadow-[0_0_12px_rgba(251,191,36,0.8)]",
                statusTone === "rose" &&
                  "bg-rose-400 shadow-[0_0_12px_rgba(248,113,113,0.8)]",
              )}
            />
            {statusLabel}
          </div>
        </div>
      </header>

      <main ref={listRef} className="flex-1 overflow-y-auto px-6 pb-6">
        <div className="flex items-center justify-between text-[11px] uppercase tracking-widest text-slate-500">
          <span>Conversation</span>
          <button
            type="button"
            onClick={handleLoadHistory}
            className="text-[10px] text-cyan-300 transition hover:text-cyan-200"
          >
            Load full history
          </button>
        </div>
        <div className="mt-3 space-y-3">
          {messages.length === 0 && (
            <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-400">
              No messages yet.
            </div>
          )}
          {messages.map((msg, idx) => (
            <div
              key={msg.id}
              className={cn(
                "w-full animate-fade-up rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm",
                msg.role === "user"
                  ? "ml-auto max-w-[85%] bg-white/10 text-white ring-1 ring-white/10"
                  : "mr-auto max-w-[90%] bg-slate-900/60 text-slate-100 ring-1 ring-white/5",
              )}
              style={{ animationDelay: `${80 + idx * 90}ms` }}
            >
              <div className="flex items-center justify-between gap-4 text-[11px] uppercase tracking-wider text-slate-400">
                <span>{msg.role === "user" ? "You" : "Jason"}</span>
                <span>{msg.time}</span>
              </div>
              <div className="mt-2">{msg.text}</div>
            </div>
          ))}
        </div>
      </main>

      <footer className="px-5 pb-6 pt-3">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-2">
          <div className="flex items-center gap-2">
            <input
              value={input}
              onChange={(event) => setInput(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter" && !event.shiftKey) {
                  event.preventDefault();
                  handleSend();
                }
              }}
              placeholder="Type a message..."
              className="flex-1 bg-transparent px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 outline-none"
            />
            <button
              type="button"
              onClick={handleSend}
              disabled={isSending || !input.trim()}
              className={cn(
                "rounded-xl px-4 py-2 text-xs font-semibold uppercase tracking-widest transition",
                isSending || !input.trim()
                  ? "bg-white/5 text-slate-500"
                  : "bg-cyan-500/80 text-white hover:bg-cyan-500",
              )}
            >
              {isSending ? "Sending" : "Send"}
            </button>
          </div>
        </div>
        <div className="mt-3 text-[11px] text-slate-500">2026.</div>
      </footer>
    </div>
  );
}

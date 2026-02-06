"use client";

import React from "react";
import { cn } from "@/lib/utils";

type ChatMessage = {
    id: string;
    role: "user" | "assistant";
    text: string;
    time?: string;
};

const SAMPLE_MESSAGES: ChatMessage[] = [
    { id: "m1", role: "user", text: "Hi, Jason", time: "09:41" },
    { id: "m2", role: "assistant", text: "Mình nghe đây. Bạn cần gì?", time: "09:41" },
];

export function ChatView() {
    return (
        <div className="flex h-full flex-col">
            <header className="px-6 pt-6 pb-4">
                <div className="flex items-center justify-between">
                    <div>
                        <div className="text-[11px] uppercase tracking-[0.24em] text-slate-400">
                            Trợ Lý
                        </div>
                        <div className="text-2xl font-semibold text-white">Jason</div>
                    </div>
                    <div className="flex items-center gap-2 rounded-full bg-emerald-500/10 px-3 py-1 text-[11px] font-semibold text-emerald-300">
                        <span className="h-2 w-2 rounded-full bg-emerald-400 shadow-[0_0_12px_rgba(52,211,153,0.8)]" />
                        Sẵn sàng
                    </div>
                </div>
            </header>

            <main className="flex-1 overflow-y-auto px-6 pb-6">
                <div className="space-y-3">
                    {SAMPLE_MESSAGES.map((msg, idx) => (
                        <div
                            key={msg.id}
                            className={cn(
                                "w-full animate-fade-up rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm",
                                msg.role === "user"
                                    ? "ml-auto max-w-[85%] bg-white/10 text-white ring-1 ring-white/10"
                                    : "mr-auto max-w-[90%] bg-slate-900/60 text-slate-100 ring-1 ring-white/5"
                            )}
                            style={{ animationDelay: `${80 + idx * 90}ms` }}
                        >
                            <div className="flex items-center justify-between gap-4 text-[11px] uppercase tracking-wider text-slate-400">
                                <span>{msg.role === "user" ? "Bạn" : "Jason"}</span>
                                <span>{msg.time}</span>
                            </div>
                            <div className="mt-2">{msg.text}</div>
                        </div>
                    ))}
                </div>
            </main>

            <footer className="px-5 pb-6 pt-3">
                <div className="text-[11px] text-slate-500">
                    2026.
                </div>
            </footer>
        </div>
    );
}

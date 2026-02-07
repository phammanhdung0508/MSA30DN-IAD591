"use client";

import React from "react";
import { ChatView } from "@/components/chat/ChatView";
import { SensorsView } from "@/components/sensors/SensorsView";
import { cn } from "@/lib/utils";

export default function Page() {
    const [activeTab, setActiveTab] = React.useState<"chat" | "sensors">("chat");
    return (
        <div className="min-h-screen bg-slate-950 px-4 py-6">
            <div className="mx-auto h-[92vh] w-full max-w-[430px] overflow-hidden rounded-[36px] border border-white/10 bg-gradient-to-b from-slate-900/90 via-slate-950/85 to-slate-950/95 shadow-[0_24px_80px_rgba(15,23,42,0.55)] backdrop-blur">
                <div className="relative h-full overflow-hidden">
                    <div className="pointer-events-none absolute -top-10 right-[-35%] h-56 w-56 rounded-full bg-cyan-500/10 blur-[90px]" />
                    <div className="pointer-events-none absolute bottom-[-20%] left-[-30%] h-64 w-64 rounded-full bg-blue-500/10 blur-[100px]" />
                    <div className="flex h-full flex-col">
                        <div className="px-6 pt-6">
                            <div className="flex rounded-full border border-white/10 bg-white/5 p-1 text-[11px] uppercase tracking-widest text-slate-400">
                                {(["chat", "sensors"] as const).map((tab) => (
                                    <button
                                        key={tab}
                                        type="button"
                                        onClick={() => setActiveTab(tab)}
                                        className={cn(
                                            "flex-1 rounded-full px-3 py-2 font-semibold transition",
                                            activeTab === tab
                                                ? "bg-white/10 text-white"
                                                : "text-slate-400 hover:text-slate-200"
                                        )}
                                    >
                                        {tab === "chat" ? "Chat" : "Sensors"}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div className="flex-1 overflow-hidden">
                            {activeTab === "chat" ? <ChatView /> : <SensorsView />}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

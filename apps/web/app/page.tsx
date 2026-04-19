"use client";

import React from "react";
import { ChatView } from "@/components/chat/ChatView";
import { SensorsView } from "@/components/sensors/SensorsView";
import { RoomView } from "@/components/room/RoomView";
import { cn } from "@/lib/utils";

export default function Page() {
  const [activeTab, setActiveTab] = React.useState<"chat" | "sensors" | "room">(
    "chat",
  );
  return (
    <div className="min-h-screen bg-slate-950">
      <div className="relative min-h-screen w-full overflow-hidden bg-gradient-to-b from-slate-900/90 via-slate-950/85 to-slate-950/95">
        <div className="pointer-events-none absolute -top-10 right-[-10%] h-72 w-72 rounded-full bg-cyan-500/10 blur-[100px]" />
        <div className="pointer-events-none absolute bottom-[-20%] left-[-10%] h-80 w-80 rounded-full bg-blue-500/10 blur-[120px]" />
        <div className="relative flex min-h-screen flex-col">
          <div className="px-6 pt-6">
            <div className="mx-auto flex w-full max-w-5xl rounded-full border border-white/10 bg-white/5 p-1 text-[11px] uppercase tracking-widest text-slate-400">
              {(["chat", "sensors", "room"] as const).map((tab) => (
                <button
                  key={tab}
                  type="button"
                  onClick={() => setActiveTab(tab)}
                  className={cn(
                    "flex-1 rounded-full px-3 py-2 font-semibold transition",
                    activeTab === tab
                      ? "bg-white/10 text-white"
                      : "text-slate-400 hover:text-slate-200",
                  )}
                >
                  {tab === "chat"
                    ? "Chat"
                    : tab === "sensors"
                      ? "Sensors"
                      : "Room"}
                </button>
              ))}
            </div>
          </div>
          <div className="flex-1 overflow-hidden">
            <div className="mx-auto h-full w-full max-w-5xl px-4 pb-6 pt-2">
              {activeTab === "chat" ? (
                <ChatView />
              ) : activeTab === "sensors" ? (
                <SensorsView />
              ) : (
                <RoomView />
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

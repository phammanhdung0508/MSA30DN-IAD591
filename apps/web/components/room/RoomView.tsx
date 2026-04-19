"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import { cn } from "@/lib/utils";
import { getChatLast } from "@/lib/api";
import { Fan, Lightbulb, Snowflake, Tv2 } from "lucide-react";

type DeviceId = "lamp" | "fan" | "ac" | "tv";

type DeviceDef = {
  id: DeviceId;
  label: string;
  room: string;
  icon: React.ComponentType<{ className?: string }>;
  synonyms: string[];
  position: { x: string; y: string };
};

const DEVICE_DEFS: DeviceDef[] = [
  {
    id: "lamp",
    label: "Living Lamp",
    room: "Living",
    icon: Lightbulb,
    synonyms: ["den", "lamp", "light"],
    position: { x: "10%", y: "16%" },
  },
  {
    id: "fan",
    label: "Ceiling Fan",
    room: "Living",
    icon: Fan,
    synonyms: ["quat", "fan"],
    position: { x: "58%", y: "12%" },
  },
  {
    id: "ac",
    label: "AC Unit",
    room: "Bedroom",
    icon: Snowflake,
    synonyms: ["may lanh", "aircon", "ac", "air conditioner"],
    position: { x: "64%", y: "62%" },
  },
  {
    id: "tv",
    label: "Smart TV",
    room: "Living",
    icon: Tv2,
    synonyms: ["tv", "tivi", "television"],
    position: { x: "18%", y: "64%" },
  },
];

const DEFAULT_STATE: Record<DeviceId, boolean> = {
  lamp: false,
  fan: false,
  ac: false,
  tv: false,
};

const normalizeText = (value: string) =>
  value
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");

const formatNow = () =>
  new Date().toLocaleTimeString("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
  });

type LogItem = {
  id: string;
  text: string;
  ts: string;
  tone: "ok" | "warn";
};

type RoomCommandPayload = {
  id?: number;
  text?: string;
  source?: string;
  ts?: string;
};

const ACTION_KEYWORDS = {
  on: ["bat", "on", "turn on", "mo", "open"],
  off: ["tat", "off", "turn off", "dong", "close"],
};

const ALL_KEYWORDS = ["tat ca", "all", "everything", "everyone"];

export function RoomView() {
  const [deviceState, setDeviceState] = useState<Record<DeviceId, boolean>>(
    () => {
      if (typeof window === "undefined") return DEFAULT_STATE;
      const raw = window.localStorage.getItem("room_device_state");
      if (!raw) return DEFAULT_STATE;
      try {
        const parsed = JSON.parse(raw) as Partial<Record<DeviceId, boolean>>;
        return { ...DEFAULT_STATE, ...parsed };
      } catch {
        return DEFAULT_STATE;
      }
    },
  );
  const lastProcessedRef = useRef(0);
  const lastDeviceMessageRef = useRef(0);

  useEffect(() => {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(
      "room_device_state",
      JSON.stringify(deviceState),
    );
  }, [deviceState]);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const loadQueue = () => {
      try {
        const rawQueue = window.localStorage.getItem("room_command_queue");
        const parsedQueue = rawQueue ? JSON.parse(rawQueue) : [];
        const queue = Array.isArray(parsedQueue) ? parsedQueue : [];
        let lastProcessed = Number(
          window.localStorage.getItem("room_command_last_processed") ?? "0",
        );
        queue
          .filter(
            (item) =>
              item &&
              typeof item.text === "string" &&
              typeof item.id === "number",
          )
          .sort((a, b) => a.id - b.id)
          .forEach((item) => {
            if (item.id > lastProcessed) {
              applyCommand(item.text, "chat");
              lastProcessed = item.id;
            }
          });
        lastProcessedRef.current = lastProcessed;
        window.localStorage.setItem(
          "room_command_last_processed",
          String(lastProcessed),
        );
      } catch {
        // ignore parse issues
      }
    };

    const handleEvent = (event: Event) => {
      const detail = (event as CustomEvent).detail as RoomCommandPayload;
      const text = detail?.text;
      if (!text || typeof text !== "string") return;
      const incomingId = typeof detail.id === "number" ? detail.id : Date.now();
      if (incomingId <= lastProcessedRef.current) return;
      applyCommand(text, "chat");
      lastProcessedRef.current = incomingId;
      window.localStorage.setItem(
        "room_command_last_processed",
        String(incomingId),
      );
    };

    loadQueue();
    window.addEventListener("room-command", handleEvent as EventListener);
    return () =>
      window.removeEventListener("room-command", handleEvent as EventListener);
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") return;

    const rawLast = window.localStorage.getItem("room_device_last_id");
    const lastId = rawLast ? Number(rawLast) : 0;
    if (Number.isFinite(lastId)) {
      lastDeviceMessageRef.current = lastId;
    }

    const pollDeviceCommand = async () => {
      const last = await getChatLast();
      if (!last || !Array.isArray(last.messages)) return;
      const candidate = [...last.messages].reverse().find((msg) => {
        if (!msg || msg.role !== "user") return false;
        const meta = msg.meta;
        if (!meta || typeof meta !== "object") return false;
        return (meta as { source?: string }).source === "device";
      });
      if (!candidate) return;
      const id = Number(candidate.id);
      if (!Number.isFinite(id)) return;
      if (id <= lastDeviceMessageRef.current) return;
      applyCommand(candidate.text, "device");
      lastDeviceMessageRef.current = id;
      window.localStorage.setItem("room_device_last_id", String(id));
    };

    pollDeviceCommand();
    const interval = setInterval(pollDeviceCommand, 3000);
    return () => clearInterval(interval);
  }, []);

  const applyCommand = (
    raw: string,
    source: "text" | "voice" | "chat" | "device",
  ) => {
    const normalized = normalizeText(raw);
    if (!normalized) return;

    const targetAll = ALL_KEYWORDS.some((key) => normalized.includes(key));
    const cleaned = normalized.replace(/tat ca/g, " ").replace(/all/g, " ");

    const action = ACTION_KEYWORDS.off.some((key) => cleaned.includes(key))
      ? "off"
      : ACTION_KEYWORDS.on.some((key) => cleaned.includes(key))
        ? "on"
        : null;

    const matches = DEVICE_DEFS.filter((device) =>
      device.synonyms.some((syn) => cleaned.includes(syn)),
    );

    if (targetAll && !action) return;
    if (!targetAll && matches.length === 0) return;

    setDeviceState((prev) => {
      const next = { ...prev };
      const targets = targetAll
        ? DEVICE_DEFS.map((d) => d.id)
        : matches.map((d) => d.id);
      targets.forEach((id) => {
        if (!action) {
          next[id] = !prev[id];
        } else {
          next[id] = action === "on";
        }
      });
      return next;
    });
  };

  const handleToggle = (device: DeviceDef) => {
    setDeviceState((prev) => ({ ...prev, [device.id]: !prev[device.id] }));
  };

  const deviceBadges = useMemo(
    () =>
      DEVICE_DEFS.map((device) => ({
        id: device.id,
        label: device.label,
        active: deviceState[device.id],
      })),
    [deviceState],
  );

  return (
    <div className="flex h-full flex-col">
      <header className="px-6 pt-6 pb-4">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-[11px] uppercase tracking-[0.24em] text-slate-400">
              Room Simulator
            </div>
            <div className="text-2xl font-semibold text-white">Living Room</div>
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto px-6 pb-6 space-y-4">
        <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
          <div
            className="relative aspect-[4/3] w-full overflow-hidden rounded-2xl border border-white/10"
            style={{
              background:
                "radial-gradient(380px 200px at 15% 20%, rgba(34,211,238,0.15), transparent 60%), radial-gradient(420px 260px at 85% 30%, rgba(59,130,246,0.12), transparent 60%), linear-gradient(135deg, rgba(15,23,42,0.9), rgba(2,6,23,0.92))",
            }}
          >
            <div className="pointer-events-none absolute inset-4 rounded-2xl border border-white/10" />
            <div className="pointer-events-none absolute left-1/2 top-4 bottom-4 w-px bg-white/10" />
            <div className="pointer-events-none absolute left-4 right-4 top-1/2 h-px bg-white/10" />

            {DEVICE_DEFS.map((device) => {
              const Icon = device.icon;
              const isOn = deviceState[device.id];
              return (
                <button
                  key={device.id}
                  type="button"
                  onClick={() => handleToggle(device)}
                  className={cn(
                    "absolute w-28 rounded-2xl border px-3 py-2 text-left text-[11px] transition",
                    isOn
                      ? "border-emerald-400/50 bg-emerald-500/10 shadow-[0_0_20px_rgba(16,185,129,0.35)]"
                      : "border-white/10 bg-slate-900/70 hover:border-white/30",
                  )}
                  style={{ left: device.position.x, top: device.position.y }}
                >
                  <div className="flex items-center gap-2">
                    <Icon
                      className={cn(
                        "h-4 w-4",
                        isOn ? "text-emerald-300" : "text-slate-400",
                      )}
                    />
                    <span className="text-xs font-semibold text-white">
                      {device.label}
                    </span>
                  </div>
                  <div className="mt-1 text-[10px] uppercase tracking-widest text-slate-400">
                    {isOn ? "ON" : "OFF"} · {device.room}
                  </div>
                </button>
              );
            })}
          </div>

          <div className="mt-4 grid grid-cols-2 gap-2 text-[11px] text-slate-300">
            {deviceBadges.map((device) => (
              <div
                key={device.id}
                className={cn(
                  "flex items-center justify-between rounded-xl border px-3 py-2",
                  device.active
                    ? "border-emerald-400/40 bg-emerald-500/10 text-emerald-200"
                    : "border-white/10 bg-slate-900/60 text-slate-300",
                )}
              >
                <span>{device.label}</span>
                <span className="text-[10px] uppercase tracking-widest">
                  {device.active ? "ON" : "OFF"}
                </span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  );
}

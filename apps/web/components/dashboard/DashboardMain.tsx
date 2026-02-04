"use client";

import React, { useState, useEffect } from "react";
import {
    Power, Thermometer, Droplets, Wind, Zap,
    ChevronUp, ChevronDown, Snowflake, Sun, Fan, CloudRain
} from "lucide-react";
import { GlassCard } from "@/components/shared/GlassCard";
import { cn } from "@/lib/utils";
import { getACStatus, controlAC, type ACState } from "@/lib/api";

type Mode = "cool" | "heat" | "fan" | "dry";

export function DashboardMain() {
    const [isOn, setIsOn] = useState(false);
    const [temperature, setTemperature] = useState(24);
    const [mode, setMode] = useState<Mode>("cool");
    const [fanSpeed, setFanSpeed] = useState(2);
    const [humidity, setHumidity] = useState(55);
    const lastUpdate = React.useRef(0);

    // Poll for status updates
    useEffect(() => {
        const fetchStatus = async () => {
            if (Date.now() - lastUpdate.current < 4000) return;

            const status = await getACStatus();
            if (status) {
                setIsOn(status.power);
                setTemperature(status.temperature);
                setMode(status.mode);
                setFanSpeed(status.fanSpeed);
                if (status.humidity) setHumidity(status.humidity);
            }
        };
        fetchStatus(); // Initial fetch
        const interval = setInterval(fetchStatus, 3000); // Poll every 3s
        return () => clearInterval(interval);
    }, []);

    // Helper to send updates
    const updateState = async (updates: Partial<ACState>) => {
        lastUpdate.current = Date.now();
        // Optimistic update
        if (updates.power !== undefined) setIsOn(updates.power);
        if (updates.temperature !== undefined) setTemperature(updates.temperature);
        if (updates.mode !== undefined) setMode(updates.mode);
        if (updates.fanSpeed !== undefined) setFanSpeed(updates.fanSpeed);

        // Send to API
        try {
            await controlAC({
                power: updates.power ?? isOn,
                temperature: updates.temperature ?? temperature,
                mode: updates.mode ?? mode,
                fanSpeed: updates.fanSpeed ?? fanSpeed,
            } as ACState);
        } catch (e) {
            console.error("Failed to sync state", e);
            // Revert (could be implemented here)
        }
    };

    return (
        <div className="space-y-6 h-full flex flex-col">
            {/* Header */}
            <header className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-white">Living Room</h1>
                    <p className="text-slate-400 mt-1">Daikin Model X {"\u2022"} Online</p>
                </div>
                {/* Removed redundant header stats */}
            </header>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 xl:grid-cols-12 gap-8 flex-1">

                {/* Left Column: Thermostat (Main Focus) */}
                <div className="xl:col-span-7 flex flex-col justify-center items-center relative min-h-[400px] p-8">
                    {/* Thermostat Circle */}
                    <div className="relative scale-110">
                        <div className="w-[340px] h-[340px] rounded-full border-[20px] border-slate-800/50 shadow-2xl relative flex items-center justify-center bg-slate-900/40 backdrop-blur-sm">
                            {/* Mode Glow */}
                            <div className={cn(
                                "absolute inset-0 rounded-full blur-[60px] opacity-40 transition-all duration-1000",
                                isOn && mode === 'cool' ? "bg-cyan-500" : "",
                                isOn && mode === 'heat' ? "bg-orange-500" : "",
                                !isOn ? "bg-transparent" : "bg-blue-500"
                            )} />

                            {/* Inner Content */}
                            <div className="flex flex-col items-center z-10">
                                <span className={cn(
                                    "text-sm uppercase tracking-widest font-bold mb-4 transition-colors",
                                    isOn ? "text-white" : "text-slate-600"
                                )}>
                                    {isOn ? mode : "OFF"}
                                </span>
                                <div className="flex items-start">
                                    <span className={cn(
                                        "text-8xl font-bold tracking-tighter transition-all duration-500",
                                        isOn ? "text-white scale-100" : "text-slate-700 scale-90"
                                    )}>
                                        {temperature}
                                    </span>
                                    <span className="text-4xl text-slate-500 mt-2">{"\u00B0"}</span>
                                </div>
                                <div className="text-sm text-slate-500 mt-2 font-medium">Target Temp</div>
                            </div>

                            {/* Controls */}
                            <div className="absolute inset-0 pointer-events-none">
                                <button
                                    onClick={() => isOn && updateState({ temperature: Math.min(30, temperature + 1) })}
                                    className="pointer-events-auto absolute top-4 left-1/2 -translate-x-1/2 w-12 h-12 bg-slate-800 hover:bg-slate-700 rounded-full flex items-center justify-center text-white transition-all active:scale-95 shadow-lg border border-white/5"
                                >
                                    <ChevronUp />
                                </button>
                                <button
                                    onClick={() => isOn && updateState({ temperature: Math.max(16, temperature - 1) })}
                                    className="pointer-events-auto absolute bottom-4 left-1/2 -translate-x-1/2 w-12 h-12 bg-slate-800 hover:bg-slate-700 rounded-full flex items-center justify-center text-white transition-all active:scale-95 shadow-lg border border-white/5"
                                >
                                    <ChevronDown />
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Power Button */}
                    <button
                        onClick={() => updateState({ power: !isOn })}
                        className={cn(
                            "mt-16 w-20 h-20 rounded-full flex items-center justify-center transition-all duration-500 shadow-2xl border border-white/5",
                            isOn ? "bg-cyan-500 text-white shadow-cyan-500/40 scale-110" : "bg-slate-800 text-slate-500 hover:bg-slate-700 hover:text-white"
                        )}
                    >
                        <Power className="w-8 h-8" />
                    </button>
                </div>

                {/* Right Column: Controls & Stats */}
                <div className="xl:col-span-5 flex flex-col justify-center gap-6">

                    {/* Environment Stats Row */}
                    <div className="grid grid-cols-1 gap-4">
                        {/* Humidity */}
                        <GlassCard className="p-5 flex flex-col justify-between h-32 relative overflow-hidden group">
                            <div className="absolute right-[-10%] top-[-10%] opacity-10 group-hover:opacity-20 transition-opacity">
                                <Droplets className="w-24 h-24 text-blue-500" />
                            </div>
                            <div className="p-2 w-fit rounded-lg bg-blue-500/10 text-blue-400 mb-2">
                                <Droplets className="w-5 h-5" />
                            </div>
                            <div>
                                <div className="text-3xl font-bold text-white mb-1">{humidity}%</div>
                                <div className="text-xs text-slate-400 font-medium uppercase tracking-wider">Humidity</div>
                            </div>
                        </GlassCard>
                    </div>

                    {/* Mode Selector */}
                    <GlassCard className="p-6">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest">Operation Mode</h3>
                            <div className="w-2 h-2 rounded-full bg-slate-700"></div>
                        </div>
                        <div className="grid grid-cols-4 gap-3">
                            {[{ id: 'cool', Icon: Snowflake }, { id: 'heat', Icon: Sun }, { id: 'fan', Icon: Fan }, { id: 'dry', Icon: CloudRain }].map((m) => (
                                <button
                                    key={m.id}
                                    onClick={() => isOn && updateState({ mode: m.id as Mode })}
                                    disabled={!isOn}
                                    className={cn(
                                        "aspect-square rounded-xl flex flex-col items-center justify-center gap-2 transition-all duration-300",
                                        mode === m.id && isOn
                                            ? "bg-cyan-500 text-white shadow-lg shadow-cyan-500/25 scale-105"
                                            : "bg-slate-800/50 text-slate-500 hover:bg-slate-800 hover:text-slate-300"
                                    )}
                                >
                                    <m.Icon className="w-6 h-6" />
                                    <span className="text-[10px] uppercase font-bold">{m.id}</span>
                                </button>
                            ))}
                        </div>
                    </GlassCard>

                    {/* Fan Speed Slider */}
                    <GlassCard className="p-6">
                        <div className="flex justify-between items-center mb-6">
                            <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest">Fan Speed</h3>
                            <Wind className={cn("w-4 h-4 transition-all", isOn ? "text-cyan-400 animate-pulse" : "text-slate-600")} />
                        </div>
                        <div className="flex items-end gap-2 h-20 px-2">
                            {[1, 2, 3, 4, 5].map((level) => (
                                <button
                                    key={level}
                                    onClick={() => isOn && updateState({ fanSpeed: level })}
                                    disabled={!isOn}
                                    style={{ height: `${30 + level * 14}%` }}
                                    className={cn(
                                        "flex-1 rounded-lg transition-all duration-300",
                                        isOn && fanSpeed >= level
                                            ? "bg-cyan-500 shadow-[0_0_15px_rgba(6,182,212,0.4)]"
                                            : "bg-slate-800 hover:bg-slate-700"
                                    )}
                                />
                            ))}
                        </div>
                    </GlassCard>

                </div>
            </div>
        </div>
    );
}

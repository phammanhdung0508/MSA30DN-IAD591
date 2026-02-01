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
    const [isLoading, setIsLoading] = useState(false);
    const lastUpdate = React.useRef(0);

    // Poll for status updates
    useEffect(() => {
        const fetchStatus = async () => {
            // Don't poll if we just updated (simple debounce could be better, but let's just check a timestamp or flag)
            if (Date.now() - lastUpdate.current < 4000) return;

            const status = await getACStatus();
            if (status) {
                // ...
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
                    <p className="text-slate-400 mt-1">Daikin Model X • Online</p>
                </div>
                <div className="flex gap-4">
                    <div className="text-right">
                        <div className="text-sm text-slate-400">Indoor Temp</div>
                        <div className="text-2xl font-bold text-white">26.5°C</div>
                    </div>
                    <div className="w-[1px] bg-white/10" />
                    <div className="text-right">
                        <div className="text-sm text-slate-400">Outdoor Temp</div>
                        <div className="text-2xl font-bold text-slate-300">32.0°C</div>
                    </div>
                </div>
            </header>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 flex-1">

                {/* Left Column: Thermostat */}
                <div className="lg:col-span-7 flex flex-col justify-center items-center relative min-h-[400px]">
                    {/* Thermostat Circle */}
                    <div className="relative">
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
                                    <span className="text-4xl text-slate-500 mt-2">°</span>
                                </div>
                            </div>

                            {/* Controls */}
                            <div className="absolute inset-0 pointer-events-none">
                                <button
                                    onClick={() => isOn && updateState({ temperature: Math.min(30, temperature + 1) })}
                                    className="pointer-events-auto absolute top-4 left-1/2 -translate-x-1/2 w-12 h-12 bg-slate-800 hover:bg-slate-700 rounded-full flex items-center justify-center text-white transition-all active:scale-95"
                                >
                                    <ChevronUp />
                                </button>
                                <button
                                    onClick={() => isOn && updateState({ temperature: Math.max(16, temperature - 1) })}
                                    className="pointer-events-auto absolute bottom-4 left-1/2 -translate-x-1/2 w-12 h-12 bg-slate-800 hover:bg-slate-700 rounded-full flex items-center justify-center text-white transition-all active:scale-95"
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
                            "mt-12 w-20 h-20 rounded-full flex items-center justify-center transition-all duration-500 shadow-xl",
                            isOn ? "bg-cyan-500 text-white shadow-cyan-500/40" : "bg-slate-800 text-slate-500 hover:bg-slate-700 hover:text-white"
                        )}
                    >
                        <Power className="w-8 h-8" />
                    </button>
                </div>

                {/* Right Column: Controls & Stats */}
                <div className="lg:col-span-5 space-y-4 flex flex-col justify-center">

                    {/* Mode Selector */}
                    <GlassCard className="p-6">
                        <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest mb-4">Operation Mode</h3>
                        <div className="grid grid-cols-4 gap-2">
                            {[{ id: 'cool', Icon: Snowflake }, { id: 'heat', Icon: Sun }, { id: 'fan', Icon: Fan }, { id: 'dry', Icon: CloudRain }].map((m) => (
                                <button
                                    key={m.id}
                                    onClick={() => isOn && updateState({ mode: m.id as Mode })}
                                    disabled={!isOn}
                                    className={cn(
                                        "aspect-square rounded-xl flex flex-col items-center justify-center gap-2 transition-all",
                                        mode === m.id && isOn
                                            ? "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30"
                                            : "bg-slate-800/50 text-slate-500 hover:bg-slate-700/50"
                                    )}
                                >
                                    <m.Icon className="w-6 h-6" />
                                    <span className="text-[10px] uppercase font-bold">{m.id}</span>
                                </button>
                            ))}
                        </div>
                    </GlassCard>

                    {/* Quick Stats */}
                    <div className="grid grid-cols-1 gap-4">
                        <GlassCard className="p-4 flex items-center gap-4">
                            <div className="p-3 rounded-full bg-blue-500/10 text-blue-400">
                                <Droplets className="w-6 h-6" />
                            </div>
                            <div>
                                <div className="text-2xl font-bold text-white">{humidity}%</div>
                                <div className="text-xs text-slate-400">Humidity</div>
                            </div>
                        </GlassCard>
                    </div>

                    {/* Fan Speed Slider */}
                    <GlassCard className="p-6">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-slate-400 text-xs font-bold uppercase tracking-widest">Fan Speed</h3>
                            <Wind className="w-4 h-4 text-slate-500" />
                        </div>
                        <div className="flex items-end gap-2 h-16">
                            {[1, 2, 3, 4, 5].map((level) => (
                                <button
                                    key={level}
                                    onClick={() => isOn && updateState({ fanSpeed: level })}
                                    disabled={!isOn}
                                    style={{ height: `${20 + level * 15}%` }}
                                    className={cn(
                                        "flex-1 rounded-lg transition-all duration-300",
                                        isOn && fanSpeed >= level
                                            ? "bg-cyan-500 shadow-[0_0_10px_rgba(34,211,238,0.3)]"
                                            : "bg-slate-800"
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

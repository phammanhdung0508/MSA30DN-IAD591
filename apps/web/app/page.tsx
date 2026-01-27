"use client";

import React, { useState, useEffect } from "react";
import {
    Power,
    Thermometer,
    Droplets,
    Wind,
    Zap,
    Bell,
    Sun,
    Snowflake,
    Fan,
    CloudRain,
    ChevronUp,
    ChevronDown,
} from "lucide-react";

// Utility for classes
function cn(...classes: (string | undefined | null | false)[]) {
    return classes.filter(Boolean).join(" ");
}

type Mode = "cool" | "heat" | "fan" | "dry";

export default function ACDashboard() {
    const [isOn, setIsOn] = useState(false);
    const [temperature, setTemperature] = useState(24);
    const [mode, setMode] = useState<Mode>("cool");
    const [fanSpeed, setFanSpeed] = useState(2); // 1-3
    const [humidity, setHumidity] = useState(55); // Mocked
    const [powerUsage, setPowerUsage] = useState(1.2); // kW/h
    const [notifications, setNotifications] = useState([
        { id: 1, message: "Filter cleaning recommended", type: "warning" },
        { id: 2, message: "Energy saving mode active", type: "info" },
    ]);

    // Mock live updates
    useEffect(() => {
        if (!isOn) return;
        const interval = setInterval(() => {
            // Fluctuate humidity slightly
            setHumidity((prev) => Math.max(30, Math.min(80, prev + (Math.random() - 0.5) * 2)));
            // Fluctuate power usage
            setPowerUsage((prev) => Math.max(0.5, Math.min(3.0, prev + (Math.random() - 0.5) * 0.1)));
        }, 3000);
        return () => clearInterval(interval);
    }, [isOn]);

    const handleTempChange = (delta: number) => {
        if (!isOn) return;
        setTemperature((prev) => Math.max(16, Math.min(30, prev + delta)));
    };

    const togglePower = () => setIsOn(!isOn);

    const getModeIcon = (m: Mode) => {
        switch (m) {
            case "cool": return <Snowflake className="w-6 h-6" />;
            case "heat": return <Sun className="w-6 h-6" />;
            case "fan": return <Fan className="w-6 h-6" />;
            case "dry": return <CloudRain className="w-6 h-6" />;
        }
    };

    const getModeColor = (m: Mode) => {
        switch (m) {
            case "cool": return "text-cyan-400 bg-cyan-400/20 shadow-[0_0_15px_rgba(34,211,238,0.3)]";
            case "heat": return "text-orange-400 bg-orange-400/20 shadow-[0_0_15px_rgba(251,146,60,0.3)]";
            case "fan": return "text-emerald-400 bg-emerald-400/20 shadow-[0_0_15px_rgba(52,211,153,0.3)]";
            case "dry": return "text-blue-400 bg-blue-400/20 shadow-[0_0_15px_rgba(96,165,250,0.3)]";
        }
    };

    return (
        <main className="min-h-screen text-slate-100 p-8 flex flex-col items-center justify-center font-sans">
            <div className="max-w-7xl w-full grid grid-cols-3 gap-8">

                {/* Header / Main Control Panel */}
                <div className="col-span-2 space-y-8">
                    <header className="flex justify-between items-center mb-8">
                        <div>
                            <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-cyan-300">
                                My AC Controller
                            </h1>
                            <p className="text-slate-400 text-sm">Living Room • Daikin Model X</p>
                        </div>
                        <div className="flex items-center gap-4">
                            <div className="relative group cursor-pointer">
                                <Bell className="w-6 h-6 text-slate-400 group-hover:text-white transition-colors" />
                                {notifications.length > 0 && (
                                    <span className="absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full animate-pulse" />
                                )}
                                {/* Notification Dropdown */}
                                <div className="absolute right-0 top-full mt-2 w-64 bg-slate-800/90 backdrop-blur-xl border border-white/10 rounded-xl p-4 shadow-2xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10 transform translate-y-2 group-hover:translate-y-0">
                                    <h3 className="text-sm font-semibold mb-2 text-slate-300">Notifications</h3>
                                    <div className="space-y-2">
                                        {notifications.map((n) => (
                                            <div key={n.id} className="text-xs p-2 rounded bg-white/5 border border-white/5">
                                                {n.message}
                                            </div>
                                        ))}
                                        {notifications.length === 0 && <p className="text-xs text-slate-500">No new notifications</p>}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </header>

                    {/* Main Thermostat Circle */}
                    <div className="relative">
                        <div className="aspect-square max-w-[400px] mx-auto relative flex items-center justify-center">
                            {/* Outer Glow Ring */}
                            <div className={cn(
                                "absolute inset-0 rounded-full border-[20px] transition-all duration-700",
                                isOn ? "border-slate-800 shadow-[0_0_50px_rgba(0,0,0,0.3)]" : "border-slate-900 shadow-none"
                            )}></div>

                            {/* Active Mode Ring */}
                            <div className={cn(
                                "absolute inset-4 rounded-full border-[4px] border-t-transparent transition-all duration-700 animate-[spin_10s_linear_infinite]",
                                isOn && mode === 'cool' ? "border-cyan-500/50" : "border-transparent",
                                isOn && mode === 'heat' ? "border-orange-500/50" : "",
                                isOn && mode === 'fan' ? "border-emerald-500/50" : "",
                                isOn && mode === 'dry' ? "border-blue-500/50" : "",
                            )} style={{ transform: `rotate(${temperature * 10}deg)` }}></div>

                            {/* Inner Circle Content */}
                            <div className={cn(
                                "w-64 h-64 rounded-full bg-slate-800/50 backdrop-blur-sm border border-white/5 flex flex-col items-center justify-center relative shadow-inner transition-all duration-500",
                                isOn ? "shadow-[inset_0_0_30px_rgba(0,0,0,0.5)]" : "opacity-50 grayscale"
                            )}>
                                <span className="text-sm text-slate-400 mb-2 uppercase tracking-widest">{isOn ? mode : "OFF"}</span>
                                <div className="flex items-start">
                                    <span className="text-7xl font-bold tracking-tighter text-white">
                                        {temperature}
                                    </span>
                                    <span className="text-3xl text-slate-400 mt-2">°C</span>
                                </div>
                                <div className="mt-4 flex gap-6">
                                    <button
                                        onClick={() => handleTempChange(-1)}
                                        disabled={!isOn}
                                        className="p-3 rounded-full hover:bg-white/10 active:scale-95 transition-all text-slate-300 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
                                    >
                                        <ChevronDown className="w-8 h-8" />
                                    </button>
                                    <button
                                        onClick={() => handleTempChange(1)}
                                        disabled={!isOn}
                                        className="p-3 rounded-full hover:bg-white/10 active:scale-95 transition-all text-slate-300 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed"
                                    >
                                        <ChevronUp className="w-8 h-8" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Controls Row */}
                    <div className="flex justify-center gap-6">
                        <button
                            onClick={togglePower}
                            className={cn(
                                "w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 shadow-lg",
                                isOn
                                    ? "bg-red-500 text-white shadow-[0_0_20px_rgba(239,68,68,0.4)] hover:shadow-[0_0_30px_rgba(239,68,68,0.6)]"
                                    : "bg-slate-700 text-slate-400 hover:bg-slate-600 shadow-[0_0_20px_rgba(0,0,0,0.3)]"
                            )}
                        >
                            <Power className="w-8 h-8" />
                        </button>
                    </div>
                </div>

                {/* Sidebar Stats & Settings */}
                <div className="space-y-6">
                    {/* Modes Card */}
                    <div className="bg-slate-800/40 backdrop-blur-xl border border-white/5 rounded-3xl p-6">
                        <h3 className="text-lg font-medium text-slate-300 mb-4">Operation Mode</h3>
                        <div className="grid grid-cols-2 gap-4">
                            {(["cool", "heat", "fan", "dry"] as Mode[]).map((m) => (
                                <button
                                    key={m}
                                    onClick={() => setMode(m)}
                                    disabled={!isOn}
                                    className={cn(
                                        "p-4 rounded-xl flex flex-col items-center gap-2 transition-all duration-300 border",
                                        isOn && mode === m
                                            ? `${getModeColor(m)} border-transparent`
                                            : "bg-slate-900/50 border-white/5 text-slate-500 hover:bg-slate-800"
                                    )}
                                >
                                    {getModeIcon(m)}
                                    <span className="text-xs uppercase font-bold tracking-wider">{m}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Stats Card */}
                    <div className="bg-slate-800/40 backdrop-blur-xl border border-white/5 rounded-3xl p-6 space-y-6">
                        <h3 className="text-lg font-medium text-slate-300 mb-4">Environment & Status</h3>

                        <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-900/50 border border-white/5">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400">
                                    <Droplets className="w-5 h-5" />
                                </div>
                                <div>
                                    <p className="text-xs text-slate-400">Humidity</p>
                                    <p className="text-lg font-bold text-slate-200">{humidity.toFixed(1)}%</p>
                                </div>
                            </div>
                            <div className="h-10 w-[1px] bg-white/10"></div>
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-yellow-500/10 rounded-lg text-yellow-400">
                                    <Zap className="w-5 h-5" />
                                </div>
                                <div>
                                    <p className="text-xs text-slate-400">Power</p>
                                    <p className="text-lg font-bold text-slate-200">{isOn ? powerUsage.toFixed(1) : 0} kW</p>
                                </div>
                            </div>
                        </div>

                        <div className="flex items-center justify-between p-4 rounded-2xl bg-slate-900/50 border border-white/5">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-purple-500/10 rounded-lg text-purple-400">
                                    <Wind className="w-5 h-5" />
                                </div>
                                <div>
                                    <p className="text-xs text-slate-400">Fan Speed</p>
                                    <div className="flex gap-1 mt-1">
                                        {[1, 2, 3].map((level) => (
                                            <div
                                                key={level}
                                                className={cn(
                                                    "w-6 h-1.5 rounded-full transition-colors",
                                                    isOn && fanSpeed >= level ? "bg-purple-400" : "bg-slate-700"
                                                )}
                                            />
                                        ))}
                                    </div>
                                </div>
                            </div>
                            <div className="flex gap-2">
                                <button
                                    disabled={!isOn}
                                    onClick={() => setFanSpeed(s => Math.max(1, s - 1))}
                                    className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center hover:bg-slate-700 disabled:opacity-50"
                                >-</button>
                                <button
                                    disabled={!isOn}
                                    onClick={() => setFanSpeed(s => Math.min(3, s + 1))}
                                    className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center hover:bg-slate-700 disabled:opacity-50"
                                >+</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    );
}

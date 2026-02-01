"use client";

import React from "react";
import { GlassCard } from "@/components/shared/GlassCard";
import { User, Wifi, Bell, Shield, Smartphone } from "lucide-react";

export function SettingsView() {
    return (
        <div className="max-w-4xl mx-auto space-y-6">
            <header>
                <h1 className="text-3xl font-bold text-white">Settings</h1>
                <p className="text-slate-400 mt-1">Manage your device and preferences</p>
            </header>

            <div className="space-y-4">
                <GlassCard className="p-0 overflow-hidden">
                    <div className="p-4 border-b border-white/5 bg-white/5 font-bold text-slate-300">Account</div>
                    <div className="p-4 space-y-4">
                        <div className="flex items-center justify-between p-2 hover:bg-white/5 rounded-lg cursor-pointer transition">
                            <div className="flex items-center gap-4">
                                <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
                                    <User className="w-5 h-5" />
                                </div>
                                <div>
                                    <div className="text-white font-medium">Profile Information</div>
                                    <div className="text-xs text-slate-500">Update your email and personal details</div>
                                </div>
                            </div>
                            <div className="text-slate-500">{'>'}</div>
                        </div>
                    </div>
                </GlassCard>

                <GlassCard className="p-0 overflow-hidden">
                    <div className="p-4 border-b border-white/5 bg-white/5 font-bold text-slate-300">Device</div>
                    <div className="p-4 space-y-1">
                        <div className="flex items-center justify-between p-2 hover:bg-white/5 rounded-lg cursor-pointer transition">
                            <div className="flex items-center gap-4">
                                <div className="p-2 bg-green-500/20 rounded-lg text-green-400">
                                    <Wifi className="w-5 h-5" />
                                </div>
                                <div>
                                    <div className="text-white font-medium">Network Settings</div>
                                    <div className="text-xs text-slate-500">Living Room AC (192.168.1.104)</div>
                                </div>
                            </div>
                            <div className="text-green-500 text-sm">Connected</div>
                        </div>

                        <div className="flex items-center justify-between p-2 hover:bg-white/5 rounded-lg cursor-pointer transition">
                            <div className="flex items-center gap-4">
                                <div className="p-2 bg-purple-500/20 rounded-lg text-purple-400">
                                    <Smartphone className="w-5 h-5" />
                                </div>
                                <div>
                                    <div className="text-white font-medium">Device Link</div>
                                    <div className="text-xs text-slate-500">Link with Google Home / Alexa</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </GlassCard>
            </div>
        </div>
    );
}

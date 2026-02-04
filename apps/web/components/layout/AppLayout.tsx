"use client";

import React, { useState } from "react";
import {
    LayoutDashboard,
    BarChart3,
    CalendarClock,
    Settings,
    Leaf,
    Sparkles,
    Home,
    LogOut,
    Mic
} from "lucide-react";
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from "framer-motion";

export type ViewType = "dashboard" | "analytics" | "schedule" | "settings" | "wake";

interface AppLayoutProps {
    children: React.ReactNode;
    currentView: ViewType;
    onNavigate: (view: ViewType) => void;
}

export function AppLayout({ children, currentView, onNavigate }: AppLayoutProps) {
    const menuItems = [
        { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
        { id: "analytics", label: "Analytics", icon: BarChart3 },
        { id: "schedule", label: "Smart Schedule", icon: CalendarClock },
        { id: "wake", label: "Wake Lab", icon: Mic },
        { id: "settings", label: "Settings", icon: Settings },
    ];

    return (
        <div className="flex h-screen w-full bg-[#0a0f1c] text-slate-100 font-sans overflow-hidden">

            {/* Sidebar */}
            <aside className="w-20 lg:w-64 border-r border-white/5 bg-slate-900/50 backdrop-blur-xl flex flex-col justify-between py-8 px-4 relative z-50">

                {/* Logo Area */}
                <div className="flex items-center gap-3 pl-2 mb-12">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                        <Sparkles className="text-white w-6 h-6" />
                    </div>
                    <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400 hidden lg:block">
                        SmartAC
                    </span>
                </div>

                {/* Menu */}
                <nav className="flex-1 space-y-2">
                    {menuItems.map((item) => {
                        const isActive = currentView === item.id;
                        return (
                            <button
                                key={item.id}
                                onClick={() => onNavigate(item.id as ViewType)}
                                className={cn(
                                    "w-full flex items-center gap-4 p-3 rounded-xl transition-all duration-300 group relative overflow-hidden",
                                    isActive
                                        ? "bg-white/10 text-white shadow-inner"
                                        : "text-slate-400 hover:text-white hover:bg-white/5"
                                )}
                            >
                                {isActive && (
                                    <motion.div
                                        layoutId="activeTab"
                                        className="absolute inset-0 bg-gradient-to-r from-blue-500/20 to-cyan-500/10 rounded-xl"
                                    />
                                )}
                                <item.icon className={cn("w-6 h-6 relative z-10", isActive && "text-cyan-400")} />
                                <span className="font-medium hidden lg:block relative z-10">{item.label}</span>

                                {isActive && (
                                    <div className="absolute right-2 w-1.5 h-1.5 rounded-full bg-cyan-400 hidden lg:block" />
                                )}
                            </button>
                        )
                    })}
                </nav>

                {/* Bottom Actions */}
                <div className="space-y-4">
                    {/* Eco Badge */}
                    <div className="p-4 rounded-2xl bg-gradient-to-br from-emerald-500/10 to-emerald-900/10 border border-emerald-500/20 hidden lg:block">
                        <div className="flex items-center gap-3 mb-2">
                            <Leaf className="w-5 h-5 text-emerald-400" />
                            <span className="text-sm font-bold text-emerald-300">Eco Active</span>
                        </div>
                        <div className="text-xs text-emerald-500/80">
                            You saved 14kWh this week.
                        </div>
                    </div>

                    <button className="w-full flex items-center gap-4 p-3 rounded-xl text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition-all">
                        <LogOut className="w-6 h-6" />
                        <span className="font-medium hidden lg:block">Logout</span>
                    </button>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 flex flex-col relative overflow-hidden">
                {/* Background Gradients */}
                <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] rounded-full bg-blue-600/10 blur-[120px]" />
                <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] rounded-full bg-cyan-600/5 blur-[120px]" />

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-4 lg:p-8 relative z-10">
                    <AnimatePresence mode="wait">
                        <motion.div
                            key={currentView}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            transition={{ duration: 0.3 }}
                            className="h-full"
                        >
                            {children}
                        </motion.div>
                    </AnimatePresence>
                </div>
            </main>
        </div>
    );
}

/*
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
            // AC dashboard UI
        </div>
    );
}
*/

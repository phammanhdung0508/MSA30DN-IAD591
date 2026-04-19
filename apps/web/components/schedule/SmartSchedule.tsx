"use client";

import React, { useState, useEffect } from "react";
import { GlassCard } from "@/components/shared/GlassCard";
import { cn } from "@/lib/utils";
import { Clock, CheckCircle2, RotateCcw, Loader2 } from "lucide-react";
// import { getSchedule, saveSchedule } from "@/lib/api";

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const HOURS = Array.from({ length: 24 }, (_, i) => i);

const createEmptySchedule = () =>
  Array.from({ length: 7 }, () => Array.from({ length: 24 }, () => false));

const normalizeSchedule = (input: boolean[][]) => {
  if (!Array.isArray(input) || input.length !== 7) return createEmptySchedule();
  return input.map((day) => {
    if (!Array.isArray(day) || day.length !== 24) return Array(24).fill(false);
    return day.map((v) => Boolean(v));
  });
};

export function SmartSchedule() {
  // Simple grid state: [dayIndex][hourIndex] = boolean (isActive)
  const [schedule, setSchedule] = useState<boolean[][]>(createEmptySchedule());
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // useEffect(() => {
  //     const load = async () => {
  //         setIsLoading(true);
  //         const data = await getSchedule();
  //         setSchedule(normalizeSchedule(data));
  //         setIsLoading(false);
  //     };
  //     load();
  // }, []);

  // const handleSave = async () => {
  //     setIsSaving(true);
  //     try {
  //         await saveSchedule(schedule);
  //         // Could add toast here
  //     } finally {
  //         setIsSaving(false);
  //     }
  // };

  const toggleBlock = (d: number, h: number) => {
    const newSchedule = schedule.map((row) => [...row]);
    newSchedule[d][h] = !newSchedule[d][h];
    setSchedule(newSchedule);
  };

  return (
    <div className="space-y-6 h-full flex flex-col">
      <header className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-white">Smart Schedule</h1>
          <p className="text-slate-400 mt-1">Automate your comfort.</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setSchedule(createEmptySchedule())}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 transition"
          >
            <RotateCcw className="w-4 h-4" /> Reset
          </button>
          {/* <button
                        onClick={handleSave}
                        disabled={isSaving}
                        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-600 text-white hover:bg-cyan-500 transition disabled:opacity-50"
                    >
                        {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                        Save Schedule
                    </button> */}
        </div>
      </header>

      <GlassCard className="p-6 flex-1 overflow-auto">
        <div className="min-w-[800px]">
          {/* Header Row */}
          <div className="flex mb-2">
            <div className="w-16 shrink-0" />
            {HOURS.map((h) => (
              <div
                key={h}
                className="flex-1 text-center text-xs text-slate-500"
              >
                {h}
              </div>
            ))}
          </div>

          {/* Days Rows */}
          <div className="space-y-2">
            {DAYS.map((day, dIndex) => (
              <div key={day} className="flex items-center h-12">
                <div className="w-16 shrink-0 text-sm font-bold text-slate-400">
                  {day}
                </div>
                <div className="flex-1 flex gap-1 h-full">
                  {HOURS.map((h) => {
                    const active = schedule[dIndex][h];
                    return (
                      <button
                        key={h}
                        onMouseEnter={(e) => {
                          if (e.buttons === 1) toggleBlock(dIndex, h);
                        }}
                        onMouseDown={() => toggleBlock(dIndex, h)}
                        className={cn(
                          "flex-1 h-full rounded transition-colors duration-200",
                          active
                            ? "bg-cyan-500 shadow-[0_0_8px_rgba(6,182,212,0.5)]"
                            : "bg-slate-800/50 hover:bg-slate-700",
                        )}
                        title={`${day} ${h}:00 - ${h + 1}:00`}
                      />
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-8 flex gap-8 items-center justify-center text-sm text-slate-400">
          {/* <div className="flex items-center gap-2">
                        <div className="w-4 h-4 bg-cyan-500 rounded" />
                        <span>AC On (22\u00B0C Cool)</span>
                    </div> */}
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 bg-slate-800/50 rounded" />
            <span>Off</span>
          </div>
          <p className="italic ml-4">
            Tip: Click and drag to quick-select time blocks.
          </p>
        </div>
      </GlassCard>
    </div>
  );
}

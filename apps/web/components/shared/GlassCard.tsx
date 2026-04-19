import React from "react";
import { cn } from "@/lib/utils";

interface GlassCardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
  intensity?: "low" | "medium" | "high";
}

export function GlassCard({
  children,
  className,
  intensity = "medium",
  ...props
}: GlassCardProps) {
  const intensityMap = {
    low: "bg-slate-900/30 backdrop-blur-md border-white/5",
    medium: "bg-slate-800/40 backdrop-blur-xl border-white/10",
    high: "bg-slate-800/60 backdrop-blur-2xl border-white/20",
  };

  return (
    <div
      className={cn(
        "rounded-3xl border shadow-xl transition-all duration-300",
        intensityMap[intensity],
        className,
      )}
      {...props}
    >
      {children}
    </div>
  );
}

"use client";

import React, { useState } from "react";
import { AppLayout, ViewType } from "@/components/layout/AppLayout";
import { DashboardMain } from "@/components/dashboard/DashboardMain";
import { AnalyticsView } from "@/components/analytics/AnalyticsView";
import { SmartSchedule } from "@/components/schedule/SmartSchedule";
import { SettingsView } from "@/components/settings/SettingsView";
import { WakeLab } from "@/components/wake/WakeLab";

export default function Page() {
    const [currentView, setCurrentView] = useState<ViewType>("dashboard");

    return (
        <AppLayout currentView={currentView} onNavigate={setCurrentView}>
            {currentView === "dashboard" && <DashboardMain />}
            {currentView === "analytics" && <AnalyticsView />}
            {currentView === "schedule" && <SmartSchedule />}
            {currentView === "wake" && <WakeLab />}
            {currentView === "settings" && <SettingsView />}
        </AppLayout>
    );
}

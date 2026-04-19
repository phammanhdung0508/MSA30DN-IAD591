"use client";

import React, { useEffect, useMemo, useState } from "react";
import {
  getSensorLatest,
  getSensorSummary,
  getSensorHistory,
  type SensorLatest,
  type SensorSummary,
  type SensorHistory,
} from "@/lib/api";

const parseTimestamp = (ts?: string) => {
  if (!ts) return null;
  const [datePart, timePart] = ts.split(" ");
  if (!datePart || !timePart) return null;
  const [year, month, day] = datePart.split("-").map(Number);
  const [hour, minute, second] = timePart.split(":").map(Number);
  if ([year, month, day, hour, minute].some(Number.isNaN)) return null;
  return new Date(year, month - 1, day, hour, minute, second || 0);
};

const formatTime = (ts?: string) => {
  if (!ts) return "";
  const parsed = parseTimestamp(ts);
  if (!parsed) return "";
  return parsed.toLocaleTimeString("vi-VN", {
    hour: "2-digit",
    minute: "2-digit",
  });
};

const toNumber = (value: unknown) => {
  if (value === null || value === undefined) return null;
  const num = Number(value);
  return Number.isFinite(num) ? num : null;
};

export function SensorsView() {
  const [sensor, setSensor] = useState<SensorLatest | null>(null);
  const [summary, setSummary] = useState<SensorSummary | null>(null);
  const [history, setHistory] = useState<SensorHistory | null>(null);

  useEffect(() => {
    const fetchSensor = async () => {
      const latest = await getSensorLatest();
      if (latest) setSensor(latest);
    };
    fetchSensor();
    const interval = setInterval(fetchSensor, 10000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const fetchSummary = async () => {
      const [sum, hist] = await Promise.all([
        getSensorSummary(),
        getSensorHistory("esp32-main", 10),
      ]);
      if (sum) setSummary(sum);
      if (hist) setHistory(hist);
    };
    fetchSummary();
    const interval = setInterval(fetchSummary, 60000);
    return () => clearInterval(interval);
  }, []);

  const latestData = sensor?.data ?? {};
  const temperature = toNumber(latestData["temperature"]);
  const humidity = toNumber(latestData["humidity"]);
  const co2 = toNumber(latestData["co2"] ?? latestData["gas"]);
  const nh3 = toNumber(latestData["nh3"]);
  const co = toNumber(latestData["co"]);
  const rs = toNumber(latestData["rs"]);
  const ratio = toNumber(latestData["ratio"]);
  const historyItems = useMemo(
    () => history?.items?.slice(0, 6) ?? [],
    [history],
  );

  return (
    <div className="flex h-full flex-col">
      <header className="px-6 pt-6 pb-4">
        <div>
          <div className="text-[11px] uppercase tracking-[0.24em] text-slate-400">
            Sensors
          </div>
          <div className="text-2xl font-semibold text-white">
            DHT11 + MQ-135
          </div>
        </div>
      </header>

      <main className="flex-1 overflow-y-auto px-6 pb-6 space-y-4">
        <div className="rounded-2xl border border-white/10 bg-white/5 p-4 text-xs text-slate-300">
          <div className="flex items-center justify-between text-[10px] uppercase tracking-widest text-slate-400">
            <span>Snapshot</span>
            <span>
              {sensor?.timestamp ? formatTime(sensor.timestamp) : "No data"}
            </span>
          </div>
          <div className="mt-3 grid grid-cols-3 gap-3 text-center">
            <div>
              <div className="text-lg font-semibold text-white">
                {temperature !== null ? `${temperature.toFixed(1)}C` : "--"}
              </div>
              <div className="text-[10px] uppercase tracking-widest text-slate-500">
                Temp
              </div>
            </div>
            <div>
              <div className="text-lg font-semibold text-white">
                {humidity !== null ? `${humidity.toFixed(0)}%` : "--"}
              </div>
              <div className="text-[10px] uppercase tracking-widest text-slate-500">
                Humidity
              </div>
            </div>
            <div>
              <div className="text-lg font-semibold text-white">
                {co2 !== null ? `${co2.toFixed(0)}ppm` : "--"}
              </div>
              <div className="text-[10px] uppercase tracking-widest text-slate-500">
                CO2
              </div>
            </div>
          </div>
          <div className="mt-3 flex flex-wrap gap-3 text-[11px] text-slate-400">
            <span>NH3: {nh3 !== null ? `${nh3.toFixed(1)} ppm` : "--"}</span>
            <span>CO: {co !== null ? `${co.toFixed(1)} ppm` : "--"}</span>
            <span>RS: {rs !== null ? rs.toFixed(1) : "--"}</span>
            <span>Ratio: {ratio !== null ? ratio.toFixed(3) : "--"}</span>
          </div>
        </div>

        {summary && (
          <div className="rounded-2xl border border-white/10 bg-slate-900/50 p-4 text-[11px] text-slate-400">
            <div className="text-[10px] uppercase tracking-widest text-slate-500">
              24h Summary
            </div>
            <div className="mt-3 grid grid-cols-3 gap-3 text-center text-slate-200">
              <div>
                <div className="text-sm font-semibold">
                  {summary.summary.temperature.avg?.toFixed(1) ?? "--"}C
                </div>
                <div className="text-[10px] uppercase tracking-widest text-slate-500">
                  Temp avg
                </div>
              </div>
              <div>
                <div className="text-sm font-semibold">
                  {summary.summary.humidity.avg?.toFixed(0) ?? "--"}%
                </div>
                <div className="text-[10px] uppercase tracking-widest text-slate-500">
                  Hum avg
                </div>
              </div>
              <div>
                <div className="text-sm font-semibold">
                  {summary.summary.co2.avg?.toFixed(0) ?? "--"}ppm
                </div>
                <div className="text-[10px] uppercase tracking-widest text-slate-500">
                  CO2 avg
                </div>
              </div>
            </div>
          </div>
        )}

        {historyItems.length > 0 && (
          <div className="rounded-2xl border border-white/10 bg-slate-900/50 p-3 text-[11px] text-slate-400">
            <div className="mb-2 text-[10px] uppercase tracking-widest text-slate-500">
              Recent Samples
            </div>
            <div className="space-y-2">
              {historyItems.map((item, idx) => {
                const itemTemp = toNumber(item.data?.["temperature"]);
                const itemHum = toNumber(item.data?.["humidity"]);
                const itemCo2 = toNumber(
                  item.data?.["co2"] ?? item.data?.["gas"],
                );
                return (
                  <div
                    key={`${item.timestamp}-${idx}`}
                    className="flex items-center justify-between"
                  >
                    <span className="text-slate-500">
                      {formatTime(item.timestamp)}
                    </span>
                    <span>
                      {itemTemp !== null ? `${itemTemp.toFixed(1)}C` : "--"} /{" "}
                      {itemHum !== null ? `${itemHum.toFixed(0)}%` : "--"} /{" "}
                      {itemCo2 !== null ? `${itemCo2.toFixed(0)}ppm` : "--"}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {!sensor && (
          <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-400">
            Waiting for sensor data...
          </div>
        )}
      </main>
    </div>
  );
}

"use client";

import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { GlassCard } from "@/components/shared/GlassCard";
import { Mic, Wifi, Radio, AlertTriangle, Loader2, Send, PlugZap } from "lucide-react";

type MqttStatus = "disconnected" | "connecting" | "connected" | "error";
type StreamStatus = "idle" | "connecting" | "streaming" | "error";

const DEFAULT_WAKE_PHRASE = "hey esp";
const DEFAULT_MQTT_URL = "wss://broker.hivemq.com:8884/mqtt";
const DEFAULT_MQTT_TOPIC = "sensor/wake_trigger_msa_assign1";
const DEFAULT_WS_URL = "ws://localhost:8080";

export function WakeLab() {
    const [mqttUrl, setMqttUrl] = useState(DEFAULT_MQTT_URL);
    const [mqttTopic, setMqttTopic] = useState(DEFAULT_MQTT_TOPIC);
    const [mqttStatus, setMqttStatus] = useState<MqttStatus>("disconnected");
    const [mqttError, setMqttError] = useState<string | null>(null);
    const mqttClientRef = useRef<any>(null);

    const [wakePhrase, setWakePhrase] = useState(DEFAULT_WAKE_PHRASE);
    const [listening, setListening] = useState(false);
    const recognitionRef = useRef<any>(null);

    const [wsUrl, setWsUrl] = useState(DEFAULT_WS_URL);
    const [streamStatus, setStreamStatus] = useState<StreamStatus>("idle");
    const wsRef = useRef<WebSocket | null>(null);
    const audioCtxRef = useRef<AudioContext | null>(null);
    const processorRef = useRef<ScriptProcessorNode | null>(null);
    const mediaStreamRef = useRef<MediaStream | null>(null);
    const targetSampleRate = 16000;

    const canUseSpeechApi = useMemo(() => {
        if (typeof window === "undefined") return false;
        return "webkitSpeechRecognition" in window || "SpeechRecognition" in window;
    }, []);

    const connectMqtt = useCallback(async () => {
        if (mqttClientRef.current) {
            mqttClientRef.current.end(true);
        }
        setMqttStatus("connecting");
        setMqttError(null);

        try {
            const mqtt = await import("mqtt");
            const clientId = `web-wake-${Math.random().toString(16).slice(2)}`;
            const client = mqtt.connect(mqttUrl, {
                clientId,
                reconnectPeriod: 2000,
                clean: true,
            });
            mqttClientRef.current = client;

            client.on("connect", () => {
                setMqttStatus("connected");
                setMqttError(null);
            });
            client.on("reconnect", () => setMqttStatus("connecting"));
            client.on("close", () => setMqttStatus("disconnected"));
            client.on("error", (err: Error) => {
                setMqttStatus("error");
                setMqttError(err.message);
            });
        } catch (err: any) {
            setMqttStatus("error");
            setMqttError(err?.message || "Failed to load MQTT client");
        }
    }, [mqttUrl]);

    const disconnectMqtt = useCallback(() => {
        if (mqttClientRef.current) {
            mqttClientRef.current.end(true);
            mqttClientRef.current = null;
        }
        setMqttStatus("disconnected");
    }, []);

    const publishWake = useCallback(() => {
        const client = mqttClientRef.current;
        if (!client || mqttStatus !== "connected") return;
        client.publish(mqttTopic, "WAKE", { qos: 0 });
    }, [mqttStatus, mqttTopic]);

    const startListening = useCallback(() => {
        if (!canUseSpeechApi) return;
        const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = "en-US";
        recognition.onresult = (event: any) => {
            const transcript = Array.from(event.results)
                .map((res: any) => res[0]?.transcript || "")
                .join(" ")
                .toLowerCase();
            if (transcript.includes(wakePhrase.toLowerCase())) {
                publishWake();
            }
        };
        recognition.onerror = () => setListening(false);
        recognition.onend = () => setListening(false);
        recognition.start();
        recognitionRef.current = recognition;
        setListening(true);
    }, [canUseSpeechApi, publishWake, wakePhrase]);

    const stopListening = useCallback(() => {
        if (recognitionRef.current) {
            recognitionRef.current.stop();
            recognitionRef.current = null;
        }
        setListening(false);
    }, []);

    const downsampleTo16k = (input: Float32Array, inputRate: number) => {
        if (inputRate === targetSampleRate) return input;
        const ratio = inputRate / targetSampleRate;
        const outLength = Math.round(input.length / ratio);
        const output = new Float32Array(outLength);
        let offset = 0;
        for (let i = 0; i < outLength; i++) {
            const pos = i * ratio;
            const idx = Math.floor(pos);
            const frac = pos - idx;
            const next = idx + 1 < input.length ? input[idx + 1] : input[idx];
            output[offset++] = input[idx] + (next - input[idx]) * frac;
        }
        return output;
    };

    const startStreaming = useCallback(async () => {
        if (streamStatus === "streaming") return;
        setStreamStatus("connecting");

        try {
            const ws = new WebSocket(wsUrl);
            ws.binaryType = "arraybuffer";
            ws.onopen = async () => {
                wsRef.current = ws;
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaStreamRef.current = stream;
                const ctx = new AudioContext();
                audioCtxRef.current = ctx;

                const source = ctx.createMediaStreamSource(stream);
                const processor = ctx.createScriptProcessor(4096, 1, 1);
                processorRef.current = processor;

                processor.onaudioprocess = (event) => {
                    if (ws.readyState !== WebSocket.OPEN) return;
                    const input = event.inputBuffer.getChannelData(0);
                    const down = downsampleTo16k(input, ctx.sampleRate);
                    const pcm = new Int16Array(down.length);
                    for (let i = 0; i < down.length; i++) {
                        const s = Math.max(-1, Math.min(1, down[i]));
                        pcm[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
                    }
                    ws.send(pcm.buffer);
                };

                source.connect(processor);
                processor.connect(ctx.destination);
                setStreamStatus("streaming");
            };
            ws.onerror = () => setStreamStatus("error");
            ws.onclose = () => setStreamStatus("idle");
        } catch {
            setStreamStatus("error");
        }
    }, [streamStatus, wsUrl]);

    const stopStreaming = useCallback(() => {
        if (wsRef.current) {
            wsRef.current.close();
            wsRef.current = null;
        }
        if (processorRef.current) {
            processorRef.current.disconnect();
            processorRef.current = null;
        }
        if (audioCtxRef.current) {
            audioCtxRef.current.close();
            audioCtxRef.current = null;
        }
        if (mediaStreamRef.current) {
            mediaStreamRef.current.getTracks().forEach((t) => t.stop());
            mediaStreamRef.current = null;
        }
        setStreamStatus("idle");
    }, []);

    useEffect(() => {
        return () => {
            disconnectMqtt();
            stopListening();
            stopStreaming();
        };
    }, [disconnectMqtt, stopListening, stopStreaming]);

    return (
        <div className="max-w-6xl mx-auto space-y-6">
            <header>
                <h1 className="text-3xl font-bold text-white">Wake Lab</h1>
                <p className="text-slate-400 mt-1">Trigger ESP32 wake via MQTT (A) or stream audio via UDP bridge (B)</p>
            </header>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
                <GlassCard className="p-6 space-y-6">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400">
                            <Wifi className="w-5 h-5" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-white">A) MQTT Wake Trigger</h2>
                            <p className="text-xs text-slate-400">Web detects keyword and publishes to MQTT</p>
                        </div>
                    </div>

                    <div className="space-y-3">
                        <label className="text-xs text-slate-400 uppercase tracking-wider">Broker (WebSocket)</label>
                        <input
                            className="w-full rounded-xl bg-slate-900/60 border border-white/10 px-4 py-2 text-sm text-white"
                            value={mqttUrl}
                            onChange={(e) => setMqttUrl(e.target.value)}
                            placeholder="wss://broker:port/mqtt"
                        />
                        <label className="text-xs text-slate-400 uppercase tracking-wider">Topic</label>
                        <input
                            className="w-full rounded-xl bg-slate-900/60 border border-white/10 px-4 py-2 text-sm text-white"
                            value={mqttTopic}
                            onChange={(e) => setMqttTopic(e.target.value)}
                            placeholder="sensor/wake_trigger_msa_assign1"
                        />
                    </div>

                    <div className="flex items-center gap-3">
                        {mqttStatus === "connecting" && <Loader2 className="w-4 h-4 text-cyan-400 animate-spin" />}
                        {mqttStatus === "connected" && <div className="w-2 h-2 rounded-full bg-emerald-400" />}
                        {mqttStatus === "error" && <AlertTriangle className="w-4 h-4 text-amber-400" />}
                        <span className="text-sm text-slate-300 capitalize">{mqttStatus}</span>
                    </div>
                    {mqttError && <div className="text-xs text-amber-400">{mqttError}</div>}

                    <div className="flex flex-wrap gap-3">
                        <button
                            onClick={connectMqtt}
                            className="px-4 py-2 rounded-xl bg-cyan-500 text-white text-sm font-semibold flex items-center gap-2"
                        >
                            <PlugZap className="w-4 h-4" />
                            Connect
                        </button>
                        <button
                            onClick={disconnectMqtt}
                            className="px-4 py-2 rounded-xl bg-slate-800 text-slate-200 text-sm font-semibold"
                        >
                            Disconnect
                        </button>
                        <button
                            onClick={publishWake}
                            disabled={mqttStatus !== "connected"}
                            className="px-4 py-2 rounded-xl bg-emerald-500 text-white text-sm font-semibold flex items-center gap-2 disabled:opacity-50"
                        >
                            <Send className="w-4 h-4" />
                            Trigger Wake
                        </button>
                    </div>

                    <div className="pt-4 border-t border-white/10 space-y-3">
                        <div className="flex items-center gap-2 text-sm text-slate-300">
                            <Mic className="w-4 h-4 text-cyan-400" />
                            Web Speech API (keyword)
                        </div>
                        <div className="flex gap-3">
                            <input
                                className="flex-1 rounded-xl bg-slate-900/60 border border-white/10 px-4 py-2 text-sm text-white"
                                value={wakePhrase}
                                onChange={(e) => setWakePhrase(e.target.value)}
                                placeholder="hey esp"
                            />
                            <button
                                onClick={listening ? stopListening : startListening}
                                disabled={!canUseSpeechApi || mqttStatus !== "connected"}
                                className="px-4 py-2 rounded-xl bg-slate-800 text-slate-200 text-sm font-semibold disabled:opacity-50"
                            >
                                {listening ? "Stop" : "Listen"}
                            </button>
                        </div>
                        {!canUseSpeechApi && (
                            <div className="text-xs text-amber-400">
                                Speech API not supported in this browser. Use manual trigger or another browser.
                            </div>
                        )}
                    </div>
                </GlassCard>

                <GlassCard className="p-6 space-y-6">
                    <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
                            <Radio className="w-5 h-5" />
                        </div>
                        <div>
                            <h2 className="text-lg font-semibold text-white">B) UDP Audio Stream (via bridge)</h2>
                            <p className="text-xs text-slate-400">Browser -> WebSocket bridge -> UDP to ESP32</p>
                        </div>
                    </div>

                    <div className="space-y-3">
                        <label className="text-xs text-slate-400 uppercase tracking-wider">Bridge WebSocket URL</label>
                        <input
                            className="w-full rounded-xl bg-slate-900/60 border border-white/10 px-4 py-2 text-sm text-white"
                            value={wsUrl}
                            onChange={(e) => setWsUrl(e.target.value)}
                            placeholder="ws://localhost:8080"
                        />
                    </div>

                    <div className="flex items-center gap-3">
                        {streamStatus === "connecting" && <Loader2 className="w-4 h-4 text-purple-400 animate-spin" />}
                        {streamStatus === "streaming" && <div className="w-2 h-2 rounded-full bg-emerald-400" />}
                        {streamStatus === "error" && <AlertTriangle className="w-4 h-4 text-amber-400" />}
                        <span className="text-sm text-slate-300 capitalize">{streamStatus}</span>
                    </div>

                    <div className="flex gap-3">
                        <button
                            onClick={startStreaming}
                            className="px-4 py-2 rounded-xl bg-purple-500 text-white text-sm font-semibold"
                        >
                            Start Stream
                        </button>
                        <button
                            onClick={stopStreaming}
                            className="px-4 py-2 rounded-xl bg-slate-800 text-slate-200 text-sm font-semibold"
                        >
                            Stop
                        </button>
                    </div>

                    <div className="text-xs text-slate-400 leading-relaxed">
                        Requires the UDP bridge script on your machine. The bridge forwards raw PCM 16kHz
                        mono audio to ESP32 UDP port 3333. See `apps/web/scripts/ws-udp-bridge.mjs`.
                    </div>
                </GlassCard>
            </div>
        </div>
    );
}

#!/usr/bin/env node
import dgram from "node:dgram";

const args = new Map();
for (let i = 2; i < process.argv.length; i += 2) {
    args.set(process.argv[i], process.argv[i + 1]);
}

const target = args.get("--target") || "192.168.1.50:3333";
const [host, portStr] = target.split(":");
const port = Number(portStr || 3333);

const durationSec = Number(args.get("--duration") || 5);
const freq = Number(args.get("--freq") || 440);
const sampleRate = 16000;
const frameMs = 20;
const samplesPerFrame = Math.floor(sampleRate * (frameMs / 1000));

if (!host || Number.isNaN(port)) {
    console.error("Usage: node udp-audio-test.mjs --target 192.168.1.50:3333 [--duration 5] [--freq 440]");
    process.exit(1);
}

const socket = dgram.createSocket("udp4");
const totalFrames = Math.floor((durationSec * 1000) / frameMs);
let frameIndex = 0;

const sendFrame = () => {
    const pcm = new Int16Array(samplesPerFrame);
    for (let i = 0; i < samplesPerFrame; i++) {
        const t = (frameIndex * samplesPerFrame + i) / sampleRate;
        const s = Math.sin(2 * Math.PI * freq * t);
        pcm[i] = s * 0x3fff;
    }
    socket.send(Buffer.from(pcm.buffer), port, host);
    frameIndex += 1;
    if (frameIndex >= totalFrames) {
        clearInterval(timer);
        socket.close();
        console.log("Done.");
    }
};

const timer = setInterval(sendFrame, frameMs);
console.log(`Sending ${durationSec}s of ${freq}Hz tone to udp://${host}:${port}`);

#!/usr/bin/env node
import dgram from "node:dgram";
import { WebSocketServer } from "ws";

const args = new Map();
for (let i = 2; i < process.argv.length; i += 2) {
    args.set(process.argv[i], process.argv[i + 1]);
}

const wsPort = Number(args.get("--port") || 8080);
const target = args.get("--target") || "192.168.1.50:3333";
const [targetHost, targetPortStr] = target.split(":");
const targetPort = Number(targetPortStr || 3333);

if (!targetHost || Number.isNaN(targetPort)) {
    console.error("Usage: node ws-udp-bridge.mjs --port 8080 --target 192.168.1.50:3333");
    process.exit(1);
}

const udp = dgram.createSocket("udp4");
const wss = new WebSocketServer({ port: wsPort });

console.log(`WS-UDP bridge listening on ws://localhost:${wsPort}`);
console.log(`Forwarding to UDP ${targetHost}:${targetPort}`);

wss.on("connection", (ws) => {
    ws.on("message", (data) => {
        if (!(data instanceof Buffer)) return;
        udp.send(data, targetPort, targetHost);
    });
});

"use client";

import React, { useRef, useState } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, PerspectiveCamera, Environment, Html } from "@react-three/drei";
import * as THREE from "three";
import { Power, Fan, Thermometer, Wind } from "lucide-react";

// --- COMPONENTS ---

function ACSimpleModel({ isOn, mode, fanSpeed }: { isOn: boolean; mode: string, fanSpeed: number }) {
    const meshRef = useRef<THREE.Group>(null);
    const bladeRef = useRef<THREE.Mesh>(null);

    // Animation loop
    useFrame((state, delta) => {
        if (isOn && bladeRef.current) {
            // Rotate fan blades based on speed
            // Speed 1: slow, Speed 3: fast
            const speed = fanSpeed * 5;
            bladeRef.current.rotation.x += delta * speed;
        }
    });

    return (
        <group ref={meshRef} position={[0, 1, -2]}>
            {/* Main Body */}
            <mesh position={[0, 0, 0]}>
                <boxGeometry args={[4, 1.2, 0.8]} />
                <meshStandardMaterial color="#f0f0f0" roughness={0.2} metalness={0.1} />
            </mesh>

            {/* Air Vent / Flap */}
            <mesh position={[0, -0.4, 0.4]} rotation={[isOn ? (Math.PI / 6) : 0, 0, 0]}>
                <boxGeometry args={[3.8, 0.2, 0.1]} />
                <meshStandardMaterial color="#ddd" />
            </mesh>

            {/* Internal Fan Blades (Visual representation only visible if looking usually) */}
            <mesh ref={bladeRef} position={[0, 0, 0]} visible={false}> {/* Hidden for simple box, but logic is there */}
                <boxGeometry args={[0.5, 0.5, 0.5]} />
            </mesh>


            {/* Status Light */}
            <mesh position={[1.5, 0.2, 0.41]}>
                <circleGeometry args={[0.05, 32]} />
                <meshStandardMaterial
                    color={isOn ? (mode === 'heat' ? '#ff4d4d' : '#00ff00') : '#333'}
                    emissive={isOn ? (mode === 'heat' ? '#ff4d4d' : '#00ff00') : '#000'}
                    emissiveIntensity={isOn ? 2 : 0}
                />
            </mesh>

            {/* Brand Text */}
            <Html position={[0, 0.2, 0.41]} transform occlude scale={0.2}>
                <div className="text-gray-400 font-bold text-xs select-none pointer-events-none">
                    DAIKIN
                </div>
            </Html>
        </group>
    );
}

function ColdAirParticles({ isOn, mode }: { isOn: boolean; mode: string }) {
    // A simple particle system to visualize air
    // In a real app, use @react-three/drei instances or a shader
    if (!isOn || mode === 'off') return null;

    return (
        <group position={[0, 0.5, -1.5]}>
            {/* Placeholder for particles */}
            {/* Ideally this would be a Points system */}
        </group>
    )
}

function Room() {
    return (
        <group>
            {/* Floor */}
            <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -2, 0]}>
                <planeGeometry args={[10, 10]} />
                <meshStandardMaterial color="#e2e8f0" />
            </mesh>
            {/* Back Wall */}
            <mesh position={[0, 0, -5]}>
                <planeGeometry args={[10, 10]} />
                <meshStandardMaterial color="#f8fafc" />
            </mesh>
        </group>
    )
}

// --- MAIN PAGE ---

export default function SimulationPage() {
    const [isOn, setIsOn] = useState(false);
    const [mode, setMode] = useState("cool"); // cool, heat, fan
    const [fanSpeed, setFanSpeed] = useState(1);
    const [temp, setTemp] = useState(24);

    return (
        <div className="w-full h-screen bg-slate-950 flex flex-col md:flex-row">

            {/* 3D Viewport */}
            <div className="flex-1 relative h-[60vh] md:h-auto">
                <Canvas shadows>
                    <PerspectiveCamera makeDefault position={[0, 0, 6]} fov={50} />
                    <OrbitControls
                        enablePan={false}
                        minPolarAngle={Math.PI / 4}
                        maxPolarAngle={Math.PI / 2}
                        minDistance={4}
                        maxDistance={8}
                    />

                    <ambientLight intensity={0.5} />
                    <spotLight position={[5, 10, 5]} angle={0.5} penumbra={1} intensity={100} castShadow />
                    <Environment preset="city" />

                    <Room />
                    <ACSimpleModel isOn={isOn} mode={mode} fanSpeed={fanSpeed} />
                    <ColdAirParticles isOn={isOn} mode={mode} />

                </Canvas>

                {/* HUD Info */}
                <div className="absolute top-4 left-4 p-4 bg-black/50 backdrop-blur-md rounded-xl text-white border border-white/10">
                    <h2 className="text-xl font-bold">Living Room</h2>
                    <div className="text-4xl font-light mt-2">
                        {temp}
                        {"\u00B0C"}
                    </div>
                    <div className="text-sm text-gray-400 mt-1">Current Temperature</div>
                </div>
            </div>

            {/* Sidebar Controls */}
            <div className="w-full md:w-[400px] bg-slate-900 border-l border-white/10 p-8 flex flex-col gap-8 overflow-y-auto">

                {/* Header */}
                <div>
                    <h1 className="text-2xl font-bold text-white mb-1">AC Remote</h1>
                    <p className="text-slate-400 text-sm">Interactive 3D Simulation</p>
                </div>

                {/* Main Power Toggle */}
                <div className="flex justify-center">
                    <button
                        onClick={() => setIsOn(!isOn)}
                        className={`w-24 h-24 rounded-full flex items-center justify-center transition-all duration-500 shadow-2xl ${isOn
                                ? "bg-red-500 text-white shadow-red-500/40 scale-110"
                                : "bg-slate-800 text-slate-600 shadow-black/50 hover:bg-slate-700"
                            }`}
                    >
                        <Power size={48} />
                    </button>
                </div>

                {/* Controls Container */}
                <div className={`space-y-6 transition-all duration-300 ${isOn ? 'opacity-100' : 'opacity-40 pointer-events-none'}`}>

                    {/* Mode Selection */}
                    <div className="bg-slate-800/50 p-4 rounded-2xl border border-white/5">
                        <label className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-3 block">Mode</label>
                        <div className="grid grid-cols-3 gap-2">
                            {['cool', 'heat', 'fan'].map((m) => (
                                <button
                                    key={m}
                                    onClick={() => setMode(m)}
                                    className={`p-3 rounded-xl flex flex-col items-center gap-2 transition-all ${mode === m
                                            ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                                            : 'bg-slate-700/50 text-slate-400 hover:bg-slate-700'
                                        }`}
                                >
                                    {m === 'cool' && <Thermometer size={20} />}
                                    {m === 'heat' && <Power size={20} className="text-orange-400" />}
                                    {m === 'fan' && <Fan size={20} />}
                                    <span className="text-xs font-medium capitalize">{m}</span>
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Temperature Control */}
                    <div className="bg-slate-800/50 p-6 rounded-2xl border border-white/5 flex items-center justify-between">
                        <button
                            onClick={() => setTemp(t => t - 1)}
                            className="w-12 h-12 rounded-full bg-slate-700 hover:bg-slate-600 flex items-center justify-center text-white text-xl font-bold transition-colors"
                        >-</button>
                        <div className="text-center">
                            <div className="text-3xl font-bold text-white">
                                {temp}
                                {"\u00B0"}
                            </div>
                            <div className="text-xs text-slate-400">Target Temp</div>
                        </div>
                        <button
                            onClick={() => setTemp(t => t + 1)}
                            className="w-12 h-12 rounded-full bg-slate-700 hover:bg-slate-600 flex items-center justify-center text-white text-xl font-bold transition-colors"
                        >+</button>
                    </div>

                    {/* Fan Speed */}
                    <div className="bg-slate-800/50 p-6 rounded-2xl border border-white/5">
                        <div className="flex justify-between items-center mb-4">
                            <label className="text-xs font-bold text-slate-500 uppercase tracking-widest">Fan Speed</label>
                            <Wind size={16} className="text-slate-400" />
                        </div>
                        <input
                            type="range"
                            min="1"
                            max="3"
                            step="1"
                            value={fanSpeed}
                            onChange={(e) => setFanSpeed(parseInt(e.target.value))}
                            className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-blue-500"
                        />
                        <div className="flex justify-between mt-2 text-xs text-slate-400 font-medium">
                            <span>Low</span>
                            <span>Med</span>
                            <span>High</span>
                        </div>
                    </div>

                </div>

            </div>
        </div>
    );
}

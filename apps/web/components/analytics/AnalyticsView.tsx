// /*
// "use client";
//
// import React from "react";
// import {
//     AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar
// } from "recharts";
// import { GlassCard } from "@/components/shared/GlassCard";
// import { Zap, DollarSign, TrendingDown } from "lucide-react";
// import { getEnergyAnalytics, getTempAnalytics } from "@/lib/api";
//
// const energyData = [
//     { time: "00:00", active: 0.2, idle: 0.1 },
//     { time: "04:00", active: 0.1, idle: 0.1 },
//     { time: "08:00", active: 0.8, idle: 0.2 },
//     { time: "12:00", active: 2.5, idle: 0.5 },
//     { time: "16:00", active: 1.8, idle: 0.3 },
//     { time: "20:00", active: 3.2, idle: 0.6 },
//     { time: "23:59", active: 1.5, idle: 0.2 },
// ];
//
// // Mock data removed
//
// export function AnalyticsView() {
//     const [tempData, setTempData] = React.useState<any[]>([]);
//
//     React.useEffect(() => {
//         const loadData = async () => {
//             try {
//                 const temp = await getTempAnalytics();
//                 setTempData(temp);
//             } catch (e) {
//                 console.error("Failed to load analytics", e);
//             }
//         };
//         loadData();
//         const interval = setInterval(loadData, 5000); // Update every 5s
//         return () => clearInterval(interval);
//     }, []);
//
//     return (
//         <div className="space-y-6 h-full overflow-y-auto pb-8">
//             <header>
//                 <h1 className="text-3xl font-bold text-white">Analytics</h1>
//                 <p className="text-slate-400 mt-1">Temperature reports</p>
//             </header>
//
//             {/* Charts */}
//             <div className="grid grid-cols-1 gap-6">
//                 <GlassCard className="p-6 h-[500px]">
//                     <h3 className="text-lg font-bold text-white mb-6">Temperature Trends</h3>
//                     <ResponsiveContainer width="100%" height="100%">
//                         <AreaChart data={tempData}>
//                             <defs>
//                                 <linearGradient id="colorIndoor" x1="0" y1="0" x2="0" y2="1">
//                                     <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
//                                     <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
//                                 </linearGradient>
//                             </defs>
//                             <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
//                             <XAxis dataKey="time" stroke="#94a3b8" />
//                             <YAxis stroke="#94a3b8" unit="\u00B0C" domain={['auto', 'auto']} />
//                             <Tooltip
//                                 cursor={{ stroke: '#ffffff20' }}
//                                 contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }}
//                             />
//                             <Area type="monotone" dataKey="indoor" name="Indoor Temp" stroke="#3b82f6" fillOpacity={1} fill="url(#colorIndoor)" />
//                         </AreaChart>
//                     </ResponsiveContainer>
//                 </GlassCard>
//             </div>
//         </div>
//     );
// }
//
// // Sparkles icon override since it was used in layout but might not be imported here
// function Sparkles({ className }: { className?: string }) {
//     return (
//         <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}>
//             <path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z" />
//         </svg>
//     )
// }
// */
//
// export function AnalyticsView() {
//     return null;
// }

export function AnalyticsView() {
  return null;
}

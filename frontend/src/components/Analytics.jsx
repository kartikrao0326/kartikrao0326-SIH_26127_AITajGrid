import React, { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';

const Analytics = () => {
  const [flow, setFlow] = useState({});
  const [congestion, setCongestion] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [flowRes, congRes] = await Promise.all([
          fetch('http://localhost:8000/api/analytics/flow'),
          fetch('http://localhost:8000/api/analytics/congestion')
        ]);
        setFlow(await flowRes.json());
        setCongestion(await congRes.json());
      } catch (e) {
        console.error(e);
      }
    };
    
    fetchData();
    const intv = setInterval(fetchData, 5000);
    return () => clearInterval(intv);
  }, []);

  // Format flow data for Recharts (merge by time)
  const timeMap = {};
  Object.keys(flow).forEach(node => {
    flow[node].forEach(pt => {
      if (!timeMap[pt.time]) timeMap[pt.time] = { time: pt.time.split(' ')[1] };
      timeMap[pt.time][node] = pt.count;
    });
  });
  const flowData = Object.values(timeMap).sort((a, b) => a.time.localeCompare(b.time));

  return (
    <div className="relative z-10">
      <div className="flex items-center space-x-2 mb-6">
        <h3 className="text-xl font-bold tracking-wide text-slate-100">Live Telemetry</h3>
        <span className="flex h-2 w-2 ml-2">
          <span className="animate-ping absolute inline-flex h-2 w-2 rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        </span>
      </div>
      
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-8">
        <div className="h-64">
          <h4 className="text-xs font-mono text-slate-400 mb-4 uppercase tracking-wider">Junction Flow (events/min)</h4>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={flowData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="time" stroke="#9CA3AF" />
            <YAxis stroke="#9CA3AF" />
            <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none' }} />
            <Legend />
            {Object.keys(flow).map((node, i) => (
              <Line key={node} type="monotone" dataKey={node} stroke={`hsl(${i * 45}, 70%, 50%)`} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="h-64">
        <h4 className="text-sm text-gray-400 mb-2">Congestion by Edge (Ratio)</h4>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={congestion}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="edge_id" stroke="#9CA3AF" fontSize={10} />
            <YAxis stroke="#9CA3AF" />
            <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none' }} />
            <Bar dataKey="ratio">
              {congestion.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.is_congested ? '#ef4444' : '#3b82f6'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
      </div>
    </div>
  );
};

export default Analytics;

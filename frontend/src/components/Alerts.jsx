import React, { useState, useEffect } from 'react';

const AlertsPanel = ({ user }) => {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    if (!user) return;
    
    const ws = new WebSocket('ws://localhost:8000/ws');
    ws.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === 'alert') {
        setAlerts(prev => [data.data, ...prev].slice(0, 10)); // keep last 10
      }
    };
    return () => ws.close();
  }, [user]);

  return (
    <div className="space-y-3">
      {alerts.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-32 text-slate-500">
          <p className="text-sm">No alerts detected in system</p>
        </div>
      ) : (
        alerts.map((a, i) => (
          <div key={i} className="bg-red-950/40 border border-red-500/50 p-3 rounded-xl text-sm relative overflow-hidden group hover:bg-red-900/40 transition-colors">
            <div className="absolute left-0 top-0 bottom-0 w-1 bg-red-500"></div>
            <div className="flex justify-between items-start mb-1 ml-2">
              <strong className="text-red-400 font-mono tracking-tight text-base">{a.plate}</strong>
              <div className="text-xs text-slate-500 font-mono">{new Date(a.timestamp).toLocaleTimeString()}</div>
            </div>
            <div className="text-slate-300 ml-2">Location: {a.node_id}</div>
            <div className="text-slate-400 ml-2 mt-1 text-xs">{a.message}</div>
          </div>
        ))
      )}
    </div>
  );
};

export default AlertsPanel;

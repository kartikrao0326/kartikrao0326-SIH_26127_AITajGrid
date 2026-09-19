import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, Polyline, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

const FitBounds = ({ routes }) => {
  const map = useMap();
  useEffect(() => {
    if (routes && routes.length > 0) {
      const bounds = [];
      routes.forEach(route => {
        if (route.positions) {
          bounds.push(...route.positions);
        }
      });
      if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 });
      }
    }
  }, [routes, map]);
  return null;
};

// Fix leaflet icon issue in react
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Graph nodes (hardcoded based on backend)
const nodes = {
  "SEC1-N1": { lat: 28.6139, lon: 77.2090, name: "Sector 1 Entrance", cam: true },
  "SEC1-N2": { lat: 28.6150, lon: 77.2100, name: "Sector 1 Market", cam: true },
  "SEC2-N1": { lat: 28.6160, lon: 77.2080, name: "Sector 2 Junction", cam: false },
  "SEC2-N2": { lat: 28.6170, lon: 77.2110, name: "Sector 2 Hospital", cam: true },
  "SEC3-N1": { lat: 28.6180, lon: 77.2130, name: "Sector 3 Mall", cam: true },
  "SEC3-N2": { lat: 28.6190, lon: 77.2120, name: "Sector 3 Plaza", cam: false },
  "SEC4-N1": { lat: 28.6200, lon: 77.2150, name: "Sector 4 Park", cam: true },
  "SEC4-N2": { lat: 28.6210, lon: 77.2180, name: "Sector 4 Exit", cam: true },
};

const TrajMap = ({ liveEvent, searchedTrajectory, onClear }) => {
  const [pulses, setPulses] = useState([]);
  const [routes, setRoutes] = useState([]);

  useEffect(() => {
    if (liveEvent && liveEvent.node_id && nodes[liveEvent.node_id]) {
      const newPulse = { id: Date.now(), node_id: liveEvent.node_id, plate: liveEvent.plate };
      setPulses(p => [...p, newPulse]);
      // Remove pulse after 1 second
      setTimeout(() => {
        setPulses(p => p.filter(x => x.id !== newPulse.id));
      }, 1000);
    }
  }, [liveEvent]);

  useEffect(() => {
    const fetchRoutes = async () => {
      if (!searchedTrajectory || !searchedTrajectory.segments) {
        setRoutes([]);
        return;
      }
      
      const resolvedRoutes = await Promise.all(searchedTrajectory.segments.map(async (seg) => {
        const fromNode = nodes[seg.from_node];
        const toNode = nodes[seg.to_node];
        if (!fromNode || !toNode) return null;

        let positions = [[fromNode.lat, fromNode.lon], [toNode.lat, toNode.lon]];
        
        // Fetch road geometry from free public OSRM API
        try {
          const res = await fetch(`https://router.project-osrm.org/route/v1/driving/${fromNode.lon},${fromNode.lat};${toNode.lon},${toNode.lat}?overview=full&geometries=geojson`);
          const data = await res.json();
          if (data.routes && data.routes[0]) {
            positions = data.routes[0].geometry.coordinates.map(c => [c[1], c[0]]); // Convert [lon, lat] to [lat, lon]
          }
        } catch (e) {
          console.error("OSRM fetch failed, falling back to straight line");
        }

        let color = '#3b82f6'; // blue for clean
        let dashArray = '';
        if (seg.status === 'inferred') {
          color = '#f59e0b'; dashArray = '5, 5';
        } else if (seg.status === 'anomaly') {
          color = '#ef4444'; dashArray = '5, 10';
        }
        
        return { ...seg, positions, color, dashArray };
      }));
      
      setRoutes(resolvedRoutes.filter(r => r !== null));
    };

    fetchRoutes();
  }, [searchedTrajectory]);

  return (
    <div className="h-[600px] w-full rounded-2xl overflow-hidden relative border border-slate-700/50 shadow-2xl">
      {/* Floating Trajectory Card */}
      {searchedTrajectory && searchedTrajectory.segments && (
        <div className="absolute top-6 left-6 z-[1000] bg-slate-900/95 backdrop-blur-md border border-slate-700 p-5 rounded-2xl shadow-2xl text-slate-100 min-w-[340px]">
          <div className="flex items-center justify-between mb-5">
            <div className="flex items-center space-x-3">
              <span className="bg-slate-800/80 border border-cyan-500/30 px-3 py-1.5 rounded-lg text-sm font-mono font-bold text-cyan-400 shadow-inner">
                {searchedTrajectory.plate || 'UNKNOWN'}
              </span>
              <span className={`px-3 py-1.5 rounded-lg text-xs font-black tracking-wider border shadow-inner ${searchedTrajectory.segments.some(s => s.status === 'anomaly') ? 'bg-red-500/20 text-red-400 border-red-500/30' : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'}`}>
                {searchedTrajectory.segments.some(s => s.status === 'anomaly') ? 'ANOMALY DETECTED' : 'CLEAN STITCHED PATH'}
              </span>
            </div>
            <button onClick={onClear} className="text-xs bg-slate-800/80 hover:bg-slate-700 px-3 py-1.5 rounded-lg text-slate-300 border border-slate-600 transition-colors shadow-sm">
              Clear
            </button>
          </div>
          <div className="grid grid-cols-3 gap-4 text-left">
            <div>
              <div className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1.5">Total Nodes</div>
              <div className="font-bold text-lg tracking-tight">{searchedTrajectory.segments.length + 1} points</div>
            </div>
            <div>
              <div className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1.5">Status</div>
              <div className="font-bold text-lg text-cyan-400 tracking-tight">Tracked</div>
            </div>
            <div>
              <div className="text-[10px] text-slate-500 font-bold uppercase tracking-widest mb-1.5">Graph Conf</div>
              <div className="font-bold text-lg text-blue-400 tracking-tight">
                {Math.round((searchedTrajectory.segments.reduce((acc, s) => acc + s.to_confidence, 100) / (searchedTrajectory.segments.length + 1)))}%
              </div>
            </div>
          </div>
        </div>
      )}

      <MapContainer center={[28.6175, 77.2135]} zoom={15} style={{ height: '100%', width: '100%' }}>
        <FitBounds routes={routes} />
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        
        {Object.entries(nodes).map(([id, data]) => (
          <Marker key={id} position={[data.lat, data.lon]}>
            <Popup>{data.name} {data.cam ? "(Camera)" : "(No Camera)"}</Popup>
          </Marker>
        ))}

        {searchedTrajectory && searchedTrajectory.segments && (
          // Generate an ordered list of visited nodes
          searchedTrajectory.segments.reduce((acc, seg, i) => {
            if (i === 0) acc.push({ id: seg.from_node, time: seg.from_timestamp });
            acc.push({ id: seg.to_node, time: seg.to_timestamp });
            return acc;
          }, []).map((nodeData, idx) => {
            const n = nodes[nodeData.id];
            if (!n) return null;
            
            const numIcon = L.divIcon({
              className: 'clear-bg',
              html: `<div style="background-color: #3b82f6; color: white; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 2px solid white; box-shadow: 0 4px 6px rgba(0,0,0,0.3); font-size: 14px; margin-top: -12px; margin-left: -12px;">${idx + 1}</div>`,
              iconSize: [0, 0]
            });

            return (
              <Marker key={`seq-${idx}-${nodeData.id}`} position={[n.lat, n.lon]} icon={numIcon} zIndexOffset={1000}>
                <Popup>
                  <div className="font-sans">
                    <strong className="text-blue-600 block mb-1">Stop {idx + 1}: {n.name}</strong>
                    <div className="text-xs text-slate-600">
                      <strong>Time:</strong> {nodeData.time ? new Date(nodeData.time).toLocaleTimeString() : 'Unknown'}
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          })
        )}

        {routes.map((route, idx) => (
           <Polyline 
              key={idx}
              positions={route.positions}
              color={route.color}
              weight={4}
              dashArray={route.dashArray}
           >
              <Popup>
                 Status: {route.status} <br/>
                 Note: {route.note} <br/>
                 Conf: {route.from_confidence} -> {route.to_confidence}
              </Popup>
           </Polyline>
        ))}

        {pulses.map(pulse => {
          const node = nodes[pulse.node_id];
          return (
            <CircleMarker
              key={pulse.id}
              center={[node.lat, node.lon]}
              radius={20}
              pathOptions={{
                color: '#ef4444',
                fillColor: '#ef4444',
                fillOpacity: 0.6,
                className: 'animate-ping'
              }}
            >
              <Popup>Detected: {pulse.plate}</Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
};

export default TrajMap;

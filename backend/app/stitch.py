import networkx as nx
from datetime import datetime
from typing import List, Dict

try:
    from app.graph import ROAD_GRAPH
except ImportError:
    from graph import ROAD_GRAPH

def process_trajectory(events: List[Dict]) -> List[Dict]:
    """
    Takes a chronological list of events for a SINGLE plate.
    Returns a list of segment hops (status, note, from_event, to_event).
    """
    if len(events) < 2:
        return []
        
    segments = []
    
    for i in range(1, len(events)):
        prev = events[i-1]
        curr = events[i]
        
        t1 = datetime.fromisoformat(prev["timestamp"])
        t2 = datetime.fromisoformat(curr["timestamp"])
        dt_min = (t2 - t1).total_seconds() / 60.0
        
        u = prev["node_id"]
        v = curr["node_id"]
        
        segment = {
            "from_event": prev,
            "to_event": curr,
            "status": "clean",
            "note": None
        }
        
        if ROAD_GRAPH.has_edge(u, v):
            edge = ROAD_GRAPH.edges[u, v]
            if dt_min < edge['t_min_min']:
                segment["status"] = "anomaly"
                segment["note"] = f"Impossible speed (dt={dt_min:.1f}m < min={edge['t_min_min']:.1f}m)"
            elif dt_min > edge['t_max_min']:
                # Not really an anomaly, just a broken trip (vehicle parked).
                # The segment ends cleanly. We can just mark it as "clean" but disconnected,
                # but the schema says trajectory_segments has 'clean', 'inferred', 'anomaly'.
                # We can just return it as 'clean' but note it's a new trip? 
                # Actually, the instructions say:
                # "dt > edge.t_max -> close the current segment cleanly (vehicle parked / trip ended), start a new one."
                # So we just don't create a trajectory_segment link for this pair!
                continue
            else:
                segment["status"] = "clean"
                segment["note"] = f"Direct link (dt={dt_min:.1f}m)"
        else:
            # No direct edge
            try:
                path = nx.shortest_path(ROAD_GRAPH, u, v, weight='distance_km')
                total_t_min = 0
                total_t_max = 0
                for j in range(1, len(path)):
                    edge = ROAD_GRAPH.edges[path[j-1], path[j]]
                    total_t_min += edge['t_min_min']
                    total_t_max += edge['t_max_min']
                    
                if total_t_min <= dt_min <= total_t_max:
                    segment["status"] = "inferred"
                    segment["note"] = f"Inferred path via skipped nodes. (dt={dt_min:.1f}m)"
                elif dt_min < total_t_min:
                    segment["status"] = "anomaly"
                    segment["note"] = f"Impossible speed on inferred path (dt={dt_min:.1f}m < min={total_t_min:.1f}m)"
                else: # dt_min > total_t_max
                    # Broken trip
                    continue
            except nx.NetworkXNoPath:
                segment["status"] = "anomaly"
                segment["note"] = "No path exists in graph"
                
        segments.append(segment)
        
    return segments

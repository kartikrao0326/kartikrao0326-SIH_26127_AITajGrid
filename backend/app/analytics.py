import networkx as nx
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
import datetime
import statistics

from app.models import PlateEvent, TrajectorySegment, RoadNode, SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

try:
    from app.graph import ROAD_GRAPH
except ImportError:
    from graph import ROAD_GRAPH

router = APIRouter()

@router.get("/api/analytics/flow")
def get_junction_flow(db: Session = Depends(get_db)):
    """Count of plate_events per camera node per minute."""
    # SQLite doesn't have date_trunc, we can use strftime
    results = db.query(
        PlateEvent.node_id,
        func.strftime('%Y-%m-%d %H:%M:00', PlateEvent.timestamp).label('minute'),
        func.count(PlateEvent.id).label('count')
    ).group_by(
        PlateEvent.node_id,
        func.strftime('%Y-%m-%d %H:%M:00', PlateEvent.timestamp)
    ).all()
    
    flow = {}
    for r in results:
        node = r.node_id
        if node not in flow:
            flow[node] = []
        flow[node].append({"time": r.minute, "count": r.count})
        
    return flow

@router.get("/api/analytics/congestion")
def get_congestion(db: Session = Depends(get_db)):
    """Median travel time and congestion ratio per edge."""
    from sqlalchemy.orm import aliased
    FromEvent = aliased(PlateEvent)
    ToEvent = aliased(PlateEvent)
    
    segments = db.query(TrajectorySegment, FromEvent, ToEvent).join(
        FromEvent, TrajectorySegment.from_event_id == FromEvent.id
    ).join(
        ToEvent, TrajectorySegment.to_event_id == ToEvent.id
    ).filter(
        TrajectorySegment.status.in_(['clean', 'inferred'])
    ).all()
    
    edge_times = {}
    
    # We will compute shortest paths manually for inferred links
    for seg, from_ev, to_ev in segments:
        u = from_ev.node_id
        v = to_ev.node_id
        dt_min = (to_ev.timestamp - from_ev.timestamp).total_seconds() / 60.0
        
        try:
            path = nx.shortest_path(ROAD_GRAPH, u, v, weight='distance_km')
            # To distribute time, just assign the full dt to all edges in path for simplicity
            # Or better, distribute proportionally by distance.
            total_dist = sum(ROAD_GRAPH.edges[path[i-1], path[i]]['distance_km'] for i in range(1, len(path)))
            
            for i in range(1, len(path)):
                edge_u = path[i-1]
                edge_v = path[i]
                # Normalize edge direction
                if edge_u > edge_v:
                    edge_u, edge_v = edge_v, edge_u
                    
                edge = ROAD_GRAPH.edges[edge_u, edge_v]
                edge_dist = edge['distance_km']
                
                if total_dist > 0:
                    allocated_time = dt_min * (edge_dist / total_dist)
                    edge_id = f"{edge_u}_{edge_v}"
                    if edge_id not in edge_times:
                        edge_times[edge_id] = []
                    edge_times[edge_id].append(allocated_time)
        except nx.NetworkXNoPath:
            continue
            
    results = []
    
    for (u, v, data) in ROAD_GRAPH.edges(data=True):
        edge_u, edge_v = u, v
        if edge_u > edge_v:
            edge_u, edge_v = edge_v, edge_u
            
        edge_id = f"{edge_u}_{edge_v}"
        
        free_flow_time = (data['distance_km'] / data['speed_limit_kmh']) * 60.0
        
        if edge_id in edge_times and edge_times[edge_id]:
            median_time = statistics.median(edge_times[edge_id])
            ratio = median_time / free_flow_time
        else:
            median_time = free_flow_time
            ratio = 1.0
            
        results.append({
            "edge_id": edge_id,
            "source": u,
            "target": v,
            "median_time_min": round(median_time, 2),
            "free_flow_min": round(free_flow_time, 2),
            "ratio": round(ratio, 2),
            "is_congested": ratio > 1.4
        })
        
    return results

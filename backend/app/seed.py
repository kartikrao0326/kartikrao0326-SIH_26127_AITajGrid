import os
import sys

# Add parent directory to path so we can run as script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import Base, engine, SessionLocal, RoadNode, RoadEdge
from app.graph import ROAD_GRAPH

def reset_db():
    print("Dropping existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

def seed_graph(db):
    print("Seeding graph into DB...")
    
    # Insert nodes
    for node_id, data in ROAD_GRAPH.nodes(data=True):
        db_node = RoadNode(
            id=node_id,
            name=data['name'],
            lat=data['lat'],
            lon=data['lon'],
            has_camera=data['has_camera']
        )
        db.add(db_node)
    
    db.commit()
    
    # Insert edges
    for u, v, data in ROAD_GRAPH.edges(data=True):
        db_edge = RoadEdge(
            from_node=u,
            to_node=v,
            distance_km=data['distance_km'],
            speed_limit_kmh=data['speed_limit_kmh'],
            t_min_min=data['t_min_min'],
            t_max_min=data['t_max_min']
        )
        db.add(db_edge)
    
    db.commit()

if __name__ == "__main__":
    reset_db()
    
    db = SessionLocal()
    seed_graph(db)
    
    print("\n--- Checkpoint: Phase 1 ---")
    node_count = db.query(RoadNode).count()
    edge_count = db.query(RoadEdge).count()
    
    print(f"Graph from NetworkX: {ROAD_GRAPH.number_of_nodes()} nodes, {ROAD_GRAPH.number_of_edges()} edges.")
    print(f"Database contains: {node_count} nodes, {edge_count} edges.")
    
    if node_count == 8 and edge_count in range(10, 13):
        print("SUCCESS: Node and edge counts match expected values.")
    else:
        print("WARNING: Counts do not match expected values (8 nodes, ~10-12 edges).")
        
    db.close()

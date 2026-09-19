import networkx as nx
import random
import math

def build_graph():
    random.seed(42)
    G = nx.Graph()

    # 8 nodes: 6 with cameras, 2 camera-less
    nodes = [
        {"id": "SEC1-N1", "name": "Sector 1 Entrance", "lat": 28.6139, "lon": 77.2090, "has_camera": True},
        {"id": "SEC1-N2", "name": "Sector 1 Market", "lat": 28.6150, "lon": 77.2100, "has_camera": True},
        {"id": "SEC2-N1", "name": "Sector 2 Junction", "lat": 28.6160, "lon": 77.2080, "has_camera": False}, # Camera-less
        {"id": "SEC2-N2", "name": "Sector 2 Hospital", "lat": 28.6170, "lon": 77.2110, "has_camera": True},
        {"id": "SEC3-N1", "name": "Sector 3 Mall", "lat": 28.6180, "lon": 77.2130, "has_camera": True},
        {"id": "SEC3-N2", "name": "Sector 3 Plaza", "lat": 28.6190, "lon": 77.2120, "has_camera": False}, # Camera-less
        {"id": "SEC4-N1", "name": "Sector 4 Park", "lat": 28.6200, "lon": 77.2150, "has_camera": True},
        {"id": "SEC4-N2", "name": "Sector 4 Exit", "lat": 28.6210, "lon": 77.2180, "has_camera": True},
    ]

    for n in nodes:
        G.add_node(n["id"], **n)

    # 11 edges
    edges = [
        ("SEC1-N1", "SEC1-N2"),
        ("SEC1-N2", "SEC2-N1"),
        ("SEC2-N1", "SEC2-N2"),
        ("SEC1-N2", "SEC2-N2"),
        ("SEC2-N2", "SEC3-N1"),
        ("SEC3-N1", "SEC3-N2"),
        ("SEC3-N2", "SEC4-N1"),
        ("SEC3-N1", "SEC4-N1"),
        ("SEC4-N1", "SEC4-N2"),
        ("SEC2-N2", "SEC3-N2"),
        ("SEC1-N1", "SEC2-N1"),
    ]

    for u, v in edges:
        distance_km = random.uniform(1.0, 4.0)
        speed_limit_kmh = random.choice([40, 50, 60])
        # t_min_min = distance_km / (speed_limit_kmh * 1.4) * 60
        t_min_min = (distance_km / (speed_limit_kmh * 1.4)) * 60.0
        t_max_min = 45.0 # Flat generous cutoff

        G.add_edge(u, v, 
                   distance_km=distance_km, 
                   speed_limit_kmh=speed_limit_kmh, 
                   t_min_min=t_min_min, 
                   t_max_min=t_max_min)

    return G

ROAD_GRAPH = build_graph()

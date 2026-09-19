import random
import datetime
import string
import json
import networkx as nx
from typing import List, Dict

try:
    from app.graph import ROAD_GRAPH
except ImportError:
    from graph import ROAD_GRAPH

# Constants
PATTERN = r"^[A-Z]{2}[0-9]{1,2}[A-Z]{1,3}[0-9]{4}$"
LETTER_SLOT_CONFUSIONS = {'0':'O', '1':'I', '8':'B', '5':'S', '2':'Z', '6':'G'}
DIGIT_SLOT_CONFUSIONS  = {'O':'0', 'I':'1', 'B':'8', 'S':'5', 'Z':'2', 'G':'6'}

def generate_plate():
    # DL 9 C AA 1234
    state = "DL"
    district = str(random.randint(1, 14))
    letters = "".join(random.choices(string.ascii_uppercase, k=random.randint(1, 3)))
    numbers = f"{random.randint(1, 9999):04d}"
    return f"{state}{district}{letters}{numbers}"

def corrupt_plate(plate):
    plate_list = list(plate)
    
    # Try to corrupt up to 3 times to find a suitable character to corrupt
    for _ in range(3):
        idx = random.randint(0, len(plate_list) - 1)
        char = plate_list[idx]
        if char.isalpha() and char in DIGIT_SLOT_CONFUSIONS.values():
            # It's a letter, swap with a digit confusion if it matches one
            # Wait, the prompt says: "a digit slot only becomes another digit, a letter slot only becomes another letter"
            # Actually prompt says: "swapping one character using this confusion-pair map (apply in a slot-aware way — a digit slot only becomes another digit, a letter slot only becomes another letter)"
            # Let's read carefully: "confusion-pair map ... letter slot only becomes another letter". No wait.
            # LETTER_SLOT_CONFUSIONS = {'0':'O', '1':'I', '8':'B', '5':'S', '2':'Z', '6':'G'} 
            # This means if the slot SHOULD be a letter but the OCR saw a digit, it maps digit->letter.
            # So to simulate OCR corruption, if we have a letter 'O', the OCR output would be '0'.
            # If we have a digit '0', OCR output would be 'O'.
            # Let's map real char to confused char.
            inv_letter = {v: k for k, v in LETTER_SLOT_CONFUSIONS.items()} # e.g. 'O' -> '0'
            inv_digit = {v: k for k, v in DIGIT_SLOT_CONFUSIONS.items()}   # e.g. '0' -> 'O'
            
            if char in inv_letter:
                plate_list[idx] = inv_letter[char]
                return "".join(plate_list)
            elif char in inv_digit:
                plate_list[idx] = inv_digit[char]
                return "".join(plate_list)
                
    return plate

def generate_simulation_data(start_time: datetime.datetime):
    events = []
    vehicles = []
    watchlist_plates = []
    
    num_vehicles = 18
    
    nodes_list = list(ROAD_GRAPH.nodes)
    
    # Select special vehicles
    anomaly_vehicles = [generate_plate(), generate_plate()]
    watchlist_vehicle = generate_plate()
    duplicate_vehicles = [generate_plate(), generate_plate(), generate_plate()]
    
    all_plates = [generate_plate() for _ in range(num_vehicles - 3)] + anomaly_vehicles + [watchlist_vehicle]
    random.shuffle(all_plates)
    
    watchlist_plates.append({"plate": watchlist_vehicle, "reason": "Suspected stolen", "added_by": "admin", "added_at": (start_time - datetime.timedelta(days=1)).isoformat()})

    event_id_counter = 1
    
    for plate in all_plates:
        source, dest = random.sample(nodes_list, 2)
        try:
            path = nx.shortest_path(ROAD_GRAPH, source, dest, weight='distance_km')
        except nx.NetworkXNoPath:
            continue
            
        current_time = start_time + datetime.timedelta(seconds=random.randint(0, 300))
        
        # Determine if this is an anomaly vehicle
        is_anomaly = plate in anomaly_vehicles
        is_duplicate = plate in duplicate_vehicles
        
        vehicle_events = []
        
        for i, node in enumerate(path):
            node_data = ROAD_GRAPH.nodes[node]
            
            # Skip if camera-less, unless it's the anomaly jump logic which handles nodes differently
            
            if i > 0:
                prev_node = path[i-1]
                edge_data = ROAD_GRAPH.edges[prev_node, node]
                
                if is_anomaly and i == len(path) // 2:
                    # Impossible hop: advance time by 1 second instead of actual travel time
                    current_time += datetime.timedelta(seconds=1)
                else:
                    # Normal hop
                    speed = random.uniform(edge_data['speed_limit_kmh'] * 0.8, edge_data['speed_limit_kmh'] * 1.1)
                    travel_time_hours = edge_data['distance_km'] / speed
                    current_time += datetime.timedelta(hours=travel_time_hours)
            
            if node_data.get('has_camera'):
                # 8% drop rate
                if not is_anomaly and plate != watchlist_vehicle and random.random() < 0.08:
                    continue
                    
                # Corrupt
                confidence = round(random.uniform(0.85, 0.99), 2)
                read_plate = plate
                if random.random() < 0.10:
                    read_plate = corrupt_plate(plate)
                    if read_plate != plate:
                        confidence = round(random.uniform(0.40, 0.70), 2)
                        
                vehicle_events.append({
                    "id": event_id_counter,
                    "plate_raw": read_plate,
                    "node_id": node,
                    "timestamp": current_time.isoformat(),
                    "confidence": confidence,
                    "actual_plate_hidden": plate # For debugging
                })
                event_id_counter += 1
                
                # Deduplication simulation (multiple reads at same camera)
                if is_duplicate and random.random() < 0.5:
                    dup_time = current_time + datetime.timedelta(seconds=random.randint(1, 4))
                    vehicle_events.append({
                        "id": event_id_counter,
                        "plate_raw": read_plate,
                        "node_id": node,
                        "timestamp": dup_time.isoformat(),
                        "confidence": min(1.0, confidence + random.uniform(-0.1, 0.1)),
                        "actual_plate_hidden": plate
                    })
                    event_id_counter += 1
                    
        events.extend(vehicle_events)
        
    events.sort(key=lambda x: x["timestamp"])
    
    return {
        "events": events,
        "watchlist": watchlist_plates,
        "anomaly_vehicles": anomaly_vehicles,
        "watchlist_vehicle": watchlist_vehicle
    }

if __name__ == "__main__":
    start = datetime.datetime.now()
    data = generate_simulation_data(start)
    
    with open("simulation_dump.json", "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"Dumped {len(data['events'])} events to simulation_dump.json")
    print(f"Watchlist vehicle: {data['watchlist_vehicle']}")
    print(f"Forced anomaly vehicles: {data['anomaly_vehicles']}")
    
    # Checkpoint validations
    anomaly_reads = [e for e in data['events'] if e['actual_plate_hidden'] in data['anomaly_vehicles']]
    print(f"Generated {len(anomaly_reads)} reads for anomaly vehicles.")
    
    watchlist_reads = [e for e in data['events'] if e['actual_plate_hidden'] == data['watchlist_vehicle']]
    print(f"Generated {len(watchlist_reads)} reads for the watchlist vehicle.")

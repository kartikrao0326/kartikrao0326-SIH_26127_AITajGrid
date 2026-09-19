import json
from ingest import repair_plate, should_dedup
from stitch import process_trajectory

def run_checkpoint():
    with open("simulation_dump.json", "r") as f:
        data = json.load(f)
        
    raw_events = data["events"]
    anomaly_vehicles = data["anomaly_vehicles"]
    
    # 1. Ingest (Repair + Dedup)
    processed_events = []
    
    for event in raw_events:
        plate_raw = event["plate_raw"]
        repaired, was_repaired = repair_plate(plate_raw)
        
        if not repaired:
            continue
            
        event["plate_normalized"] = repaired
        event["was_repaired"] = was_repaired
        
        # Dedup check against the last event of the same plate
        # For a streaming system we'd check recent state, here we can just look backwards
        is_dup = False
        for prev in reversed(processed_events):
            if should_dedup(prev, event):
                # Duplicate! Keep highest confidence
                if event["confidence"] > prev["confidence"]:
                    prev["confidence"] = event["confidence"]
                    prev["plate_raw"] = event["plate_raw"]
                    prev["was_repaired"] = event["was_repaired"]
                is_dup = True
                break
        
        if not is_dup:
            processed_events.append(event)
            
    # Group by plate
    plate_to_events = {}
    for event in processed_events:
        plate_to_events.setdefault(event["plate_normalized"], []).append(event)
        
    print("\n--- Checkpoint: Phase 3 ---")
    
    # Print 1 clean vehicle and 1 anomaly vehicle
    printed_clean = False
    printed_anomaly = False
    
    for plate, evs in plate_to_events.items():
        segments = process_trajectory(evs)
        
        is_anomaly_vehicle = plate in anomaly_vehicles
        
        if is_anomaly_vehicle:
            print(f"\n[ANOMALY VEHICLE] Plate: {plate}")
            for seg in segments:
                print(f"  {seg['from_event']['node_id']} -> {seg['to_event']['node_id']} | Status: {seg['status']:<8} | {seg['note']}")
            
        elif not is_anomaly_vehicle and not printed_clean and len(segments) >= 2:
            print(f"\n[CLEAN VEHICLE] Plate: {plate}")
            for seg in segments:
                print(f"  {seg['from_event']['node_id']} -> {seg['to_event']['node_id']} | Status: {seg['status']:<8} | {seg['note']}")
            printed_clean = True

if __name__ == "__main__":
    run_checkpoint()

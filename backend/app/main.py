import asyncio
import json
import random
import datetime
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models import Base, engine, SessionLocal, PlateEvent, Vehicle, TrajectorySegment, Watchlist, Alert
from app.ws import manager
from app.ingest import repair_plate, should_dedup
from app.stitch import process_trajectory
from app.seed import reset_db, seed_graph
from app.simulate import generate_simulation_data
from app.analytics import router as analytics_router
from app.search import router as search_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="TrajGrid API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analytics_router)
app.include_router(search_router)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# In-memory flag to control simulation loop
sim_running = False

async def simulation_loop():
    global sim_running
    sim_running = True
    
    # Generate fresh data
    start = datetime.datetime.now()
    data = generate_simulation_data(start)
    events = data["events"]
    watchlist_plates = data["watchlist"]
    
    db = SessionLocal()
    
    # Pre-seed watchlist
    for w in watchlist_plates:
        existing = db.query(Watchlist).filter(Watchlist.plate == w["plate"]).first()
        if not existing:
            db.add(Watchlist(
                plate=w["plate"],
                reason=w["reason"],
                added_by=w["added_by"],
                added_at=datetime.datetime.fromisoformat(w["added_at"])
            ))
            db.commit()
    
    recent_events = [] # For dedup context
    
    for event_data in events:
        if not sim_running:
            break
            
        await asyncio.sleep(random.uniform(0.2, 0.8))
        
        plate_raw = event_data["plate_raw"]
        repaired, was_repaired = repair_plate(plate_raw)
        
        if not repaired:
            continue
            
        # Format for dedup
        event_dict = {
            "plate_normalized": repaired,
            "node_id": event_data["node_id"],
            "timestamp": event_data["timestamp"],
            "plate_raw": plate_raw,
            "confidence": event_data["confidence"],
            "was_repaired": was_repaired
        }
        
        is_dup = False
        for prev in reversed(recent_events):
            if should_dedup(prev, event_dict):
                is_dup = True
                break
                
        if is_dup:
            continue
            
        recent_events.append(event_dict)
        if len(recent_events) > 100:
            recent_events = recent_events[-100:]
            
        # Persist Event
        dt_timestamp = datetime.datetime.fromisoformat(event_dict["timestamp"])
        db_event = PlateEvent(
            plate_raw=event_dict["plate_raw"],
            plate_normalized=event_dict["plate_normalized"],
            node_id=event_dict["node_id"],
            timestamp=dt_timestamp,
            confidence=event_dict["confidence"],
            was_repaired=event_dict["was_repaired"]
        )
        db.add(db_event)
        db.commit()
        db.refresh(db_event)
        
        # Upsert Vehicle
        vehicle = db.query(Vehicle).filter(Vehicle.plate == event_dict["plate_normalized"]).first()
        if not vehicle:
            # Check if watchlisted
            is_wl = db.query(Watchlist).filter(Watchlist.plate == event_dict["plate_normalized"]).first() is not None
            vehicle = Vehicle(
                plate=event_dict["plate_normalized"],
                first_seen=dt_timestamp,
                last_seen=dt_timestamp,
                is_watchlisted=is_wl
            )
            db.add(vehicle)
        else:
            vehicle.last_seen = dt_timestamp
        db.commit()
        
        # Broadcast Plate Event
        await manager.broadcast({
            "type": "plate_event",
            "data": {
                "id": db_event.id,
                "plate": db_event.plate_normalized,
                "node_id": db_event.node_id,
                "timestamp": db_event.timestamp.isoformat()
            }
        })
        
        # Watchlist Check (Phase 5)
        if vehicle.is_watchlisted:
            alert_msg = f"Watchlist match for plate {vehicle.plate} at {db_event.node_id}"
            db_alert = Alert(
                plate=vehicle.plate,
                node_id=db_event.node_id,
                timestamp=dt_timestamp,
                message=alert_msg
            )
            db.add(db_alert)
            db.commit()
            
            await manager.broadcast({
                "type": "alert",
                "data": {
                    "plate": vehicle.plate,
                    "node_id": db_event.node_id,
                    "timestamp": dt_timestamp.isoformat(),
                    "message": alert_msg
                }
            })
            
        # Trigger Stitching
        plate_events = db.query(PlateEvent).filter(
            PlateEvent.plate_normalized == event_dict["plate_normalized"]
        ).order_by(PlateEvent.timestamp.asc()).all()
        
        # Convert to dict format for process_trajectory
        events_for_stitch = [
            {
                "id": e.id,
                "plate_normalized": e.plate_normalized,
                "node_id": e.node_id,
                "timestamp": e.timestamp.isoformat()
            } for e in plate_events
        ]
        
        segments = process_trajectory(events_for_stitch)
        
        # Clear old segments for this plate
        db.query(TrajectorySegment).filter(TrajectorySegment.plate == event_dict["plate_normalized"]).delete()
        
        # Insert new segments
        for seg in segments:
            db.add(TrajectorySegment(
                plate=event_dict["plate_normalized"],
                from_event_id=seg["from_event"]["id"],
                to_event_id=seg["to_event"]["id"],
                status=seg["status"],
                note=seg["note"]
            ))
        db.commit()
        
        if segments:
            await manager.broadcast({
                "type": "trajectory_update",
                "data": {
                    "plate": event_dict["plate_normalized"],
                    "segments": [
                        {
                            "from_node": seg["from_event"]["node_id"],
                            "to_node": seg["to_event"]["node_id"],
                            "status": seg["status"]
                        } for seg in segments
                    ]
                }
            })
            
    db.close()
    sim_running = False

@app.post("/api/seed")
async def seed_and_start(background_tasks: BackgroundTasks):
    global sim_running
    sim_running = False
    
    db = SessionLocal()
    reset_db()
    seed_graph(db)
    db.close()
    
    # Give it a moment to stop any running loop, then start
    background_tasks.add_task(simulation_loop)
    return {"status": "ok", "message": "Database reset, simulation started"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# HTML test page for checkpoint 4
html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WS Test</title>
    </head>
    <body>
        <h1>WebSocket Test</h1>
        <button onclick="seedAndStart()">Start Simulation</button>
        <ul id='messages'>
        </ul>
        <script>
            var ws = new WebSocket("ws://localhost:8000/ws");
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages');
                var message = document.createElement('li');
                var content = document.createTextNode(event.data);
                message.appendChild(content);
                messages.appendChild(message);
                
                // Keep only last 20
                if (messages.childNodes.length > 20) {
                    messages.removeChild(messages.childNodes[0]);
                }
            };
            
            function seedAndStart() {
                fetch('/api/seed', {method: 'POST'});
            }
        </script>
    </body>
</html>
"""

@app.get("/test_ws")
async def get():
    return HTMLResponse(html)

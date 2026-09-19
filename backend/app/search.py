from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import datetime

from app.models import TrajectorySegment, AuditLog, PlateEvent, SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

class SearchRequest(BaseModel):
    plate: str
    reason: str
    user: str

@router.post("/api/search")
def search_trajectory(req: SearchRequest, db: Session = Depends(get_db)):
    if not req.reason.strip():
        raise HTTPException(status_code=400, detail="Reason/case reference is required.")
        
    # Log to audit_log
    audit_entry = AuditLog(
        user=req.user,
        plate_queried=req.plate,
        reason_given=req.reason,
        timestamp=datetime.datetime.now()
    )
    db.add(audit_entry)
    db.commit()
    
    # Fetch trajectory
    segments = db.query(TrajectorySegment).filter(
        TrajectorySegment.plate == req.plate
    ).all()
    
    result = []
    for seg in segments:
        from_ev = db.query(PlateEvent).get(seg.from_event_id)
        to_ev = db.query(PlateEvent).get(seg.to_event_id)
        
        result.append({
            "from_node": from_ev.node_id,
            "to_node": to_ev.node_id,
            "status": seg.status,
            "note": seg.note,
            "from_confidence": from_ev.confidence,
            "to_confidence": to_ev.confidence,
            "from_timestamp": from_ev.timestamp.isoformat() if from_ev.timestamp else None,
            "to_timestamp": to_ev.timestamp.isoformat() if to_ev.timestamp else None
        })
        
    return {"plate": req.plate, "segments": result}

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)  # 'Operator' or 'Admin'

class RoadNode(Base):
    __tablename__ = 'road_nodes'
    id = Column(String, primary_key=True, index=True) # e.g. SEC17-N1
    name = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    has_camera = Column(Boolean)

class RoadEdge(Base):
    __tablename__ = 'road_edges'
    from_node = Column(String, ForeignKey('road_nodes.id'), primary_key=True)
    to_node = Column(String, ForeignKey('road_nodes.id'), primary_key=True)
    distance_km = Column(Float)
    speed_limit_kmh = Column(Float)
    t_min_min = Column(Float)
    t_max_min = Column(Float)

class PlateEvent(Base):
    __tablename__ = 'plate_events'
    id = Column(Integer, primary_key=True, index=True)
    plate_raw = Column(String)
    plate_normalized = Column(String, index=True)
    node_id = Column(String, ForeignKey('road_nodes.id'))
    timestamp = Column(DateTime, index=True)
    confidence = Column(Float)
    was_repaired = Column(Boolean)

class Vehicle(Base):
    __tablename__ = 'vehicles'
    plate = Column(String, primary_key=True, index=True)
    first_seen = Column(DateTime)
    last_seen = Column(DateTime)
    is_watchlisted = Column(Boolean, default=False)

class TrajectorySegment(Base):
    __tablename__ = 'trajectory_segments'
    id = Column(Integer, primary_key=True, index=True)
    plate = Column(String, index=True)
    from_event_id = Column(Integer, ForeignKey('plate_events.id'))
    to_event_id = Column(Integer, ForeignKey('plate_events.id'))
    status = Column(String) # 'clean', 'inferred', 'anomaly'
    note = Column(String, nullable=True)

class Watchlist(Base):
    __tablename__ = 'watchlist'
    plate = Column(String, primary_key=True, index=True)
    reason = Column(String)
    added_by = Column(String)
    added_at = Column(DateTime)

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True, index=True)
    plate = Column(String, index=True)
    node_id = Column(String, ForeignKey('road_nodes.id'))
    timestamp = Column(DateTime)
    message = Column(String)

class AuditLog(Base):
    __tablename__ = 'audit_log'
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String)
    plate_queried = Column(String)
    reason_given = Column(String)
    timestamp = Column(DateTime)

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./trajgrid.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from __future__ import annotations

import os
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, create_engine, desc, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./forestguard.db")
API_KEY = os.getenv("FORESTGUARD_API_KEY", "CAMBIA_ESTA_CLAVE_LOCAL")
OFFLINE_AFTER_MINUTES = max(1, int(os.getenv("OFFLINE_AFTER_MINUTES", "15")))

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String(60), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    location_note: Mapped[str] = mapped_column(String(250), default="")
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    battery_v: Mapped[float | None] = mapped_column(Float, nullable=True)
    current_state: Mapped[str] = mapped_column(String(20), default="unknown", nullable=False)


class Reading(Base):
    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    node_id: Mapped[str] = mapped_column(ForeignKey("devices.id"), index=True, nullable=False)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    temperature_c: Mapped[float | None] = mapped_column(Float, nullable=True)
    humidity_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    smoke_raw: Mapped[int | None] = mapped_column(Integer, nullable=True)
    battery_v: Mapped[float | None] = mapped_column(Float, nullable=True)
    alert_level: Mapped[str] = mapped_column(String(20), nullable=False)
    packet_seq: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rssi_dbm: Mapped[int | None] = mapped_column(Integer, nullable=True)
    snr_db: Mapped[float | None] = mapped_column(Float, nullable=True)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    node_id: Mapped[str] = mapped_column(ForeignKey("devices.id"), index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    level: Mapped[str] = mapped_column(String(20), nullable=False)
    message: Mapped[str] = mapped_column(String(300), nullable=False)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="ForestGuard API",
    version="0.2.0",
    description="API del prototipo académico ForestGuard. No es un sistema certificado de emergencia.",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def require_gateway_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")):
    if not x_api_key or not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(status_code=401, detail="API key inválida o ausente")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    # SQLite puede devolver datetime sin zona aunque el modelo declare timezone=True.
    return value.replace(tzinfo=timezone.utc) if value.tzinfo is None else value.astimezone(timezone.utc)


class TelemetryIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    node_id: str = Field(min_length=1, max_length=60)
    temperature_c: float | None = Field(default=None, ge=-40, le=85)
    humidity_pct: float | None = Field(default=None, ge=0, le=100)
    smoke_raw: int | None = Field(default=None, ge=0, le=65535)
    battery_v: float | None = Field(default=None, ge=0, le=20)
    alert_level: Literal["normal", "prealert", "alert"] = "normal"
    packet_seq: int | None = Field(default=None, ge=0)
    rssi_dbm: int | None = None
    snr_db: float | None = None


@app.get("/api/health")
def health(db: Session = Depends(get_db)):
    db.execute(select(Device.id).limit(1)).all()
    return {"status": "ok", "database": "connected", "api_version": "0.2.0"}


@app.post("/api/telemetry", dependencies=[Depends(require_gateway_key)])
def receive_telemetry(payload: TelemetryIn, db: Session = Depends(get_db)):
    device = db.get(Device, payload.node_id)
    if device is None:
        raise HTTPException(status_code=404, detail=f"Nodo no registrado: {payload.node_id}")

    now = utc_now()
    previous_state = device.current_state
    device.last_seen = now
    device.current_state = payload.alert_level
    if payload.battery_v is not None:
        device.battery_v = payload.battery_v

    db.add(Reading(
        node_id=payload.node_id,
        received_at=now,
        temperature_c=payload.temperature_c,
        humidity_pct=payload.humidity_pct,
        smoke_raw=payload.smoke_raw,
        battery_v=payload.battery_v,
        alert_level=payload.alert_level,
        packet_seq=payload.packet_seq,
        rssi_dbm=payload.rssi_dbm,
        snr_db=payload.snr_db,
    ))

    # Una alerta se crea al entrar a prealert/alert, no por cada paquete repetido.
    if payload.alert_level in ("prealert", "alert") and payload.alert_level != previous_state:
        message = (
            "Posible incendio: requiere verificación humana"
            if payload.alert_level == "alert"
            else "Condiciones ambientales clasificadas como prealerta"
        )
        db.add(Alert(node_id=payload.node_id, created_at=now, level=payload.alert_level, message=message))

    db.commit()
    return {
        "received": True,
        "node_id": payload.node_id,
        "received_at": now.isoformat(),
        "state": payload.alert_level,
    }


@app.get("/api/devices")
def get_devices(db: Session = Depends(get_db)):
    now = utc_now()
    devices = db.scalars(select(Device).order_by(Device.id)).all()
    result = []
    for device in devices:
        last_seen = as_utc(device.last_seen)
        online = bool(last_seen and now - last_seen <= timedelta(minutes=OFFLINE_AFTER_MINUTES))
        result.append({
            "id": device.id,
            "name": device.name,
            "latitude": device.latitude,
            "longitude": device.longitude,
            "location_note": device.location_note,
            "last_seen": last_seen.isoformat() if last_seen else None,
            "online": online,
            "battery_v": device.battery_v,
            "alert_level": device.current_state,
        })
    return result


@app.get("/api/overview")
def overview(db: Session = Depends(get_db)):
    devices = get_devices(db)
    alerts = db.scalars(select(Alert).where(Alert.acknowledged.is_(False))).all()
    return {
        "total_nodes": len(devices),
        "online_nodes": sum(1 for d in devices if d["online"]),
        "offline_nodes": sum(1 for d in devices if not d["online"]),
        "prealerts": sum(1 for d in devices if d["alert_level"] == "prealert"),
        "alerts": sum(1 for a in alerts if a.level == "alert"),
        "unacknowledged_alerts": len(alerts),
        "updated_at": utc_now().isoformat(),
    }


@app.get("/api/alerts")
def get_alerts(limit: int = Query(default=25, ge=1, le=100), db: Session = Depends(get_db)):
    rows = db.scalars(select(Alert).order_by(desc(Alert.created_at)).limit(limit)).all()
    return [{
        "id": a.id,
        "node_id": a.node_id,
        "created_at": as_utc(a.created_at).isoformat(),
        "level": a.level,
        "message": a.message,
        "acknowledged": a.acknowledged,
    } for a in rows]


@app.post("/api/alerts/{alert_id}/ack")
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.get(Alert, alert_id)
    if alert is None:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    alert.acknowledged = True
    db.commit()
    return {"updated": True, "id": alert_id}


@app.get("/api/readings")
def get_readings(
    node_id: str | None = None,
    limit: int = Query(default=30, ge=1, le=200),
    db: Session = Depends(get_db),
):
    stmt = select(Reading).order_by(desc(Reading.received_at)).limit(limit)
    if node_id:
        stmt = select(Reading).where(Reading.node_id == node_id).order_by(desc(Reading.received_at)).limit(limit)
    rows = db.scalars(stmt).all()
    return [{
        "id": r.id,
        "node_id": r.node_id,
        "received_at": as_utc(r.received_at).isoformat(),
        "temperature_c": r.temperature_c,
        "humidity_pct": r.humidity_pct,
        "smoke_raw": r.smoke_raw,
        "battery_v": r.battery_v,
        "alert_level": r.alert_level,
        "packet_seq": r.packet_seq,
        "rssi_dbm": r.rssi_dbm,
        "snr_db": r.snr_db,
    } for r in rows]


app.mount("/", StaticFiles(directory=str(BASE_DIR / "static"), html=True), name="static")

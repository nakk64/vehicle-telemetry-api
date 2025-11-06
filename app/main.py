from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, Float
from sqlalchemy.exc import SQLAlchemyError
import os

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:pass@db:5432/telemetry")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
metadata = MetaData()

telemetry = Table(
    "telemetry", metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("car_id", String(50), nullable=False),
    Column("speed", Float),
    Column("temperature", Float),
    Column("latitude", Float),
    Column("longitude", Float)
)

metadata.create_all(engine)

app = FastAPI(title="Vehicle Telemetry API")

class TelemetryIn(BaseModel):
    car_id: str
    speed: float | None = None
    temperature: float | None = None
    latitude: float | None = None
    longitude: float | None = None

@app.post("/vehicle")
def ingest(data: TelemetryIn):
    try:
        with engine.begin() as conn:
            conn.execute(telemetry.insert().values(
                car_id=data.car_id,
                speed=data.speed,
                temperature=data.temperature,
                latitude=data.latitude,
                longitude=data.longitude
            ))
        return {"status": "received"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from bson import ObjectId

class GeoLocation(BaseModel):
    type: str = "Point"
    coordinates: List[float]  # [longitude, latitude] - MongoDB format

class Device(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    device_id: str = Field(..., unique=True)
    name: str
    type: str  # sensorNode, camera, gateway
    status: str  # safe, warning, alert
    location: GeoLocation
    description: Optional[str] = None
    voltage: Optional[float] = None
    last_heartbeat: datetime
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class DeviceCreate(BaseModel):
    device_id: str
    name: str
    type: str
    latitude: float
    longitude: float
    description: Optional[str] = None

class DeviceUpdate(BaseModel):
    status: Optional[str] = None
    voltage: Optional[float] = None
    description: Optional[str] = None

class Alert(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    device_id: str
    type: str
    message: str
    severity: str
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    created_at: datetime

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
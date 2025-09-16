from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from . import PyObjectId
class ImageRecord(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    image_id: str = Field(..., unique=True)
    device_id: str
    filename: str
    status: str  # legal, illegal, unreviewed
    notes: Optional[str] = None
    captured_at: datetime
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class ImageUpdate(BaseModel):
    status: str
    notes: Optional[str] = None

class ImageFilter(BaseModel):
    status: Optional[str] = None
    device_id: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
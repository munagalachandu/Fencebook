from typing import List, Optional
from datetime import datetime, timedelta
from database import get_database
from models.devices import Device, DeviceCreate, DeviceUpdate, Alert, GeoLocation
from bson import ObjectId
import random

async def get_all_devices() -> List[Device]:
    db = get_database()
    devices_cursor = db.devices.find()
    devices = await devices_cursor.to_list(length=None)
    return [Device(**device) for device in devices]

async def get_device(device_id: str) -> Optional[Device]:
    db = get_database()
    device_doc = await db.devices.find_one({"device_id": device_id})
    if device_doc:
        return Device(**device_doc)
    return None

async def create_device(device: DeviceCreate) -> Device:
    db = get_database()
    device_doc = {
        "device_id": device.device_id,
        "name": device.name,
        "type": device.type,
        "status": "safe",
        "location": {
            "type": "Point",
            "coordinates": [device.longitude, device.latitude]  # MongoDB uses [lng, lat]
        },
        "description": device.description,
        "voltage": 3.25,  # Default voltage
        "last_heartbeat": datetime.utcnow(),
        "created_at": datetime.utcnow()
    }
    result = await db.devices.insert_one(device_doc)
    device_doc["_id"] = result.inserted_id
    return Device(**device_doc)

async def update_device(device_id: str, update: DeviceUpdate) -> Optional[Device]:
    db = get_database()
    update_data = {}
    if update.status:
        update_data["status"] = update.status
    if update.voltage is not None:
        update_data["voltage"] = update.voltage
    if update.description:
        update_data["description"] = update.description
    
    update_data["last_heartbeat"] = datetime.utcnow()
    
    await db.devices.update_one({"device_id": device_id}, {"$set": update_data})
    return await get_device(device_id)

async def get_recent_alerts(limit: int = 10) -> List[Alert]:
    db = get_database()
    alerts_cursor = db.alerts.find().sort("created_at", -1).limit(limit)
    alerts = await alerts_cursor.to_list(length=limit)
    return [Alert(**alert) for alert in alerts]

async def create_alert(device_id: str, alert_type: str, message: str, severity: str) -> Alert:
    db = get_database()
    alert_doc = {
        "device_id": device_id,
        "type": alert_type,
        "message": message,
        "severity": severity,
        "acknowledged": False,
        "created_at": datetime.utcnow()
    }
    result = await db.alerts.insert_one(alert_doc)
    alert_doc["_id"] = result.inserted_id
    return Alert(**alert_doc)

async def get_devices_in_radius(longitude: float, latitude: float, radius_meters: float) -> List[Device]:
    """Get devices within a specified radius using MongoDB geospatial queries"""
    db = get_database()
    devices_cursor = db.devices.find({
        "location": {
            "$near": {
                "$geometry": {"type": "Point", "coordinates": [longitude, latitude]},
                "$maxDistance": radius_meters
            }
        }
    })
    devices = await devices_cursor.to_list(length=None)
    return [Device(**device) for device in devices]

# Mock data generation for demo
async def generate_mock_data():
    db = get_database()
    # Check if devices already exist
    existing = await db.devices.find_one()
    if existing:
        return
    
    # Create default user if not exists
    existing_user = await db.users.find_one({"username": "operator"})
    if not existing_user:
        user_doc = {
            "username": "operator",
            "hashed_password": get_password_hash("password"),
            "role": "Operator",
            "created_at": datetime.utcnow()
        }
        await db.users.insert_one(user_doc)
    
    # Create mock devices
    mock_devices = [
        {"device_id": "MAG-001-A", "name": "Magnetometer Unit 1", "type": "sensorNode", "lat": 51.505, "lng": -0.09},
        {"device_id": "CAM-002-B", "name": "Security Camera 2", "type": "camera", "lat": 51.506, "lng": -0.08},
        {"device_id": "GW-003-C", "name": "Gateway Node 3", "type": "gateway", "lat": 51.504, "lng": -0.10},
        {"device_id": "MAG-004-D", "name": "Perimeter Sensor 4", "type": "sensorNode", "lat": 51.507, "lng": -0.09},
        {"device_id": "CAM-005-E", "name": "Entrance Camera 5", "type": "camera", "lat": 51.503, "lng": -0.11},
    ]
    
    for device_data in mock_devices:
        device = DeviceCreate(
            device_id=device_data["device_id"],
            name=device_data["name"],
            type=device_data["type"],
            latitude=device_data["lat"],
            longitude=device_data["lng"],
            description=f"Monitoring device located at perimeter zone"
        )
        await create_device(device)
    
    # Create sample images
    mock_images = [
        {
            "image_id": "img-001",
            "device_id": "CAM-002-B",
            "filename": "capture_20240726_1030.jpg",
            "status": "illegal",
            "captured_at": datetime.fromisoformat("2024-07-26T10:30:00"),
            "notes": None
        },
        {
            "image_id": "img-002", 
            "device_id": "CAM-005-E",
            "filename": "capture_20240726_0915.jpg",
            "status": "legal",
            "captured_at": datetime.fromisoformat("2024-07-26T09:15:00"),
            "notes": "Regular patrol activity"
        },
        {
            "image_id": "img-003",
            "device_id": "CAM-002-B", 
            "filename": "capture_20240725_1600.jpg",
            "status": "unreviewed",
            "captured_at": datetime.fromisoformat("2024-07-25T16:00:00"),
            "notes": None
        }
    ]
    
    await db.images.insert_many(mock_images)
    
    # Create a sample alert
    await create_alert(
        "MAG-001-A",
        "voltage_spike",
        "Unexpected voltage spike detected in Magnetometer Unit 1. Review system logs immediately.",
        "critical"
    )

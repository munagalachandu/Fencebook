from fastapi import APIRouter, Depends
from typing import List
from models.auth import User
from models.devices import Device, Alert
from services.device_service import get_all_devices, get_recent_alerts, generate_mock_data
from routes.auth import get_current_user
import random
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/init")
async def initialize_dashboard():
    """Initialize dashboard with mock data"""
    await generate_mock_data()
    return {"message": "Dashboard initialized with mock data"}

@router.get("/overview")
async def get_dashboard_overview(current_user: User = Depends(get_current_user)):
    devices = await get_all_devices()
    alerts = await get_recent_alerts(5)
    
    # Generate mock magnetometer readings
    voltage_data = []
    base_time = datetime.utcnow() - timedelta(hours=1)
    for i in range(60):  # Last hour, minute by minute
        voltage_data.append({
            "timestamp": (base_time + timedelta(minutes=i)).isoformat(),
            "voltage": round(3.25 + random.uniform(-0.1, 0.1), 3)
        })
    
    # System status summary
    device_status_counts = {"safe": 0, "warning": 0, "alert": 0}
    for device in devices:
        device_status_counts[device.status] += 1
    
    return {
        "summary": {
            "total_devices": len(devices),
            "magnetometer_voltage": round(3.25 + random.uniform(-0.05, 0.05), 3),
            "perimeter_status": "Safe",
            "system_heartbeat": "Online",
            "device_status_counts": device_status_counts
        },
        "voltage_trend": voltage_data,
        "recent_alerts": alerts,
        "system_status": [
            {
                "device_id": "MAG-001-A",
                "name": "Magnetometer Unit 1",
                "status": "Online",
                "last_update": "2 minutes ago"
            }
        ]
    }

@router.get("/devices", response_model=List[Device])
async def get_devices(current_user: User = Depends(get_current_user)):
    return await get_all_devices()

@router.get("/alerts", response_model=List[Alert])
async def get_alerts(current_user: User = Depends(get_current_user)):
    return await get_recent_alerts()
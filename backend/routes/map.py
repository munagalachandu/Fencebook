from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from models.auth import User
from models.devices import Device
from services.device_service import get_all_devices, get_devices_in_radius
from routes.auth import get_current_user

router = APIRouter()

@router.get("/devices")
async def get_map_devices(current_user: User = Depends(get_current_user)):
    """Get all devices for map display"""
    devices = await get_all_devices()
    
    # Format for map component
    map_pins = []
    for device in devices:
        # Extract coordinates from GeoJSON format
        longitude, latitude = device.location.coordinates
        map_pins.append({
            "id": device.device_id,
            "position": [latitude, longitude],  # Frontend expects [lat, lng]
            "status": device.status,
            "type": device.type,
            "name": device.name,
            "description": device.description
        })
    
    return {"pins": map_pins}

@router.get("/devices/nearby")
async def get_nearby_devices(
    longitude: float,
    latitude: float, 
    radius: float = 1000,  # meters
    current_user: User = Depends(get_current_user)
):
    """Get devices within specified radius"""
    devices = await get_devices_in_radius(longitude, latitude, radius)
    
    map_pins = []
    for device in devices:
        longitude, latitude = device.location.coordinates
        map_pins.append({
            "id": device.device_id,
            "position": [latitude, longitude],
            "status": device.status,
            "type": device.type,
            "name": device.name,
            "description": device.description
        })
    
    return {"pins": map_pins}

@router.get("/overlays") 
async def get_map_overlays(current_user: User = Depends(get_current_user)):
    """Get map overlays for zones and alerts"""
    overlays = [
        {
            "type": "tampering",
            "bounds": [[51.504, -0.11], [51.506, -0.09]], 
            "label": "Tampering Detection Zone Alpha"
        },
        {
            "type": "illegal",
            "bounds": [[51.507, -0.08], [51.508, -0.07]],
            "label": "Illegal Activity Alert - Sector B" 
        }
    ]
    
    return {"overlays": overlays}

@router.get("/filters")
async def get_available_filters(current_user: User = Depends(get_current_user)):
    """Get available filter options"""
    return {
        "status_filters": ["safe", "warning", "alert"],
        "type_filters": ["sensorNode", "camera", "gateway"]
    }

@router.post("/filters")
async def apply_map_filters(
    filters: Dict[str, bool],
    current_user: User = Depends(get_current_user)
):
    """Apply filters and return filtered devices"""
    devices = await get_all_devices()
    
    filtered_pins = []
    for device in devices:
        # Check if device matches active filters
        if filters.get(device.status, False) and filters.get(device.type, False):
            longitude, latitude = device.location.coordinates
            filtered_pins.append({
                "id": device.device_id,
                "position": [latitude, longitude],
                "status": device.status,
                "type": device.type,
                "name": device.name,
                "description": device.description
            })
    
    return {"pins": filtered_pins}
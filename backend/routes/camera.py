from fastapi import APIRouter, Depends, HTTPException
from typing import List
from models.auth import User
from models.images import ImageRecord, ImageUpdate, ImageFilter
from routes.auth import get_current_user
from database import get_database
from datetime import datetime

router = APIRouter()

@router.get("/live-feed")
async def get_live_feed(current_user: User = Depends(get_current_user)):
    """Get current live feed status"""
    return {
        "stream_url": "/api/camera/stream",
        "status": "live",
        "camera_id": "CAM-002-B",
        "resolution": "1920x1080",
        "fps": 30
    }

@router.get("/images")
async def get_images(
    status: str = None,
    device_id: str = None,
    current_user: User = Depends(get_current_user)
):
    """Get filtered images from gallery"""
    db = get_database()
    filter_query = {}
    
    if status:
        filter_query["status"] = status
    if device_id:
        filter_query["device_id"] = device_id
    
    images_cursor = db.images.find(filter_query).sort("captured_at", -1)
    images = await images_cursor.to_list(length=None)
    
    # Convert MongoDB documents to the expected format
    formatted_images = []
    for img in images:
        formatted_images.append({
            "id": img.get("image_id"),
            "device_id": img.get("device_id"),
            "filename": img.get("filename"),
            "status": img.get("status"),
            "timestamp": img.get("captured_at").strftime("%Y-%m-%d %I:%M %p") if img.get("captured_at") else None,
            "notes": img.get("notes")
        })
    
    return formatted_images

@router.put("/images/{image_id}/tag")
async def tag_image(
    image_id: str,
    update: ImageUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update image status and notes"""
    db = get_database()
    update_data = {
        "status": update.status,
        "notes": update.notes,
        "reviewed_by": current_user.username,
        "reviewed_at": datetime.utcnow()
    }
    
    result = await db.images.update_one(
        {"image_id": image_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Get updated image
    updated_image = await db.images.find_one({"image_id": image_id})
    return {"message": "Image tagged successfully", "image": updated_image}

@router.post("/images/{image_id}/notes")
async def save_image_notes(
    image_id: str,
    notes: str,
    current_user: User = Depends(get_current_user)
):
    """Save notes for an image"""
    db = get_database()
    update_data = {
        "notes": notes,
        "reviewed_by": current_user.username,
        "reviewed_at": datetime.utcnow()
    }
    
    result = await db.images.update_one(
        {"image_id": image_id},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Image not found")
    
    return {"message": "Notes saved successfully"}

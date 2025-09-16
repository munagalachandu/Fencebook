from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from routes import auth, dashboard, camera
from routes import map as map_routes
from database import connect_to_mongo, close_mongo_connection

app = FastAPI(
    title="SentinelGuard API",
    description="Military perimeter monitoring system API with MongoDB",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React/Vite dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for images/assets
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(camera.router, prefix="/api/camera", tags=["Camera"])
app.include_router(map_routes.router, prefix="/api/map", tags=["Map"])

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

@app.get("/")
async def root():
    return {"message": "SentinelGuard API v1.0.0 with MongoDB"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "sentinelguard-api", "database": "mongodb"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ServerSelectionTimeoutError
import logging


# MongoDB configuration
MONGODB_URL = "mongodb://localhost:27017"
DATABASE_NAME = "sentinelguard"

# Global variables
mongodb_client: AsyncIOMotorClient = None
mongodb: object = None

async def connect_to_mongo():
    """Create database connection"""
    global mongodb_client, mongodb
    try:
        mongodb_client = AsyncIOMotorClient('mongodb+srv://sih:sih123@cluster0.ga6g9fv.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
        mongodb = mongodb_client['sih1']
        
        # Test the connection
        await mongodb_client.admin.command('ping')
        print(f"Successfully connected to MongoDB at {MONGODB_URL}")
        
        # Create indexes
        await create_indexes()
        
    except ServerSelectionTimeoutError:
        print("Failed to connect to MongoDB. Please ensure MongoDB is running.")
        raise

async def close_mongo_connection():
    """Close database connection"""
    global mongodb_client
    if mongodb_client:
        mongodb_client.close()
        print("Disconnected from MongoDB")

async def create_indexes():
    """Create database indexes for better performance"""
    global mongodb
    
    # Users collection indexes
    await mongodb.users.create_index("username", unique=True)
    
    # Devices collection indexes
    await mongodb.devices.create_index("device_id", unique=True)
    await mongodb.devices.create_index("type")
    await mongodb.devices.create_index("status")
    await mongodb.devices.create_index([("location", "2dsphere")])  # Geospatial index
    
    # Images collection indexes
    await mongodb.images.create_index("device_id")
    await mongodb.images.create_index("status")
    await mongodb.images.create_index("captured_at")
    
    # Alerts collection indexes
    await mongodb.alerts.create_index("device_id")
    await mongodb.alerts.create_index("created_at")
    await mongodb.alerts.create_index("severity")

def get_database():
    return mongodb
from fastapi import FastAPI, APIRouter
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List
import uuid
from datetime import datetime

# Import route modules
from budget_routes import router as budget_router
from meal_routes import router as meal_router
from database import init_default_categories, close_database

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', '')
db_name = os.environ.get('DB_NAME', 'budget_db')

if not mongo_url:
    print("WARNING: MONGO_URL environment variable not set!")
    client = None
    db = None
else:
    try:
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        print(f"Connected to MongoDB database: {db_name}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        client = None
        db = None

# Create the main app without a prefix
app = FastAPI(title="Budget Planner API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Health check routes
@api_router.get("/")
async def root():
    return {"message": "Budget Planner API is running!"}

@api_router.get("/health")
async def health_check():
    db_status = "connected" if db is not None else "disconnected"
    return {
        "status": "healthy" if db is not None else "degraded",
        "timestamp": datetime.utcnow(),
        "database": db_status
    }

# Include route modules
app.include_router(budget_router)
app.include_router(meal_router)

# Include the main API router
app.include_router(api_router)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Budget Planner API...")
    await init_default_categories()
    logger.info("Default categories initialized")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Budget Planner API...")
    await close_database()
    logger.info("Database connection closed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
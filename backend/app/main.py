from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import os

from app.core.config import settings
from app.api.v1.router import api_router
from app.db.session import engine
from app.db.base import Base
from app.background_tasks import background_tasks_runner
from app.cache import cache

# Global task reference
background_task = None

# Check if background tasks should run (disabled in multi-worker mode)
ENABLE_BACKGROUND_TASKS = os.getenv("ENABLE_BACKGROUND_TASKS", "true").lower() == "true"

@asynccontextmanager
async def lifespan(app: FastAPI):
    global background_task
    
    # Startup: Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Connect to Redis
    await cache.connect()
    
    # Start background tasks only if enabled (disabled in multi-worker production)
    if ENABLE_BACKGROUND_TASKS:
        print("🔄 Starting background tasks in this worker")
        background_task = asyncio.create_task(background_tasks_runner())
    else:
        print("⏭️  Background tasks disabled (run separately with run_background_tasks.py)")
    
    yield
    
    # Shutdown: Cancel background tasks and cleanup
    if background_task:
        background_task.cancel()
        try:
            await background_task
        except asyncio.CancelledError:
            pass
    
    # Disconnect Redis
    await cache.disconnect()
    
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for ParkingSpots - A parking space rental marketplace",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {
        "message": "Welcome to ParkingSpots API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

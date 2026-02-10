"""Initialize database tables."""
import asyncio
from app.db.session import engine
from app.db.base import Base

# Import all models so they're registered with Base
from app.models.user import User
from app.models.parking_spot import ParkingSpot
from app.models.booking import Booking
from app.models.payment import Payment
from app.models.review import Review

async def init_db():
    """Create all database tables."""
    async with engine.begin() as conn:
        # Drop all tables (for development)
#        await conn.run_sync(Base.metadata.drop_all)
        
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("✓ Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())

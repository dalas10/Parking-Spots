"""Initialize database tables."""
import asyncio
from sqlalchemy import text
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

        # Enable btree_gist and add exclusion constraint to prevent
        # double-booking the same slot concurrently (idempotent)
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist"))
        await conn.execute(text("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_constraint
                    WHERE conname = 'no_overlapping_bookings'
                ) THEN
                    ALTER TABLE bookings
                    ADD CONSTRAINT no_overlapping_bookings
                    EXCLUDE USING gist (
                        parking_spot_id WITH =,
                        tstzrange(start_time, end_time, '[)') WITH &&
                    ) WHERE (status IN ('PENDING', 'CONFIRMED', 'IN_PROGRESS'));
                END IF;
            END $$;
        """))
    
    print("✓ Database tables created successfully!")
    print("✓ Exclusion constraint for concurrent booking protection applied!")

if __name__ == "__main__":
    asyncio.run(init_db())

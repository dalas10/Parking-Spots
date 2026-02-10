"""Background tasks for automatic booking status updates."""
import asyncio
import logging
from datetime import datetime, timezone
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal
from app.models.booking import Booking, BookingStatus
from app.models.parking_spot import ParkingSpot
from app.models.user import User  # Import User to resolve SQLAlchemy mapper relationships
from app.models.review import Review  # Import Review to resolve all relationships

logger = logging.getLogger(__name__)


async def auto_checkout_expired_bookings():
    """Automatically checkout bookings that have passed their end time."""
    try:
        async with AsyncSessionLocal() as db:
            # Find bookings that are IN_PROGRESS or CONFIRMED but past their end time
            now = datetime.now(timezone.utc)
            result = await db.execute(
                select(Booking).where(
                    and_(
                        Booking.status.in_([BookingStatus.IN_PROGRESS, BookingStatus.CONFIRMED]),
                        Booking.end_time <= now
                    )
                )
            )
            expired_bookings = result.scalars().all()
            
            if expired_bookings:
                logger.info(f"Found {len(expired_bookings)} expired bookings to auto-checkout")
                
                for booking in expired_bookings:
                    # Auto-checkout
                    booking.status = BookingStatus.COMPLETED
                    booking.checked_out_at = now
                    
                    # Update parking spot stats
                    spot_result = await db.execute(
                        select(ParkingSpot).where(ParkingSpot.id == booking.parking_spot_id)
                    )
                    spot = spot_result.scalar_one_or_none()
                    if spot:
                        spot.total_bookings += 1
                    
                    logger.info(f"Auto-checkout booking {booking.id}")
                
                await db.commit()
                logger.info(f"Successfully auto-checkout {len(expired_bookings)} bookings")
            
    except Exception as e:
        logger.error(f"Error in auto_checkout_expired_bookings: {e}")


async def auto_start_bookings():
    """Automatically start bookings that have reached their start time."""
    try:
        async with AsyncSessionLocal() as db:
            # Find CONFIRMED bookings that have reached their start time
            now = datetime.now(timezone.utc)
            result = await db.execute(
                select(Booking).where(
                    and_(
                        Booking.status == BookingStatus.CONFIRMED,
                        Booking.start_time <= now,
                        Booking.end_time > now
                    )
                )
            )
            starting_bookings = result.scalars().all()
            
            if starting_bookings:
                logger.info(f"Found {len(starting_bookings)} bookings to auto-start")
                
                for booking in starting_bookings:
                    # Auto-start (check-in)
                    booking.status = BookingStatus.IN_PROGRESS
                    booking.checked_in_at = now
                    logger.info(f"Auto-start booking {booking.id}")
                
                await db.commit()
                logger.info(f"Successfully auto-started {len(starting_bookings)} bookings")
            
    except Exception as e:
        logger.error(f"Error in auto_start_bookings: {e}")


async def background_tasks_runner():
    """Run background tasks periodically."""
    logger.info("Starting background tasks runner...")
    
    while True:
        try:
            # Run auto-start every minute
            await auto_start_bookings()
            
            # Run auto-checkout every minute
            await auto_checkout_expired_bookings()
            
            # Wait 60 seconds before next run
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Error in background tasks runner: {e}")
            # Wait a bit before retrying
            await asyncio.sleep(60)

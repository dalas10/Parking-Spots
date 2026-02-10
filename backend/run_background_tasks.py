"""Standalone background tasks runner for production multi-worker setup."""
import asyncio
import signal
import sys

from app.db.session import AsyncSessionLocal
from app.background_tasks import background_tasks_runner
from app.cache import cache

# Global flag for graceful shutdown
shutdown_event = asyncio.Event()

def signal_handler(signum, frame):
    """Handle shutdown signals."""
    print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
    shutdown_event.set()

async def main():
    """Run background tasks continuously."""
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🔄 Starting background tasks worker...")
    print("   - Auto-checkout expired bookings")
    print("   - Auto-start confirmed bookings")
    
    # Connect to Redis
    await cache.connect()
    
    try:
        # Run background tasks until shutdown signal
        task = asyncio.create_task(background_tasks_runner())
        
        # Wait for shutdown signal
        await shutdown_event.wait()
        
        # Cancel background task
        print("   Canceling background tasks...")
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        
    finally:
        # Disconnect Redis
        await cache.disconnect()
        print("✅ Background tasks worker stopped")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n✅ Background tasks worker stopped")
        sys.exit(0)

"""Redis caching utilities for the application."""
import json
import hashlib
from typing import Optional, Any, Callable
from functools import wraps
import redis.asyncio as redis
from app.core.config import settings

class RedisCache:
    """Redis cache manager."""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = True
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                db=0,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            # Test connection
            await self.redis_client.ping()
            print("✓ Redis connected successfully")
        except Exception as e:
            print(f"⚠ Redis connection failed: {e}. Caching disabled.")
            self.enabled = False
            self.redis_client = None
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            print("✓ Redis disconnected")
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if not self.enabled or not self.redis_client:
            return None
        try:
            return await self.redis_client.get(key)
        except Exception as e:
            print(f"Redis GET error: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: int = 300) -> bool:
        """Set value in cache with TTL (default 5 minutes)."""
        if not self.enabled or not self.redis_client:
            return False
        try:
            await self.redis_client.setex(key, ttl, value)
            return True
        except Exception as e:
            print(f"Redis SET error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.enabled or not self.redis_client:
            return False
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            print(f"Redis DELETE error: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern."""
        if not self.enabled or not self.redis_client:
            return 0
        try:
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            print(f"Redis DELETE_PATTERN error: {e}")
            return 0
    
    def generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from prefix and parameters."""
        # Sort kwargs for consistent keys
        params = sorted(kwargs.items())
        params_str = json.dumps(params, sort_keys=True, default=str)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()[:12]
        return f"{prefix}:{params_hash}"


# Global cache instance
cache = RedisCache()


def cached(prefix: str, ttl: int = 300):
    """
    Decorator to cache function results.
    
    Args:
        prefix: Cache key prefix
        ttl: Time to live in seconds (default 5 minutes)
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function arguments
            cache_key = cache.generate_cache_key(prefix, **kwargs)
            
            # Try to get from cache
            cached_value = await cache.get(cache_key)
            if cached_value:
                try:
                    return json.loads(cached_value)
                except json.JSONDecodeError:
                    pass
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache the result
            try:
                await cache.set(cache_key, json.dumps(result, default=str), ttl=ttl)
            except Exception as e:
                print(f"Cache serialization error: {e}")
            
            return result
        return wrapper
    return decorator


async def invalidate_spot_cache(spot_id: str):
    """Invalidate cache for a specific parking spot."""
    await cache.delete(f"spot:{spot_id}")
    # Also invalidate search results that might contain this spot
    await cache.delete_pattern("search:*")


async def invalidate_search_cache():
    """Invalidate all search result caches."""
    deleted = await cache.delete_pattern("search:*")
    if deleted > 0:
        print(f"✓ Invalidated {deleted} search cache entries")

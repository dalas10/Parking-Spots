"""
Concurrent booking conflict test:
10 users attempt to book the exact same spot for the same time simultaneously.
"""
import asyncio
import aiohttp
import time
import json

BASE = "http://localhost:8000/api/v1"
OWNER_EMAIL   = "owner@zakynthos.gr"
RENTER_EMAIL  = "renter@zakynthos.gr"
PASSWORD      = "Test1234"

async def get_token(session, email, password):
    async with session.post(f"{BASE}/auth/login",
                            json={"email": email, "password": password}) as r:
        d = await r.json()
        return d.get("access_token")

async def get_first_spot(session):
    async with session.get(f"{BASE}/parking-spots/?limit=1") as r:
        data = await r.json()
        spots = data if isinstance(data, list) else data.get("spots", data)
        return spots[0]["id"], spots[0]["title"]

async def try_book(session, token, spot_id, start, end, user_id):
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "parking_spot_id": spot_id,
        "start_time": start,
        "end_time":   end,
        "vehicle_plate": f"TEST-{user_id:03d}",
    }
    t0 = time.perf_counter()
    async with session.post(f"{BASE}/bookings/", json=payload, headers=headers) as r:
        ms   = (time.perf_counter() - t0) * 1000
        ct = r.headers.get("content-type", "")
        if "json" in ct:
            body = await r.json()
        else:
            text = await r.text()
            body = {"detail": text[:200]}
        return user_id, r.status, ms, body

async def main():
    print("\n=== CONCURRENT BOOKING CONFLICT TEST ===\n")

    async with aiohttp.ClientSession() as session:
        # -- Get spot info
        spot_id, spot_title = await get_first_spot(session)
        print(f"Target spot   : {spot_title}")
        print(f"Spot ID       : {spot_id}")

        # (no cleanup needed — unique time window chosen below)

        # -- Time window: 21 days from now, 10:00-12:00 (clean slot for each test run)
        from datetime import datetime, timezone, timedelta
        target_day = datetime.now(timezone.utc) + timedelta(days=21)
        start = target_day.replace(hour=10, minute=0, second=0, microsecond=0).isoformat()
        end   = target_day.replace(hour=12, minute=0, second=0, microsecond=0).isoformat()
        print(f"Time window   : {start[:16]} → {end[:16]} UTC")
        print(f"Concurrent    : 10 users\n")

        # -- Get 10 tokens (all same renter account — simulates same user in
        #    race; or different users — the conflict rule applies regardless)
        print("Obtaining tokens for 10 users...")
        tokens = await asyncio.gather(*[
            get_token(session, RENTER_EMAIL, PASSWORD) for _ in range(10)
        ])
        print(f"Tokens ready  : {sum(1 for t in tokens if t)}/10\n")

        # -- Fire all 10 booking attempts simultaneously
        print("Firing 10 simultaneous booking requests...")
        t_wall = time.perf_counter()
        results = await asyncio.gather(*[
            try_book(session, tokens[i], spot_id, start, end, i + 1)
            for i in range(10)
        ])
        wall_ms = (time.perf_counter() - t_wall) * 1000

        # -- Analyse
        successes = [(uid, ms, body) for uid, status, ms, body in results if status in (200, 201)]
        conflicts = [(uid, ms, body) for uid, status, ms, body in results if status == 409]
        errors    = [(uid, status, ms, body) for uid, status, ms, body in results
                     if status not in (200, 201, 409)]

        print(f"\n{'─'*50}")
        print(f"{'User':>5}  {'HTTP':>4}  {'ms':>8}  Outcome")
        print(f"{'─'*5}  {'─'*4}  {'─'*8}  {'─'*30}")
        for uid, status, ms, body in sorted(results, key=lambda x: x[0]):
            if status in (200, 201):
                tag = f"✅ BOOKED  (id={str(body.get('id','?'))[:8]})"
            elif status == 409:
                tag = f"❌ CONFLICT  ({body.get('detail','spot not available')[:40]})"
            else:
                tag = f"⚠️  ERROR {status}  ({str(body)[:40]})"
            print(f"{uid:>5}  {status:>4}  {ms:>7.1f}ms  {tag}")

        print(f"{'─'*50}")
        print(f"\nWall time     : {wall_ms:.0f}ms")
        print(f"Succeeded     : {len(successes)}")
        print(f"Conflicts     : {len(conflicts)}")
        print(f"Errors        : {len(errors)}")
        print(f"\nResult        : {'✅ CORRECT — exactly 1 booking created' if len(successes)==1 else '❌ PROBLEM — ' + str(len(successes)) + ' bookings created!'}")

        return results, wall_ms, spot_title, spot_id, start, end

if __name__ == "__main__":
    asyncio.run(main())

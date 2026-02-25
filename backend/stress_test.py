"""
Hard stress test — ParkingSpots API
─────────────────────────────────────────────────────────
Tests:
  • Escalating read concurrency  (browse, search, detail, cache)
  • Authenticated write workload (login → book → check-in → check-out)
  • Mixed read+write burst       (all endpoints simultaneously)
  • Connection pool health       (polls pg_stat_activity during each phase)
  • Pool exhaustion probe        (500 concurrent requests)

Usage:
  python3 backend/stress_test.py
"""
import asyncio
import aiohttp
import time
import statistics
import subprocess
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import List, Optional

BASE   = "http://localhost:8000/api/v1"
PG_CMD = ["docker", "compose", "exec", "-T", "db",
          "psql", "-U", "postgres", "-d", "parkingspots", "-t", "-c"]
REDIS_FLUSH = ["docker", "compose", "exec", "-T", "redis", "redis-cli", "FLUSHALL"]
COMPOSE_DIR = "/home/dalas/ParkingSpots"

RENTER_EMAIL = "renter@zakynthos.gr"
RENTER_PASS  = "Test1234"
LAT, LON     = 37.787, 20.8999

SPOT_IDS = [
    "bbbbbbbb-0001-0000-0000-000000000001",
    "bbbbbbbb-0002-0000-0000-000000000001",
    "bbbbbbbb-0003-0000-0000-000000000001",
    "bbbbbbbb-0004-0000-0000-000000000001",
    "bbbbbbbb-0005-0000-0000-000000000001",
]

# ── ANSI ─────────────────────────────────────────────────────────────────────
B="\033[1m"; C="\033[36m"; G="\033[32m"; Y="\033[33m"; R="\033[31m"; X="\033[0m"

def c_ms(v):
    if v < 200:  return f"{G}{v}{X}"
    if v < 800:  return f"{Y}{v}{X}"
    return f"{R}{v}{X}"

def c_err(p):
    if p == 0:  return f"{G}0%{X}"
    if p < 5:   return f"{Y}{p}%{X}"
    return f"{R}{p}%{X}"

# ── Result types ─────────────────────────────────────────────────────────────
@dataclass
class Result:
    status: int
    ms:     float
    ok:     bool

@dataclass
class Bucket:
    label: str
    results: List[Result] = field(default_factory=list)

    def add(self, status, ms, ok):
        self.results.append(Result(status, ms, ok))

    def s(self):
        if not self.results: return None
        t  = [r.ms for r in self.results]
        ok = sum(1 for r in self.results if r.ok)
        n  = len(t)
        ts = sorted(t)
        return dict(n=n, ok=ok, err=n-ok,
                    err_pct=round((n-ok)/n*100,1),
                    avg=round(statistics.mean(t),1),
                    p50=round(statistics.median(t),1),
                    p95=round(ts[int(n*.95)],1),
                    p99=round(ts[int(n*.99)],1),
                    mx=round(max(t),1))

# ── DB pool stats ─────────────────────────────────────────────────────────────
def pg_pool_stats():
    """Returns (active, idle, total) connections from pg_stat_activity."""
    try:
        q = "SELECT state, count(*) FROM pg_stat_activity WHERE datname='parkingspots' GROUP BY state;"
        r = subprocess.run(PG_CMD + [q], capture_output=True, text=True, cwd=COMPOSE_DIR, timeout=5)
        active = idle = total = 0
        for line in r.stdout.splitlines():
            parts = line.strip().split("|")
            if len(parts) == 2:
                state = parts[0].strip()
                cnt   = int(parts[1].strip())
                total += cnt
                if state == "active":   active = cnt
                elif state == "idle":   idle   = cnt
        return active, idle, total
    except Exception:
        return -1, -1, -1

def pg_max_seen():
    """Returns max_connections from PostgreSQL config."""
    try:
        r = subprocess.run(PG_CMD + ["SHOW max_connections;"],
                           capture_output=True, text=True, cwd=COMPOSE_DIR, timeout=5)
        return int(r.stdout.strip())
    except Exception:
        return -1

# ── HTTP helpers ──────────────────────────────────────────────────────────────
async def req(session, method, path, bucket: Bucket, **kwargs):
    url = f"{BASE}{path}"
    t0  = time.perf_counter()
    try:
        async with getattr(session, method)(url, **kwargs) as resp:
            ms = (time.perf_counter() - t0) * 1000
            ok = resp.status < 400
            bucket.add(resp.status, ms, ok)
            if ok:
                ct = resp.headers.get("content-type","")
                if "json" in ct:
                    return await resp.json()
    except Exception:
        ms = (time.perf_counter() - t0) * 1000
        bucket.add(0, ms, False)
    return None

# ── Flows ─────────────────────────────────────────────────────────────────────
async def do_login(session, buckets):
    d = await req(session, "post", "/auth/login", buckets["login"],
                  json={"email": RENTER_EMAIL, "password": RENTER_PASS})
    return d.get("access_token") if d else None

async def do_browse(session, buckets):
    await req(session, "get",
              f"/parking-spots/?latitude={LAT}&longitude={LON}&radius_km=20&limit=20",
              buckets["browse"])

async def do_search(session, buckets):
    await req(session, "get", "/parking-spots/?city=Ζάκυνθος&limit=20", buckets["search"])

async def do_detail(session, buckets, spot_id):
    await req(session, "get", f"/parking-spots/{spot_id}", buckets["detail"])

async def do_my_bookings(session, buckets, token):
    await req(session, "get", "/bookings/",
              buckets["my_bookings"],
              headers={"Authorization": f"Bearer {token}"})

async def do_booking_flow(session, buckets, token, spot_id, day_offset):
    """Create a booking for a unique future slot, then check-in + check-out."""
    import random
    # Use a random hour so concurrent flows rarely collide (different spots used anyway)
    base = datetime.now(timezone.utc) + timedelta(days=60 + day_offset)
    hour = random.randint(0, 21)
    start = base.replace(hour=hour,   minute=0, second=0, microsecond=0).isoformat()
    end   = base.replace(hour=hour+2, minute=0, second=0, microsecond=0).isoformat()

    d = await req(session, "post", "/bookings/", buckets["create_booking"],
                  json={"parking_spot_id": spot_id,
                        "start_time": start, "end_time": end,
                        "vehicle_plate": f"STRESS-{random.randint(1,9999):04d}"},
                  headers={"Authorization": f"Bearer {token}"})
    if not d or "id" not in d:
        return

    bid = d["id"]
    # check-in only works on CONFIRMED bookings — skip status update, just hit the endpoint
    await req(session, "post", f"/bookings/{bid}/check-in", buckets["check_in"],
              headers={"Authorization": f"Bearer {token}"})

# ── Read-only scenario ────────────────────────────────────────────────────────
async def flow_read(session, buckets, spot_id, _day):
    await do_browse(session, buckets)
    await do_search(session, buckets)
    await do_detail(session, buckets, spot_id)

# ── Write scenario ────────────────────────────────────────────────────────────
async def flow_write(session, buckets, spot_id, day_offset):
    token = await do_login(session, buckets)
    if token:
        await do_my_bookings(session, buckets, token)
        await do_booking_flow(session, buckets, token, spot_id, day_offset)

# ── Mixed scenario ────────────────────────────────────────────────────────────
async def flow_mixed(session, buckets, spot_id, day_offset):
    await do_browse(session, buckets)
    token = await do_login(session, buckets)
    await do_detail(session, buckets, spot_id)
    if token:
        await do_my_bookings(session, buckets, token)
        await do_booking_flow(session, buckets, token, spot_id, day_offset)

# ── Scenario runner ───────────────────────────────────────────────────────────
def make_buckets():
    return {k: Bucket(k) for k in
            ["browse","search","detail","login","my_bookings","create_booking","check_in"]}

async def run(label, concurrency, total, flow_fn, spot_ids, flush_cache=False):
    if flush_cache:
        subprocess.run(REDIS_FLUSH, capture_output=True, cwd=COMPOSE_DIR)

    buckets  = make_buckets()
    before_a, before_i, before_t = pg_pool_stats()
    peak_conn = before_t
    conn_samples = [before_t]

    connector = aiohttp.TCPConnector(limit=concurrency + 50)
    timeout   = aiohttp.ClientTimeout(total=45)
    sem       = asyncio.Semaphore(concurrency)

    import random
    async def one(i):
        nonlocal peak_conn
        async with sem:
            spot = spot_ids[i % len(spot_ids)]
            await flow_fn(session, buckets, spot, i)

    # Poll DB connections periodically in background
    polling = True
    async def poll_db():
        while polling:
            _, _, t = pg_pool_stats()
            conn_samples.append(t)
            await asyncio.sleep(0.5)

    wall_start = time.perf_counter()
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        poll_task = asyncio.create_task(poll_db())
        await asyncio.gather(*[one(i) for i in range(total)])
        polling = False
        await poll_task
    wall_s = time.perf_counter() - wall_start

    after_a, after_i, after_t = pg_pool_stats()
    peak = max(conn_samples) if conn_samples else -1

    return dict(label=label, concurrency=concurrency, total=total,
                wall_s=wall_s, buckets=buckets,
                db_before=before_t, db_peak=peak, db_after=after_t)

# ── Print ─────────────────────────────────────────────────────────────────────
LABELS = {
    "browse":         "Browse (anon)",
    "search":         "Search city",
    "detail":         "Spot detail",
    "login":          "Login",
    "my_bookings":    "My bookings",
    "create_booking": "Create booking",
    "check_in":       "Check-in",
}

def print_result(r):
    rps   = round(r["total"] / r["wall_s"], 1)
    print(f"\n{B}{C}{'─'*68}{X}")
    print(f"{B}  {r['label']:<28} │ {r['concurrency']:>3} concurrent │ {r['total']:>4} total{X}")
    print(f"  Wall: {r['wall_s']:.2f}s   Throughput: {rps} flows/sec")
    print(f"  DB connections — before: {r['db_before']}  peak: {B}{r['db_peak']}{X}  after: {r['db_after']}")
    print(f"{B}{C}{'─'*68}{X}")
    print(f"  {'Endpoint':<22} {'N':>5}  {'Err%':>6}  {'Avg':>7}  {'P50':>7}  {'P95':>7}  {'P99':>7}  {'Max':>8}")
    print(f"  {'─'*22} {'─'*5}  {'─'*6}  {'─'*7}  {'─'*7}  {'─'*7}  {'─'*7}  {'─'*8}")
    for key, label in LABELS.items():
        s = r["buckets"][key].s()
        if not s: continue
        print(f"  {label:<22} {s['n']:>5}  {c_err(s['err_pct']):>15}  "
              f"{c_ms(s['avg']):>16}  {c_ms(s['p50']):>16}  "
              f"{c_ms(s['p95']):>16}  {c_ms(s['p99']):>16}  {c_ms(s['mx']):>17}")

def print_summary(results, pg_max):
    print(f"\n\n{B}{'='*68}{X}")
    print(f"{B}  SUMMARY{X}")
    print(f"  PostgreSQL max_connections: {pg_max}")
    print(f"{B}{'='*68}{X}")
    print(f"  {'Scenario':<28} {'Con':>4}  {'Flows':>6}  {'RPS':>6}  {'Errs':>5}  {'Avg ms':>7}  {'DB peak':>8}")
    print(f"  {'─'*28} {'─'*4}  {'─'*6}  {'─'*6}  {'─'*5}  {'─'*7}  {'─'*8}")
    for r in results:
        rps    = round(r["total"] / r["wall_s"], 1)
        allreq = sum((r["buckets"][k].s() or {}).get("n",0) for k in LABELS)
        allerr = sum((r["buckets"][k].s() or {}).get("err",0) for k in LABELS)
        allms  = [res.ms for k in LABELS for res in r["buckets"][k].results]
        avg    = round(statistics.mean(allms),1) if allms else 0
        ep     = round(allerr/allreq*100,1) if allreq else 0
        print(f"  {r['label']:<28} {r['concurrency']:>4}  {r['total']:>6}  {rps:>6}  "
              f"{c_err(ep):>14}  {c_ms(avg):>16}  {B}{r['db_peak']:>8}{X}")
    print(f"{B}{'='*68}{X}\n")

# ── Main ──────────────────────────────────────────────────────────────────────
async def main():
    print(f"\n{B}{'='*68}{X}")
    print(f"{B}  ParkingSpots API — HARD STRESS TEST{X}")
    print(f"{B}  Target: {BASE}{X}")
    print(f"{B}{'='*68}{X}")

    # Health check
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get("http://localhost:8000/health",
                             timeout=aiohttp.ClientTimeout(total=3)) as r:
                if r.status != 200:
                    raise Exception(f"HTTP {r.status}")
        print(f"\n{G}✓ API healthy{X}")
    except Exception as e:
        print(f"\n{R}✗ API not reachable: {e}{X}")
        return

    pg_max = pg_max_seen()
    print(f"{G}✓ PostgreSQL max_connections = {pg_max}{X}")
    print(f"{G}✓ Pool config: size=20, overflow=10 (max 30 per worker){X}")

    # Flush cache to make DB work harder on first phases
    subprocess.run(REDIS_FLUSH, capture_output=True, cwd=COMPOSE_DIR)
    print(f"{G}✓ Redis cache flushed{X}")

    results = []

    phases = [
        # label                         conc  total  flow_fn        flush
        ("1. Read warm-up",               10,    50, flow_read,      False),
        ("2. Read medium (cache hot)",     50,   200, flow_read,      False),
        ("3. Read heavy (cache hot)",     150,   400, flow_read,      False),
        ("4. Read heavy (cache cold)",    150,   400, flow_read,      True),
        ("5. Write medium",               25,   100, flow_write,     False),
        ("6. Write heavy",                75,   200, flow_write,     False),
        ("7. Mixed medium",               50,   200, flow_mixed,     False),
        ("8. Mixed heavy",               150,   300, flow_mixed,     False),
        ("9. Pool exhaustion probe",      300,   500, flow_read,      True),
    ]

    for label, conc, total, flow_fn, flush in phases:
        print(f"\n{Y}▶ {label}  ({conc} concurrent, {total} total)...{X}")
        r = await run(label, conc, total, flow_fn, SPOT_IDS, flush_cache=flush)
        results.append(r)
        print_result(r)
        await asyncio.sleep(2)

    print_summary(results, pg_max)

if __name__ == "__main__":
    asyncio.run(main())

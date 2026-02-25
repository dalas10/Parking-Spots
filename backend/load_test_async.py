"""
Async load test for ParkingSpots API
Tests realistic user flows at escalating concurrency levels
Usage: python load_test_async.py
"""
import asyncio
import aiohttp
import time
import statistics
import json
from dataclasses import dataclass, field
from typing import List, Optional

BASE = "http://localhost:8000/api/v1"

# Test credentials
RENTER_EMAIL = "renter@zakynthos.gr"
RENTER_PASS  = "Test1234"

# Zakynthos coords
LAT, LON = 37.787, 20.8999

# ── Result bucket ────────────────────────────────────────────────────────────

@dataclass
class Result:
    name: str
    status: int
    ms: float
    ok: bool

@dataclass
class Stats:
    name: str
    results: List[Result] = field(default_factory=list)

    def add(self, r: Result):
        self.results.append(r)

    def summary(self):
        if not self.results:
            return {}
        times   = [r.ms for r in self.results]
        ok      = sum(1 for r in self.results if r.ok)
        total   = len(self.results)
        return {
            "total":    total,
            "ok":       ok,
            "errors":   total - ok,
            "err_pct":  round((total - ok) / total * 100, 1),
            "min_ms":   round(min(times), 1),
            "max_ms":   round(max(times), 1),
            "avg_ms":   round(statistics.mean(times), 1),
            "p50_ms":   round(statistics.median(times), 1),
            "p95_ms":   round(sorted(times)[int(len(times) * 0.95)], 1),
            "p99_ms":   round(sorted(times)[int(len(times) * 0.99)], 1),
        }

# ── Individual requests ──────────────────────────────────────────────────────

async def req(session, method, path, stats_obj: Stats, **kwargs) -> Optional[dict]:
    url = f"{BASE}{path}"
    start = time.perf_counter()
    try:
        async with getattr(session, method)(url, **kwargs) as resp:
            ms = (time.perf_counter() - start) * 1000
            ok = resp.status < 400
            stats_obj.add(Result(path, resp.status, ms, ok))
            if ok:
                return await resp.json()
    except Exception as e:
        ms = (time.perf_counter() - start) * 1000
        stats_obj.add(Result(path, 0, ms, False))
    return None

# ── User flows ────────────────────────────────────────────────────────────────

async def flow_browse(session: aiohttp.ClientSession, stats: dict):
    """Anonymous user browses nearby spots"""
    await req(session, "get", f"/parking-spots/?latitude={LAT}&longitude={LON}&radius_km=20&limit=10",
              stats["browse"])

async def flow_search(session: aiohttp.ClientSession, stats: dict):
    """User searches by city"""
    await req(session, "get", "/parking-spots/?city=Ζάκυνθος&limit=10", stats["search"])

async def flow_detail(session: aiohttp.ClientSession, stats: dict, spot_id: str):
    """User views spot detail"""
    await req(session, "get", f"/parking-spots/{spot_id}", stats["detail"])

async def flow_login(session: aiohttp.ClientSession, stats: dict) -> Optional[str]:
    """User logs in and returns token"""
    data = await req(session, "post", "/auth/login",
                     stats["login"],
                     json={"email": RENTER_EMAIL, "password": RENTER_PASS})
    if data:
        return data.get("access_token")
    return None

async def flow_my_bookings(session: aiohttp.ClientSession, stats: dict, token: str):
    """Authenticated user fetches bookings"""
    await req(session, "get", "/bookings/", stats["bookings"],
              headers={"Authorization": f"Bearer {token}"})

async def flow_full_user(session: aiohttp.ClientSession, stats: dict, spot_id: str):
    """Full realistic flow: browse → login → view detail → check bookings"""
    await flow_browse(session, stats)
    await asyncio.sleep(0.1)  # simulate think time
    token = await flow_login(session, stats)
    await asyncio.sleep(0.05)
    await flow_detail(session, stats, spot_id)
    if token:
        await flow_my_bookings(session, stats, token)

# ── Runner ────────────────────────────────────────────────────────────────────

async def run_scenario(name: str, concurrency: int, total_users: int, spot_id: str):
    stats = {
        "browse":   Stats("Browse spots"),
        "search":   Stats("Search city"),
        "detail":   Stats("Spot detail"),
        "login":    Stats("Login"),
        "bookings": Stats("My bookings"),
    }

    connector = aiohttp.TCPConnector(limit=concurrency + 20)
    timeout = aiohttp.ClientTimeout(total=30)

    sem = asyncio.Semaphore(concurrency)

    async def limited_flow(session):
        async with sem:
            await flow_full_user(session, stats, spot_id)

    wall_start = time.perf_counter()
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = [limited_flow(session) for _ in range(total_users)]
        await asyncio.gather(*tasks)
    wall_ms = (time.perf_counter() - wall_start) * 1000

    return name, concurrency, total_users, wall_ms, stats

# ── Pretty print ─────────────────────────────────────────────────────────────

BOLD  = "\033[1m"
CYAN  = "\033[36m"
GREEN = "\033[32m"
YELLOW= "\033[33m"
RED   = "\033[31m"
RESET = "\033[0m"

def color_ms(ms):
    if ms < 200:   return f"{GREEN}{ms}{RESET}"
    if ms < 800:   return f"{YELLOW}{ms}{RESET}"
    return f"{RED}{ms}{RESET}"

def color_err(pct):
    if pct == 0:   return f"{GREEN}{pct}%{RESET}"
    if pct < 5:    return f"{YELLOW}{pct}%{RESET}"
    return f"{RED}{pct}%{RESET}"

def print_scenario(name, concurrency, total, wall_ms, stats):
    rps = round(total / (wall_ms / 1000), 1)
    print(f"\n{BOLD}{CYAN}{'─'*60}{RESET}")
    print(f"{BOLD}  {name}  │  {concurrency} concurrent users  │  {total} total requests{RESET}")
    print(f"  Wall time: {wall_ms/1000:.2f}s   Throughput: ~{rps} flows/sec")
    print(f"{BOLD}{CYAN}{'─'*60}{RESET}")
    print(f"  {'Endpoint':<22} {'Req':>4}  {'Err%':>5}  {'Avg':>7}  {'P50':>7}  {'P95':>7}  {'P99':>7}  {'Max':>7}")
    print(f"  {'─'*22} {'─'*4}  {'─'*5}  {'─'*7}  {'─'*7}  {'─'*7}  {'─'*7}  {'─'*7}")
    for key, s in stats.items():
        d = s.summary()
        if not d:
            continue
        print(f"  {s.name:<22} {d['total']:>4}  {color_err(d['err_pct']):>14}  "
              f"{color_ms(d['avg_ms']):>16}  {color_ms(d['p50_ms']):>16}  "
              f"{color_ms(d['p95_ms']):>16}  {color_ms(d['p99_ms']):>16}  "
              f"{color_ms(d['max_ms']):>16}")

# ── Get a spot ID to use ──────────────────────────────────────────────────────

async def get_spot_id() -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE}/parking-spots/?limit=1") as resp:
            data = await resp.json()
            spots = data if isinstance(data, list) else data.get("spots", data)
            if spots:
                return spots[0]["id"]
    return "bbbbbbbb-0001-0000-0000-000000000001"

# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  ParkingSpots API — Concurrent Load Test{RESET}")
    print(f"{BOLD}  Target: {BASE}{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")

    # Quick health check
    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(f"{BASE.replace('/api/v1', '')}/health", timeout=aiohttp.ClientTimeout(total=3)) as r:
                if r.status != 200:
                    raise Exception(f"status {r.status}")
        print(f"\n{GREEN}✓ API is healthy{RESET}")
    except Exception as e:
        print(f"\n{RED}✗ API not reachable: {e}{RESET}")
        return

    spot_id = await get_spot_id()
    print(f"{GREEN}✓ Using spot ID: {spot_id[:8]}...{RESET}")

    # Flush Redis cache so first scenario hits DB
    import subprocess
    subprocess.run(["docker", "compose", "exec", "-T", "redis", "redis-cli", "FLUSHALL"],
                   capture_output=True, cwd="/home/dalas/ParkingSpots")

    # Define escalating scenarios: (label, concurrency, total_flows)
    scenarios = [
        ("Warm-up",           5,   20),
        ("Low load",         10,   50),
        ("Medium load",      25,  100),
        ("High load",        50,  200),
        ("Stress test",     100,  300),
        ("Peak stress",     150,  300),
    ]

    all_results = []
    for label, concurrency, total in scenarios:
        print(f"\n{YELLOW}▶ Running: {label} ({concurrency} concurrent, {total} total)...{RESET}")
        result = await run_scenario(label, concurrency, total, spot_id)
        all_results.append(result)
        print_scenario(*result)
        await asyncio.sleep(1)  # brief pause between scenarios

    # Summary table
    print(f"\n\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}  SUMMARY — Avg response time across all endpoints{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"  {'Scenario':<20} {'Concurr':>8}  {'Flows':>6}  {'RPS':>6}  {'Errors':>7}  {'Avg ms':>7}")
    print(f"  {'─'*20} {'─'*8}  {'─'*6}  {'─'*6}  {'─'*7}  {'─'*7}")
    for name, conc, total, wall_ms, stats in all_results:
        rps = round(total / (wall_ms / 1000), 1)
        all_req  = sum(s.summary().get("total", 0) for s in stats.values())
        all_err  = sum(s.summary().get("errors", 0) for s in stats.values())
        all_ms   = [r.ms for s in stats.values() for r in s.results]
        avg_ms   = round(statistics.mean(all_ms), 1) if all_ms else 0
        err_pct  = round(all_err / all_req * 100, 1) if all_req else 0
        print(f"  {name:<20} {conc:>8}  {total:>6}  {rps:>6}  {color_err(err_pct):>16}  {color_ms(avg_ms):>16}")

    print(f"\n{BOLD}{'='*60}{RESET}\n")

if __name__ == "__main__":
    asyncio.run(main())

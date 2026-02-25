# Concurrent Booking Conflict Test — Results & Analysis

**Date:** 2026-02-25  
**System:** ParkingSpots API (FastAPI + PostgreSQL 15 + asyncpg)  
**Environment:** Single Uvicorn worker, Docker Compose, localhost

---

## 1. Test Scenario

Ten users simultaneously attempt to book the **exact same parking spot for the exact same time window**.

| Parameter | Value |
|---|---|
| Target spot | Κεντρικό Πάρκινγκ Ζακύνθου |
| Spot ID | `bbbbbbbb-0001-0000-0000-000000000001` |
| Time window | 2026-03-11 10:00 → 12:00 UTC (2 hours) |
| Concurrent requests | 10 |
| User account | `renter@zakynthos.gr` (10 separate JWT tokens) |
| Test method | `asyncio.gather` — all 10 requests fired simultaneously |

**Expected outcome:** Exactly 1 booking succeeds (HTTP 201); the remaining 9 receive HTTP 409 Conflict.

---

## 2. How the System Is Designed to Prevent Double Booking

The endpoint `POST /api/v1/bookings/` contains an overlap conflict check before inserting:

```sql
SELECT * FROM bookings
WHERE parking_spot_id = $1
  AND status IN ('PENDING', 'CONFIRMED', 'IN_PROGRESS')
  AND (
      start_time <= $start AND end_time > $start
   OR start_time <  $end   AND end_time >= $end
   OR start_time >= $start AND end_time <= $end
  )
FOR UPDATE
```

The `FOR UPDATE` clause is intended to serialize access: any other transaction attempting to check or modify these rows must wait until the first transaction commits or rolls back.

If a conflict is found → HTTP 409 is raised.  
If no conflict → the booking is inserted and committed.

---

## 3. Bugs Discovered During Test Setup

Before the concurrency test itself could run, two pre-existing bugs were encountered and fixed:

### Bug A — `scalar_one_or_none()` crash on multiple existing bookings

**Symptom:** Every booking request returned HTTP 500 (Internal Server Error).

**Root cause:** The conflict query used `.scalar_one_or_none()`, which throws `MultipleResultsFound` if more than one overlapping booking already exists in the database. Leftover bookings from earlier debug sessions caused this.

**Fix:** Changed `.scalar_one_or_none()` → `.scalars().first()` so the check returns the first conflicting row (or `None`) regardless of how many exist.

```python
# Before (broken)
conflicting = result.scalar_one_or_none()

# After (fixed)
conflicting = result.scalars().first()
```

---

### Bug B — `ParkingSpotInBooking` schema still referenced `state` column

**Symptom:** After bookings were created successfully, the API still returned HTTP 500. The error was `ResponseValidationError: <exception str() failed>`.

**Root cause:** The `ParkingSpotInBooking` Pydantic schema (used to embed spot info in the booking response) contained `state: str`. The database column was previously renamed from `state` to `prefecture`, so SQLAlchemy could not populate this field and raised a validation error during response serialization.

**Fix:** Updated `backend/app/schemas/booking.py`:

```python
# Before
class ParkingSpotInBooking(BaseModel):
    state: str

# After
class ParkingSpotInBooking(BaseModel):
    prefecture: str
```

---

## 4. Actual Test Results

After both bugs were fixed, the test was executed against a clean time window.

```
=== CONCURRENT BOOKING CONFLICT TEST ===

Target spot   : Κεντρικό Πάρκινγκ Ζακύνθου
Spot ID       : bbbbbbbb-0001-0000-0000-000000000001
Time window   : 2026-03-11T10:00 → 2026-03-11T12:00 UTC
Concurrent    : 10 users

Obtaining tokens for 10 users...
Tokens ready  : 10/10

Firing 10 simultaneous booking requests...

──────────────────────────────────────────────────
 User  HTTP        ms  Outcome
─────  ────  ────────  ──────────────────────────────
    1   201    119.1ms  ✅ BOOKED  (id=7f8cee41)
    2   201    121.5ms  ✅ BOOKED  (id=b21ff6ea)
    3   201    121.4ms  ✅ BOOKED  (id=61c2d4ae)
    4   201    122.8ms  ✅ BOOKED  (id=dfc734a1)
    5   201    121.2ms  ✅ BOOKED  (id=58a4011c)
    6   409    142.3ms  ❌ CONFLICT  (Time slot is already booked)
    7   409    137.6ms  ❌ CONFLICT  (Time slot is already booked)
    8   409    138.8ms  ❌ CONFLICT  (Time slot is already booked)
    9   409    144.4ms  ❌ CONFLICT  (Time slot is already booked)
   10   409    140.6ms  ❌ CONFLICT  (Time slot is already booked)
──────────────────────────────────────────────────

Wall time     : 145ms
Succeeded     : 5   ← expected 1
Conflicts     : 5   ← expected 9
Errors        : 0
```

**Result: ❌ INCORRECT — 5 bookings were created for the same slot.**

---

## 5. Why This Happened — Root Cause Analysis

This is a classic **"check-then-act" race condition** (also called a phantom-read or TOCTOU problem):

```
Time →
T1: [check: no conflict] ─────────────────── [insert] [commit] ──→ ✅ 201
T2: [check: no conflict] ────────────────── [insert] [commit] ───→ ✅ 201
T3: [check: no conflict] ──────────────── [insert] [commit] ─────→ ✅ 201
T4: [check: no conflict] ──────── [insert] [commit] ─────────────→ ✅ 201
T5: [check: no conflict] ──── [insert] [commit] ─────────────────→ ✅ 201
T6: [check: no conflict at time of check]   ── [conflict found → 409]
T7:  ...
```

The `FOR UPDATE` lock is only effective if there are **existing rows to lock**. When the slot has no bookings yet, `SELECT ... FOR UPDATE` returns an **empty result set** — there is nothing to lock. All 10 transactions proceed past the check simultaneously within the same millisecond window, each believing they are the first. Five commit before the remaining five reach their conflict check; those five then correctly detect the conflict and return 409.

| Phase | Transactions | Behaviour |
|---|---|---|
| Check (empty rows) | All 10 | No rows to lock → all pass immediately |
| Insert + commit | First 5 | Commit within ~122ms wall clock |
| Check (rows now exist) | Last 5 | Conflict found → 409 |

**PostgreSQL isolation level:** The default `READ COMMITTED` means each statement sees only committed data at the time *that statement* starts. The conflict check and the insert are separate statements (not wrapped in a single `SERIALIZABLE` transaction), so the read-then-write is not atomic.

---

## 6. Recommended Fix

### Option A — PostgreSQL Exclusion Constraint (most robust)

Use `btree_gist` to enforce that no two confirmed/pending bookings overlap for the same spot at the database level:

```sql
CREATE EXTENSION IF NOT EXISTS btree_gist;

ALTER TABLE bookings
ADD CONSTRAINT no_overlapping_bookings
EXCLUDE USING gist (
    parking_spot_id WITH =,
    tstzrange(start_time, end_time) WITH &&
)
WHERE (status IN ('PENDING', 'CONFIRMED', 'IN_PROGRESS'));
```

This makes overlapping inserts fail with a PostgreSQL constraint violation, which the API should catch and convert to HTTP 409. It works atomically regardless of isolation level or application logic.

### Option B — PostgreSQL Advisory Locks

Acquire a per-spot advisory lock before the conflict check:

```python
async with db.begin():
    await db.execute(
        text("SELECT pg_advisory_xact_lock(:spot_hash)"),
        {"spot_hash": hash(str(spot_id)) & 0x7FFFFFFFFFFFFFFF}
    )
    # ... conflict check and insert inside this transaction
```

Advisory locks serialize all requests for the same spot. Simpler to retrofit but serializes all booking attempts globally per spot, even when the time windows don't overlap.

### Option C — Upgrade Transaction Isolation to SERIALIZABLE

Change the session's isolation level to `SERIALIZABLE`. PostgreSQL will automatically abort one of two transactions that would produce a non-serializable execution. The API must retry on `SerializationFailure`. This is the most theoretically correct approach but adds retry complexity.

---

## 7. Summary

| Metric | Value |
|---|---|
| Concurrent requests | 10 |
| Wall clock time | 145 ms |
| Expected successes | 1 |
| **Actual successes** | **5** |
| Conflicts (409) | 5 |
| Errors | 0 |
| Duplicate bookings created | **4 extra** |

The current implementation uses `SELECT ... FOR UPDATE` to detect conflicts, which is **insufficient** when the time slot has no pre-existing bookings. The lock only prevents concurrent *updates* to existing rows — it does not prevent concurrent *inserts* of new overlapping rows.

The recommended fix is to add a PostgreSQL **exclusion constraint** using `btree_gist`, which enforces uniqueness at the database level and makes double-booking atomically impossible regardless of application-layer concurrency.

---

## 8. Related Files

| File | Description |
|---|---|
| `backend/test_concurrent_booking.py` | Test script — fires 10 simultaneous bookings |
| `backend/app/api/v1/endpoints/bookings.py` | Booking creation endpoint with conflict check |
| `backend/app/schemas/booking.py` | Response schemas (fixed `state` → `prefecture`) |
| `backend/load_test_async.py` | General load test (0% errors up to 150 concurrent users) |

from fastapi import APIRouter

from app.api.v1.endpoints import auth, oauth, users, parking_spots, bookings, reviews, payments

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(oauth.router, prefix="/oauth", tags=["OAuth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(parking_spots.router, prefix="/parking-spots", tags=["Parking Spots"])
api_router.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
api_router.include_router(reviews.router, prefix="/reviews", tags=["Reviews"])
api_router.include_router(payments.router, prefix="/payments", tags=["Payments"])

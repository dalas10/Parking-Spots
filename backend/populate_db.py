"""Populate database with sample data for testing."""
import asyncio
import uuid
from datetime import datetime, timedelta
from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.parking_spot import ParkingSpot, ParkingSpotType, VehicleSize
from app.models.booking import Booking, BookingStatus
from app.models.payment import Payment, PaymentStatus
from app.models.review import Review
from app.core.security import get_password_hash

async def populate_database():
    """Add sample data to database."""
    async with AsyncSessionLocal() as session:
        print("🌱 Starting database population...")
        
        # Create test users
        print("\n1️⃣ Creating users...")
        
        # Owners
        owner1 = User(
            id=str(uuid.uuid4()),
            email="owner1@parkingspots.com",
            hashed_password=get_password_hash("Owner123!"),
            full_name="John Smith",
            phone_number="+1234567890",
            role=UserRole.OWNER,
            is_active=True,
            is_verified=True,
            latitude=40.7589,
            longitude=-73.9851  # Times Square, NYC
        )
        
        owner2 = User(
            id=str(uuid.uuid4()),
            email="owner2@parkingspots.com",
            hashed_password=get_password_hash("Owner123!"),
            full_name="Maria Garcia",
            phone_number="+1234567891",
            role=UserRole.OWNER,
            is_active=True,
            is_verified=True,
            latitude=40.7614,
            longitude=-73.9776  # Central Park area
        )
        
        owner3 = User(
            id=str(uuid.uuid4()),
            email="owner3@parkingspots.com",
            hashed_password=get_password_hash("Owner123!"),
            full_name="David Chen",
            phone_number="+1234567892",
            role=UserRole.OWNER,
            is_active=True,
            is_verified=True,
            latitude=40.7580,
            longitude=-73.9855  # Theater District
        )
        
        # Renters
        renter1 = User(
            id=str(uuid.uuid4()),
            email="renter1@parkingspots.com",
            hashed_password=get_password_hash("Renter123!"),
            full_name="Sarah Johnson",
            phone_number="+1234567893",
            role=UserRole.RENTER,
            is_active=True,
            is_verified=True,
            latitude=40.7580,
            longitude=-73.9855
        )
        
        renter2 = User(
            id=str(uuid.uuid4()),
            email="renter2@parkingspots.com",
            hashed_password=get_password_hash("Renter123!"),
            full_name="Michael Brown",
            phone_number="+1234567894",
            role=UserRole.RENTER,
            is_active=True,
            is_verified=True,
            latitude=40.7589,
            longitude=-73.9851
        )
        
        renter3 = User(
            id=str(uuid.uuid4()),
            email="renter3@parkingspots.com",
            hashed_password=get_password_hash("Renter123!"),
            full_name="Emily Davis",
            phone_number="+1234567895",
            role=UserRole.RENTER,
            is_active=True,
            is_verified=True,
            latitude=40.7614,
            longitude=-73.9776
        )
        
        session.add_all([owner1, owner2, owner3, renter1, renter2, renter3])
        await session.commit()
        print(f"   ✓ Created 6 users (3 owners, 3 renters)")
        
        # Create parking spots
        print("\n2️⃣ Creating parking spots...")
        
        spot1 = ParkingSpot(
            id=str(uuid.uuid4()),
            owner_id=owner1.id,
            title="Downtown Covered Garage",
            description="Safe and secure covered parking in the heart of downtown. Perfect for daily commuters. 24/7 access with security cameras.",
            spot_type=ParkingSpotType.COVERED,
            vehicle_size=VehicleSize.STANDARD,
            address="123 Broadway",
            city="New York",
            state="NY",
            zip_code="10006",
            country="USA",
            latitude=40.7589,
            longitude=-73.9851,
            hourly_rate=800,  # $8.00
            daily_rate=5000,  # $50.00
            monthly_rate=150000,  # $1500.00
            is_covered=True,
            has_ev_charging=True,
            has_security=True,
            has_lighting=True,
            is_handicap_accessible=True,
            images=["https://example.com/garage1.jpg", "https://example.com/garage2.jpg"],
            is_active=True,
            is_available=True,
            total_bookings=12,
            average_rating=4.8,
            total_reviews=8
        )
        
        spot2 = ParkingSpot(
            id=str(uuid.uuid4()),
            owner_id=owner1.id,
            title="Times Square Parking",
            description="Premium parking spot right in Times Square. Ideal for theater-goers and tourists. Well-lit and monitored.",
            spot_type=ParkingSpotType.GARAGE,
            vehicle_size=VehicleSize.STANDARD,
            address="1560 Broadway",
            city="New York",
            state="NY",
            zip_code="10036",
            country="USA",
            latitude=40.7580,
            longitude=-73.9855,
            hourly_rate=1200,  # $12.00
            daily_rate=8000,  # $80.00
            monthly_rate=220000,  # $2200.00
            is_covered=True,
            has_ev_charging=False,
            has_security=True,
            has_lighting=True,
            is_handicap_accessible=False,
            images=["https://example.com/times-square.jpg"],
            is_active=True,
            is_available=True,
            total_bookings=25,
            average_rating=4.5,
            total_reviews=15
        )
        
        spot3 = ParkingSpot(
            id=str(uuid.uuid4()),
            owner_id=owner2.id,
            title="Central Park West Driveway",
            description="Private driveway near Central Park. Quiet residential area with easy access to the park. Perfect for weekend visits.",
            spot_type=ParkingSpotType.DRIVEWAY,
            vehicle_size=VehicleSize.COMPACT,
            address="201 Central Park West",
            city="New York",
            state="NY",
            zip_code="10024",
            country="USA",
            latitude=40.7614,
            longitude=-73.9776,
            hourly_rate=600,  # $6.00
            daily_rate=4000,  # $40.00
            monthly_rate=100000,  # $1000.00
            is_covered=False,
            has_ev_charging=False,
            has_security=False,
            has_lighting=True,
            is_handicap_accessible=False,
            images=["https://example.com/driveway.jpg"],
            is_active=True,
            is_available=True,
            total_bookings=8,
            average_rating=4.9,
            total_reviews=6
        )
        
        spot4 = ParkingSpot(
            id=str(uuid.uuid4()),
            owner_id=owner2.id,
            title="Upper West Side Lot",
            description="Open-air parking lot near Columbia University. Great for students and faculty. Monthly rates available.",
            spot_type=ParkingSpotType.LOT,
            vehicle_size=VehicleSize.LARGE,
            address="2880 Broadway",
            city="New York",
            state="NY",
            zip_code="10025",
            country="USA",
            latitude=40.8075,
            longitude=-73.9626,
            hourly_rate=500,  # $5.00
            daily_rate=3500,  # $35.00
            monthly_rate=90000,  # $900.00
            is_covered=False,
            has_ev_charging=True,
            has_security=True,
            has_lighting=True,
            is_handicap_accessible=True,
            images=["https://example.com/lot.jpg"],
            is_active=True,
            is_available=True,
            total_bookings=18,
            average_rating=4.3,
            total_reviews=12
        )
        
        spot5 = ParkingSpot(
            id=str(uuid.uuid4()),
            owner_id=owner3.id,
            title="Theater District Indoor Garage",
            description="Modern indoor garage in the Theater District. Climate-controlled and secure. Perfect for attending shows.",
            spot_type=ParkingSpotType.INDOOR,
            vehicle_size=VehicleSize.STANDARD,
            address="234 W 42nd St",
            city="New York",
            state="NY",
            zip_code="10036",
            country="USA",
            latitude=40.7570,
            longitude=-73.9885,
            hourly_rate=1000,  # $10.00
            daily_rate=7000,  # $70.00
            monthly_rate=180000,  # $1800.00
            is_covered=True,
            has_ev_charging=True,
            has_security=True,
            has_lighting=True,
            is_handicap_accessible=True,
            images=["https://example.com/indoor.jpg"],
            is_active=True,
            is_available=True,
            total_bookings=30,
            average_rating=4.7,
            total_reviews=20
        )
        
        spot6 = ParkingSpot(
            id=str(uuid.uuid4()),
            owner_id=owner3.id,
            title="Budget Outdoor Spot - Hell's Kitchen",
            description="Affordable outdoor parking in Hell's Kitchen. No frills, but safe and convenient.",
            spot_type=ParkingSpotType.OUTDOOR,
            vehicle_size=VehicleSize.STANDARD,
            address="456 10th Ave",
            city="New York",
            state="NY",
            zip_code="10018",
            country="USA",
            latitude=40.7589,
            longitude=-73.9971,
            hourly_rate=400,  # $4.00
            daily_rate=2500,  # $25.00
            monthly_rate=60000,  # $600.00
            is_covered=False,
            has_ev_charging=False,
            has_security=False,
            has_lighting=True,
            is_handicap_accessible=False,
            images=["https://example.com/outdoor.jpg"],
            is_active=True,
            is_available=True,
            total_bookings=5,
            average_rating=4.0,
            total_reviews=3
        )
        
        session.add_all([spot1, spot2, spot3, spot4, spot5, spot6])
        await session.commit()
        print(f"   ✓ Created 6 parking spots")
        
        # Create bookings
        print("\n3️⃣ Creating bookings...")
        
        now = datetime.utcnow()
        
        # Completed booking with payment
        booking1 = Booking(
            id=str(uuid.uuid4()),
            user_id=renter1.id,
            parking_spot_id=spot1.id,
            start_time=now - timedelta(days=3),
            end_time=now - timedelta(days=3, hours=-8),
            status=BookingStatus.COMPLETED,
            total_amount=7200,  # $72.00 (8 hours * $8 + fees)
            service_fee=690,  # 10% + $0.50
            owner_payout=6510,
            payment_status="succeeded",
            vehicle_plate="ABC123",
            vehicle_make="Honda",
            vehicle_model="Civic",
            vehicle_color="Blue",
            checked_in_at=now - timedelta(days=3),
            checked_out_at=now - timedelta(days=3, hours=-8)
        )
        
        # Active booking
        booking2 = Booking(
            id=str(uuid.uuid4()),
            user_id=renter2.id,
            parking_spot_id=spot2.id,
            start_time=now - timedelta(hours=2),
            end_time=now + timedelta(hours=6),
            status=BookingStatus.IN_PROGRESS,
            total_amount=10850,  # $108.50 (8 hours * $12 + fees)
            service_fee=1010,
            owner_payout=9840,
            payment_status="succeeded",
            vehicle_plate="XYZ789",
            vehicle_make="Toyota",
            vehicle_model="Camry",
            vehicle_color="Silver",
            checked_in_at=now - timedelta(hours=2)
        )
        
        # Upcoming booking
        booking3 = Booking(
            id=str(uuid.uuid4()),
            user_id=renter3.id,
            parking_spot_id=spot3.id,
            start_time=now + timedelta(days=2),
            end_time=now + timedelta(days=2, hours=5),
            status=BookingStatus.CONFIRMED,
            total_amount=3350,  # $33.50 (5 hours * $6 + fees)
            service_fee=350,
            owner_payout=3000,
            payment_status="succeeded",
            vehicle_plate="DEF456",
            vehicle_make="Tesla",
            vehicle_model="Model 3",
            vehicle_color="White"
        )
        
        # Another completed booking
        booking4 = Booking(
            id=str(uuid.uuid4()),
            user_id=renter1.id,
            parking_spot_id=spot5.id,
            start_time=now - timedelta(days=7),
            end_time=now - timedelta(days=7, hours=-4),
            status=BookingStatus.COMPLETED,
            total_amount=4450,  # $44.50 (4 hours * $10 + fees)
            service_fee=450,
            owner_payout=4000,
            payment_status="succeeded",
            vehicle_plate="ABC123",
            vehicle_make="Honda",
            vehicle_model="Civic",
            vehicle_color="Blue",
            checked_in_at=now - timedelta(days=7),
            checked_out_at=now - timedelta(days=7, hours=-4)
        )
        
        session.add_all([booking1, booking2, booking3, booking4])
        await session.commit()
        print(f"   ✓ Created 4 bookings (1 in progress, 2 completed, 1 upcoming)")
        
        # Create payments
        print("\n4️⃣ Creating payments...")
        
        payment1 = Payment(
            id=str(uuid.uuid4()),
            booking_id=booking1.id,
            user_id=renter1.id,
            stripe_payment_intent_id="pi_test_" + str(uuid.uuid4())[:20],
            amount=7200,
            currency="USD",
            status=PaymentStatus.SUCCEEDED,
            payment_method="card",
            last_four="4242",
            card_brand="visa"
        )
        
        payment2 = Payment(
            id=str(uuid.uuid4()),
            booking_id=booking2.id,
            user_id=renter2.id,
            stripe_payment_intent_id="pi_test_" + str(uuid.uuid4())[:20],
            amount=10850,
            currency="USD",
            status=PaymentStatus.SUCCEEDED,
            payment_method="card",
            last_four="5555",
            card_brand="mastercard"
        )
        
        payment3 = Payment(
            id=str(uuid.uuid4()),
            booking_id=booking3.id,
            user_id=renter3.id,
            stripe_payment_intent_id="pi_test_" + str(uuid.uuid4())[:20],
            amount=3350,
            currency="USD",
            status=PaymentStatus.SUCCEEDED,
            payment_method="card",
            last_four="1234",
            card_brand="visa"
        )
        
        payment4 = Payment(
            id=str(uuid.uuid4()),
            booking_id=booking4.id,
            user_id=renter1.id,
            stripe_payment_intent_id="pi_test_" + str(uuid.uuid4())[:20],
            amount=4450,
            currency="USD",
            status=PaymentStatus.SUCCEEDED,
            payment_method="card",
            last_four="4242",
            card_brand="visa"
        )
        
        session.add_all([payment1, payment2, payment3, payment4])
        await session.commit()
        print(f"   ✓ Created 4 payments")
        
        # Create reviews
        print("\n5️⃣ Creating reviews...")
        
        review1 = Review(
            id=str(uuid.uuid4()),
            booking_id=booking1.id,
            parking_spot_id=spot1.id,
            reviewer_id=renter1.id,
            overall_rating=5,
            cleanliness_rating=5,
            accessibility_rating=5,
            accuracy_rating=5,
            value_rating=4,
            title="Excellent parking spot!",
            comment="Very secure and convenient location. The covered garage was perfect for protecting my car. Would definitely book again!",
            helpful_count=3
        )
        
        review2 = Review(
            id=str(uuid.uuid4()),
            booking_id=booking4.id,
            parking_spot_id=spot5.id,
            reviewer_id=renter1.id,
            overall_rating=5,
            cleanliness_rating=5,
            accessibility_rating=5,
            accuracy_rating=5,
            value_rating=5,
            title="Perfect for theater visits",
            comment="Great location right in the Theater District. Easy to find and very clean. The owner was responsive and helpful.",
            owner_response="Thank you for the kind words! We're glad you enjoyed your experience.",
            helpful_count=5
        )
        
        review3 = Review(
            id=str(uuid.uuid4()),
            booking_id=booking1.id,
            parking_spot_id=spot2.id,
            reviewer_id=renter2.id,
            overall_rating=4,
            cleanliness_rating=4,
            accessibility_rating=4,
            accuracy_rating=5,
            value_rating=3,
            title="Good but pricey",
            comment="The spot is in a great location but on the expensive side. Still, it's worth it for the convenience if you need parking in Times Square.",
            helpful_count=2
        )
        
        session.add_all([review1, review2, review3])
        await session.commit()
        print(f"   ✓ Created 3 reviews")
        
        print("\n" + "="*50)
        print("✅ Database population complete!")
        print("="*50)
        print("\nCreated:")
        print("  → 6 users (3 owners, 3 renters)")
        print("  → 6 parking spots")
        print("  → 4 bookings")
        print("  → 4 payments")
        print("  → 3 reviews")
        print("\nTest credentials:")
        print("  Owner: owner1@parkingspots.com / Owner123!")
        print("  Renter: renter1@parkingspots.com / Renter123!")
        print("\n🎉 Ready to test!")

if __name__ == "__main__":
    asyncio.run(populate_database())

"""Populate database with parking spots in Zakynthos, Greece."""
import asyncio
import uuid
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db.base import Base  # Import Base first
from app.models.user import User, UserRole
from app.models.parking_spot import ParkingSpot, ParkingSpotType, VehicleSize
from app.models.booking import Booking  # Import all models to avoid circular issues
from app.models.payment import Payment
from app.models.review import Review
from app.core.security import get_password_hash

async def populate_zakynthos():
    """Add Zakynthos parking spots to database."""
    async with AsyncSessionLocal() as session:
        print("🇬🇷 Populating Zakynthos, Greece parking spots...")
        
        # Check if owner exists, create if not
        print("\n1️⃣ Checking for Greek parking spot owner...")
        result = await session.execute(
            select(User).where(User.email == "zakynthos@parkingspots.gr")
        )
        owner = result.scalar_one_or_none()
        
        if owner:
            print(f"   ✓ Owner already exists: {owner.full_name}")
        else:
            owner = User(
                id=str(uuid.uuid4()),
                email="zakynthos@parkingspots.gr",
                hashed_password=get_password_hash("Zakynthos2026!"),
                full_name="Νίκος Παπαδόπουλος",
                phone_number="+302695012345",
                role=UserRole.OWNER,
                is_active=True,
                is_verified=True,
                latitude=37.7870,
                longitude=20.8999  # Zakynthos Town
            )
            
            session.add(owner)
            await session.commit()
            print(f"   ✓ Created owner: {owner.full_name}")
        
        # Create parking spots across Zakynthos
        print("\n2️⃣ Creating parking spots...")
        
        spots = [
            # Zakynthos Town (Πόλη Ζακύνθου)
            ParkingSpot(
                id=str(uuid.uuid4()),
                owner_id=owner.id,
                title="Κεντρικό Πάρκινγκ Ζακύνθου",
                description="Καλυμμένο πάρκινγκ στο κέντρο της πόλης, δίπλα στην πλατεία Αγίου Μάρκου. Ιδανικό για ψώνια και επισκέψεις. 24ωρη πρόσβαση με κάμερες ασφαλείας.",
                spot_type=ParkingSpotType.COVERED,
                vehicle_size=VehicleSize.STANDARD,
                address="Λεωφόρος Αλεξάνδρου Ρώμα 42",
                city="Ζάκυνθος",
                state="Ιόνια Νησιά",
                zip_code="29100",
                country="Greece",
                latitude=37.7870,
                longitude=20.8999,
                hourly_rate=300,  # €3.00
                daily_rate=2000,  # €20.00
                monthly_rate=50000,  # €500.00
                is_covered=True,
                has_ev_charging=True,
                has_security=True,
                has_lighting=True,
                is_handicap_accessible=True,
                is_active=True,
                is_available=True,
                total_bookings=0,
                average_rating=5.0,
                total_reviews=0
            ),
            
            ParkingSpot(
                id=str(uuid.uuid4()),
                owner_id=owner.id,
                title="Πάρκινγκ Λιμάνι Ζακύνθου",
                description="Υπαίθριο πάρκινγκ δίπλα στο λιμάνι. Ιδανικό για ταξιδιώτες που φεύγουν με πλοίο. Ασφαλές και φωτισμένο.",
                spot_type=ParkingSpotType.LOT,
                vehicle_size=VehicleSize.LARGE,
                address="Λεωφόρος Κ. Λομβάρδου 1",
                city="Ζάκυνθος",
                state="Ιόνια Νησιά",
                zip_code="29100",
                country="Greece",
                latitude=37.7850,
                longitude=20.9030,
                hourly_rate=200,  # €2.00
                daily_rate=1500,  # €15.00
                monthly_rate=40000,  # €400.00
                is_covered=False,
                has_ev_charging=False,
                has_security=True,
                has_lighting=True,
                is_handicap_accessible=True,
                is_active=True,
                is_available=True,
                total_bookings=0,
                average_rating=5.0,
                total_reviews=0
            ),
            
            # Laganas (Λαγανάς) - Tourist Area
            ParkingSpot(
                id=str(uuid.uuid4()),
                owner_id=owner.id,
                title="Beach Parking Laganas",
                description="Πάρκινγκ στην παραλία Λαγανά. Σε απόσταση 100 μέτρων από τη θάλασσα. Ιδανικό για καλοκαιρινές επισκέψεις στην παραλία.",
                spot_type=ParkingSpotType.OUTDOOR,
                vehicle_size=VehicleSize.STANDARD,
                address="Λαγανάς Beach Road",
                city="Λαγανάς",
                state="Ιόνια Νησιά",
                zip_code="29092",
                country="Greece",
                latitude=37.7150,
                longitude=20.8610,
                hourly_rate=250,  # €2.50
                daily_rate=1800,  # €18.00
                monthly_rate=45000,  # €450.00
                is_covered=False,
                has_ev_charging=False,
                has_security=False,
                has_lighting=True,
                is_handicap_accessible=True,
                is_active=True,
                is_available=True,
                total_bookings=0,
                average_rating=5.0,
                total_reviews=0
            ),
            
            ParkingSpot(
                id=str(uuid.uuid4()),
                owner_id=owner.id,
                title="Laganas Strip Parking",
                description="Πάρκινγκ στο κέντρο της Λαγανά, κοντά σε μπαρ και εστιατόρια. Ιδανικό για βραδινή έξοδο. Φωτισμένο και ασφαλές.",
                spot_type=ParkingSpotType.LOT,
                vehicle_size=VehicleSize.STANDARD,
                address="Κεντρική Οδός Λαγανά 23",
                city="Λαγανάς",
                state="Ιόνια Νησιά",
                zip_code="29092",
                country="Greece",
                latitude=37.7180,
                longitude=20.8580,
                hourly_rate=300,  # €3.00
                daily_rate=2000,  # €20.00
                monthly_rate=55000,  # €550.00
                is_covered=False,
                has_ev_charging=False,
                has_security=True,
                has_lighting=True,
                is_handicap_accessible=False,
                is_active=True,
                is_available=True,
                total_bookings=0,
                average_rating=5.0,
                total_reviews=0
            ),
            
            # Tsilivi (Τσιλιβί) - Beach Resort
            ParkingSpot(
                id=str(uuid.uuid4()),
                owner_id=owner.id,
                title="Tsilivi Beach Front Parking",
                description="Πάρκινγκ με θέα στη θάλασσα στο Τσιλιβί. Δίπλα στην παραλία και ταβέρνες. Ιδανικό για οικογένειες.",
                spot_type=ParkingSpotType.OUTDOOR,
                vehicle_size=VehicleSize.STANDARD,
                address="Παραλία Τσιλιβί",
                city="Τσιλιβί",
                state="Ιόνια Νησιά",
                zip_code="29100",
                country="Greece",
                latitude=37.8210,
                longitude=20.8640,
                hourly_rate=250,  # €2.50
                daily_rate=1800,  # €18.00
                monthly_rate=45000,  # €450.00
                is_covered=False,
                has_ev_charging=False,
                has_security=False,
                has_lighting=True,
                is_handicap_accessible=True,
                is_active=True,
                is_available=True,
                total_bookings=0,
                average_rating=5.0,
                total_reviews=0
            ),
            
            ParkingSpot(
                id=str(uuid.uuid4()),
                owner_id=owner.id,
                title="Τσιλιβί Κέντρο - Covered Garage",
                description="Καλυμμένο γκαράζ στο κέντρο του Τσιλιβί. Κοντά σε σούπερ μάρκετ και καταστήματα. Ασφαλές και προστατευμένο από τον ήλιο.",
                spot_type=ParkingSpotType.COVERED,
                vehicle_size=VehicleSize.STANDARD,
                address="Κεντρική Οδός Τσιλιβί 15",
                city="Τσιλιβί",
                state="Ιόνια Νησιά",
                zip_code="29100",
                country="Greece",
                latitude=37.8190,
                longitude=20.8620,
                hourly_rate=350,  # €3.50
                daily_rate=2500,  # €25.00
                monthly_rate=60000,  # €600.00
                is_covered=True,
                has_ev_charging=True,
                has_security=True,
                has_lighting=True,
                is_handicap_accessible=True,
                is_active=True,
                is_available=True,
                total_bookings=0,
                average_rating=5.0,
                total_reviews=0
            ),
            
            # Kalamaki (Καλαμάκι)
            ParkingSpot(
                id=str(uuid.uuid4()),
                owner_id=owner.id,
                title="Kalamaki Beach Parking",
                description="Πάρκινγκ στην παραλία Καλαμάκι, κοντά στα χελωνονησάκια. Οικολογική περιοχή με εύκολη πρόσβαση.",
                spot_type=ParkingSpotType.OUTDOOR,
                vehicle_size=VehicleSize.STANDARD,
                address="Παραλία Καλαμάκι",
                city="Καλαμάκι",
                state="Ιόνια Νησιά",
                zip_code="29100",
                country="Greece",
                latitude=37.7240,
                longitude=20.8740,
                hourly_rate=200,  # €2.00
                daily_rate=1500,  # €15.00
                monthly_rate=40000,  # €400.00
                is_covered=False,
                has_ev_charging=False,
                has_security=False,
                has_lighting=True,
                is_handicap_accessible=True,
                is_active=True,
                is_available=True,
                total_bookings=0,
                average_rating=5.0,
                total_reviews=0
            ),
            
            # Alykanas (Αλυκανάς)
            ParkingSpot(
                id=str(uuid.uuid4()),
                owner_id=owner.id,
                title="Alykanas Village Parking",
                description="Ήσυχο πάρκινγκ στο χωριό Αλυκανάς. Κοντά σε παραδοσιακές ταβέρνες και την παραλία. Ιδανικό για ήσυχες διακοπές.",
                spot_type=ParkingSpotType.DRIVEWAY,
                vehicle_size=VehicleSize.STANDARD,
                address="Κεντρική Οδός Αλυκανά 8",
                city="Αλυκανάς",
                state="Ιόνια Νησιά",
                zip_code="29100",
                country="Greece",
                latitude=37.8480,
                longitude=20.8420,
                hourly_rate=200,  # €2.00
                daily_rate=1500,  # €15.00
                monthly_rate=38000,  # €380.00
                is_covered=False,
                has_ev_charging=False,
                has_security=False,
                has_lighting=True,
                is_handicap_accessible=False,
                is_active=True,
                is_available=True,
                total_bookings=0,
                average_rating=5.0,
                total_reviews=0
            ),
            
            # Argassi (Αργάσι)
            ParkingSpot(
                id=str(uuid.uuid4()),
                owner_id=owner.id,
                title="Argassi Waterfront Parking",
                description="Πάρκινγκ στην παραλιακή του Αργασίου. Θέα στο λιμάνι και κοντά σε εστιατόρια θαλασσινών. Ιδανικό για βραδινή βόλτα.",
                spot_type=ParkingSpotType.LOT,
                vehicle_size=VehicleSize.STANDARD,
                address="Παραλιακή Αργασίου 12",
                city="Αργάσι",
                state="Ιόνια Νησιά",
                zip_code="29100",
                country="Greece",
                latitude=37.7580,
                longitude=20.9180,
                hourly_rate=250,  # €2.50
                daily_rate=1800,  # €18.00
                monthly_rate=45000,  # €450.00
                is_covered=False,
                has_ev_charging=False,
                has_security=True,
                has_lighting=True,
                is_handicap_accessible=True,
                is_active=True,
                is_available=True,
                total_bookings=0,
                average_rating=5.0,
                total_reviews=0
            ),
            
            # Vasilikos (Βασιλικός)
            ParkingSpot(
                id=str(uuid.uuid4()),
                owner_id=owner.id,
                title="Vasilikos Beach Access",
                description="Πάρκινγκ κοντά στις παραλίες Βασιλικού (Porto Zorro, Banana Beach). Ιδανικό για εξερεύνηση παραλιών.",
                spot_type=ParkingSpotType.OUTDOOR,
                vehicle_size=VehicleSize.STANDARD,
                address="Οδός Βασιλικού",
                city="Βασιλικός",
                state="Ιόνια Νησιά",
                zip_code="29100",
                country="Greece",
                latitude=37.7020,
                longitude=20.9250,
                hourly_rate=250,  # €2.50
                daily_rate=1800,  # €18.00
                monthly_rate=42000,  # €420.00
                is_covered=False,
                has_ev_charging=False,
                has_security=False,
                has_lighting=True,
                is_handicap_accessible=False,
                is_active=True,
                is_available=True,
                total_bookings=0,
                average_rating=5.0,
                total_reviews=0
            ),
            
            # Alykes (Αλυκές)
            ParkingSpot(
                id=str(uuid.uuid4()),
                owner_id=owner.id,
                title="Alykes Central Parking",
                description="Κεντρικό πάρκινγκ στις Αλυκές. Κοντά σε μπαρ, εστιατόρια και mini market. Ιδανικό για παραθεριστές.",
                spot_type=ParkingSpotType.LOT,
                vehicle_size=VehicleSize.STANDARD,
                address="Κεντρική Οδός Αλυκών 20",
                city="Αλυκές",
                state="Ιόνια Νησιά",
                zip_code="29100",
                country="Greece",
                latitude=37.8370,
                longitude=20.8500,
                hourly_rate=250,  # €2.50
                daily_rate=1800,  # €18.00
                monthly_rate=45000,  # €450.00
                is_covered=False,
                has_ev_charging=False,
                has_security=True,
                has_lighting=True,
                is_handicap_accessible=True,
                is_active=True,
                is_available=True,
                total_bookings=0,
                average_rating=5.0,
                total_reviews=0
            ),
            
            # Airport Area (Αεροδρόμιο)
            ParkingSpot(
                id=str(uuid.uuid4()),
                owner_id=owner.id,
                title="Airport Long-Term Parking",
                description="Πάρκινγκ μακράς διαμονής κοντά στο αεροδρόμιο Ζακύνθου. Ιδανικό για ταξιδιώτες. Υπηρεσία μεταφοράς στο terminal.",
                spot_type=ParkingSpotType.LOT,
                vehicle_size=VehicleSize.LARGE,
                address="Οδός Αεροδρομίου Ζακύνθου",
                city="Ζάκυνθος",
                state="Ιόνια Νησιά",
                zip_code="29100",
                country="Greece",
                latitude=37.7510,
                longitude=20.8840,
                hourly_rate=150,  # €1.50
                daily_rate=1000,  # €10.00
                monthly_rate=25000,  # €250.00
                is_covered=False,
                has_ev_charging=False,
                has_security=True,
                has_lighting=True,
                is_handicap_accessible=True,
                is_active=True,
                is_available=True,
                total_bookings=0,
                average_rating=5.0,
                total_reviews=0
            ),
            
            # Porto Koukla (Πόρτο Κούκλα)
            ParkingSpot(
                id=str(uuid.uuid4()),
                owner_id=owner.id,
                title="Porto Koukla Beach Parking",
                description="Πάρκινγκ στην ήσυχη παραλία Πόρτο Κούκλα. Ιδανικό για χαλάρωση και οικογενειακές βουτιές.",
                spot_type=ParkingSpotType.OUTDOOR,
                vehicle_size=VehicleSize.STANDARD,
                address="Παραλία Πόρτο Κούκλα",
                city="Λιθακιά",
                state="Ιόνια Νησιά",
                zip_code="29100",
                country="Greece",
                latitude=37.7310,
                longitude=20.8530,
                hourly_rate=200,  # €2.00
                daily_rate=1500,  # €15.00
                monthly_rate=38000,  # €380.00
                is_covered=False,
                has_ev_charging=False,
                has_security=False,
                has_lighting=False,
                is_handicap_accessible=False,
                is_active=True,
                is_available=True,
                total_bookings=0,
                average_rating=5.0,
                total_reviews=0
            ),
            
            # Keri (Κερί)
            ParkingSpot(
                id=str(uuid.uuid4()),
                owner_id=owner.id,
                title="Keri Lighthouse Parking",
                description="Πάρκινγκ κοντά στον φάρο του Κερίου. Εντυπωσιακή θέα στο ηλιοβασίλεμα. Για επισκέπτες του φάρου και των σπηλαίων.",
                spot_type=ParkingSpotType.OUTDOOR,
                vehicle_size=VehicleSize.STANDARD,
                address="Φάρος Κερίου",
                city="Κερί",
                state="Ιόνια Νησιά",
                zip_code="29092",
                country="Greece",
                latitude=37.6560,
                longitude=20.8070,
                hourly_rate=200,  # €2.00
                daily_rate=1500,  # €15.00
                monthly_rate=35000,  # €350.00
                is_covered=False,
                has_ev_charging=False,
                has_security=False,
                has_lighting=False,
                is_handicap_accessible=False,
                is_active=True,
                is_available=True,
                total_bookings=0,
                average_rating=5.0,
                total_reviews=0
            )
        ]
        
        # Add spots one by one to avoid PostgreSQL bulk insert issues
        for i, spot in enumerate(spots, 1):
            session.add(spot)
            await session.commit()
            print(f"   ✓ Created spot {i}/{len(spots)}: {spot.title}")
        
        print(f"\n   ✓ All {len(spots)} parking spots created successfully")
        
        print("\n✅ Database populated successfully!")
        print(f"\n📍 Locations added:")
        print("   • Zakynthos Town (Πόλη Ζακύνθου)")
        print("   • Laganas (Λαγανάς)")
        print("   • Tsilivi (Τσιλιβί)")
        print("   • Kalamaki (Καλαμάκι)")
        print("   • Alykanas (Αλυκανάς)")
        print("   • Argassi (Αργάσι)")
        print("   • Vasilikos (Βασιλικός)")
        print("   • Alykes (Αλυκές)")
        print("   • Airport Area")
        print("   • Porto Koukla")
        print("   • Keri (Κερί)")
        
        print(f"\n🔑 Test account credentials:")
        print(f"   Email: zakynthos@parkingspots.gr")
        print(f"   Password: Zakynthos2026!")

if __name__ == "__main__":
    asyncio.run(populate_zakynthos())

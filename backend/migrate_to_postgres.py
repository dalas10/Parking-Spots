"""Migrate data from SQLite to PostgreSQL."""
import asyncio
import sqlite3
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text

# Source: SQLite
SQLITE_DB = "parkingspots.db"

# Destination: PostgreSQL
POSTGRES_URL = "postgresql+asyncpg://parking_user:parking_secure_2026@localhost:5432/parkingspots"

async def migrate_data():
    """Migrate all data from SQLite to PostgreSQL."""
    print("🔄 Starting migration from SQLite to PostgreSQL...")
    
    # Connect to PostgreSQL
    pg_engine = create_async_engine(POSTGRES_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(pg_engine, class_=AsyncSession, expire_on_commit=False)
    
    # Connect to SQLite
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    sqlite_conn.row_factory = sqlite3.Row
    cursor = sqlite_conn.cursor()
    
    async with AsyncSessionLocal() as session:
       # Create tables first (using the existing models)
        print("\n1️⃣ Creating PostgreSQL schema...")
        from app.db.base import Base
        async with pg_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        print("   ✓ Schema created")
        
        # Migrate users
        print("\n2️⃣ Migrating users...")
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        for user in users:
            user_dict = dict(user)
            # Convert SQLite integers to PostgreSQL booleans
            user_dict['is_active'] = bool(user_dict['is_active'])
            user_dict['is_verified'] = bool(user_dict['is_verified'])
            # Convert string floats to actual floats
            if user_dict.get('latitude'):
                user_dict['latitude'] = float(user_dict['latitude'])
            if user_dict.get('longitude'):
                user_dict['longitude'] = float(user_dict['longitude'])
                
            await session.execute(text("""
                INSERT INTO users (id, email, hashed_password, full_name, phone_number, profile_image,
                                 role, is_active, is_verified, oauth_provider, oauth_id, stripe_customer_id,
                                 latitude, longitude, created_at, updated_at)
                VALUES (:id, :email, :hashed_password, :full_name, :phone_number, :profile_image,
                        :role, :is_active, :is_verified, :oauth_provider, :oauth_id, :stripe_customer_id,
                        :latitude, :longitude, :created_at, :updated_at)
            """), user_dict)
        
        await session.commit()
        print(f"   ✓ Migrated {len(users)} users")
        
        # Migrate parking spots
        print("\n3️⃣ Migrating parking spots...")
        cursor.execute("SELECT * FROM parking_spots")
        spots = cursor.fetchall()
        
        for spot in spots:
            spot_dict = dict(spot)
            # Convert SQLite integers to PostgreSQL booleans
            spot_dict['is_covered'] = bool(spot_dict['is_covered'])
            spot_dict['has_ev_charging'] = bool(spot_dict['has_ev_charging'])
            spot_dict['has_security'] = bool(spot_dict['has_security'])
            spot_dict['has_lighting'] = bool(spot_dict['has_lighting'])
            spot_dict['is_handicap_accessible'] = bool(spot_dict['is_handicap_accessible'])
            spot_dict['is_active'] = bool(spot_dict['is_active'])
            spot_dict['is_available'] = bool(spot_dict['is_available'])
            
            await session.execute(text("""
                INSERT INTO parking_spots (id, owner_id, title, description, spot_type, vehicle_size,
                                         address, city, state, zip_code, country, latitude, longitude,
                                         hourly_rate, daily_rate, monthly_rate, is_covered, has_ev_charging,
                                         has_security, has_lighting, is_handicap_accessible, images,
                                         is_active, is_available, operating_hours, access_instructions,
                                         total_bookings, average_rating, total_reviews, created_at, updated_at)
                VALUES (:id, :owner_id, :title, :description, :spot_type, :vehicle_size,
                        :address, :city, :state, :zip_code, :country, :latitude, :longitude,
                        :hourly_rate, :daily_rate, :monthly_rate, :is_covered, :has_ev_charging,
                        :has_security, :has_lighting, :is_handicap_accessible, :images,
                        :is_active, :is_available, :operating_hours, :access_instructions,
                        :total_bookings, :average_rating, :total_reviews, :created_at, :updated_at)
            """), spot_dict)
        
        await session.commit()
        print(f"   ✓ Migrated {len(spots)} parking spots")
        
        # Migrate bookings
        print("\n4️⃣ Migrating bookings...")
        cursor.execute("SELECT * FROM bookings")
        bookings = cursor.fetchall()
        
        if bookings:
            for booking in bookings:
                await session.execute(text("""
                    INSERT INTO bookings (id, user_id, parking_spot_id, start_time, end_time, status,
                                        total_amount, service_fee, owner_payout, payment_intent_id,
                                        payment_status, vehicle_plate, vehicle_make, vehicle_model,
                                        vehicle_color, special_requests, cancellation_reason,
                                        checked_in_at, checked_out_at, created_at, updated_at)
                    VALUES (:id, :user_id, :parking_spot_id, :start_time, :end_time, :status,
                            :total_amount, :service_fee, :owner_payout, :payment_intent_id,
                            :payment_status, :vehicle_plate, :vehicle_make, :vehicle_model,
                            :vehicle_color, :special_requests, :cancellation_reason,
                            :checked_in_at, :checked_out_at, :created_at, :updated_at)
                """), dict(booking))
            
            await session.commit()
            print(f"   ✓ Migrated {len(bookings)} bookings")
        else:
            print("   ℹ No bookings to migrate")
        
        # Migrate reviews
        print("\n5️⃣ Migrating reviews...")
        cursor.execute("SELECT * FROM reviews")
        reviews = cursor.fetchall()
        
        if reviews:
            for review in reviews:
                await session.execute(text("""
                    INSERT INTO reviews (id, user_id, parking_spot_id, booking_id, rating, comment,
                                       owner_response, created_at, updated_at)
                    VALUES (:id, :user_id, :parking_spot_id, :booking_id, :rating, :comment,
                            :owner_response, :created_at, :updated_at)
                """), dict(review))
            
            await session.commit()
            print(f"   ✓ Migrated {len(reviews)} reviews")
        else:
            print("   ℹ No reviews to migrate")
    
    sqlite_conn.close()
    await pg_engine.dispose()
    
    print("\n✅ Migration completed successfully!")
    print("\n📊 Summary:")
    print(f"   • Users: {len(users)}")
    print(f"   • Parking Spots: {len(spots)}")
    print(f"   • Bookings: {len(bookings) if bookings else 0}")
    print(f"   • Reviews: {len(reviews) if reviews else 0}")
    print("\n🚀 PostgreSQL database is ready!")
    print("   Connection: postgresql+asyncpg://parking_user:***@localhost:5432/parkingspots")

if __name__ == "__main__":
    asyncio.run(migrate_data())

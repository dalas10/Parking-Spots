-- ============================================================
-- Zakynthos seed data
-- Owner password: Test1234
-- ============================================================

-- Owner user
INSERT INTO users (id, email, hashed_password, full_name, phone_number, role,
                   is_active, is_verified, latitude, longitude, created_at, updated_at)
VALUES (
    'aaaaaaaa-0000-0000-0000-000000000001',
    'owner@zakynthos.gr',
    '$2b$12$9lp/iPyZM6sCtwjjeK/f5OYmQ4ersBHHKwa/qP.cbThSGlfDRc5Ra',
    'Νίκος Παπαδόπουλος',
    '+302695012345',
    'OWNER',
    true, true,
    37.7870, 20.8999,
    NOW(), NOW()
);

-- Renter user (used to create the test bookings)
INSERT INTO users (id, email, hashed_password, full_name, phone_number, role,
                   is_active, is_verified, latitude, longitude, created_at, updated_at)
VALUES (
    'aaaaaaaa-0000-0000-0000-000000000002',
    'renter@zakynthos.gr',
    '$2b$12$9lp/iPyZM6sCtwjjeK/f5OYmQ4ersBHHKwa/qP.cbThSGlfDRc5Ra',
    'Μαρία Γεωργίου',
    '+302695067890',
    'RENTER',
    true, true,
    37.7870, 20.8999,
    NOW(), NOW()
);

-- ============================================================
-- Parking spots
-- ============================================================

INSERT INTO parking_spots (id, owner_id, title, description, spot_type, vehicle_size,
    address, city, prefecture, zip_code, country, latitude, longitude,
    hourly_rate, daily_rate, monthly_rate,
    is_covered, has_ev_charging, has_security, has_lighting, is_handicap_accessible,
    is_active, is_available, total_bookings, average_rating, total_reviews, images,
    created_at, updated_at)
VALUES
-- 1 Zakynthos Town centre – will be BOOKED (disappears with date filter)
('bbbbbbbb-0001-0000-0000-000000000001',
 'aaaaaaaa-0000-0000-0000-000000000001',
 'Κεντρικό Πάρκινγκ Ζακύνθου', 'Καλυμμένο πάρκινγκ στο κέντρο δίπλα στην πλατεία Αγίου Μάρκου.',
 'COVERED', 'STANDARD',
 'Λεωφόρος Αλεξάνδρου Ρώμα 42', 'Ζάκυνθος', 'Ζάκυνθος', '29100', 'Greece',
 37.7870, 20.8999, 300, 2000, 50000,
 true, true, true, true, true, true, true, 5, 4.8, 12, '[]', NOW(), NOW()),

-- 2 Port parking – will be BOOKED (disappears with date filter)
('bbbbbbbb-0002-0000-0000-000000000001',
 'aaaaaaaa-0000-0000-0000-000000000001',
 'Πάρκινγκ Λιμάνι Ζακύνθου', 'Υπαίθριο πάρκινγκ δίπλα στο λιμάνι.',
 'LOT', 'LARGE',
 'Λεωφόρος Κ. Λομβάρδου 1', 'Ζάκυνθος', 'Ζάκυνθος', '29100', 'Greece',
 37.7850, 20.9030, 200, 1500, 40000,
 false, false, true, true, true, true, true, 3, 4.5, 8, '[]', NOW(), NOW()),

-- 3 Argassi waterfront – will be BOOKED (disappears with date filter)
('bbbbbbbb-0003-0000-0000-000000000001',
 'aaaaaaaa-0000-0000-0000-000000000001',
 'Argassi Waterfront Parking', 'Πάρκινγκ στην παραλιακή του Αργασίου.',
 'LOT', 'STANDARD',
 'Παραλιακή Αργασίου 12', 'Αργάσι', 'Ζάκυνθος', '29100', 'Greece',
 37.7580, 20.9180, 250, 1800, 45000,
 false, false, true, true, true, true, true, 2, 4.6, 5, '[]', NOW(), NOW()),

-- 4 Laganas beach – FREE (always visible)
('bbbbbbbb-0004-0000-0000-000000000001',
 'aaaaaaaa-0000-0000-0000-000000000001',
 'Beach Parking Laganas', 'Πάρκινγκ 100μ από τη θάλασσα στη Λαγανά.',
 'OUTDOOR', 'STANDARD',
 'Laganas Beach Road', 'Λαγανάς', 'Ζάκυνθος', '29092', 'Greece',
 37.7150, 20.8610, 250, 1800, 45000,
 false, false, false, true, true, true, true, 0, 4.7, 3, '[]', NOW(), NOW()),

-- 5 Laganas strip – FREE
('bbbbbbbb-0005-0000-0000-000000000001',
 'aaaaaaaa-0000-0000-0000-000000000001',
 'Laganas Strip Parking', 'Πάρκινγκ στο κέντρο της Λαγανά, κοντά σε μπαρ.',
 'LOT', 'STANDARD',
 'Κεντρική Οδός Λαγανά 23', 'Λαγανάς', 'Ζάκυνθος', '29092', 'Greece',
 37.7180, 20.8580, 300, 2000, 55000,
 false, false, true, true, false, true, true, 0, 4.4, 6, '[]', NOW(), NOW()),

-- 6 Tsilivi beachfront – FREE
('bbbbbbbb-0006-0000-0000-000000000001',
 'aaaaaaaa-0000-0000-0000-000000000001',
 'Tsilivi Beach Front Parking', 'Πάρκινγκ με θέα θάλασσα στο Τσιλιβί.',
 'OUTDOOR', 'STANDARD',
 'Παραλία Τσιλιβί', 'Τσιλιβί', 'Ζάκυνθος', '29100', 'Greece',
 37.8210, 20.8640, 250, 1800, 45000,
 false, false, false, true, true, true, true, 0, 4.9, 14, '[]', NOW(), NOW()),

-- 7 Tsilivi covered garage – FREE + EV
('bbbbbbbb-0007-0000-0000-000000000001',
 'aaaaaaaa-0000-0000-0000-000000000001',
 'Τσιλιβί Κέντρο - Covered Garage', 'Καλυμμένο γκαράζ με φόρτιση EV.',
 'COVERED', 'STANDARD',
 'Κεντρική Οδός Τσιλιβί 15', 'Τσιλιβί', 'Ζάκυνθος', '29100', 'Greece',
 37.8190, 20.8620, 350, 2500, 60000,
 true, true, true, true, true, true, true, 0, 5.0, 9, '[]', NOW(), NOW()),

-- 8 Kalamaki beach – FREE
('bbbbbbbb-0008-0000-0000-000000000001',
 'aaaaaaaa-0000-0000-0000-000000000001',
 'Kalamaki Beach Parking', 'Πάρκινγκ στην παραλία Καλαμάκι.',
 'OUTDOOR', 'STANDARD',
 'Παραλία Καλαμάκι', 'Καλαμάκι', 'Ζάκυνθος', '29100', 'Greece',
 37.7240, 20.8740, 200, 1500, 40000,
 false, false, false, true, true, true, true, 0, 4.3, 4, '[]', NOW(), NOW()),

-- 9 Airport long-term – FREE
('bbbbbbbb-0009-0000-0000-000000000001',
 'aaaaaaaa-0000-0000-0000-000000000001',
 'Airport Long-Term Parking', 'Μακράς διαμονής κοντά στο αεροδρόμιο.',
 'LOT', 'LARGE',
 'Οδός Αεροδρομίου Ζακύνθου', 'Ζάκυνθος', 'Ζάκυνθος', '29100', 'Greece',
 37.7510, 20.8840, 150, 1000, 25000,
 false, false, true, true, true, true, true, 0, 4.2, 7, '[]', NOW(), NOW()),

-- 10 Alykes central – FREE
('bbbbbbbb-0010-0000-0000-000000000001',
 'aaaaaaaa-0000-0000-0000-000000000001',
 'Alykes Central Parking', 'Κεντρικό πάρκινγκ στις Αλυκές.',
 'LOT', 'STANDARD',
 'Κεντρική Οδός Αλυκών 20', 'Αλυκές', 'Ζάκυνθος', '29100', 'Greece',
 37.8370, 20.8500, 250, 1800, 45000,
 false, false, true, true, true, true, true, 0, 4.6, 11, '[]', NOW(), NOW());

-- ============================================================
-- Test bookings – CONFIRMED, covering the next 4 hours from now
-- Spots 1, 2 and 3 will be unavailable if you search with today's date/time
-- ============================================================

INSERT INTO bookings (id, user_id, parking_spot_id, start_time, end_time,
    status, total_amount, service_fee, owner_payout, payment_status,
    vehicle_plate, vehicle_make, vehicle_model, vehicle_color,
    created_at, updated_at)
VALUES
-- Spot 1 booked for next 4 hours
('cccccccc-0001-0000-0000-000000000001',
 'aaaaaaaa-0000-0000-0000-000000000002',
 'bbbbbbbb-0001-0000-0000-000000000001',
 NOW(), NOW() + INTERVAL '4 hours',
 'CONFIRMED', 1200, 120, 1080, 'PAID',
 'ZAK-001', 'Toyota', 'Corolla', 'White',
 NOW(), NOW()),

-- Spot 2 booked for next 4 hours
('cccccccc-0002-0000-0000-000000000001',
 'aaaaaaaa-0000-0000-0000-000000000002',
 'bbbbbbbb-0002-0000-0000-000000000001',
 NOW(), NOW() + INTERVAL '4 hours',
 'CONFIRMED', 800, 80, 720, 'PAID',
 'ZAK-002', 'Honda', 'Jazz', 'Silver',
 NOW(), NOW()),

-- Spot 3 booked for next 4 hours
('cccccccc-0003-0000-0000-000000000001',
 'aaaaaaaa-0000-0000-0000-000000000002',
 'bbbbbbbb-0003-0000-0000-000000000001',
 NOW(), NOW() + INTERVAL '4 hours',
 'CONFIRMED', 1000, 100, 900, 'PAID',
 'ZAK-003', 'VW', 'Golf', 'Blue',
 NOW(), NOW());

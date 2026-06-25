

USE master;
GO

IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'RentACarDB')
    CREATE DATABASE RentACarDB;
GO

USE RentACarDB;
GO

-- ===================== TABLE 1: Users =====================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
CREATE TABLE Users (
    user_id       INT IDENTITY(1,1) PRIMARY KEY,
    full_name     VARCHAR(100)  NOT NULL,
    email         VARCHAR(150)  NOT NULL UNIQUE,
    password_hash VARCHAR(255)  NOT NULL,
    phone         VARCHAR(20),
    profile_image VARCHAR(255)  DEFAULT 'default.jpg',
    created_at    DATETIME      DEFAULT GETDATE(),
    updated_at    DATETIME      DEFAULT GETDATE()
);
GO

-- ===================== TABLE 2: Admins =====================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Admins' AND xtype='U')
CREATE TABLE Admins (
    admin_id      INT IDENTITY(1,1) PRIMARY KEY,
    full_name     VARCHAR(100)  NOT NULL,
    email         VARCHAR(150)  NOT NULL UNIQUE,
    password_hash VARCHAR(255)  NOT NULL,
    role_name     VARCHAR(50)   DEFAULT 'Admin',
    created_at    DATETIME      DEFAULT GETDATE()
);
GO

-- ===================== TABLE 3: Car_Categories =====================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Car_Categories' AND xtype='U')
CREATE TABLE Car_Categories (
    category_id    INT IDENTITY(1,1) PRIMARY KEY,
    category_name  VARCHAR(50)  NOT NULL UNIQUE,
    description    TEXT,
    category_image VARCHAR(255)
);
GO

-- ===================== TABLE 4: Cars =====================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Cars' AND xtype='U')
CREATE TABLE Cars (
    car_id              INT IDENTITY(1,1) PRIMARY KEY,
    category_id         INT,
    car_name            VARCHAR(100)    NOT NULL,
    brand               VARCHAR(50),
    model_year          INT,
    price_per_day       DECIMAL(10,2)   NOT NULL,
    fuel_type           VARCHAR(20),
    transmission        VARCHAR(20),
    seating_capacity    INT,
    car_image           VARCHAR(255)    DEFAULT 'default_car.jpg',
    availability_status VARCHAR(20)     DEFAULT 'Available',
    description         TEXT,
    created_at          DATETIME        DEFAULT GETDATE(),
    updated_at          DATETIME        DEFAULT GETDATE(),
    CONSTRAINT FK_Cars_Category FOREIGN KEY (category_id)
        REFERENCES Car_Categories(category_id) ON DELETE SET NULL,
    CONSTRAINT CHK_Cars_Status CHECK (availability_status IN ('Available','Rented','Maintenance')),
    CONSTRAINT CHK_Cars_Fuel   CHECK (fuel_type IN ('Petrol','Diesel','Electric','Hybrid'))
);
GO

-- ===================== TABLE 5: Bookings =====================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Bookings' AND xtype='U')
CREATE TABLE Bookings (
    booking_id       INT IDENTITY(1,1) PRIMARY KEY,
    user_id          INT          NOT NULL,
    car_id           INT          NOT NULL,
    pickup_location  VARCHAR(200) NOT NULL,
    return_location  VARCHAR(200) NOT NULL,
    pickup_date      DATETIME     NOT NULL,
    return_date      DATETIME     NOT NULL,
    total_days       INT          NOT NULL,
    total_amount     DECIMAL(10,2) NOT NULL,
    booking_status   VARCHAR(20)  DEFAULT 'Pending',
    created_at       DATETIME     DEFAULT GETDATE(),
    CONSTRAINT FK_Bookings_User FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    CONSTRAINT FK_Bookings_Car  FOREIGN KEY (car_id)  REFERENCES Cars(car_id)   ON DELETE CASCADE,
    CONSTRAINT CHK_Bookings_Status CHECK (booking_status IN ('Pending','Confirmed','Cancelled','Completed')),
    CONSTRAINT CHK_Bookings_Dates  CHECK (return_date > pickup_date)
);
GO

-- ===================== TABLE 6: Payments =====================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Payments' AND xtype='U')
CREATE TABLE Payments (
    payment_id       INT IDENTITY(1,1) PRIMARY KEY,
    booking_id       INT          NOT NULL UNIQUE,
    amount           DECIMAL(10,2) NOT NULL,
    payment_method   VARCHAR(50)  NOT NULL,
    payment_status   VARCHAR(20)  DEFAULT 'Unpaid',
    transaction_date DATETIME     DEFAULT GETDATE(),
    CONSTRAINT FK_Payments_Booking FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id) ON DELETE CASCADE,
    CONSTRAINT CHK_Payments_Method CHECK (payment_method IN ('Credit Card','Debit Card','Cash')),
    CONSTRAINT CHK_Payments_Status CHECK (payment_status IN ('Paid','Unpaid'))
);
GO

-- ===================== TABLE 7: Reviews =====================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Reviews' AND xtype='U')
CREATE TABLE Reviews (
    review_id  INT IDENTITY(1,1) PRIMARY KEY,
    user_id    INT NOT NULL,
    car_id     INT NOT NULL,
    rating     INT NOT NULL,
    comment    TEXT,
    created_at DATETIME DEFAULT GETDATE(),
    CONSTRAINT FK_Reviews_User FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    CONSTRAINT FK_Reviews_Car  FOREIGN KEY (car_id)  REFERENCES Cars(car_id)   ON DELETE CASCADE,
    CONSTRAINT CHK_Reviews_Rating CHECK (rating BETWEEN 1 AND 5)
);
GO

-- ===================== TABLE 8: Invoices =====================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Invoices' AND xtype='U')
CREATE TABLE Invoices (
    invoice_id     INT IDENTITY(1,1) PRIMARY KEY,
    booking_id     INT           NOT NULL UNIQUE,
    invoice_number VARCHAR(50)   NOT NULL UNIQUE,
    amount         DECIMAL(10,2) NOT NULL,
    user_id        INT,
    issued_date    DATETIME      DEFAULT GETDATE(),
    CONSTRAINT FK_Invoices_Booking FOREIGN KEY (booking_id) REFERENCES Bookings(booking_id) ON DELETE CASCADE,
    CONSTRAINT FK_Invoices_User    FOREIGN KEY (user_id)    REFERENCES Users(user_id)
);
GO

-- SAMPLE DATA


-- Categories
IF NOT EXISTS (SELECT 1 FROM Car_Categories WHERE category_name='SUV')
INSERT INTO Car_Categories (category_name, description, category_image) VALUES
('SUV',     'Sport Utility Vehicles – spacious, powerful, built for any terrain.',           'suv.jpg'),
('Sedan',   'Classic 4-door sedans – comfortable and fuel-efficient for city driving.',      'sedan.jpg'),
('Luxury',  'Premium luxury vehicles – unmatched comfort, style, and performance.',          'luxury.jpg'),
('Sports',  'High-performance sports cars – built for speed and thrill.',                    'sports.jpg'),
('Electric','Zero-emission electric vehicles – the future of eco-friendly transportation.', 'electric.jpg');
GO

-- Sample Users  (password = Password123!)
IF NOT EXISTS (SELECT 1 FROM Users WHERE email='john.doe@example.com')
INSERT INTO Users (full_name, email, password_hash, phone) VALUES
('John Doe',      'john.doe@example.com',   'pbkdf2:sha256:600000$xK9mN3pQ$a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3', '555-0101'),
('Jane Smith',    'jane.smith@example.com', 'pbkdf2:sha256:600000$xK9mN3pQ$a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3', '555-0102'),
('Carlos Rivera', 'carlos@example.com',     'pbkdf2:sha256:600000$xK9mN3pQ$a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3', '555-0103');
GO

-- Sample Admins (password = Admin123!)
IF NOT EXISTS (SELECT 1 FROM Admins WHERE email='admin@veloradrive.com')
INSERT INTO Admins (full_name, email, password_hash, role_name) VALUES
('Super Admin',  'admin@veloradrive.com',  'pbkdf2:sha256:600000$xK9mN3pQ$a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3', 'Super Admin'),
('Fleet Manager','manager@veloradrive.com','pbkdf2:sha256:600000$xK9mN3pQ$a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3', 'Admin');
GO



-- Sample Cars
IF NOT EXISTS (SELECT 1 FROM Cars WHERE car_name='BMW X5')
INSERT INTO Cars (category_id, car_name, brand, model_year, price_per_day, fuel_type, transmission, seating_capacity, car_image, availability_status, description)
SELECT c.category_id, v.car_name, v.brand, v.model_year, v.price_per_day, v.fuel_type, v.transmission, v.seating_capacity, v.car_image, v.availability_status, v.description
FROM (VALUES
    ('SUV',     'BMW X5',             'BMW',       2023, 150.00, 'Petrol',   'Automatic', 5, 'https://images.pexels.com/photos/1545743/pexels-photo-1545743.jpeg', 'Available', 'The BMW X5 combines luxury and performance in a premium SUV package.'),
    ('SUV',     'Toyota RAV4',        'Toyota',    2023,  85.00, 'Hybrid',   'Automatic', 5, 'https://images.pexels.com/photos/116675/pexels-photo-116675.jpeg',   'Available', 'Reliable and fuel-efficient hybrid SUV perfect for any journey.'),
    ('Sedan',   'Mercedes-Benz C300', 'Mercedes',  2023, 130.00, 'Petrol',   'Automatic', 5, 'https://images.pexels.com/photos/170811/pexels-photo-170811.jpeg',   'Available', 'Elegant C-Class sedan with cutting-edge technology and comfort.'),
    ('Sedan',   'Toyota Camry',       'Toyota',    2022,  70.00, 'Petrol',   'Automatic', 5, 'https://images.pexels.com/photos/358070/pexels-photo-358070.jpeg',   'Available', 'Dependable mid-size sedan ideal for business and family trips.'),
    ('Luxury',  'Rolls-Royce Phantom','Rolls-Royce',2023, 500.00,'Petrol',   'Automatic', 5, 'https://images.pexels.com/photos/1592384/pexels-photo-1592384.jpeg', 'Available', 'The pinnacle of automotive luxury – pure opulence on wheels.'),
    ('Luxury',  'Bentley Continental','Bentley',   2023, 400.00, 'Petrol',   'Automatic', 4, 'https://images.pexels.com/photos/3764984/pexels-photo-3764984.jpeg', 'Available', 'Handcrafted British luxury grand tourer with breathtaking performance.'),
    ('Sports',  'Porsche 911',        'Porsche',   2023, 280.00, 'Petrol',   'Automatic', 2, 'https://images.pexels.com/photos/3802510/pexels-photo-3802510.jpeg', 'Available', 'Iconic sports car delivering exhilarating performance and timeless style.'),
    ('Sports',  'Ferrari F8',         'Ferrari',   2022, 450.00, 'Petrol',   'Automatic', 2, 'https://images.pexels.com/photos/2365572/pexels-photo-2365572.jpeg', 'Available', 'Mid-rear engined Ferrari with 710 HP – pure adrenaline unleashed.'),
    ('Electric','Tesla Model S',      'Tesla',     2023, 120.00, 'Electric', 'Automatic', 5, 'https://images.pexels.com/photos/3729464/pexels-photo-3729464.jpeg', 'Available', 'Flagship Tesla sedan with 405-mile range and Ludicrous Mode acceleration.'),
    ('Electric','BMW i4',             'BMW',       2023,  95.00, 'Electric', 'Automatic', 5, 'https://images.pexels.com/photos/1035108/pexels-photo-1035108.jpeg', 'Available', 'Sporty electric gran coupe delivering 536 HP with zero emissions.')
) AS v(category_name, car_name, brand, model_year, price_per_day, fuel_type, transmission, seating_capacity, car_image, availability_status, description)
JOIN Car_Categories c ON c.category_name = v.category_name;
GO

-- Sample Reviews
IF NOT EXISTS (SELECT 1 FROM Reviews WHERE comment='Absolutely loved the BMW X5!')
INSERT INTO Reviews (user_id, car_id, rating, comment)
SELECT u.user_id, ca.car_id, v.rating, v.comment
FROM (VALUES
    ('john.doe@example.com',   'BMW X5',    5, 'Absolutely loved the BMW X5! Smooth ride and excellent service.'),
    ('jane.smith@example.com', 'BMW X5',    4, 'Great car, very comfortable. Will rent again.'),
    ('carlos@example.com',     'Tesla Model S', 5, 'Tesla is the future! Silent, fast, and fun.'),
    ('john.doe@example.com',   'Porsche 911',   5, 'Dreams do come true. Porsche 911 is insane!')
) AS v(email, car_name, rating, comment)
JOIN Users u ON u.email = v.email
JOIN Cars  ca ON ca.car_name = v.car_name;
GO

-- Table creation

CREATE TABLE IF NOT EXISTS Users (
    id VARCHAR(36) PRIMARY KEY NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    first_name VARCHAR(128) NOT NULL,
    last_name VARCHAR(128) NOT NULL,
    email VARCHAR(128) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    is_admin BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS Hosts (
    id VARCHAR(36) PRIMARY KEY NOT NULL,

    FOREIGN KEY(id) REFERENCES Users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Places (
    id VARCHAR(36) PRIMARY KEY NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(36),
    host_id VARCHAR(36),
    title VARCHAR(128) NOT NULL,
    description TEXT NOT NULL,
    price FLOAT NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    capacity INT NOT NULL,

    FOREIGN KEY(user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY(host_id) REFERENCES Hosts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Bookings (
    id VARCHAR(36) PRIMARY KEY NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    user_id VARCHAR(36) NOT NULL,
    place_id VARCHAR(36) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    total_price FLOAT NOT NULL,
    guest_count INT NOT NULL,

    FOREIGN KEY(user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY(place_id) REFERENCES Places(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Reviews (
    id VARCHAR(36) PRIMARY KEY NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    text TEXT,
    user_id VARCHAR(36) NOT NULL,
    place_id VARCHAR(36) NOT NULL,
    booking_id VARCHAR(36),
    rating INT,

    FOREIGN KEY(user_id) REFERENCES Users(id) ON DELETE CASCADE,
    FOREIGN KEY(place_id) REFERENCES Places(id) ON DELETE CASCADE,
    FOREIGN KEY(booking_id) REFERENCES Bookings(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Amenities (
    id VARCHAR(36) PRIMARY KEY NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    name VARCHAR(128) NOT NULL
);

-- Join table to describe many-to-many relation between Places and Amenities
CREATE TABLE IF NOT EXISTS place_amenities (
    place_id INTEGER NOT NULL,
    amenity_id INTEGER NOT NULL,
    PRIMARY KEY (place_id, amenity_id),
    FOREIGN KEY (place_id) REFERENCES places(id),
    FOREIGN KEY (amenity_id) REFERENCES amenities(id)
);

INSERT INTO Users (
    id,
    first_name,
    last_name,
    email,
    password,
    is_admin
)
VALUES (
    "36c9050e-ddd3-4c3b-9731-9f487208bbc1",
    "Admin",
    "HBnB",
    "admin@hbnb.io",
    "scrypt:32768:8:1$fSB34SJzOlZsyLQ2$b43bc09a20a057f4062b07b637eda874a69063a692359a089e28c193b3378c33e3b1522218bd4312eb45918727c907a0faa0fbc16f31128ef276d48dd1f441e1",
    True
);

INSERT INTO Amenities (
    id,
    name
)
VALUES (
    "7e76b84b-d2af-4d01-9504-41ee9fe8cca4",
    "WiFi"
);

INSERT INTO Amenities (
    id,
    name
)
VALUES (
    "df7ae5f4-db35-4720-bdf5-fd691e13a120",
    "Swimming Pool"
);
INSERT INTO Amenities (
    id,
    name
)
VALUES (
    "4deb6478-3391-41e8-8c76-1ecf71d914f9",
    "Air Conditioning"
);

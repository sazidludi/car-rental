from pathlib import Path
import sqlite3


DB_PATH = Path(__file__).resolve().parent / "driveshare.db"

# helper for db connections
def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

# starts db and makes table if needed
def init_db():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        # tables
        """
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL DEFAULT 1,
            make TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            mileage INTEGER NOT NULL,
            location TEXT NOT NULL,
            daily_price REAL NOT NULL,
            availability_start TEXT NOT NULL,
            availability_end TEXT NOT NULL,
            description TEXT NOT NULL
        )
        """
    )
    # bookings table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            car_id INTEGER NOT NULL,
            renter_id INTEGER NOT NULL DEFAULT 1,
            owner_id INTEGER NOT NULL DEFAULT 1,
            start_date TEXT NOT NULL,
            end_date TEXT NOT NULL,
            total_price REAL NOT NULL,
            is_paid INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    connection.commit()
    connection.close()


# saves car listings
def save_car(make, model, year, mileage, location, daily_price, start_date, end_date, description):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO cars (
            make,
            model,
            year,
            mileage,
            location,
            daily_price,
            availability_start,
            availability_end,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (make, model, year, mileage, location, daily_price, str(start_date), str(end_date), description),
    )
    connection.commit()
    connection.close()

# gets lsitings
def get_cars():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cars ORDER BY id DESC")
    cars = cursor.fetchall()
    connection.close()
    return cars

# updates listing with new info from edit 
def update_car(car_id, make, model, year, mileage, location, daily_price, start_date, end_date, description):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        UPDATE cars
        SET make = ?,
            model = ?,
            year = ?,
            mileage = ?,
            location = ?,
            daily_price = ?,
            availability_start = ?,
            availability_end = ?,
            description = ?
        WHERE id = ?
        """,
        (make, model, year, mileage, location, daily_price, str(start_date), str(end_date), description, car_id),
    )
    connection.commit()
    connection.close()


def has_booking_overlap(car_id, start_date, end_date):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT id
        FROM bookings
        WHERE car_id = ?
        AND start_date <= ?
        AND end_date >= ?
        LIMIT 1
        """,
        (car_id, str(end_date), str(start_date)),
    )
    booking = cursor.fetchone()
    connection.close()
    return booking is not None


def save_booking(car_id, owner_id, start_date, end_date, total_price):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO bookings (
            car_id,
            owner_id,
            start_date,
            end_date,
            total_price
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (car_id, owner_id, str(start_date), str(end_date), total_price),
    )
    connection.commit()
    booking_id = cursor.lastrowid
    connection.close()
    return booking_id


def get_bookings_for_car(car_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT *
        FROM bookings
        WHERE car_id = ?
        ORDER BY start_date
        """,
        (car_id,),
    )
    bookings = cursor.fetchall()
    connection.close()
    return bookings


def get_bookings():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM bookings ORDER BY id DESC")
    bookings = cursor.fetchall()
    connection.close()
    return bookings

# gets booking history and details
def get_booking_history():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            bookings.*,
            cars.make,
            cars.model,
            cars.year,
            cars.location
        FROM bookings
        JOIN cars ON cars.id = bookings.car_id
        ORDER BY bookings.id DESC
        """
    )
    bookings = cursor.fetchall()
    connection.close()
    return bookings

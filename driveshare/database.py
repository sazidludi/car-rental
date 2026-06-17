from pathlib import Path
import sqlite3


DB_PATH = Path(__file__).resolve().parent / "driveshare.db"

# db connection
def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection

# database setup
def init_db():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        # users table
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            email TEXT NOT NULL UNIQUE,
            role TEXT NOT NULL,
            balance REAL NOT NULL
        )
        """
    )
    cursor.execute(
        # cars table
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
    # payments table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            renter_id INTEGER NOT NULL DEFAULT 1,
            owner_id INTEGER NOT NULL DEFAULT 1,
            amount REAL NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    # notifications table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            booking_id INTEGER,
            is_read INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    # seed users
    cursor.execute(
        """
        INSERT OR IGNORE INTO users (id, email, role, balance)
        VALUES (1, 'owner@example.com', 'owner', 0)
        """
    )
    # seed renter with balance for testing
    cursor.execute(
        """
        INSERT OR IGNORE INTO users (id, email, role, balance)
        VALUES (2, 'renter@example.com', 'renter', 1000)
        """
    )
    cursor.execute("UPDATE bookings SET renter_id = 2 WHERE renter_id = 1 AND owner_id = 1")
    connection.commit()
    connection.close()


# save listing
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

# get listings
def get_cars():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM cars ORDER BY id DESC")
    cars = cursor.fetchall()
    connection.close()
    return cars

# update listing
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

# save booking
def save_booking(car_id, owner_id, start_date, end_date, total_price):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO bookings (
            car_id,
            renter_id,
            owner_id,
            start_date,
            end_date,
            total_price
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (car_id, 2, owner_id, str(start_date), str(end_date), total_price),
    )
    booking_id = cursor.lastrowid

    # renter notice
    cursor.execute(
        """
        INSERT INTO notifications (user_id, title, message, booking_id)
        VALUES (?, ?, ?, ?)
        """,
        (2, "booking confirmed", f"booking {booking_id} is reserved", booking_id),
    )

    # owner notice
    cursor.execute(
        """
        INSERT INTO notifications (user_id, title, message, booking_id)
        VALUES (?, ?, ?, ?)
        """,
        (owner_id, "new booking", f"booking {booking_id} was created", booking_id),
    )
    connection.commit()
    connection.close()
    return booking_id

# get bookings for car
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

# booking history
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


# user balance
def get_user_balance(user_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    connection.close()
    if user is None:
        return 0
    return user["balance"]


# payment history
def get_payments():
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM payments ORDER BY id DESC")
    payments = cursor.fetchall()
    connection.close()
    return payments


# add notification
def add_notification(user_id, title, message, booking_id=None):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO notifications (
            user_id,
            title,
            message,
            booking_id
        )
        VALUES (?, ?, ?, ?)
        """,
        (user_id, title, message, booking_id),
    )
    connection.commit()
    connection.close()


# get notifications
def get_notifications(user_id=None):
    connection = get_connection()
    cursor = connection.cursor()
    if user_id is None:
        cursor.execute("SELECT * FROM notifications ORDER BY id DESC")
    else:
        cursor.execute(
            "SELECT * FROM notifications WHERE user_id = ? ORDER BY id DESC",
            (user_id,),
        )
    notifications = cursor.fetchall()
    connection.close()
    return notifications


# unread count
def get_unread_count(user_id=None):
    connection = get_connection()
    cursor = connection.cursor()
    if user_id is None:
        cursor.execute("SELECT COUNT(*) AS count FROM notifications WHERE is_read = 0")
    else:
        cursor.execute(
            "SELECT COUNT(*) AS count FROM notifications WHERE user_id = ? AND is_read = 0",
            (user_id,),
        )
    row = cursor.fetchone()
    connection.close()
    return row["count"]


# mark read
def mark_notification_read(notification_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))
    connection.commit()
    connection.close()


# process payment
def process_payment(booking_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
    booking = cursor.fetchone()

    if booking is None:
        connection.close()
        return False, "booking not found", 0

    if booking["is_paid"]:
        connection.close()
        return False, "booking already paid", booking["total_price"]

    cursor.execute("SELECT * FROM users WHERE id = ?", (booking["renter_id"],))
    renter = cursor.fetchone()
    cursor.execute("SELECT * FROM users WHERE id = ?", (booking["owner_id"],))
    owner = cursor.fetchone()

    # validate users
    if renter is None or owner is None:
        connection.close()
        return False, "payment users missing", booking["total_price"]

    # check renter balance
    if renter["balance"] < booking["total_price"]:
        connection.close()
        return False, "not enough balance", booking["total_price"]

    # create payment record
    cursor.execute(
        """
        INSERT INTO payments (
            booking_id,
            renter_id,
            owner_id,
            amount,
            status
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            booking["id"],
            booking["renter_id"],
            booking["owner_id"],
            booking["total_price"],
            "paid",
        ),
    )
    # update balances and booking status
    cursor.execute(
        "UPDATE users SET balance = balance - ? WHERE id = ?",
        (booking["total_price"], booking["renter_id"]),
    )

    # transfer payment to owner
    cursor.execute(
        "UPDATE users SET balance = balance + ? WHERE id = ?",
        (booking["total_price"], booking["owner_id"]),
    )

    # mark booking as paid
    cursor.execute("UPDATE bookings SET is_paid = 1 WHERE id = ?", (booking_id,))

    # renter notice
    cursor.execute(
        """
        INSERT INTO notifications (user_id, title, message, booking_id)
        VALUES (?, ?, ?, ?)
        """,
        (
            booking["renter_id"],
            "payment sent",
            f"payment for booking {booking_id} is complete",
            booking_id,
        ),
    )

    # owner notice
    cursor.execute(
        """
        INSERT INTO notifications (user_id, title, message, booking_id)
        VALUES (?, ?, ?, ?)
        """,
        (
            booking["owner_id"],
            "payment received",
            f"payment for booking {booking_id} was received",
            booking_id,
        ),
    )
    connection.commit()
    connection.close()

    # return success
    return True, "payment complete", booking["total_price"]

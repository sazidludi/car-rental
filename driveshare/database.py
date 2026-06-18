from pathlib import Path
import hashlib
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
            balance REAL NOT NULL,
            password_hash TEXT,
            security_question_one TEXT,
            security_answer_one_hash TEXT,
            security_question_two TEXT,
            security_answer_two_hash TEXT,
            security_question_three TEXT,
            security_answer_three_hash TEXT
        )
        """
    )
    ensure_user_columns(cursor)
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
    # watchlist table
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL DEFAULT 2,
            car_id INTEGER NOT NULL,
            target_price REAL NOT NULL,
            desired_start TEXT NOT NULL,
            desired_end TEXT NOT NULL,
            is_notified INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    # seed users
    cursor.execute(
        """
        INSERT OR IGNORE INTO users (
            id,
            email,
            role,
            balance,
            password_hash,
            security_question_one,
            security_answer_one_hash,
            security_question_two,
            security_answer_two_hash,
            security_question_three,
            security_answer_three_hash
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        demo_user_values(1, "owner@example.com", "owner", 0, "owner123"),
    )
    # seed renter with balance for testing
    cursor.execute(
        """
        INSERT OR IGNORE INTO users (
            id,
            email,
            role,
            balance,
            password_hash,
            security_question_one,
            security_answer_one_hash,
            security_question_two,
            security_answer_two_hash,
            security_question_three,
            security_answer_three_hash
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        demo_user_values(2, "renter@example.com", "renter", 1000, "renter123"),
    )
    backfill_demo_user(cursor, 1, "owner123")
    backfill_demo_user(cursor, 2, "renter123")
    cursor.execute("UPDATE bookings SET renter_id = 2 WHERE renter_id = 1 AND owner_id = 1")
    connection.commit()
    connection.close()


def ensure_user_columns(cursor):
    cursor.execute("PRAGMA table_info(users)")
    columns = [row["name"] for row in cursor.fetchall()]
    needed_columns = {
        "password_hash": "TEXT",
        "security_question_one": "TEXT",
        "security_answer_one_hash": "TEXT",
        "security_question_two": "TEXT",
        "security_answer_two_hash": "TEXT",
        "security_question_three": "TEXT",
        "security_answer_three_hash": "TEXT",
    }

    # small migration
    for column_name, column_type in needed_columns.items():
        if column_name not in columns:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def hash_answer(answer):
    clean_answer = answer.strip().lower()
    return hashlib.sha256(clean_answer.encode()).hexdigest()


def demo_user_values(user_id, email, role, balance, password):
    return (
        user_id,
        email,
        role,
        balance,
        hash_password(password),
        "favorite color",
        hash_answer("blue"),
        "first pet",
        hash_answer("spot"),
        "favorite food",
        hash_answer("pizza"),
    )


def backfill_demo_user(cursor, user_id, password):
    cursor.execute(
        """
        UPDATE users
        SET password_hash = COALESCE(password_hash, ?),
            security_question_one = COALESCE(security_question_one, ?),
            security_answer_one_hash = COALESCE(security_answer_one_hash, ?),
            security_question_two = COALESCE(security_question_two, ?),
            security_answer_two_hash = COALESCE(security_answer_two_hash, ?),
            security_question_three = COALESCE(security_question_three, ?),
            security_answer_three_hash = COALESCE(security_answer_three_hash, ?)
        WHERE id = ?
        """,
        (
            hash_password(password),
            "favorite color",
            hash_answer("blue"),
            "first pet",
            hash_answer("spot"),
            "favorite food",
            hash_answer("pizza"),
            user_id,
        ),
    )


def create_user(email, password, role, questions, answers):
    connection = get_connection()
    cursor = connection.cursor()
    balance = 1000 if role == "renter" else 0

    try:
        cursor.execute(
            """
            INSERT INTO users (
                email,
                role,
                balance,
                password_hash,
                security_question_one,
                security_answer_one_hash,
                security_question_two,
                security_answer_two_hash,
                security_question_three,
                security_answer_three_hash
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                email.strip().lower(),
                role,
                balance,
                hash_password(password),
                questions[0],
                hash_answer(answers[0]),
                questions[1],
                hash_answer(answers[1]),
                questions[2],
                hash_answer(answers[2]),
            ),
        )
        user_id = cursor.lastrowid
        connection.commit()
    except sqlite3.IntegrityError:
        connection.close()
        return None, "email already registered"

    connection.close()
    return get_user(user_id), "account created"


def get_user(user_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    connection.close()
    return user


def get_user_by_email(email):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
    user = cursor.fetchone()
    connection.close()
    return user


def verify_user(email, password):
    user = get_user_by_email(email)
    if user is None:
        return None
    if user["password_hash"] != hash_password(password):
        return None
    return user


def get_recovery_user(email):
    user = get_user_by_email(email)
    if user is None:
        return None

    return {
        "id": user["id"],
        "email": user["email"],
        "question_one": user["security_question_one"],
        "answer_one_hash": user["security_answer_one_hash"],
        "question_two": user["security_question_two"],
        "answer_two_hash": user["security_answer_two_hash"],
        "question_three": user["security_question_three"],
        "answer_three_hash": user["security_answer_three_hash"],
    }


def update_password(user_id, new_password):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE id = ?",
        (hash_password(new_password), user_id),
    )
    updated = cursor.rowcount == 1
    connection.commit()
    connection.close()
    return updated


# save listing
def save_car(make, model, year, mileage, location, daily_price, start_date, end_date, description, owner_id=1):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO cars (
            owner_id,
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
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (owner_id, make, model, year, mileage, location, daily_price, str(start_date), str(end_date), description),
    )
    car_id = cursor.lastrowid
    connection.commit()
    connection.close()
    notify_watch_matches(car_id)

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
    notify_watch_matches(car_id)


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
def save_booking(car_id, owner_id, start_date, end_date, total_price, renter_id=2):
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
        (car_id, renter_id, owner_id, str(start_date), str(end_date), total_price),
    )
    booking_id = cursor.lastrowid

    # renter notice
    cursor.execute(
        """
        INSERT INTO notifications (user_id, title, message, booking_id)
        VALUES (?, ?, ?, ?)
        """,
        (renter_id, "booking confirmed", f"booking {booking_id} is reserved", booking_id),
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
def get_booking_history(user_id=None, role=None):
    connection = get_connection()
    cursor = connection.cursor()
    query = """
        SELECT
            bookings.*,
            cars.make,
            cars.model,
            cars.year,
            cars.location
        FROM bookings
        JOIN cars ON cars.id = bookings.car_id
    """
    params = []

    if user_id is not None and role == "owner":
        query += " WHERE bookings.owner_id = ?"
        params.append(user_id)
    elif user_id is not None:
        query += " WHERE bookings.renter_id = ?"
        params.append(user_id)

    query += " ORDER BY bookings.id DESC"
    cursor.execute(query, params)
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
def get_payments(user_id=None, role=None):
    connection = get_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM payments"
    params = []

    if user_id is not None and role == "owner":
        query += " WHERE owner_id = ?"
        params.append(user_id)
    elif user_id is not None:
        query += " WHERE renter_id = ?"
        params.append(user_id)

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
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


# save watch
def save_watch(car_id, target_price, desired_start, desired_end, user_id=2):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        INSERT INTO watchlist (
            user_id,
            car_id,
            target_price,
            desired_start,
            desired_end
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_id, car_id, target_price, str(desired_start), str(desired_end)),
    )
    watch_id = cursor.lastrowid
    connection.commit()
    connection.close()
    notify_watch_matches(car_id)
    return watch_id


# get watches
def get_watchlist(user_id=2):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT
            watchlist.id AS watch_id,
            watchlist.user_id,
            watchlist.car_id,
            watchlist.target_price,
            watchlist.desired_start,
            watchlist.desired_end,
            watchlist.is_notified,
            watchlist.created_at,
            cars.make,
            cars.model,
            cars.year,
            cars.location,
            cars.daily_price,
            cars.availability_start,
            cars.availability_end
        FROM watchlist
        JOIN cars ON cars.id = watchlist.car_id
        WHERE watchlist.user_id = ?
        ORDER BY watchlist.id DESC
        """,
        (user_id,),
    )
    watches = cursor.fetchall()
    connection.close()
    return watches


# remove watch
def delete_watch(watch_id):
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM watchlist WHERE id = ?", (watch_id,))
    connection.commit()
    connection.close()


# notify watchers
def notify_watch_matches(car_id=None):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT
            watchlist.*,
            cars.make,
            cars.model,
            cars.year,
            cars.daily_price,
            cars.availability_start,
            cars.availability_end
        FROM watchlist
        JOIN cars ON cars.id = watchlist.car_id
        WHERE watchlist.is_notified = 0
    """
    params = []
    if car_id is not None:
        query += " AND watchlist.car_id = ?"
        params.append(car_id)

    cursor.execute(query, params)
    watches = cursor.fetchall()

    for watch in watches:
        price_matches = watch["daily_price"] <= watch["target_price"]
        dates_match = (
            watch["availability_start"] <= watch["desired_start"]
            and watch["availability_end"] >= watch["desired_end"]
        )

        cursor.execute(
            """
            SELECT id
            FROM bookings
            WHERE car_id = ?
            AND start_date <= ?
            AND end_date >= ?
            LIMIT 1
            """,
            (watch["car_id"], watch["desired_end"], watch["desired_start"]),
        )
        has_overlap = cursor.fetchone() is not None

        if price_matches and dates_match and not has_overlap:
            car_name = f"{watch['year']} {watch['make']} {watch['model']}"
            cursor.execute(
                """
                INSERT INTO notifications (user_id, title, message, booking_id)
                VALUES (?, ?, ?, ?)
                """,
                (
                    watch["user_id"],
                    "watched car available",
                    f"{car_name} matches your watch target",
                    None,
                ),
            )
            cursor.execute(
                "UPDATE watchlist SET is_notified = 1 WHERE id = ?",
                (watch["id"],),
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
def process_payment(booking_id, renter_id=None):
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

    if renter_id is not None and booking["renter_id"] != renter_id:
        connection.close()
        return False, "this booking belongs to another renter", booking["total_price"]

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

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

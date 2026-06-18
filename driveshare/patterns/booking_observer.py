from driveshare.database import get_connection


class WatchObserver:
    def notify(self, car_id=None):
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

        # notify watchers
        for watch in watches:
            if self.watch_matches(cursor, watch):
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

    
    def watch_matches(self, cursor, watch):
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
        return price_matches and dates_match and not has_overlap

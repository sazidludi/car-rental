from datetime import date, timedelta

import streamlit as st

from driveshare.database import get_bookings_for_car, has_booking_overlap, save_booking


def render_booking(cars):
    st.subheader("booking")

    # booking message
    if st.session_state["booking_notice"]:
        st.success(st.session_state["booking_notice"])
        st.session_state["booking_notice"] = ""

    selected_car = None
    for car in cars:
        if car["id"] == st.session_state["selected_car_id"]:
            selected_car = car
            break

    if selected_car is None:
        st.info("choose a car from search results first")
        return

    st.write(f"{selected_car['year']} {selected_car['make']} {selected_car['model']}")
    st.write(f"{selected_car['location']}  ${selected_car['daily_price']} per day")

    available_start = date.fromisoformat(selected_car["availability_start"])
    available_end = date.fromisoformat(selected_car["availability_end"])
    saved_trip_dates = st.session_state["selected_trip_dates"]
    car_bookings = get_bookings_for_car(selected_car["id"])

    default_dates = (available_start, min(available_end, available_start + timedelta(days=1)))
    if len(saved_trip_dates) == 2:
        if saved_trip_dates[0] >= available_start and saved_trip_dates[1] <= available_end:
            default_dates = saved_trip_dates

    st.caption(f"listing availability  {selected_car['availability_start']} to {selected_car['availability_end']}")

    # already booked
    if car_bookings:
        st.write("booked dates")
        for booking in car_bookings:
            paid_status = "paid" if booking["is_paid"] else "unpaid"
            st.caption(f"{booking['start_date']} to {booking['end_date']}  {paid_status}")
    else:
        st.caption("no bookings yet for this car")

    with st.form("booking_form"):
        booking_dates = st.date_input(
            "booking dates",
            value=default_dates,
            min_value=available_start,
            max_value=available_end,
            key=f"booking_dates_{selected_car['id']}",
        )
        confirm_booking = st.form_submit_button("confirm booking")

    if len(booking_dates) != 2:
        st.info("choose start and end dates")
        return

    st.session_state["selected_trip_dates"] = booking_dates
    total_days = (booking_dates[1] - booking_dates[0]).days + 1
    total_price = total_days * selected_car["daily_price"]
    st.metric("estimated total", f"${total_price}")

    # save booking
    if confirm_booking:
        if total_days <= 0:
            st.error("choose a valid date range")
        elif booking_dates[0] < available_start or booking_dates[1] > available_end:
            st.error("dates must stay inside car availability")
        elif has_booking_overlap(selected_car["id"], booking_dates[0], booking_dates[1]):
            st.error("these dates are already booked")
        else:
            booking_id = save_booking(
                selected_car["id"],
                selected_car["owner_id"],
                booking_dates[0],
                booking_dates[1],
                total_price,
            )
            st.session_state["booking_notice"] = f"booking confirmed  id {booking_id}"
            st.session_state["selected_booking_id"] = booking_id
            st.session_state["page"] = "Rental History"
            st.rerun()

import streamlit as st


def render_home(cars, booking_history, unread_total, user):
    st.subheader("dashboard")

    if user["role"] == "owner":
        shown_cars = [car for car in cars if car["owner_id"] == user["id"]]
        car_label = "your cars"
        empty_message = "add a listing from the owner dashboard"
    else:
        shown_cars = cars
        car_label = "cars available"
        empty_message = "no cars are listed yet"

    total_locations = len({car["location"] for car in shown_cars})
    unpaid_count = len([booking for booking in booking_history if not booking["is_paid"]])

    # quick totals
    first, second, third, fourth = st.columns(4)
    first.metric(car_label, len(shown_cars))
    second.metric("bookings", len(booking_history))
    third.metric("unpaid", unpaid_count)
    fourth.metric("unread", unread_total)

    st.divider()
    if not shown_cars:
        st.info(empty_message)
    else:
        st.write(f"available locations  {total_locations}")

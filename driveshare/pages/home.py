import streamlit as st


def render_home(cars, booking_history, unread_total):
    st.subheader("dashboard")

    total_locations = len({car["location"] for car in cars})
    unpaid_count = len([booking for booking in booking_history if not booking["is_paid"]])

    # quick totals
    first, second, third, fourth = st.columns(4)
    first.metric("cars listed", len(cars))
    second.metric("bookings", len(booking_history))
    third.metric("unpaid", unpaid_count)
    fourth.metric("unread", unread_total)

    st.divider()
    if not cars:
        st.info("add a listing from the owner dashboard")
    else:
        st.write(f"available locations  {total_locations}")

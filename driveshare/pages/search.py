from datetime import date

import streamlit as st

from driveshare.database import has_booking_overlap, save_watch


def render_search(cars, user):
    st.subheader("search cars")

    with st.expander("filters", expanded=True):
        left, right = st.columns(2)
        location_filter = left.text_input("location")
        make_filter = left.text_input("make")
        model_filter = right.text_input("model")
        trip_dates = right.date_input("trip dates", value=st.session_state["selected_trip_dates"])
        max_price = st.slider("max daily price", 20, 500, 100)
        st.caption("watchlist uses these trip dates and max price")

    # save dates
    if len(trip_dates) == 2:
        st.session_state["selected_trip_dates"] = trip_dates

    results = []
    for car in cars:
        if location_filter and location_filter.lower() not in car["location"].lower():
            continue
        if make_filter and make_filter.lower() not in car["make"].lower():
            continue
        if model_filter and model_filter.lower() not in car["model"].lower():
            continue
        if car["daily_price"] > max_price:
            continue

        # date checks
        if len(trip_dates) == 2:
            trip_start = trip_dates[0]
            trip_end = trip_dates[1]
            available_start = date.fromisoformat(car["availability_start"])
            available_end = date.fromisoformat(car["availability_end"])

            if trip_start < available_start or trip_end > available_end:
                continue
            if has_booking_overlap(car["id"], trip_start, trip_end):
                continue

        results.append(car)

    st.metric("matches", len(results))

    if not results:
        st.info("no cars match these filters")

    # car results
    for car in results:
        with st.expander(f"{car['year']} {car['make']} {car['model']}  ${car['daily_price']}/day"):
            left, right = st.columns([2, 1])
            left.write(car["description"])
            right.write(car["location"])
            st.caption(f"available  {car['availability_start']} to {car['availability_end']}")

            book_col, watch_col = st.columns(2)

            if book_col.button("book this car", key=f"book_{car['id']}"):
                st.session_state["selected_car_id"] = car["id"]
                if len(trip_dates) == 2:
                    st.session_state["selected_trip_dates"] = trip_dates
                st.session_state["page"] = "Booking"
                st.rerun()

            # watch button
            if watch_col.button("add to watchlist", key=f"watch_{car['id']}"):
                if len(trip_dates) != 2:
                    st.error("choose start and end dates")
                else:
                    save_watch(car["id"], max_price, trip_dates[0], trip_dates[1], user["id"])
                    st.success("car added to watchlist")

from datetime import date

import streamlit as st

from driveshare.database import delete_watch, get_watchlist


def render_watchlist(cars=None):
    st.subheader("watchlist")

    if "watch_notice" in st.session_state:
        st.success(st.session_state.pop("watch_notice"))

    watches = get_watchlist()
    st.metric("watched cars", len(watches))

    if not watches:
        st.info("no watched cars yet")
        st.caption("add cars from the search page")

    # saved watches
    for watch in watches:
        status = "matched" if watch["is_notified"] else "watching"
        label = f"{watch['year']} {watch['make']} {watch['model']}  {status}"

        with st.expander(label):
            st.write(f"target price  ${watch['target_price']:.2f}")
            st.write(f"current price  ${watch['daily_price']:.2f}")
            st.write(f"desired dates  {watch['desired_start']} to {watch['desired_end']}")
            st.write(f"available  {watch['availability_start']} to {watch['availability_end']}")
            st.write(f"location  {watch['location']}")

            first, second = st.columns(2)
            if first.button("book this car", key=f"watch_book_{watch['watch_id']}"):
                st.session_state["selected_car_id"] = watch["car_id"]
                st.session_state["selected_trip_dates"] = (
                    date.fromisoformat(watch["desired_start"]),
                    date.fromisoformat(watch["desired_end"]),
                )
                st.session_state["page"] = "Booking"
                st.rerun()

            if second.button("remove watch", key=f"watch_remove_{watch['watch_id']}"):
                delete_watch(watch["watch_id"])
                st.rerun()

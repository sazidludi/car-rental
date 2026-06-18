from datetime import date, timedelta

import streamlit as st

from driveshare.database import save_car, update_car


def render_owner(cars, user):
    st.subheader("owner dashboard")

    # only for owners listings
    if user["role"] != "owner":
        st.info("only owners can manage listings")
        return

    cars = [car for car in cars if car["owner_id"] == user["id"]]

    if "owner_notice" in st.session_state:
        st.success(st.session_state.pop("owner_notice"))

    create_tab, listings_tab, edit_tab = st.tabs(["create listing", "your listings", "edit listing"])

    # create listing
    with create_tab:
        with st.form("create_listing_form"):
            left, right = st.columns(2)
            make = left.text_input("make")
            model = right.text_input("model")
            year = left.number_input("year", min_value=2000, max_value=2026, value=2020)
            daily_price = right.number_input("daily price", min_value=20, max_value=300, value=65)
            mileage = left.number_input("mileage", min_value=0, value=25000)
            location = st.text_input("pickup location")
            availability = st.date_input("availability", value=(date.today(), date.today() + timedelta(days=7)))
            description = st.text_area("description")
            save_listing = st.form_submit_button("save listing")

        if save_listing:
            if not make or not model or not location or not description:
                st.error("fill in all listing fields")
            elif len(availability) != 2:
                st.error("choose start and end dates")
            else:
                save_car(make, model, year, mileage, location, daily_price, availability[0], availability[1], description, user["id"])
                st.session_state["owner_notice"] = "listing saved"
                st.rerun()

    # listing cards
    with listings_tab:
        st.metric("total listings", len(cars))
        if not cars:
            st.info("no listings yet")

        for car in cars:
            with st.expander(f"{car['year']} {car['make']} {car['model']}"):
                left, right = st.columns(2)
                left.write(f"price per day  ${car['daily_price']}")
                left.write(f"mileage  {car['mileage']}")
                right.write(f"location  {car['location']}")
                right.write(f"available  {car['availability_start']} to {car['availability_end']}")
                st.write(car["description"])

    # edit listing
    with edit_tab:
        if not cars:
            st.info("create a listing before editing")
            return

        car_labels = {f"{car['id']}  {car['year']} {car['make']} {car['model']}": car for car in cars}
        selected_label = st.selectbox("choose listing", list(car_labels.keys()))
        selected_car = car_labels[selected_label]
        edit_start = date.fromisoformat(selected_car["availability_start"])
        edit_end = date.fromisoformat(selected_car["availability_end"])

        with st.form("edit_listing_form"):
            edit_make = st.text_input("edit make", value=selected_car["make"])
            edit_model = st.text_input("edit model", value=selected_car["model"])
            edit_year = st.number_input("edit year", min_value=2000, max_value=2026, value=selected_car["year"])
            edit_mileage = st.number_input("edit mileage", min_value=0, value=selected_car["mileage"])
            edit_price = st.number_input("edit daily price", min_value=20, max_value=300, value=int(selected_car["daily_price"]))
            edit_location = st.text_input("edit location", value=selected_car["location"])
            edit_dates = st.date_input("edit availability", value=(edit_start, edit_end))
            edit_description = st.text_area("edit description", value=selected_car["description"])
            update_listing = st.form_submit_button("update listing")

        if update_listing:
            if not edit_make or not edit_model or not edit_location or not edit_description:
                st.error("fill in all listing fields")
            elif len(edit_dates) != 2:
                st.error("choose start and end dates")
            else:
                update_car(
                    selected_car["id"],
                    edit_make,
                    edit_model,
                    edit_year,
                    edit_mileage,
                    edit_location,
                    edit_price,
                    edit_dates[0],
                    edit_dates[1],
                    edit_description,
                )
                st.session_state["owner_notice"] = "listing updated"
                st.rerun()

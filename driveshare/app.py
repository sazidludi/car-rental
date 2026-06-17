from datetime import date, timedelta
from importlib import reload

import streamlit as st

import driveshare.database as database

database = reload(database)

from driveshare.database import (
    get_booking_history,
    get_bookings_for_car,
    get_cars,
    get_payments,
    get_user_balance,
    has_booking_overlap,
    init_db,
    process_payment,
    save_booking,
    save_car,
    update_car,
)


st.set_page_config(page_title="DriveShare", layout="wide")
init_db()

# session state
if "page" not in st.session_state:
    st.session_state["page"] = "Home"
if "selected_car_id" not in st.session_state:
    st.session_state["selected_car_id"] = None
if "booking_notice" not in st.session_state:
    st.session_state["booking_notice"] = ""
if "selected_trip_dates" not in st.session_state: 
    st.session_state["selected_trip_dates"] = (date.today(), date.today() + timedelta(days=2))
if "selected_booking_id" not in st.session_state:
    st.session_state["selected_booking_id"] = None
if "payment_notice" not in st.session_state:
    st.session_state["payment_notice"] = ""

# sidebar
pages = ["Home", "Search Cars", "Booking", "Rental History", "Owner Dashboard", "Messages"]
st.sidebar.title("DriveShare")
st.sidebar.caption("car sharing dashboard")
current_page = st.session_state["page"]
if current_page not in pages:
    current_page = "Home"
st.session_state["page"] = st.sidebar.radio("navigation", pages, index=pages.index(current_page))

# main
st.title("DriveShare")
st.caption("peer to peer car rental")

# page data
cars = get_cars()
booking_history = get_booking_history()
renter_balance = get_user_balance(2)
owner_balance = get_user_balance(1)

# home dashboard
if st.session_state["page"] == "Home":
    st.subheader("dashboard")
    total_locations = len({car["location"] for car in cars})
    unpaid_count = len([booking for booking in booking_history if not booking["is_paid"]])
    first, second, third = st.columns(3)
    first.metric("cars listed", len(cars))
    second.metric("bookings", len(booking_history))
    third.metric("unpaid", unpaid_count)

    st.divider()
    if not cars:
        st.info("add a listing from the owner dashboard")
    else:
        st.write(f"available locations  {total_locations}")

# search page
if st.session_state["page"] == "Search Cars":
    st.subheader("search cars")

    with st.expander("filters", expanded=True):
        left, right = st.columns(2)
        location_filter = left.text_input("location")
        make_filter = left.text_input("make")
        model_filter = right.text_input("model")
        trip_dates = right.date_input("trip dates", value=st.session_state["selected_trip_dates"])
        max_price = st.slider("max daily price", 20, 500, 100)

    # save trip dates
    if len(trip_dates) == 2:
        st.session_state["selected_trip_dates"] = trip_dates

    # search filters
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

        # availability check
        if len(trip_dates) == 2:
            trip_start = trip_dates[0]
            trip_end = trip_dates[1]
            available_start = date.fromisoformat(car["availability_start"])
            available_end = date.fromisoformat(car["availability_end"])
            if trip_start < available_start or trip_end > available_end:
                continue
            # overlap check
            if has_booking_overlap(car["id"], trip_start, trip_end):
                continue

        results.append(car)

    st.metric("matches", len(results))

    if not results:
        st.info("no cars match these filters")

    # results
    for car in results:
        with st.expander(f"{car['year']} {car['make']} {car['model']}  ${car['daily_price']}/day"):
            left, right = st.columns([2, 1])
            left.write(car["description"])
            right.write(car["location"])
            st.caption(f"available  {car['availability_start']} to {car['availability_end']}")
            if st.button("book this car", key=f"book_{car['id']}"):
                st.session_state["selected_car_id"] = car["id"]
                if len(trip_dates) == 2:
                    st.session_state["selected_trip_dates"] = trip_dates
                st.session_state["page"] = "Booking"
                st.rerun()

# booking page
if st.session_state["page"] == "Booking":
    st.subheader("booking")

    # booking notice
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
    else:
        st.write(f"{selected_car['year']} {selected_car['make']} {selected_car['model']}")
        st.write(f"{selected_car['location']}  ${selected_car['daily_price']} per day")
       
        # car availability
        available_start = date.fromisoformat(selected_car["availability_start"])
        available_end = date.fromisoformat(selected_car["availability_end"])
        saved_trip_dates = st.session_state["selected_trip_dates"]
        car_bookings = get_bookings_for_car(selected_car["id"])

        # default dates
        default_dates = (available_start, min(available_end, available_start + timedelta(days=1)))
        if len(saved_trip_dates) == 2:
            if saved_trip_dates[0] >= available_start and saved_trip_dates[1] <= available_end:
                default_dates = saved_trip_dates
        # listing dates
        st.caption(f"listing availability  {selected_car['availability_start']} to {selected_car['availability_end']}")

        # booked dates
        if car_bookings:
            st.write("booked dates")
            for booking in car_bookings:
                paid_status = "paid" if booking["is_paid"] else "unpaid"
                st.caption(f"{booking['start_date']} to {booking['end_date']}  {paid_status}")
        else:
            st.caption("no bookings yet for this car")

        # booking form
        with st.form("booking_form"):
            booking_dates = st.date_input(
                "booking dates",
                value=default_dates,
                min_value=available_start,
                max_value=available_end,
                key=f"booking_dates_{selected_car['id']}",
            )
            confirm_booking = st.form_submit_button("confirm booking")

        # save booking
        if len(booking_dates) == 2:
            st.session_state["selected_trip_dates"] = booking_dates
            total_days = (booking_dates[1] - booking_dates[0]).days + 1
            total_price = total_days * selected_car["daily_price"]
            st.metric("estimated total", f"${total_price}")

            # booking checks
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
        else:
            st.info("choose start and end dates")




if st.session_state["page"] == "Rental History":
    st.subheader("rental history")
    if st.session_state["booking_notice"]:
        st.success(st.session_state["booking_notice"])
        st.session_state["booking_notice"] = ""
    if st.session_state["payment_notice"]:
        st.success(st.session_state["payment_notice"])
        st.session_state["payment_notice"] = ""

    # booking summary in history
    history = get_booking_history()
    unpaid_count = len([booking for booking in history if not booking["is_paid"]])
    total_spent = sum(booking["total_price"] for booking in history)

    # metrics for booking
    first, second, third = st.columns(3)
    first.metric("total bookings", len(history))
    second.metric("unpaid bookings", unpaid_count)
    third.metric("total value", f"${total_spent:.2f}")

    # shows balances
    balance_left, balance_right = st.columns(2)
    balance_left.metric("renter balance", f"${renter_balance:.2f}")
    balance_right.metric("owner balance", f"${owner_balance:.2f}")

    if not history:
        st.info("no bookings yet")


    # history rows
    for booking in history:
        paid_status = "paid" if booking["is_paid"] else "unpaid"
        start = date.fromisoformat(booking["start_date"])
        end = date.fromisoformat(booking["end_date"])
        total_days = (end - start).days + 1
        expanded = booking["id"] == st.session_state["selected_booking_id"]


        # booking details
        with st.expander(f"booking {booking['id']}  {booking['year']} {booking['make']} {booking['model']}", expanded=expanded):
            st.write(f"location  {booking['location']}")
            st.write(f"dates  {booking['start_date']} to {booking['end_date']}")
            st.write(f"days  {total_days}")
            st.write(f"total  ${booking['total_price']:.2f}")
            st.write(f"status  {paid_status}")

            # payment button
            if not booking["is_paid"]:
                if st.button("pay now", key=f"pay_{booking['id']}"):
                    success, message, amount = process_payment(booking["id"])
                    if success:
                        st.session_state["payment_notice"] = f"{message}  ${amount:.2f}"
                        st.session_state["selected_booking_id"] = booking["id"]
                        st.rerun()
                    else:
                        st.error(message)
            if st.button("view car", key=f"history_car_{booking['id']}"):
                st.session_state["selected_car_id"] = booking["car_id"]
                st.session_state["page"] = "Booking"
                st.rerun()

    # payment records
    st.subheader("payment records")
    payments = get_payments()
    if not payments:
        st.info("no payments yet")

    # payment rows
    for payment in payments:
        payment_left, payment_right = st.columns([3, 1])
        payment_left.caption(
            f"payment {payment['id']}  booking {payment['booking_id']}  "
            f"${payment['amount']:.2f}  {payment['status']}"
        )

        # view booking from payment record
        if payment_right.button("view booking", key=f"payment_booking_{payment['id']}"):
            st.session_state["selected_booking_id"] = payment["booking_id"]
            st.rerun()

if st.session_state["page"] == "Owner Dashboard":
    st.subheader("owner dashboard")

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

        # save listing
        if save_listing:
            if not make or not model or not location or not description:
                st.error("fill in all listing fields")
            elif len(availability) != 2:
                st.error("choose start and end dates")
            else:
                save_car(make, model, year, mileage, location, daily_price, availability[0], availability[1], description)
                st.session_state["owner_notice"] = "listing saved"
                st.rerun()

    # listings overview
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
        else:
            car_labels = {f"{car['id']}  {car['year']} {car['make']} {car['model']}": car for car in cars}
            selected_label = st.selectbox("choose listing", list(car_labels.keys()))
            selected_car = car_labels[selected_label]
            edit_start = date.fromisoformat(selected_car["availability_start"])
            edit_end = date.fromisoformat(selected_car["availability_end"])

            # edit form
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


            # update listing
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

if st.session_state["page"] == "Messages":
    st.subheader("messages")

    # contacts and chats
    contacts, chat = st.columns([1, 2])

    with contacts:
        st.write("conversations")
        st.info("conversations will appear here")
        st.text_input("participant")
        st.button("start chat")

    with chat:
        st.write("current chat")
        st.caption("linked to a booking or car listing")
        st.info("select a conversation or start a new one")
        st.text_area("message", placeholder="type your message here")
        first, second = st.columns(2)
        first.button("send message")
        second.button("attach booking note")

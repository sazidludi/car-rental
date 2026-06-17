from datetime import date, timedelta
from importlib import reload

import streamlit as st

import driveshare.database as database

database = reload(database)

from driveshare.database import (
    get_booking_history,
    get_cars,
    get_unread_count,
    get_user_balance,
    init_db,
)
from driveshare.pages.booking import render_booking
from driveshare.pages.history import render_history
from driveshare.pages.home import render_home
from driveshare.pages.messages import render_messages
from driveshare.pages.notif import render_notif
from driveshare.pages.owner import render_owner
from driveshare.pages.search import render_search
from driveshare.pages.watchlist import render_watchlist


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
if "notification_view" not in st.session_state:
    st.session_state["notification_view"] = "renter"

# sidebar
pages = ["Home", "Notifications", "Search Cars", "Watchlist", "Booking", "Rental History", "Owner Dashboard", "Messages"]
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
unread_total = get_unread_count()

# page routes
if st.session_state["page"] == "Home":
    render_home(cars, booking_history, unread_total)

if st.session_state["page"] == "Notifications":
    render_notif()

if st.session_state["page"] == "Search Cars":
    render_search(cars)

if st.session_state["page"] == "Watchlist":
    render_watchlist(cars)

if st.session_state["page"] == "Booking":
    render_booking(cars)

if st.session_state["page"] == "Rental History":
    render_history(renter_balance, owner_balance)

if st.session_state["page"] == "Owner Dashboard":
    render_owner(cars)

if st.session_state["page"] == "Messages":
    render_messages()

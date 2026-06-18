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
from driveshare.pages.login_page import render_login
from driveshare.pages.recovery_page import render_recovery
from driveshare.pages.register_page import render_register
from driveshare.pages.booking import render_booking
from driveshare.pages.history import render_history
from driveshare.pages.home import render_home
from driveshare.pages.messages import render_messages
from driveshare.pages.notif import render_notif
from driveshare.pages.owner import render_owner
from driveshare.pages.search import render_search
from driveshare.pages.watchlist import render_watchlist
from driveshare.patterns.session_manager import SessionManager
from driveshare.patterns.ui_mediator import UIMediator


st.set_page_config(page_title="DriveShare", layout="wide")
init_db()

# session manager
session = SessionManager()
session.setup()

# auth pages
if not session.is_logged_in():
    st.title("DriveShare")
    st.caption("peer to peer car rental")

    auth_pages = ["Login", "Register"]
    if st.session_state["auth_page"] in auth_pages:
        st.session_state["auth_page"] = st.sidebar.radio(
            "account",
            auth_pages,
            index=auth_pages.index(st.session_state["auth_page"]),
        )
    else:
        st.sidebar.write("account")
        st.sidebar.caption("password recovery")

    if st.session_state["auth_page"] == "Login":
        render_login(session)
    if st.session_state["auth_page"] == "Register":
        render_register(session)
    if st.session_state["auth_page"] == "Recover":
        render_recovery()

    st.stop()

current_user = session.current_user()
user_id = current_user["id"]
user_role = current_user["role"]

# sidebar
if user_role == "owner":
    pages = ["Home", "Notifications", "Owner Dashboard", "Rental History", "Messages"]
else:
    pages = ["Home", "Notifications", "Search Cars", "Watchlist", "Booking", "Rental History", "Messages"]

mediator = UIMediator(pages)
if mediator.render_sidebar(current_user):
    session.logout()
    st.rerun()

# main
st.title("DriveShare")
st.caption("peer to peer car rental")

# page data
cars = get_cars()
booking_history = get_booking_history(user_id, user_role)
user_balance = get_user_balance(user_id)
unread_total = get_unread_count(user_id)

# page routes
if mediator.is_page("Home"):
    render_home(cars, booking_history, unread_total)

if mediator.is_page("Notifications"):
    render_notif(current_user)

if mediator.is_page("Search Cars"):
    render_search(cars, current_user)

if mediator.is_page("Watchlist"):
    render_watchlist(cars, current_user)

if mediator.is_page("Booking"):
    render_booking(cars, current_user)

if mediator.is_page("Rental History"):
    render_history(current_user, user_balance)

if mediator.is_page("Owner Dashboard"):
    render_owner(cars, current_user)

if mediator.is_page("Messages"):
    render_messages(current_user)

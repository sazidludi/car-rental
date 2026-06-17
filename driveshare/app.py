from datetime import date, timedelta

import streamlit as st

from database import init_db, save_car


st.set_page_config(page_title="DriveShare")
init_db()

# starts page at home
if "page" not in st.session_state:
    st.session_state["page"] = "Home"

# sidebar
pages = ["Home", "Search Cars", "Owner Dashboard", "Messages"]
st.session_state["page"] = st.sidebar.radio("pages", pages)

# main
st.title("DriveShare")
st.caption("peer to peer car rental")

# content
if st.session_state["page"] == "Home":
    st.subheader("welcome")
    st.write("DriveShare helps owners list cars and renters book them")

    
    # metrics for renters and cars and locations
    first, second, third = st.columns(3)
    first.metric("cars listed", "12")
    second.metric("active renters", "8")
    third.metric("cities", "3")
    st.info("Use the sidebar to explore search owner tools and messages")

if st.session_state["page"] == "Search Cars":
    st.subheader("search cars")

    # search 
    left, right = st.columns(2)
    left.text_input("location")
    right.text_input("make or model")
    st.date_input("trip dates", value=(date.today(), date.today() + timedelta(days=2)))
    st.slider("max daily price", 20, 200, 100)
    st.success("search results will appear here")

if st.session_state["page"] == "Owner Dashboard":
    st.subheader("owner dashboard")
   
    # listing form
    left, right = st.columns(2)
    # allows inputs for car details 
    make = left.text_input("make")
    model = right.text_input("model")
    year = left.number_input("year", min_value=2000, max_value=2026, value=2020)
    daily_price = right.number_input("daily price", min_value=20, max_value=300, value=65)
    mileage = left.number_input("mileage", min_value=0, value=25000)
    location = st.text_input("pickup location")
    start_date, end_date = st.date_input("availability", value=(date.today(), date.today() + timedelta(days=7)))
    description = st.text_area("description")
    if st.button("save listing"):
        save_car(make, model, year, mileage, location, daily_price, start_date, end_date, description)
        st.success("listing saved")

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

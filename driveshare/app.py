from datetime import date, timedelta

import streamlit as st


st.set_page_config(page_title="DriveShare")

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
    left.text_input("make")
    right.text_input("model")
    left.number_input("year", min_value=2000, max_value=2026, value=2020)
    right.number_input("daily price", min_value=20, max_value=300, value=65)
    st.text_input("pickup location")
    st.text_area("description")
    st.button("save listing")

if st.session_state["page"] == "Messages":
    st.subheader("messages")
    st.write("owner renter chat will go here")

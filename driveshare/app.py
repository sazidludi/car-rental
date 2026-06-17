import streamlit as st


st.set_page_config(page_title="DriveShare")

if "page" not in st.session_state:
    st.session_state["page"] = "Home"

pages = ["Home", "Search Cars", "Owner Dashboard", "Messages"]
st.session_state["page"] = st.sidebar.radio("pages", pages)

st.title("DriveShare")
st.caption("peer to peer car rental")

if st.session_state["page"] == "Home":
    st.subheader("welcome")
    st.write("DriveShare helps owners list cars and renters book them")

if st.session_state["page"] == "Search Cars":
    st.subheader("search cars")
    st.write("search filters will go here")

if st.session_state["page"] == "Owner Dashboard":
    st.subheader("owner dashboard")
    st.write("listing tools will go here")

if st.session_state["page"] == "Messages":
    st.subheader("messages")
    st.write("owner renter chat will go here")

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
    st.write("search filters will go here")

if st.session_state["page"] == "Owner Dashboard":
    st.subheader("owner dashboard")
    st.write("listing tools will go here")

if st.session_state["page"] == "Messages":
    st.subheader("messages")
    st.write("owner renter chat will go here")

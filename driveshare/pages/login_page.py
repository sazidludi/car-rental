import streamlit as st

from driveshare.database import verify_user


def render_login(session):
    st.subheader("login")
    st.caption("demo owner  owner@example.com / owner123")
    st.caption("demo renter  renter@example.com / renter123")

    # login form
    with st.form("login_form"):
        email = st.text_input("email")
        password = st.text_input("password", type="password")
        login_user = st.form_submit_button("login")

    if login_user:
        user = verify_user(email, password)
        if user is None:
            st.error("email or password is wrong")
        else:
            session.login(user)
            st.rerun()

    if st.button("create account"):
        st.session_state["auth_page"] = "Register"
        st.rerun()

from datetime import date, timedelta

import streamlit as st


class SessionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def setup(self, default_page="Home"):
        defaults = {
            "page": default_page,
            "selected_car_id": None,
            "booking_notice": "",
            "selected_trip_dates": (date.today(), date.today() + timedelta(days=2)),
            "selected_booking_id": None,
            "payment_notice": "",
            "auth_page": "Login",
            "user_id": None,
            "user_email": "",
            "user_role": "",
        }

        # session defaults
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def login(self, user):
        st.session_state["user_id"] = user["id"]
        st.session_state["user_email"] = user["email"]
        st.session_state["user_role"] = user["role"]
        st.session_state["page"] = "Home"

    def logout(self):
        st.session_state["user_id"] = None
        st.session_state["user_email"] = ""
        st.session_state["user_role"] = ""
        st.session_state["auth_page"] = "Login"
        st.session_state["page"] = "Home"
        st.session_state["selected_car_id"] = None
        st.session_state["selected_booking_id"] = None

    def is_logged_in(self):
        return st.session_state["user_id"] is not None

    def current_user(self):
        if not self.is_logged_in():
            return None

        return {
            "id": st.session_state["user_id"],
            "email": st.session_state["user_email"],
            "role": st.session_state["user_role"],
        }

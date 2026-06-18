import streamlit as st

from driveshare.database import get_recovery_user, update_password
from driveshare.patterns.recovery_chain import build_recovery_chain


def render_recovery():
    st.subheader("password recovery")

    email = st.text_input("email")
    user = None

    if email:
        user = get_recovery_user(email)

    if email and user is None:
        st.info("enter the email used for registration")

    if user is not None:
        with st.form("recovery_form"):
            st.write(user["question_one"])
            answer_one = st.text_input("answer one")
            st.write(user["question_two"])
            answer_two = st.text_input("answer two")
            st.write(user["question_three"])
            answer_three = st.text_input("answer three")
            new_password = st.text_input("new password", type="password")
            reset_password = st.form_submit_button("reset password")

        if reset_password:
            answers = [answer_one, answer_two, answer_three]
            chain = build_recovery_chain(user)

            if len(new_password) < 6:
                st.error("password needs at least 6 characters")
            elif not all(answers):
                st.error("answer all security questions")
            elif not chain.handle(answers):
                st.error("security answers did not match")
            else:
                updated = update_password(user["id"], new_password)
                if updated:
                    st.session_state["login_notice"] = "password updated  try logging in"
                    st.session_state["auth_page"] = "Login"
                    st.rerun()
                else:
                    st.error("password was not updated")

    if st.button("back to login"):
        st.session_state["auth_page"] = "Login"
        st.rerun()

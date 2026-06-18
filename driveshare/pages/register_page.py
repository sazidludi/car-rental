import streamlit as st

from driveshare.database import create_user


def render_register(session):
    st.subheader("register")


    # registration form
    with st.form("register_form"):
        email = st.text_input("email")
        password = st.text_input("password", type="password")
        role = st.selectbox("role", ["renter", "owner"])

        # security questions
        st.write("security questions")
        question_one = st.text_input("question one")
        answer_one = st.text_input("answer one")
        question_two = st.text_input("question two")
        answer_two = st.text_input("answer two")
        question_three = st.text_input("question three")
        answer_three = st.text_input("answer three")

        register_user = st.form_submit_button("register")

    # handle registration
    if register_user:
        questions = [question_one, question_two, question_three]
        answers = [answer_one, answer_two, answer_three]

        # checks for fields and length. gives errors if needed
        if not email or not password:
            st.error("email and password are required")
        elif len(password) < 6:
            st.error("password needs at least 6 characters")
        elif not all(questions) or not all(answers):
            st.error("all security questions are required")
        else:
            user, message = create_user(email, password, role, questions, answers)
            if user is None:
                st.error(message)
            else:
                session.login(user)
                st.rerun()

    # back to login button
    if st.button("back to login"):
        st.session_state["auth_page"] = "Login"
        st.rerun()

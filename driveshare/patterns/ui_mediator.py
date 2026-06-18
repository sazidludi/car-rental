import streamlit as st


class UIMediator:
    def __init__(self, pages):
        self.pages = pages


    # renders the sidebar and returns if logout button is clicked
    def render_sidebar(self, user):
        st.sidebar.title("DriveShare")
        st.sidebar.caption("car sharing dashboard")
        st.sidebar.caption(f"{user['email']}  {user['role']}")

        current_page = st.session_state["page"]
        if current_page not in self.pages:
            current_page = "Home"

        # page state
        st.session_state["page"] = st.sidebar.radio(
            "navigation",
            self.pages,
            index=self.pages.index(current_page),
        )

        return st.sidebar.button("logout")

    def is_page(self, page_name):
        return st.session_state["page"] == page_name

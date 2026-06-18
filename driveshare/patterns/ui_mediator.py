import streamlit as st


class UIMediator:
    def __init__(self, pages):
        self.pages = pages


    def render_sidebar(self, user):
        st.sidebar.title("DriveShare")
        st.sidebar.caption("car sharing dashboard")
        st.sidebar.caption(f"{user['email']}  {user['role']}")
        st.sidebar.divider()

        current_page = st.session_state["page"]
        if current_page not in self.pages:
            current_page = "Home"

        st.sidebar.write("navigation")

        # page buttons
        for page in self.pages:
            button_type = "primary" if page == current_page else "secondary"
            if st.sidebar.button(page, key=f"nav_{page}", type=button_type, use_container_width=True):
                st.session_state["page"] = page

        st.sidebar.divider()
        return st.sidebar.button("logout", use_container_width=True)

    def is_page(self, page_name):
        return st.session_state["page"] == page_name

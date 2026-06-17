import streamlit as st


def render_messages():
    st.subheader("messages")

    contacts, chat = st.columns([1, 2])

    # contact side
    with contacts:
        st.write("conversations")
        st.info("conversations will appear here")
        st.text_input("participant")
        st.button("start chat")

    # chat side
    with chat:
        st.write("current chat")
        st.caption("linked to a booking or car listing")
        st.info("select a conversation or start a new one")
        st.text_area("message", placeholder="type your message here")
        first, second = st.columns(2)
        first.button("send message")
        second.button("attach booking note")

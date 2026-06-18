import streamlit as st

from driveshare.database import get_message_contacts, get_messages_between, send_message


def render_messages(user):
    st.subheader("messages")

    contacts, chat = st.columns([1, 2])
    users = get_message_contacts(user["id"])

    # contact side
    with contacts:
        st.write("conversations")
        if not users:
            st.info("no users to message yet")
            return

        labels = {f"{item['email']}  {item['role']}": item for item in users}
        selected_label = st.selectbox("participant", list(labels.keys()))
        selected_user = labels[selected_label]

    # chat side
    with chat:
        st.write(f"chat with {selected_user['email']}")
        messages = get_messages_between(user["id"], selected_user["id"])

        if not messages:
            st.info("no messages yet")

        # message rows
        for message in messages:
            st.caption(f"{message['sender_email']}  {message['created_at']}")
            st.write(message["body"])

        with st.form("message_form"):
            body = st.text_area("message", placeholder="type your message here")
            send = st.form_submit_button("send message")

        if send:
            if not body.strip():
                st.error("message cannot be empty")
            else:
                send_message(user["id"], selected_user["id"], body.strip())
                st.rerun()

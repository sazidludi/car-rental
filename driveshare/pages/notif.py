import streamlit as st

from driveshare.database import get_notifications, get_unread_count, mark_notification_read


def render_notif():
    st.subheader("notifications")

    # user filter
    user_options = {"renter": 2, "owner": 1}
    selected_user = st.selectbox(
        "show for",
        list(user_options.keys()),
        index=list(user_options.keys()).index(st.session_state["notification_view"]),
    )
    
    st.session_state["notification_view"] = selected_user
    selected_user_id = user_options[selected_user]
    notifications = get_notifications(selected_user_id)
    unread_count = get_unread_count(selected_user_id)


    first, second = st.columns(2)
    first.metric("all notifications", len(notifications))
    second.metric("unread", unread_count)

    if not notifications:
        st.info("no notifications yet")

    # notification rows
    for notification in notifications:
        status = "unread" if not notification["is_read"] else "read"
        expanded = not notification["is_read"]
        with st.expander(f"{notification['title']}  {status}", expanded=expanded):
            st.write(notification["message"])
            st.caption(notification["created_at"])
            left, right = st.columns(2)

            # button if notif is related to booking
            if notification["booking_id"]:
                if left.button("view booking", key=f"notice_booking_{notification['id']}"):
                    st.session_state["selected_booking_id"] = notification["booking_id"]
                    st.session_state["page"] = "Rental History"
                    st.rerun()

            # button to mark as read if unread
            if not notification["is_read"]:
                if right.button("mark read", key=f"notice_read_{notification['id']}"):
                    mark_notification_read(notification["id"])
                    st.rerun()

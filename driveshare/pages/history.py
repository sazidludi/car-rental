from datetime import date

import streamlit as st

from driveshare.database import get_booking_history, get_payments, process_payment


def render_history(user, user_balance):
    st.subheader("rental history")

    if st.session_state["booking_notice"]:
        st.success(st.session_state["booking_notice"])
        st.session_state["booking_notice"] = ""
    if st.session_state["payment_notice"]:
        st.success(st.session_state["payment_notice"])
        st.session_state["payment_notice"] = ""

    history = get_booking_history(user["id"], user["role"])
    unpaid_count = len([booking for booking in history if not booking["is_paid"]])
    total_value = sum(booking["total_price"] for booking in history)

    # history totals
    first, second, third = st.columns(3)
    first.metric("total bookings", len(history))
    second.metric("unpaid bookings", unpaid_count)
    third.metric("total value", f"${total_value:.2f}")

    # balance
    st.metric("your balance", f"${user_balance:.2f}")

    if not history:
        st.info("no bookings yet")

    # booking rows
    for booking in history:
        paid_status = "paid" if booking["is_paid"] else "unpaid"
        start = date.fromisoformat(booking["start_date"])
        end = date.fromisoformat(booking["end_date"])
        total_days = (end - start).days + 1
        expanded = booking["id"] == st.session_state["selected_booking_id"]


        # show unpaid bookings expanded 
        with st.expander(f"booking {booking['id']}  {booking['year']} {booking['make']} {booking['model']}", expanded=expanded):
            st.write(f"location  {booking['location']}")
            st.write(f"dates  {booking['start_date']} to {booking['end_date']}")
            st.write(f"days  {total_days}")
            st.write(f"total  ${booking['total_price']:.2f}")
            st.write(f"status  {paid_status}")

            # pay booking
            if user["role"] == "renter" and not booking["is_paid"]:
                if st.button("pay now", key=f"pay_{booking['id']}"):
                    success, message, amount = process_payment(booking["id"], user["id"])
                    if success:
                        st.session_state["payment_notice"] = f"{message}  ${amount:.2f}"
                        st.session_state["selected_booking_id"] = booking["id"]
                        st.rerun()
                    else:
                        st.error(message)

            if st.button("view car", key=f"history_car_{booking['id']}"):
                st.session_state["selected_car_id"] = booking["car_id"]
                st.session_state["page"] = "Booking"
                st.rerun()

    # payment records
    st.subheader("payment records")
    payments = get_payments(user["id"], user["role"])

    if not payments:
        st.info("no payments yet")

    # payment rows
    for payment in payments:
        payment_left, payment_right = st.columns([3, 1])
        payment_left.caption(
            f"payment {payment['id']}  booking {payment['booking_id']}  "
            f"${payment['amount']:.2f}  {payment['status']}"
        )

        if payment_right.button("view booking", key=f"payment_booking_{payment['id']}"):
            st.session_state["selected_booking_id"] = payment["booking_id"]
            st.rerun()

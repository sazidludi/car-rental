from driveshare.database import process_payment


class PaymentProxy:
    def __init__(self, user):
        self.user = user

    def pay(self, booking_id):
        # payment proxy
        if self.user["role"] != "renter":
            return False, "only renters can pay", 0

        return process_payment(booking_id, self.user["id"])

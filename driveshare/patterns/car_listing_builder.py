from dataclasses import dataclass


@dataclass
class CarListing:
    owner_id: int
    make: str
    model: str
    year: int
    mileage: int
    location: str
    daily_price: float
    availability_start: object
    availability_end: object
    description: str

# builder pattern for car listing creation
class CarListingBuilder:
    def __init__(self):
        self.data = {}

    def with_owner(self, owner_id):
        self.data["owner_id"] = owner_id
        return self

    def with_basic_info(self, make, model, year):
        self.data["make"] = make
        self.data["model"] = model
        self.data["year"] = year
        return self

    def with_trip_info(self, mileage, location, daily_price):
        self.data["mileage"] = mileage
        self.data["location"] = location
        self.data["daily_price"] = daily_price
        return self

    def with_availability(self, start_date, end_date):
        self.data["availability_start"] = start_date
        self.data["availability_end"] = end_date
        return self

    def with_description(self, description):
        self.data["description"] = description
        return self

    def build(self):
        return CarListing(**self.data)

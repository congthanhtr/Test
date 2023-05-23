from .has_coord import HasCoord


class HotelModel(HasCoord):
    xid: str
    name: str
    phone: str
    email: str

    def __init__(self, xid, name, lat, lng, phone, email) -> None:
        self.xid = xid
        self.name = name
        self.lat = lat
        self.lng = lng
        self.phone = phone
        self.email = email
        
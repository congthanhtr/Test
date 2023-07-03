from .has_coord import HasCoord


class HotelModel(HasCoord):
    xid: str
    name: str
    phone: str
    email: str
    address: str
    amenities: list

    def __init__(self, xid='', name='', lat=0.0, lng=0.0, phone='', email='', address='', amenities=[]) -> None:
        self.xid = xid
        self.name = name
        self.lat = lat
        self.lng = lng
        self.phone = phone
        self.email = email
        self.address = address
        self.amenities = amenities
        
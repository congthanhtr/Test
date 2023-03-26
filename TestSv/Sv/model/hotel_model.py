from .has_coord import HasCoord


class HotelModel(HasCoord):
    name: str

    def __init__(self, name, lat, lng) -> None:
        self.name = name
        self.lat = lat
        self.lng = lng
        
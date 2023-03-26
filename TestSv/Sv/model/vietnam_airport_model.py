from .has_coord import HasCoord


class VietnamAirportModel(HasCoord):
    code: str

    def __init__(self, code, lat, lng) -> None:
        self.code = code
        self.lat = lat
        self.lng = lng

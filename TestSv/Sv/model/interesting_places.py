from .has_coord import HasCoord

class InterestingPlace(HasCoord):
    vi_name: str = ''

    def __init__(self, vi_name=None, lat=None, lng=None) -> None:
        self.vi_name = vi_name
        self.lat = lat
        self.lng = lng
from .has_coord import HasCoord



class Preview:
    source: str
    height: float
    width: float


class InterestingPlace(HasCoord):
    xid = str
    vi_name: str = ''
    description: str = ''
    preview: Preview

    def __init__(self, xid = None, vi_name=None, description=None, preview=None, lat=None, lng=None) -> None:
        self.xid = xid
        self.vi_name = vi_name
        self.description = description
        self.preview = preview
        self.lat = lat
        self.lng = lng
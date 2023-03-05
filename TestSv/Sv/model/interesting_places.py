class InterestingPlace:
    vi_name: str = ''
    province: str = ''
    summary: str = ''
    image: str = ''

    def __init__(self, vi_name=None, province=None, summary=None, image=None) -> None:
        self.vi_name = vi_name
        self.province = province
        self.summary = summary
        self.image = image
class HasCoord:
    lat: float
    lng: float

    def get_cord(self):
        '''
        get latitude, longitude of an object has which has coordinate
        '''
        return (self.lat, self.lng)
import time
from ..myutils import util
import pandas as pd

class TimeTravelService:
    distance: float = 0.0
    flight_time: float = 0
    driving_time: float = 0
    railway_time: float = 0

    DRIVING_SPEED = 50

    flight_time_xlxs = pd.read_excel('static/flight_time.xlsx')

    def calculate_time_travel(self, city_from: list, city_to: list, collection=None):
        from_location = util.get_lat_lon(city_from)
        to_location = util.get_lat_lon(city_to)

        # find neareast airport
        neareast_airport_from, cord_neareast_airport_from = util.get_neareast_airport(from_location)
        neareast_airport_to, cord_neareast_airport_to = util.get_neareast_airport(to_location)

        start = time.time()
        self.distance = util.get_distance_between_two_cord(from_location[0], cord_neareast_airport_to)
        self.driving_time = self._calculate_driving_time(collection=collection, city_from=city_from[0], city_to=city_to[0])
        self.railway_time = self._calculate_railway_time()

        # calculate flight time (include driving time from airport to destination)
        self.flight_time = self._calculate_flight_time(neareast_airport_from.code, neareast_airport_to.code)
        if self.flight_time > 0: # means if has flight from a -> b
            self.flight_time += self._calculate_driving_time(util.get_distance_between_two_cord(cord_neareast_airport_from, neareast_airport_from.get_cord()))
            self.flight_time += self._calculate_driving_time(util.get_distance_between_two_cord(neareast_airport_to.get_cord(), cord_neareast_airport_to))
        return self

    def _calculate_driving_time(self, distance=None, collection=None, city_from=None, city_to=None) -> float:
        if collection is not None and city_from is not None and city_to is not None:
            start = time.time()
            cl = list(collection.find({
                'from': util.preprocess_city_name(city_from),
                'to': util.preprocess_city_name(city_to)
            }))[0]
            return cl.get('driving_time')
        elif distance is not None:
            return (distance / self.DRIVING_SPEED) * 60.0
        return (self.distance / self.DRIVING_SPEED) * 60.0

    def _calculate_flight_time(self, airport_from, airport_to):
        flight_from = self.flight_time_xlxs['from'].to_list()
        flight_to = self.flight_time_xlxs['to'].to_list()
        flight_time = self.flight_time_xlxs['time'].to_list()
        _flight_time = 0    
        for i in range(0, len(flight_from)):
            if util.is_equals(flight_from[i], airport_from):
                if util.is_equals(flight_to[i], airport_to):
                    _flight_time = flight_time[i] * 60
                    break
            elif util.is_equals(flight_from[i], airport_to):
                if util.is_equals(flight_to[i], airport_from):
                    _flight_time = flight_time[i] * 60
                    break
            else:
                _flight_time = 0

        return _flight_time
    
    def _calculate_railway_time(self, distance=None):
        if distance is not None:
            return (distance/50.0)*60
        return (self.distance/50)*60
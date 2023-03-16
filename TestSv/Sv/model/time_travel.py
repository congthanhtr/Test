from ..myutils import util
import pandas as pd

class TimeTravelService:
    distance: float = 0.0
    flight_time: float = 0
    driving_time: float = 0
    DRIVING_SPEED = 50

    flight_time_xlxs = pd.read_excel('static/flight_time.xlsx')

    def calculate_time_travel(self, city_from: str, city_to: str):
        from_location = util.get_lat_lon(city_from)
        to_location = util.get_lat_lon(city_to)

        # find neareast airport
        neareast_airport_from, cord_neareast_airport_from = util.get_neareast_airport(from_location)
        neareast_airport_to, cord_neareast_airport_to = util.get_neareast_airport(to_location)

        self.distance = util.get_distance_between_two_cord(from_location, cord_neareast_airport_to)
        self.driving_time = self._calculate_driving_time()

        # calculate flight time (include driving time from airport to destination)
        self.flight_time = self._calculate_flight_time(neareast_airport_from.code, neareast_airport_to.code)
        if self.flight_time > 0: # means if has flight from a -> b
            self.flight_time += self._calculate_driving_time_with_distance(util.get_distance_between_two_cord(cord_neareast_airport_from, neareast_airport_from.cord))
            self.flight_time += self._calculate_driving_time_with_distance(util.get_distance_between_two_cord(neareast_airport_to.cord, cord_neareast_airport_to))
        return self

    def _calculate_driving_time(self) -> float:
        return self.distance / self.DRIVING_SPEED
    
    def _calculate_driving_time_with_distance(self, distance):
        return distance / self.DRIVING_SPEED

    def _calculate_flight_time(self, airport_from, airport_to):
        flight_from = self.flight_time_xlxs['from'].to_list()
        flight_to = self.flight_time_xlxs['to'].to_list()
        flight_time = self.flight_time_xlxs['time'].to_list()
        _flight_time = 0    
        for i in range(0, len(flight_from)):
            if util.is_equals(flight_from[i], airport_from):
                if util.is_equals(flight_to[i], airport_to):
                    _flight_time = flight_time[i]
                    break
            elif util.is_equals(flight_from[i], airport_to):
                if util.is_equals(flight_to[i], airport_from):
                    _flight_time = flight_time[i]
                    break
            else:
                _flight_time = 0

        return _flight_time
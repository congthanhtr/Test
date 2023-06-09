from .provider_get_type import GetProviderType, GetHotelProvider, GetRestaurantProvider
from ..model.has_coord import HasCoord
from ..myutils import util 


class ProviderModel(HasCoord):
    name: str = ''
    phone: str = ''
    email: str = ''
    criterias: str = ''
    type: str = ''

    def __init__(self, name, lat, lon, phone, email, criterias, type):
        self.name = name
        self.lat = lat
        self.lon = lon
        self.phone = phone
        self.email = email
        self.criterias = criterias
        self.type = type

class Provider:
    get_provider_type: GetProviderType = None

    def get_provider(self, db, types, province_name):
        result = []
        if 'hotel' in types:
            self.set_provider_type(GetHotelProvider())
            result.extend(self.get_provider_type.get_provider(db=db, province_name=province_name))
        if 'restaurant' in types:
            self.set_provider_type(GetRestaurantProvider())
            result.extend(self.get_provider_type.get_provider(db=db, province_name=province_name))

        result = [ProviderModel(
            name=res['vi_name'],
            lat=res['lat'] if 'lat' in res else res['xid'],
            lon=res['lon'] if 'lon' in res else res['xid'],
            phone=res['phone'] if 'phone' in res else res['xid'],
            email=res['email'] if 'email' in res and not util.is_null_or_empty(res['email']) else util.DEFAULT_EMAIL,
            criterias=res['criterias'],
            type=res['type']
        ) for res in result]
        return result

    def set_provider_type(self, provider_type):
        self.get_provider_type = provider_type

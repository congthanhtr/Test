class GetProviderType:

    collection_name: str = None
    criterias: list[str] = []

    def get_collection(self, db):
        return db.get_collection(self.collection_name)

    def get_provider(self, db, province_name):
        pass


class GetHotelProvider(GetProviderType):

    collection_name: str = 'vn_hotels_2'

    def get_provider(self, db, province_name):
        collection = self.get_collection(db)
        result = list(collection.find({'province_name': province_name, 'rate': {'$gte': 2}, 'criterias': {'$ne': None}}, {'_id': 0}))
        for i in range(len(result)):
            result[i]['type'] = 'hotel'
        return result

class GetRestaurantProvider(GetProviderType):
    
    collection_name: str = 'vn_restaurants'

    def get_provider(self, db, province_name):
        collection = self.get_collection(db)
        result = list(collection.find({'province_name': province_name, 'rate': {'$gte': 2}, 'criterias': {'$ne': None}}, {'_id': 0}))
        for i in range(len(result)):
            result[i]['type'] = 'restaurant'
        return result


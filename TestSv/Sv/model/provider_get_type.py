class GetProviderType:

    collection_name: str = None
    criterias: list[str] = []

    def get_collection(self, db):
        return db.get_collection(self.collection_name)

    def get_provider(self, db, province_id):
        pass


class GetHotelProvider(GetProviderType):

    collection_name: str = 'vn_hotels_2'

    def get_provider(self, db, province_id):
        collection = self.get_collection(db)
        result = list(collection.find({'province_id': province_id, 'rate': {'$gte': 2}, 'amenities': {'$ne': None}}, {'_id': 0}))
        for i in range(len(result)):
            result[i]['type'] = 'hotel'
        return result

class GetRestaurantProvider(GetProviderType):
    
    collection_name: str = 'vn_restaurants'

    def get_provider(self, db, province_id):
        collection = self.get_collection(db)
        result = list(collection.find({'province_id': province_id, 'amenities': {'$ne': None}}, {'_id': 0}))
        for i in range(len(result)):
            result[i]['type'] = 'restaurant'
        return result


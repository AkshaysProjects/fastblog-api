from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from settings import settings

# Class to handle the database
class Mongo:
    def __init__(self, database_uri: str, database_name: str):
        self.client = MongoClient(database_uri, server_api=ServerApi('1'))
        self.db = self.client.get_database(database_name)

# Create an instance of the Mongo class
mongodb = Mongo(settings.database_uri, settings.database_name)
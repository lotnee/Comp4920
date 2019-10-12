import pymongo

class DB(object):

    @staticmethod
    def init():
        client = pymongo.MongoClient("mongodb+srv://cs4920:cs4920@cs4920-8drst.gcp.mongodb.net/")
        DB.DATABASE = client['Hangouts']

    @staticmethod
    def insert(collection, data):
        DB.DATABASE[collection].insert(data)

    @staticmethod
    def find_one(collection, query):
        return DB.DATABASE[collection].find_one(query)
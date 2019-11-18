import pymongo

class DB(object):

	@staticmethod
	def init():
		client = pymongo.MongoClient("mongodb+srv://cs4920:cs4920@cs4920-8drst.gcp.mongodb.net/")
		DB.DATABASE = client['Hangouts']

	@staticmethod
	def insert(collection, data):
		hehe = DB.DATABASE[collection].insert_one(data)
		return hehe

	@staticmethod
	def find_one(collection, query):
		return DB.DATABASE[collection].find_one(query)

	@staticmethod
	def find_all(collection):
		return DB.DATABASE[collection].find()

	@staticmethod
	def find(collection, query):
		return DB.DATABASE[collection].find(query)

	@staticmethod
	def update_one(collection, filter, data):
		DB.DATABASE[collection].find_one_and_update(filter, data)

	@staticmethod
	def count(collection):
		return DB.DATABASE[collection].count_documents({})

	@staticmethod
	def createIndex(collection, query, name):
		return DB.DATABASE[collection].create_index(query, name=name)

	# TODO
	# @staticmethod
	# def aggregate(collection, query):
	#     DB.DATABASE[collection].aggregate(query)

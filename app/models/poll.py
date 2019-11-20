from app.database import DB

class Poll(object):

	def __init__(self, creator, name, description, options, voters):
		self.creator = creator
		self.name = name
		self.description = description
		self.options = options
		self.voters = voters

	def insert(self):
		if not DB.find_one("Profile", {"_id": self.creator}):
			poll = DB.insert(collection='Poll', data=self.json())
			DB.update_one(collection='Profile', filter={'_id': self.creator}, data={'$push': {'polls': poll.inserted_id}})
			return poll.inserted_id

	def json(self):
		return {
			'creator': self.creator,
			'name': self.name,
			'description': self.description,
			'options': self.options,
			'voters': self.voters
		}
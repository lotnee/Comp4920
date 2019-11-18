from app.database import DB


class Event(object):

    def __init__(self,name,description,start,end,host,invitees):
        self.name = name
        self.description = description
        self.start = start
        self.end = end
        self.host = host
        self.invitees = invitees

    def insert(self,userEmail):
        hehe = DB.insert(collection='Events', data=self.json())
        DB.update_one(collection='Profile',filter={'email':userEmail}, data = {'$push': {'events':hehe.inserted_id}})
        return hehe

    def addProfile(self, newProfile,eventId ):
        DB.update_one(collection='Profile', filter = {'_id':eventId}, data = {'$push':{'profileList':newProfile}})
        return None

    def json(self):
        return {
            'name': self.name,
        	'description': self.description,
        	'start': self.start,
        	'end': self.end,
            'host':self.host,
            'invitees':self.invitees
        }

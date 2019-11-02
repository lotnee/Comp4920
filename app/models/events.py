from app.database import DB

class Event(object):

    def __init__(self,name,description,start,end):
        self.name = name
        self.description = description
        self.start = start
        self.end = end

    def insert(self,userEmail):
        hehe = DB.insert(collection='Events', data=self.json())
        DB.update_one(collection='Profile',filter={'email':userEmail}, data = {'$push': {'events':hehe.inserted_id}})
        return hehe


    def json(self):
        return {
            'name': self.name,
        	'description': self.description,
        	'start': self.start,
        	'end': self.end,
        }

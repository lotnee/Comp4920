from app.database import DB

class Event(object):

    def __init__(self,name,description,start,end):
        self.name = name
        self.description = description
        self.start = start
        self.end = end

    def insert(self):
        print(self.start)
        DB.insert(collection='Events', data=self.json())

    def json(self):
        return {
            'name': self.name,
        	'description': self.description,
        	'start': self.start,
        	'end': self.end,
        }

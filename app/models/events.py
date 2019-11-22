from app.database import DB


class Event(object):

    def __init__(self,name,description,start,end,host,invitees, pictureDir, private):
        self.name = name
        self.description = description
        self.start = start
        self.end = end
        self.host = host
        self.invitePrivleges = []
        self.invitees = invitees
        self.pictureDir = pictureDir
        self.private = private

    def insert(self,userEmail,userId):
        event = DB.insert(collection='Events', data=self.json())
        DB.update_one(collection='Profile',filter={'email':userEmail}, data = {'$push': {'events':event.inserted_id}})
        DB.update_one(collection = "Events", filter ={'_id':event.inserted_id}, data = {'$push': {"invitees": {"id":userId, "email": userEmail, "status": "going"}}})
        return event.inserted_id

    def addProfile(self, newProfile,eventId ):
        DB.update_one(collection='Profile', filter = {'_id':eventId}, data = {'$push':{'invitees':newProfile}})
        return None

    def json(self):
        return {
            'name': self.name,
        	'description': self.description,
        	'start': self.start,
        	'end': self.end,
            'host':self.host,
            'invitePrivleges': self.invitePrivleges,
            'invitees':self.invitees,
            'pictureDir': self.pictureDir,
            'private': self.private

        }

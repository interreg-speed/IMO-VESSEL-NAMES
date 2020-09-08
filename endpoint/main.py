import pymongo

class MongoQuery:
    db = None
    collection = None
    uri = "mongodb://%s@oceans-shard-00-00.iotwb.mongodb.net:27017,oceans-shard-00-01.iotwb.mongodb.net:27017,oceans-shard-00-02.iotwb.mongodb.net:27017/oceandb?ssl=true&replicaSet=atlas-10a87j-shard-0&authSource=admin&retryWrites=true&w=majority"

    def __init__(self, u_p):
        client = pymongo.MongoClient(self.uri % (u_p))
        self.db = client.get_database("oceandb")
        self.collection = self.db["vessels"]

    def query(self, imo="NONE", name=None):
        items = list(self.collection.find({"imo": {'$regex': imo} },{"_id":0}  ).limit(10))
        if len(items) == 0:
            items = list(self.collection.find({"name": {'$regex': name ,'$options': 'i'} }, {"_id":0}  ).limit(10))
        return items

def main(d):
    imo = d.get("imo", "NONE")
    vessel_name = d.get("vessel_name","NONE")
    u_p = d.get("u_p","NONE")
    mq = MongoQuery(u_p)
    vessels = mq.query(imo,vessel_name)
    resp={"vessels":vessels}
    return resp

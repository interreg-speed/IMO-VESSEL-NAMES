import pymongo


class MongoQuery:
    db = None
    collection = None

    def __init__(self, uri):
        client = pymongo.MongoClient(uri)
        self.db = client.get_database("oceandb")
        self.collection = self.db["vessels"]

    def query(self, imo="NONE", name=None):
        items = list(self.collection.find({"imo": {'$regex': imo} },{"_id":0}  ))
        if len(items) == 0:
            items = list(self.collection.find({"name": {'$regex': name ,'$options': 'i'} }, {"_id":0}  ))

        return items


def main(d):
    imo = d.get("imo", "NONE")
    vessel_name = d.get("vessel_name","NONE")
    url = d.get("url")
    mq = MongoQuery(url)
    vessels = mq.query(imo,vessel_name)
    resp={"vessels":vessels}
    return resp

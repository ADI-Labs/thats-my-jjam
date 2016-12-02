import xml.etree.ElementTree as ET
import json
from flask import Flask,request
import requests, pymongo
from pymongo import MongoClient

tree = ET.parse('coms.xml')
root = tree.getroot()
#app = Flask(__name__)
filename = "doc.json"
def connect():
    connection = MongoClient("ds031257.mlab.com",31257)
    handle = connection["general_info_database"]
    handle.authenticate("admin","admin1")
    return handle
handle = connect()
db = handle.general_info_database
dbtracks = handle.tracks
app = Flask(__name__)
URL = 'doc.json'
db_users = handle.usernames



    
class DataGatherer:
    def __init__(self, index):
        self.index = index
        self.tree = ET.parse('coms.xml')
        self.root = self.tree.getroot()

    def getName(self):
        name = "COMS"+(root[0][self.index][5].text)
        return (name)

    def getDescription(self):
        return (root[0][self.index][18].text)
    def combineNameDescription(self):
        combined = {}
        name = self.getName()
        description = self.getDescription()
        combined[name] = description
        db.courses.update_many({"course":name},{"$set": {
            "description":description}})
        return combined


def run():
    descriptions = []
    for i in range (112):
        dg = DataGatherer(i)
        combined = dg.combineNameDescription()
        descriptions.append(combined)
    print(descriptions)
if __name__ == '__main__':
    run()

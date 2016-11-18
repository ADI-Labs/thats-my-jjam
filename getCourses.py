from flask import Flask, request
import requests
import json
app = Flask(__name__)
@app.route('/',methods = ['GET'])
URL = 'http://api.culpa.info/courses/department_id/7'

def getAllData():
    return null
def getProfessors():
    r = requests.get(URL)
    json_data = json.loads(r.text)
    array = [len(json_data['courses'])]
    for i in range(len(json_data['courses'])):
        array[i] = str(json_data['courses'][i]['name'])
    return array

def getCourseNames():
    r = requests.get(URL)
    jason_data = json.loads(r.text)
    array = ""
    for i in range(len(jason_data['courses'])):
        array = array + str(jason_data['courses'][i]['name'])+'x'
    return array

def getInfo():
    r = requests.get('http://api.culpa.info/courses/department_id/7')
    jason_data = json.loads(r.text)
    string = ""
    for i in range(len(jason_data['courses'])):
        print(string)
        string += str(jason_data['courses'][i]['number'])+" "
    data = jason_data['courses'][0]['number']
    return string
if __name__ == '__main__':
        app.debug = True
        app.run()
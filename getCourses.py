from flask import Flask, request
import requests, json, pymongo
from pymongo import MongoClient
client = MongoClient()
db = client.test_database
app = Flask(__name__)
# URL = 'http://api.culpa.info/courses/department_id/7'
URL = 'doc.json'

"""
def getAllData():
    return null
def getProfessors():
    r = requests.get(URL)
    json_data = json.loads(r.text)
    array = [len(json_data['courses'])]
    for i in range(len(json_data['courses'])):
        array[i] = str(json_data['courses'][i]['name'])
    return array
"""

"""
@app.route('/', methods=['GET'])
def getCourseNames():
    r = requests.get(URL)
    jason_data = json.loads(r.text)
    array = ""
    for i in range(len(jason_data['courses'])):
        array = array + str(jason_data['courses'][i]['name'])+'x'
    return array
"""

class Course:
    def __init__(self,  professor,
                        term,
                        course,
                        section,
                        course_title,
                        course_subtitle,
                        time,
                        location,
                        call_number,
                        num_enrolled,
                        max_size,
                        num_fixed_units,
                        description):
        self.professor = professor
        self.term = term
        self.course = course
        self.section = section
        self.course_title = course_title
        self.course_subtitle = course_subtitle
        self.time = time
        self.location = location
        self.call_number = call_number
        self.num_enrolled = num_enrolled
        self.max_size = max_size
        self.num_fixed_units = num_fixed_units
        self.description = description


def load_json_to_database(posts):
    '''This is for loading new courses to be added'''
    with open(URL) as data_file:
        data = json.load(data_file)

    # For each course in json
    for course in data:

        # COMS only
        title = course["Course"]
        if title[:4] != "COMS":
            continue

        # If the course doesnt exist already:
        if not posts.find_one({"Course": title}):
            units = course["NumFixedUnits"]
            if units:
                units = "{}.{}".format(units[1], units[2])

            to_add = Course(
                    course["Instructor1Name"].title(),

                    ("Fall {}".format(course["Term"][:4]) if
                        course["Term"][4] == "2" else
                        "Winter {}".format(course["Term"][:4])) if
                        course["Term"] else "",

                    course["Course"][:8] if course["Course"] else "",
                    course["Course"][9:] if course["Course"] else "",
                    course["CourseTitle"],
                    course["CourseSubtitle"],
                    ' '.join(course["Meets1"][:19].split())
                        if course["Meets1"] else "",
                    course["Meets1"][19] if course["Meets1"] else "",
                    course["CallNumber"],
                    course["NumEnrolled"],
                    course["MaxSize"],
                    units,
                    ""
                    )

            # Is there a way to directly insert the instance?
            posts.insert_one(to_add.__dict__)


@app.route('/', methods=['GET'])
def getInfo():
    posts = db.posts

    # Clear the database before
    posts.remove()

    load_json_to_database(posts)

    string = ""
    for post in posts.find():
        string += str(post) + "\n"

    return string

    """
    r = requests.get('http://api.culpa.info/courses/department_id/7')
    jason_data = json.loads(r.text)
    string=""
    for item in jason_data['courses']:
        string += str(item['number'])+" "
    data = jason_data['courses'][0]['number']
    return string
    """


if __name__ == '__main__':
    app.debug = True
    app.run()

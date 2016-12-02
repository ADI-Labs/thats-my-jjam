from flask import Flask, request
import requests, json, pymongo
from pymongo import MongoClient

def connect():
    connection = MongoClient("ds031257.mlab.com",31257)
    handle = connection["general_info_database"]
    handle.authenticate("admin","admin1")
    return handle

handle=connect()
db = handle.general_info_database
dbtracks = handle.tracks
app = Flask(__name__)
URL = 'doc.json'
db_users = handle.usernames


class Course:
    def __init__(self,  professor,
                        term,
                        course,
                        section,
                        course_title,
                        course_subtitle,
                        call_number,
                        num_fixed_units,
                        description):
        self.professor = professor
        self.term = term
        self.course = course
        self.section = section
        self.course_title = course_title
        self.course_subtitle = course_subtitle
        self.call_number = call_number
        self.num_fixed_units = num_fixed_units
        self.description = description
def checkRequired(coursesTaken, track):
    needToTake = []
    posts = db.courses
    if 'COMS1004' not in coursesTaken and 'COMS1007' not in coursesTaken:
        needToTake.append(posts.find_one({"course":"COMS1004"}))
    if 'COMS3134' not in coursesTaken and 'COMS3137' not in coursesTaken:
        needToTake.append(posts.find_one({"course":"COMS3134"}))
    if 'COMS3157' not in coursesTaken:
        needToTake.append(posts.find_one({"course":"COMS3157"}))
    if 'COMS3203' not in coursesTaken:
        needToTake.append(posts.find_one({"course":"COMS3203"}))
    if 'COMS3251' not in coursesTaken:
        needToTake.adppend(posts.find_one({"course":"COMS3251"}))
    if 'COMS3261' not in coursesTaken:
        needToTake.append(posts.find_one({"course":"COMS3261"}))
    if 'CSEE3827' not in coursesTaken:
        needToTake.append(posts.find_one({"course":"CSEE3827"}))
    trackObj = dbTracks.find_one({"track":track})
    required = trackObj["required"]
    electives = trackObj["electives"]
    num_electives = trackObj["num_electives"]
    for item in required:
        if item not in coursesTaken:
            needToTake.append(posts.find_one({"course":item}))
    num_elective_courses = 0
    for item in coursesTaken:
        if item in electives:
            num_elective_courses ++
            electives.remove(item)
    if num_elective_courses < num_electives:
        for item in electives:
            needToTake.append(item)
    return needToTake



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
        if not posts.find_one({"call_number": course["CallNumber"]}):
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
                    course["CallNumber"],
                    units,
                    ""
                    )

            # Is there a way to directly insert the instance?
            posts.insert_one(to_add.__dict__)


@app.route('/', methods=['GET'])
def getInfo():
    posts = db.courses
    users = db_users.login_info


    # Clear the database before
    # posts.remove()

    #load_json_to_database(posts)

    """
    string = ""
    for course in posts.find():
        x  =  "{} ({})\n".format(course["course_title"],course["course"])
        if x not in string:
            string += x
            string += "<br />"

    return string

    """

    return "loaded"

def register_user(name, password):
    # Return true on success (is unique name)
    if not db_users.login_info.find_one({"username" : name}):
        user = {"username" : name,
                "password" : password}
        db_users.login_info.insert_one(user)
        return True
    return False


def is_correct_password(name, password):
    user = db_users.login_info.find_one({"username" : name})
    if user["password"] == password:
        return True
    return False


def delete_user(name):
    if db.delete_one({"username": name}).deleted_count:
        return True
    return False


if __name__ == '__main__':
    classes = checkRequired(["COMS1007"])
    for c in classes:
        print (c['course_title'] + '\n')
    # app.debug = True
    #app.run()

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
app = Flask(__name__)
URL = 'doc.json'
db_users = handle.users_database


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
def checkRequired(coursesTaken):
    needToTake = []
    posts = db.courses
    '''try:
        first = coursesTaken.index("COMS1007")
    except ValueError:
        try:
            temp = coursesTaken.index("COMS1004")
        except ValueError:
            needToTake += "COMS1004"
    try:
        temp = coursesTaken.index("COMS3134")
    except ValueError:
        try:
            temp = coursesTaken.index("COMS3137")
        except ValueError:
            needToTake += "COMS3134"
    try:
        temp = coursesTaken.index("COMS3157")
    except ValueError:
        needToTake += "
    try:
        temp = coursesTaken.index("COMS3203")
    except ValueError:
        return False
    try:
        temp = coursesTaken.index("COMS3251")
    except ValueError:
        return False
    try:
        temp  = coursesTaken.index("COMS3261")
    except ValueError:
        return False
    try:
        temp = coursesTaken.index("CSEE3827")
    except ValueError:
        return False
    '''
    if 'COMS1004' not in coursesTaken:
        needToTake.append(posts.find_one({"course":"COMS1004"}))
    if 'COMS3134' not in coursesTaken:
        needToTake.append(posts.find_one({"course":"COMS3134"}))
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

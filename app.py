from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from pymongo import MongoClient


app = Flask(__name__)
app.config["DEBUG"] = True
app.config['MONGODB_SETTINGS'] = { 'db' : 'users'}
app.config['SECRET_KEY'] = 'JJAM'
app.config['WTF_CSRF_ENABLED'] = True

login_manager = LoginManager()
login_manager.init_app(app)

def connect():
    connection = MongoClient("ds031257.mlab.com",31257)
    handle = connection["general_info_database"]
    handle.authenticate("admin","admin1")
    return handle
	
handle = connect()
db_courses = handle.general_info_database.courses
db_user = handle.users_database.login_info

class User():

    def __init__(self, username):
        self.username = username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username


@app.route("/")
def homepage():
	return render_template("homepage.html")


@login_manager.user_loader
def load_user(name):
	users = db_user.find_one({"username" : name})
	if (len(users) != 0):
		return User(users['username'])
	else:
		return None



@app.route("/register", methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		username = request.form.get('username', None)
		password = request.form.get('password', None)
		yr = request.form.get('yr', None)
		if db_user.find_one({'username': username}) == None:
			db_user.insert_one({'username': username, 'password': password, 'year': yr, \
			"courses":{"1":[], "2":[], "3":[], "4":[], "5":[], "6":[], "7":[], "8":[]}})
			return redirect("/login")
		return redirect("/register")
	else:
		return render_template("signup.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
    	username = request.form.get('username', None)
    	password = request.form.get('password', None)
    	user = db_user.find_one({'username' : username})

    	if user == None:
    		return redirect("/login")
    	elif user["password"] == password:
            login_user(User(user['username']))
            return redirect("/pastcourses")
    	else:
    		return redirect("/login")
    else:
    	return render_template('login.html')


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")


@app.route('/pastcourses', methods=['GET', 'POST'])
@login_required
def add_courses():
	name = current_user.username
	user = db_user.find_one({'username': name})


	if request.method == 'POST':
		for course in request.form['courses'].split("\n"):
			if db_courses.find_one({'course': course}) != None:
				course = course.rstrip('\r')
				if course not in user["courses"]["1"]:
					db_user.update({'username': name}, {'$push': {"courses.1": course}})
	needToTake = checkRequired(user["courses"])
	courses_list = {}
	for i in range(1,9):
		courses_list[str(i)] = []
		for nameCourse in user['courses'][str(i)]:
			aCourse = db_courses.find_one({'course' : nameCourse})
			courses_list[str(i)].append(aCourse)
		
	return render_template("pastcourses.html", courses = courses_list, needToTake = needToTake)
    

	
@app.route("/courseinfo/<id>")
@login_required
def display_course_info(id):
    courses = list(db_courses.find({'course':id}))
    return render_template("courseinfo.html", courses = courses[0])
	
@app.route("/recommendations")
def display_recommendations():
	name = current_user.username
	user = db_user.find_one({'username': name})
	
	if request.method == 'POST':
		for course in request.form['courses'].split("\n"):
			if db_courses.find_one({'course': course}) != None:
				course = course.rstrip('\r')
				if course not in user["courses"]["1"]:
					db_user.update({'username': name}, {'$push': {"courses.1": course}})
	needToTake = checkRequired(user["courses"])
	courses_list = {}
	for i in range(1,9):
		courses_list[str(i)] = []
		for nameCourse in user['courses'][str(i)]:
			aCourse = db_courses.find_one({'course' : nameCourse})
			courses_list[str(i)].append(aCourse)
	return render_template("recommendations.html", courses = courses_list, needToTake = needToTake)
def checkRequired(coursesTaken):
	needToTake = []
	posts = db_courses
	
	courses_taken = []
	for i in range(1,9):
		for j in coursesTaken[str(i)]:
			courses_taken.append(j)
			
	if 'COMS1004' not in courses_taken and 'COMS1007' not in courses_taken:
		needToTake.append(posts.find_one({"course":"COMS1004"}))
	if 'COMS3134' not in courses_taken and 'COMS3137' not in courses_taken:
		needToTake.append(posts.find_one({"course":"COMS3134"}))
	if 'COMS3157' not in courses_taken:
		needToTake.append(posts.find_one({"course":"COMS3157"}))
	if 'COMS3203' not in courses_taken:
		needToTake.append(posts.find_one({"course":"COMS3203"}))
	if 'COMS3251' not in courses_taken:
		needToTake.append(posts.find_one({"course":"COMS3251"}))
	if 'COMS3261' not in courses_taken:
		needToTake.append(posts.find_one({"course":"COMS3261"}))
	if 'CSEE3827' not in courses_taken:
		needToTake.append(posts.find_one({"course":"CSEE3827"}))
	return needToTake

if __name__ == "__main__":
    app.run()

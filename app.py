from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from pymongo import MongoClient
from flask_mongoengine import MongoEngine
from flask_mongoengine.wtf import model_form
from wtforms import PasswordField
import numpy as np  
import graphlab
import pandas as pd


app = Flask(__name__)
app.config["DEBUG"] = True
app.config['MONGODB_SETTINGS'] = { 'db' : 'users'}
app.config['SECRET_KEY'] = 'JJAM'
app.config['WTF_CSRF_ENABLED'] = True

login_manager = LoginManager()
login_manager.init_app(app)
isLoggedIn=False

def connect():
    connection = MongoClient("ds031257.mlab.com",31257)
    handle = connection["general_info_database"]
    handle.authenticate("admin","admin1")
    return handle
	
handle = connect()
db_courses = handle.general_info_database.courses
db_user = handle.users_database.login_info
db_tracks = handle.tracks


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
	return render_template("homepage.html", isLoggedIn=False)


@login_manager.user_loader
def load_user(name):
	users = db_user.find_one({"username" : name})
	if (len(users) != 0):
		return User(users['username'])
	else:
		return None



@app.route("/signup", methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
		username = request.form.get('username', None)
		password = request.form.get('password', None)
		yr = request.form.get('yr', None)
		track = request.form.get("track",None)
		if db_user.find_one({'username': username}) == None:
			db_user.insert_one({'username': username, 'password': password, 'track': track, 'year': yr, \
			"courses":{"1":[], "2":[], "3":[], "4":[], "5":[], "6":[], "7":[], "8":[]}})
			return redirect("/login")
		return redirect("/signup")
	else:
		return render_template("signup.html", isLoggedIn=False)

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
    	return render_template('login.html', isLoggedIn=False)


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
			course_name = course.split()[0]
			course_sem = course.split()[1]
			if db_courses.find_one({'course': course_name}) != None:
				course_name = course_name.rstrip('\r')
				if course_name not in user["courses"][str(course_sem)]:
					db_user.update({'username': name}, {'$push': {"courses."+str(course_sem): course_name}})

	user = db_user.find_one({'username': name})		
	needToTake = checkRequired(user["courses"], user["track"],name)
	courses_list = {}
	for i in range(1,9):
		courses_list[str(i)] = []
		for nameCourse in user['courses'][str(i)]:
			aCourse = db_courses.find_one({'course' : nameCourse})
			courses_list[str(i)].append(aCourse)
	
	return render_template("pastcourses.html", courses = courses_list, needToTake = needToTake, isLoggedIn = True)
    

	
@app.route("/courseinfo/<id>")
@login_required
def display_course_info(id):
    courses = list(db_courses.find({'course':id}))
    return render_template("courseinfo.html", courses = courses[0], isLoggedIn = True)
	
@app.route("/recommendations", methods=['GET', 'POST'])
def display_recommendations():
	name = current_user.username
	user = db_user.find_one({'username': name})
	
	if request.method == 'POST':
		for course in request.form['courses'].split("\n"):
			course_name = course.split()[0]
			course_sem = course.split()[1]
			if db_courses.find_one({'course': course_name}) != None:
				course_name = course_name.rstrip('\r')
				if course_name not in user["courses"][str(course_sem)]:
					db_user.update({'username': name}, {'$push': {"courses."+str(course_sem): course_name}})
		return redirect('/pastcourses')

	user = db_user.find_one({'username': name})
	needToTake = checkRequired(user["courses"], user["track"], name)
	courses_list = {}
	for i in range(1,9):
		courses_list[str(i)] = []
		for nameCourse in user['courses'][str(i)]:
			aCourse = db_courses.find_one({'course' : nameCourse})
			courses_list[str(i)].append(aCourse)
	return render_template("recommendations.html", courses = courses_list, needToTake = needToTake, isLoggedIn = True)

def checkRequired(coursesTaken, track, name):
	needToTake = [[],[]]
	posts = db_courses
	
	courses_taken = []
	for i in range(1,9):
		for j in coursesTaken[str(i)]:
			courses_taken.append(j)
	coreCourses = ['COMS1004','COMS1007','COMS3134','COMS3137','COMS3203','COMS3157'
					,'COMS3251','COMS3261', 'CSEE3827']
	for course in coreCourses:
		if course not in courses_taken:
			needToTake[0].append(posts.find_one({"course":course}))
	if posts.find_one({"course":'COMS1004'}) in needToTake[0] and 'COMS1007' in courses_taken:
		needToTake[0].remove(posts.find_one({"course":'COMS1004'}))
	if posts.find_one({"course":'COMS1007'}) in needToTake[0] and 'COMS1004' in courses_taken:
		needToTake[0].remove(posts.find_one({"course":'COMS1007'}))
	if posts.find_one({"course":'COMS3134'}) in needToTake[0] and 'COMS3137' in courses_taken:
		needToTake[0].remove(posts.find_one({"course":'COMS3134'}))
	if posts.find_one({"course":'COMS3137'}) in needToTake[0] and 'COMS3134' in courses_taken:
		needToTake[0].remove(posts.find_one({"course":'COMS3137'}))

	trackObj = db_tracks.find_one({"track":track})
	required = trackObj["required"]
	electives = []
	for elective in trackObj["electives"]:
		electives.append(elective)
	num_electives = int(trackObj["num_electives"])

	for item in required:
		if item not in courses_taken and posts.find_one({"course":item}) != None:
			needToTake[0].append(posts.find_one({"course":item}))

	num_elective_courses = 0
	for item in courses_taken:
		if item in electives:
			num_elective_courses += 1
			electives.remove(item)

	recs = recommend(name)
	recs = list(set(recs)-set(coreCourses))
	recs = list(set(recs) & set(electives))

		#if item in coreCourses:
		#	print(item + " removed")
		#	recs.remove(item)

	if num_elective_courses < num_electives:
		for item in recs:
			if posts.find_one({"course": item}) != None:
				needToTake[1].append(posts.find_one({"course": item}))
		
	return needToTake
 
def recommend(name):
	#cursor = db_user.find({})
	#users = [res for res in cursor]
	#outdata = {'user':[],'course':[],'rating':[]}
	#for user in users:
	#	for sem in range(1,9):
	#		courses_list = user["courses"][str(sem)]
	#		for course in courses_list:
	#			outdata['user'].append(user["username"])
	#			outdata['course'].append(course)
	#			outdata['rating'].append(np.random.normal(8, 1,1)[0])
	#df = pd.DataFrame(outdata, columns = ['user', 'course', 'rating'])
	#df.to_csv('result.csv')
	#sf = graphlab.SFrame(data = 'result.csv')
	#m = graphlab.recommender.ranking_factorization_recommender.create(sf, user_id='user', item_id='course', target ='rating') 
	#recs = m.recommend()
	#recs.save('recs.csv',format='csv')
	recs = graphlab.SFrame(data = 'recs.csv')
	user_recs = {}
	print(recs)
	for i in range(0,len(recs['user'])):
		if recs['user'][i] not in user_recs:
			user_recs[recs['user'][i]] = []
		user_recs[recs['user'][i]].append(recs['course'][i])

	for user in user_recs:
		if user == name:
			print(user_recs[name])
			return user_recs[name]


if __name__ == "__main__":
    app.run()

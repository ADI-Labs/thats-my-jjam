from flask import Flask, render_template, redirect, request
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask_mongoengine import MongoEngine
from flask_mongoengine.wtf import model_form
from wtforms import PasswordField


app = Flask(__name__)
app.config["DEBUG"] = True
app.config['MONGODB_SETTINGS'] = { 'db' : 'users' }
app.config['SECRET_KEY'] = 'JJAM'
app.config['WTF_CSRF_ENABLED'] = True

db = MongoEngine(app)
login_manager = LoginManager()
login_manager.init_app(app)




class User(db.Document):
  name = db.StringField(required = True, unique = True)
  password = db.StringField(required = True)
  courses = db.StringField()
  def is_authenticated(self):
    users = User.objects(name = self.name, password = self.password, courses = self.courses)
    return len(users) != 0
  def is_active(self):
    return True
  def is_anonymous(self):
    return False
  def get_id(self):
    return self.name




@login_manager.user_loader
def load_user(name):
  users = User.objects(name=name)
  if len(users) != 0:
    return users[0]
  else:
    return None

UserForm = model_form(User)
UserForm.password = PasswordField('password')

@app.route("/")
def homepage():
	return render_template("homepage.html");


@app.route("/register", methods=['GET', 'POST'])
def register():
  form = UserForm(request.form)
  if request.method == 'POST' and form.validate():
    form.save()
    return redirect("/login")
  else:
  	return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
  form = UserForm(request.form)
  if request.method == 'POST' and form.validate():
    user = User(name=form.name.data,password=form.password.data)
    login_user(user)
    return redirect("/courses")
  
  return render_template('login.html', form = form)


@app.route("/logout")
def logout():
	logout_user()
	return redirect("/")


@app.route('/courses', methods=['GET', 'POST'])
@login_required
def addcourses():
  user = User.objects(name=current_user.name).first()
  if request.method == 'POST':
    user.courses = request.form['courses'].split("\n")
  return render_template("courses.html", user = user)


if __name__ == "__main__":
    app.run(host="0.0.0.0")

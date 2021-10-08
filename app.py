import os
from flask import (Flask, flash, render_template,
 redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.utils  import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"]=os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"]=os.environ.get("MONGO_URI")
app.secret_key =os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/get_jobs")
def get_jobs():
    jobs = mongo.db.jobs.find()
    return render_template("jobs.html",jobs = jobs)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        #check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))
        
        register = {
            "username": request.form.get("username"),
            "password": generate_password_hash(request.form.get("password")),
            "firstname": request.form.get("firstname"),
            "lastname": request.form.get("lastname"),
            "email": request.form.get("email"),
            "jobseeker": "true" if request.form["role"] == "jobseeker" else "false",
            "employer": "true" if request.form["role"] == "employer" else "false"
        }
        mongo.db.users.insert_one(register)
        
        # put the new user into 'session' cookie
        session["user"] = request.form.get("username")
        flash("Registration successful")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        if existing_user:
            # ensure hashed password matches user imput
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = request.form.get("username")
                    return redirect(url_for("profile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))
        
        else:
            #username doesn't exists
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/get_employer")
def get_employer():
    #employer = mongo.db.employer.find()
    return render_template("employer.html") 


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    if request.method == "POST":
        f = request.files['file']
        if f:
            f.save(os.path.join("static/images/", secure_filename(f.filename)))
            profile = {
                "username": session["user"],
                "firstname": request.form.get("firstname"),
                "lastname": request.form.get("lastname"),
                "company": request.form.get("company"),
                "designation": request.form.get("designation"),
                "phone": request.form.get("phone"),
                "address": request.form.get("address"),
                "imageurl": "images/"+f.filename
            }
        else:
            profile = {
                "username": session["user"],
                "firstname": request.foaddrm.get("firstname"),
                "lastname": request.form.get("lastname"),
                "company": request.form.get("company"),
                "designation": request.form.get("designation"),
                "phone": request.form.get("phone"),
                "address": request.form.get("address"),
            }
        mongo.db.employer_profile.update_one({"username":session["user"]},{"$set":profile})
        # mongo.db.employer_profile.insert_one(profile)
        profile = mongo.db.employer_profile.find_one(
                    {"username": session["user"]})
        return render_template(
            "employer/profile.html", profile=profile)

    username = mongo.db.users.find_one(
            {"username": session["user"]})
    session["role"] = "jobseeker" if username["jobseeker"] == 'true' else "employer"
    # render profile page if session contains user's information
    if session["user"]:
        profile = mongo.db.employer_profile.find_one(
                    {"username": session["user"]})
        return render_template(
            "employer/profile.html", profile=profile)
    
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    session.pop("role")
    #session.pop("profile")
    return redirect(url_for("login"))


@app.route('/upload', methods = ['GET', 'POST'])
def upload():
   if request.method == 'POST':
      f = request.files['file']
      f.save(os.path.join("static/images/", secure_filename(f.filename)))
      imageUrl = "static/images/"+f.filename
      mongo.db.employer_profile.update_one({"username":session["user"]},{"$set":{'imageurl':imageUrl}})
      profile = mongo.db.employer_profile.find_one(
                    {"username": session["user"]})
      return render_template(
            "employer/profile.html", profile=profile)
      #return redirect(url_for("profile", username=session["user"]),imageUrl=imageUrl)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True
            )
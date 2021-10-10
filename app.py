import os
from flask import (Flask, flash, render_template,
 redirect, request, session, url_for, jsonify)
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
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        #check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})
        
        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))
        jobSeekerRole = "true" if request.form["role"] == "jobseeker" else "false"
        employerRole = "true" if request.form["role"] == "employer" else "false"
        register = {
            "username": request.form.get("username"),
            "password": generate_password_hash(request.form.get("password")),
            "firstname": request.form.get("firstname"),
            "lastname": request.form.get("lastname"),
            "email": request.form.get("email"),
            "jobseeker":jobSeekerRole,
            "employer": employerRole
        }
        mongo.db.users.insert_one(register)
        profile={
            "username": request.form.get("username"),
            "firstname": request.form.get("firstname"),
            "lastname": request.form.get("lastname")
        }
        session["user"] = request.form.get("username")
        if employerRole == "true":
            session["role"] = "employer"
            mongo.db.employer_profile.insert_one(profile)
            return redirect(url_for("profile", username=session["user"]))
        else:
            session["role"] = "jobseeker"
            mongo.db.job_seeker_profile.insert_one(profile)
            return redirect(url_for("jobSeekerProfile", username=session["user"]))
        # put the new user into 'session' cookie
        flash("Registration successful")
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
                session["user"] = request.form.get("username").lower()
                if existing_user["employer"] == "true":
                    session["role"] = "employer"
                    return redirect(url_for("profile", username=session["user"]))
                else:
                    session["role"] = "jobseeker"
                    return redirect(url_for("jobSeekerProfile", username=session["user"]))
            else:
                # invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))
        else:
            #username doesn't exists
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    user = mongo.db.users.find_one(
            {"username": session["user"]})
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
                "companydesc": request.form.get("companydesc"),
                "imageurl": "images/"+f.filename
            }
        else:
            profile = {
                "username": session["user"],
                "firstname": request.form.get("firstname"),
                "lastname": request.form.get("lastname"),
                "company": request.form.get("company"),
                "designation": request.form.get("designation"),
                "phone": request.form.get("phone"),
                "address": request.form.get("address"),
                "companydesc": request.form.get("companydesc"),
            }
        mongo.db.employer_profile.update_one({"username":session["user"]},{"$set":profile})
        # mongo.db.employer_profile.insert_one(profile)
        profile = mongo.db.employer_profile.find_one(
                    {"username": session["user"]})
        profile["email"] = user["email"]
        flash("Profile updated successfully")
        return render_template(
            "employer/profile.html", profile=profile)

    session["role"] = "jobseeker" if user["jobseeker"] == 'true' else "employer"
    # render profile page if session contains user's information
    if session["user"]:
        profile = mongo.db.employer_profile.find_one(
                    {"username": session["user"]})
        return render_template(
            "employer/profile.html", profile=profile)
    return redirect(url_for("login"))


@app.route("/jobSeekerProfile/<username>", methods=["GET", "POST"])
def jobSeekerProfile(username):
    user = mongo.db.users.find_one(
            {"username": session["user"]})
    if request.method == "POST":
        imageFile = request.files['imageFile']
        resumeDoc = request.files['resumeDoc']
        if imageFile and resumeDoc:
            imageFile.save(os.path.join("static/images/", secure_filename(imageFile.filename)))
            resumeDoc.save(os.path.join("static/resume/", secure_filename(resumeDoc.filename)))
            profile = {
                "username": session["user"],
                "firstname": request.form.get("firstname"),
                "lastname": request.form.get("lastname"),
                "profiledesc": request.form.get("profiledesc"),
                "skills": request.form.get("skills"),
                "phone": request.form.get("phone"),
                "address": request.form.get("address"),
                "imageurl": "images/"+imageFile.filename,
                "resumeurl": "resume/"+resumeDoc.filename
            }
        elif imageFile:
            imageFile.save(os.path.join("static/images/", secure_filename(imageFile.filename)))
            profile = {
                "username": session["user"],
                "firstname": request.form.get("firstname"),
                "lastname": request.form.get("lastname"),
                "profiledesc": request.form.get("profiledesc"),
                "skills": request.form.get("skills"),
                "phone": request.form.get("phone"),
                "address": request.form.get("address"),
                "imageurl": "images/"+imageFile.filename
            }
        elif resumeDoc:
            resumeDoc.save(os.path.join("static/resume/", secure_filename(resumeDoc.filename)))
            profile = {
                "username": session["user"],
                "firstname": request.form.get("firstname"),
                "lastname": request.form.get("lastname"),
                "profiledesc": request.form.get("profiledesc"),
                "skills": request.form.get("skills"),
                "phone": request.form.get("phone"),
                "address": request.form.get("address"),
                "resumeurl": "resume/"+resumeDoc.filename
            }
        else:
            profile = {
                "username": session["user"],
                "firstname": request.form.get("firstname"),
                "lastname": request.form.get("lastname"),
                "profiledesc": request.form.get("profiledesc"),
                "skills": request.form.get("skills"),
                "phone": request.form.get("phone"),
                "address": request.form.get("address")
            }
        existing_profile = mongo.db.job_seeker_profile.find_one({"username":session["user"]})
        if existing_profile:
            mongo.db.job_seeker_profile.update_one({"username":session["user"]},{"$set":profile})
        else:
            mongo.db.job_seeker_profile.insert_one(profile)
        profile = mongo.db.job_seeker_profile.find_one(
                    {"username": session["user"]})
        # profile["email"] = user["email"]
        flash("Profile updated successfully")
        return render_template(
            "jobseeker/profile.html", profile=profile)
    # render profile page if session contains user's information
    if session["user"]:
        profile = mongo.db.job_seeker_profile.find_one(
                    {"username": session["user"]})
        return render_template(
            "jobseeker/profile.html", profile=profile)
    return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    session.pop("role")
    #session.pop("profile")
    return redirect(url_for("login"))


@app.route("/postJob", methods=["GET", "POST"])
def postJob():
    if request.method == "POST":
        job = {
                "username": session["user"],
                "title": request.form.get("title"),
                "description": request.form.get("description"),
                "skills": request.form.get("skills"),
                "location": request.form.get("location"),
                "salary": request.form.get("salary")
            }
        mongo.db.jobs.insert_one(job)
        flash("New Job created successfully")
        # mongo.db.employer_profile.insert_one(profile)
        savedJob = mongo.db.jobs.find_one(
                    {"username": session["user"]})
        return render_template(
            "employer/postJob.html", savedJob=savedJob)
    return render_template("employer/postJob.html")


@app.route("/jobs", methods=["GET", "POST"])
def jobs():
    jobs = mongo.db.jobs.find()
    return render_template("employer/jobs.html", jobs=jobs)


@app.route("/search/<keywords>", methods=["GET"])
def search(keywords):
    if keywords == '0':
        return render_template("searchJobs.html")
    else:
        jobs = mongo.db.jobs.find()
        numrows=jobs.count()
        return jsonify({'htmlresponse': render_template('response.html', jobs=jobs, numrows=numrows)})
    return render_template("searchJobs.html")


@app.route("/ajax_update", methods=["POST","GET"])
def ajax_update():
    if request.method == 'POST':
        job = {
                "title": request.form['txtTitle'],
                "description": request.form['txtDescription'],
                "skills": request.form['txtSkills'],
                "location": request.form['txtLocation'],
                "salary": request.form['txtSalary']
            }
        mongo.db.jobs.update_one({"_id": ObjectId(request.form['id'])}, {"$set":job})
        jobs = mongo.db.jobs.find()
        return "job updated successfully"
    jobs = mongo.db.jobs.find()
    return render_template("employer/jobs.html", jobs=jobs)


@app.route("/ajax_delete", methods=["POST", "GET"])
def ajax_delete():
    if request.method == 'POST':
        mongo.db.jobs.delete_one({"_id": ObjectId(request.form['id'])})
        return "Deleted Successfully"
    jobs = mongo.db.jobs.find()
    return render_template("employer/jobs.html", jobs=jobs)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True
            )
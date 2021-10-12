import os
from flask import (Flask, flash, render_template,
 redirect, request, session, url_for, jsonify)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
#from werkzeug.utils  import secure_filename
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

@app.route("/employerHome")
def employerHome():
    return render_template("employer/home.html")

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
        profile = {
            "username": session["user"],
            "firstname": request.form.get("firstname"),
            "lastname": request.form.get("lastname"),
            "company": request.form.get("company"),
            "designation": request.form.get("designation"),
            "phone": request.form.get("phone"),
            "address": request.form.get("address"),
            "companydesc": request.form.get("companydesc"),
            "imageurl": request.form.get("file")
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
        profile = {
                "username": session["user"],
                "firstname": request.form.get("firstname"),
                "lastname": request.form.get("lastname"),
                "profiledesc": request.form.get("profiledesc"),
                "skills": request.form.get("skills"),
                "phone": request.form.get("phone"),
                "address": request.form.get("address"),
                "imageurl": request.form.get("imageFile"),
                "resumeurl": request.form.get("resumeurl")
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
        profile = mongo.db.employer_profile.find_one(
                    {"username": session["user"]})
        if profile.get("company") and profile.get("companydesc") and profile.get("phone") and profile.get("address"):
            job = {
                    "username": session["user"],
                    "title": request.form.get("title"),
                    "description": request.form.get("description"),
                    "skills": request.form.get("skills"),
                    "location": request.form.get("location"),
                    "salary": request.form.get("salary"),
                    "company": profile["company"]
                }
            mongo.db.jobs.insert_one(job)
            flash("New Job created successfully")
            # mongo.db.employer_profile.insert_one(profile)
            savedJob = mongo.db.jobs.find_one(
                        {"username": session["user"]})
            return render_template(
                "employer/postJob.html", savedJob=savedJob)
        else:
            flash("Please update profile first")
            return render_template("employer/postJob.html")
    return render_template("employer/postJob.html")


@app.route("/jobs", methods=["GET", "POST"])
def jobs():
    jobs = mongo.db.jobs.find({"username":session["user"]})
    return render_template("employer/jobs.html", jobs=jobs)


@app.route("/search/<keywords>", methods=["GET"])
def search(keywords):
    if keywords == '0':
        return render_template("searchJobs.html")
    elif keywords == '1':
        jobs = mongo.db.jobs.find()
        numrows=jobs.count()
        return jsonify({'htmlresponse': render_template('response.html', jobs=jobs, numrows=numrows)})
    else:
        keywordArray = keywords.strip().split(",")
        jobs = mongo.db.jobs.find(
            {"$or":[
                    {"title": {"$in": keywordArray}},
                    {"skills": {"$in": keywordArray}},
                    {"company":{"$in": keywordArray}},
                    {"location":{"$in": keywordArray}}
                ]}
        )
        numrows=jobs.count()
        return jsonify({'htmlresponse': render_template('response.html', jobs=jobs, numrows=numrows)})
    return render_template("searchJobs.html")


@app.route("/applyJob", methods=["POST", "GET"])
def applyJob():
    if request.method == 'POST':
        jobApplied = {
                "jobId": ObjectId(request.form['id']),
                "username": session["user"]
            }
        existingApplication = mongo.db.jobs_history.find_one(
            {"jobId": ObjectId(request.form['id']), "username": session["user"]})
        if existingApplication:
            return "Job Already Applied"
        else:
            mongo.db.jobs_history.insert(jobApplied)
            return "Job Applied Successfully"
    jobs = mongo.db.jobs.find()
    return render_template("employer/jobs.html", jobs=jobs)


@app.route("/jobApplicants", methods=["GET", "POST"])
def jobApplicants():
    jobs = mongo.db.jobs.find({"username": session["user"]})
    applicants = []
    applicantsDetails = []
    
    for job in jobs:
        applicants.append(mongo.db.jobs_history.find(
                            {"jobId": job["_id"]}))
    flash(applicants[0][0])
    #flash(applicants[0][0]["username"])
    appl = list(dict.fromkeys(applicants))
    for a in appl:
        for d in a:
            applicantsDetails.append(mongo.db.job_seeker_profile.find_one(
                                 {"username": d["username"]}))
    return render_template("employer/jobApplicants.html", applicantsDetails=applicantsDetails)

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
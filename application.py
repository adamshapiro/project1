import os, requests, bcrypt
from datetime import datetime

from flask import Flask, session, render_template, redirect, url_for, request, flash, jsonify, abort
from flask_session import Session
from models import *

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)


@app.route("/", methods=["GET", "POST"])
def index():
    if not "user_id" in session:
        return redirect(url_for( 'login' ))

    locs = []

    if request.method == "POST":
        method = request.form["method"]
        search = request.form['search'].upper()
        locs = Location.query.filter(
                getattr(Location, method).like(f"%{search}%")
            ).limit(20).all()
        if len(locs) == 0:
            flash("We couldn't find any locations matching that information!", "danger")

    return render_template("index.html", locations=locs)

@app.route("/login")
def login():
    new_user = request.args.get("new_user", False)
    return render_template("login.html", new_user=new_user)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/sign_in", methods=["POST"])
def sign_in():
    username = request.form["username"]
    password = request.form["password"].encode()

    db_user = User.query.filter_by(username=username).first()

    if not db_user or not bcrypt.checkpw(password, db_user.password.encode()):
        flash("Your username and/or password is incorrect!", "danger")
        return render_template("login.html")

    session["user_id"] = db_user.id
    session["username"] = db_user.username
    return redirect(url_for("index"))

@app.route("/sign_up", methods=["POST"])
def sign_up():
    username = request.form["username"]
    password = request.form["password"].encode()
    confirm = request.form["confirm"].encode()

    if len(username) == 0 or len(password) == 0:
        flash("You must enter a username and password.", "danger")
        return render_template("login.html", new_user=True)

    if password != confirm:
        flash("Your password and confirmation do not match!", "danger")
        return render_template("login.html", new_user=True)

    if User.query.filter_by(username=username).first():
        flash("That username is taken!", "danger")
        return render_template("login.html", new_user=True)

    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    res = User(username=username, password=hashed.decode())
    db.session.add(res)
    db.session.commit()

    session["user_id"] = res.id
    session["username"] = username
    return redirect(url_for("index"))

@app.route("/<int:id>")
def location(id):
    if not "user_id" in session:
        return redirect(url_for( 'login' ))

    loc = Location.query.get(id)

    if loc is None:
        flash("No such location could not be found.", "danger")
        return redirect(url_for('index'))

    query = requests.\
        get(f"https://api.darksky.net/forecast/644dbdc3d30b81ecd8f71b0da4d17d09/{loc.latitude},{loc.longitude}").json()

    weather = query["currently"]
    time = datetime.fromtimestamp(weather["time"]).strftime("%Y-%m-%d %I:%M %p")
    return render_template("location.html", location=loc, weather=weather, time=time)

@app.route("/check_in", methods=["POST"])
def check_in():
    check = request.form
    if Check_In.query.filter(and_(
        Check_In.location_id == check["id"],
        Check_In.user_id == session["user_id"]
    )).first():
        flash("You have already checked into this location!", "danger")
        return redirect(url_for('location', id=check["id"]))

    new_check = Check_In(
        location_id=check["id"],
        user_id=session["user_id"],
        message=check["message"]
    )
    db.session.add(new_check)
    db.session.commit()
    return redirect(url_for('location', id=check["id"]))


@app.route("/api/<string:zip>")
def zip(zip):
    query = Location.query.filter_by(zip=zip).first()
    if query is None:
        return abort(404)

    return jsonify({
        "place_name": query.city,
        "state": query.state,
        "latitude": query.latitude,
        "longitude": query.longitude,
        "zip": zip,
        "population": query.population,
        "check_ins": len(query.check_ins)
    })

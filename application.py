import os, requests, bcrypt
from datetime import datetime

from flask import Flask, session, render_template, redirect, url_for, request, flash, jsonify, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET", "POST"])
def index():
    if not "user_id" in session:
        return redirect(url_for( 'login' ))

    locs = []

    if request.method == "POST":
        method = request.form["method"]
        search = request.form['search'].upper()
        select = f"SELECT * FROM locations WHERE {method} LIKE :s LIMIT 20"
        locs = db.execute(select, {"s": f"%{search}%"}).fetchall()
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
    password = str.encode(request.form["password"])

    db_user = db.execute("SELECT * FROM users WHERE username=:uname",
        {"uname": username}).fetchone()

    if not db_user or not bcrypt.checkpw(password, db_user["password"].encode()):
        flash("Your username and/or password is incorrect!", "danger")
        return render_template("login.html")

    session["user_id"] = db_user.id
    session["username"] = db_user.username
    return redirect(url_for("index"))

@app.route("/sign_up", methods=["POST"])
def sign_up():
    username = request.form["username"]
    password = str.encode(request.form["password"])
    confirm = str.encode(request.form["confirm"])

    if password != confirm:
        flash("Your password and confirmation do not match!", "danger")
        return render_template("login.html", new_user=True)

    if db.execute("SELECT * FROM users WHERE username=:uname", {"uname": username}).rowcount > 0:
        flash("That username is taken!", "danger")
        return render_template("login.html", new_user=True)

    hashed = bcrypt.hashpw(password, bcrypt.gensalt())
    db.execute("INSERT INTO users (username, password) VALUES (:uname, :pw)",
        {"uname": username, "pw": hashed.decode()})
    db.commit()

    new_user = db.execute("SELECT * FROM users WHERE username=:uname",
        {"uname": username}).fetchone()

    session["user_id"] = new_user.id
    session["username"] = new_user.username
    return redirect(url_for("index"))

@app.route("/<int:id>")
def location(id):
    if not "user_id" in session:
        return redirect(url_for( 'login' ))

    loc = db.execute("SELECT * FROM locations WHERE id=:id",
        {"id": id}).fetchone()

    print(loc)

    if loc is None:
        flash("No such location could not be found.", "danger")
        return redirect(url_for('index'))

    check_ins = db.execute("SELECT message FROM check_ins WHERE location_id=:id",
        {"id": id}).fetchall()

    query = requests.get(f"https://api.darksky.net/forecast/644dbdc3d30b81ecd8f71b0da4d17d09/{loc.latitude},{loc.longitude}").json()

    weather = query["currently"]
    time = datetime.fromtimestamp(weather["time"]).strftime("%Y-%m-%d %I:%M %p")
    return render_template("location.html", location=loc, check_ins=check_ins, weather=weather, time=time)

@app.route("/check_in", methods=["POST"])
def check_in():
    check = request.form
    if db.execute("SELECT user_id FROM check_ins WHERE location_id=:lid AND user_id=:uid",
        {"lid": check["id"], "uid": session["user_id"]}).fetchone():
        flash("You have already checked into this location!", "danger")
        return redirect(url_for('location', id=check["id"]))
    db.execute("INSERT INTO check_ins (location_id, user_id, message) VALUES (:lid, :uid, :m)",
        {"lid": check["id"], "uid": session["user_id"], "m": check["message"]})
    db.commit()
    return redirect(url_for('location', id=check["id"]))


@app.route("/api/<string:zip>")
def zip(zip):
    query = db.execute("SELECT locations.*, COUNT(check_ins.*) FROM locations JOIN check_ins ON check_ins.location_id=locations.id WHERE locations.zip=:z GROUP BY locations.id",
        {"z": zip}).fetchone()
    if query is None:
        return abort(404)

    data = {
        "place_name": query.city,
        "state": query.state,
        "latitude": query.latitude,
        "longitude": query.longitude,
        "zip": zip,
        "population": query.population,
        "check_ins": query.count
    }
    return jsonify(data)

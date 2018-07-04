import os
import requests

from flask import Flask, session, render_template, request
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


@app.route("/")
def index():
    if not session["logged_in"]:
        return redirect(url_for( 'login' ))
    return render_template("index.html")

@app.route("/login")
def login(new_user=False):
    return render_template("login.html", new_user=new_user)

@app.route("/sign_in", methods=["POST"])
def sign_in():
    user = request.form
    # TODO: USER AUTHENTICATION
    return redirect(url_for("index"))

@app.route("/location")
def location():
    zip = request.args.get("zip")
    # TODO: query database
    query = requests.get(f"https://api.darksky.net/forecast/644dbdc3d30b81ecd8f71b0da4d17d09/{lat},{long}").json()
    weather = query["current"]
    return render_template("location.html", location=loc, weather=weather)

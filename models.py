import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_

db = SQLAlchemy()

class Location(db.Model):
    __tablename__ = "locations"
    id = db.Column(db.Integer, primary_key=True)
    zip = db.Column(db.String, nullable=False, index=True)
    city = db.Column(db.String, nullable=False)
    state = db.Column(db.String(2), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    population = db.Column(db.Integer, nullable=False)
    check_ins = db.relationship("Check_In", lazy=True)

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

class Check_In(db.Model):
    __tablename__ = "check_ins"
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey("locations.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    message = db.Column(db.String)

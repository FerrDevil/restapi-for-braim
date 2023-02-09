from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    email = db.Column(db.String(55), unique=True, nullable=False)
    first_name = db.Column(db.String(16), nullable=False)
    last_name = db.Column(db.String(16), nullable=False)
    password = db.Column(db.Text, nullable=False)


class Location(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)


class AnimalType(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    type = db.Column(db.Text, unique=True)


class Animal(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    weight = db.Column(db.Float, nullable=False)
    length = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)
    gender = db.Column(db.Text, nullable=False)
    life_status = db.Column(db.Text, nullable=False)
    chipping_date_time = db.Column(db.DateTime, nullable=False)
    chipper_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    chipper_location_id = db.Column(db.Integer, db.ForeignKey(Location.id), nullable=False)
    death_date_time = db.Column(db.DateTime, nullable=True)


class AnimalTypes(db.Model):
    animal_id = db.Column(db.Integer, db.ForeignKey(Animal.id), unique=True, primary_key=True)
    type_id = db.Column(db.Integer, db.ForeignKey(AnimalType.id), unique=True, primary_key=True)


class VisitedLocations(db.Model):
    animal_id = db.Column(db.Integer, db.ForeignKey(Animal.id), unique=True, primary_key=True)
    date_time_of_visiting = db.Column(db.DateTime, nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey(Location.id), unique=True, primary_key=True)

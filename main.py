import json
import datetime
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Animal, Location, User, AnimalTypes, AnimalType, VisitedLocations
from config import ApplicationConfig
from account import account
from location import locations
from animal_type import animal_types
from authorized import authorized

app = Flask(__name__)

app.register_blueprint(account)
app.register_blueprint(locations)
app.register_blueprint(animal_types)

app.config.from_object(ApplicationConfig)
migrate = Migrate(app, db, render_as_batch=True)

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/animals/<int:animal_id>", methods=["GET", "PUT", "DELETE"])
@authorized
def manage_animal(animal_id):
    if not animal_id or animal_id <= 0:
        return jsonify({"error": "Invalid animal identifier"}), 400
    if not Animal.query.filter_by(id=animal_id).first():
        return jsonify({"error": "No such animal found"}), 404

    if request.method == "GET":
        animal = Animal.query.filter_by(id=animal_id).first()
        return jsonify({
            "id": animal.id,
            "animalTypes": [
                animal_types_result.type_id
                for animal_types_result in AnimalTypes.query.filter_by(animal_id=animal.id).all()
            ],
            "weight": animal.weight,
            "length": animal.length,
            "height": animal.height,
            "gender": animal.gender,
            "lifeStatus": animal.life_status,
            "chippingDateTime": animal.chipping_date_time,
            "chipperId": animal.chipper_id,
            "chippingLocationId": animal.chipper_location_id,
            "visitedLocations": [
                visited_locations.location_id
                for visited_locations in VisitedLocations.query.filter_by(animal_id=animal.id).all()
            ],
            "deathDateTime": animal.death_date_time
        }), 200

    if request.method == "PUT":
        form_data = json.loads(request.data, strict=False)

        weight = form_data.get("weight", None)
        length = form_data.get("length", None)
        height = form_data.get("height", None)
        gender = form_data.get("gender", None)
        life_status = form_data.get("lifeStatus", None)
        chipper_id = form_data.get("chipperId", None)
        chipping_location_id = form_data.get("chippingLocationId", None)

        if not weight or weight <= 0:
            return jsonify({"error": "Weight was not given or given with an error"}), 400
        if not length or length <= 0:
            return jsonify({"error": "Length was not given or given with an error"}), 400
        if not height or height <= 0:
            return jsonify({"error": "Height was not given or given with an error"}), 400
        if not life_status or life_status not in ["ALIVE", "DEAD"]:
            return jsonify({"error": "Life status was not given or given with an error"}), 400
        if not gender or gender not in ["MALE", "FEMALE", "OTHER"]:
            return jsonify({"error": "Gender was not given or given with an error"}), 400
        if not chipper_id or chipper_id <= 0:
            return jsonify({"error": "Chipper identifier was not given or given with an error"}), 400
        if not chipping_location_id or chipping_location_id <= 0:
            return jsonify({"error": "Chipping location identifier was not given or given with an error"}), 400

        if not Location.query.filter_by(id=chipping_location_id).first():
            return jsonify({"error": "Location is not found"}), 404
        if not User.query.filter_by(id=chipper_id).first():
            return jsonify({"error": "Chipper is not found"}), 404

        animal = Animal.query.filter_by(id=animal_id).first()

        if chipping_location_id == VisitedLocations.query.filter_by(animal_id=animal.id).first().location_id:
            return jsonify({"error": "Chipper is not found"}), 400

        animal.weight = weight
        animal.length = length
        animal.height = height
        animal.gender = gender
        animal.chipper_id = chipper_id
        animal.chipping_location_id = chipping_location_id
        animal.life_status = life_status
        if life_status == "DEAD":
            animal.death_date_time = datetime.datetime.now().isoformat(" ")

        return jsonify({
            "id": animal.id,
            "animalTypes": [
                animal_types_result.type_id
                for animal_types_result in AnimalTypes.query.filter_by(animal_id=animal.id).all()
            ],
            "weight": animal.weight,
            "length": animal.length,
            "height": animal.height,
            "gender": animal.gender,
            "lifeStatus": animal.life_status,
            "chippingDateTime": animal.chipping_date_time,
            "chipperId": animal.chipper_id,
            "chippingLocationId": animal.chipper_location_id,
            "visitedLocations": [
                visited_locations.location_id
                for visited_locations in VisitedLocations.query.filter_by(animal_id=animal.id).all()
            ],
            "deathDateTime": animal.death_date_time
        }), 201

    if request.method == "DELETE":
        animal = Animal.query.filter_by(id=animal_id).first()

        if VisitedLocations.query.filter_by(animal_id=animal.id).first():
            return jsonify({"error": "Visited locations exist for animal being deleted"}), 400
        db.session.delete(animal)
        db.session.commit()
        return "", 200


@app.route("/animals", methods=["POST"])
@authorized
def create_animal():
    form_data = json.loads(request.data, strict=False)

    animal_types_arg = form_data.get("animalTypes", None)
    weight = form_data.get("weight", None)
    length = form_data.get("length", None)
    height = form_data.get("height", None)
    gender = form_data.get("gender", None)
    chipper_id = form_data.get("chipperId", None)
    chipping_location_id = form_data.get("chippingLocationId", None)

    if not weight or weight <= 0:
        return jsonify({"error": "Weight was not given or given with an error"}), 400
    if not length or length <= 0:
        return jsonify({"error": "Length was not given or given with an error"}), 400
    if not height or height <= 0:
        return jsonify({"error": "Height was not given or given with an error"}), 400
    if not animal_types_arg:
        return jsonify({"error": "Animal types were not given or given with an error"}), 400
    if not gender or gender not in ["MALE", "FEMALE", "OTHER"]:
        return jsonify({"error": "Gender was not given or given with an error"}), 400
    if not chipper_id or chipper_id <= 0:
        return jsonify({"error": "Chipper identifier was not given or given with an error"}), 400
    if not chipping_location_id or chipping_location_id <= 0:
        return jsonify({"error": "Chipping location identifier was not given or given with an error"}), 400

    if not Location.query.filter_by(id=chipping_location_id).first():
        return jsonify({"error": "Location is not found"}), 404
    if not User.query.filter_by(id=chipper_id).first():
        return jsonify({"error": "Chipper is not found"}), 404

    animal = Animal(
        weight=weight,
        length=length,
        height=height,
        gender=gender,
        chipper_id=chipper_id,
        chipping_location_id=chipping_location_id,
        life_status="ALIVE",
        chipping_date_time=datetime.datetime.now().isoformat(" "),
        death_date_time=None
    )

    for animal_type_id in animal_types_arg:
        if not animal_type_id or animal_type_id <= 0:
            return jsonify({"error": "Animal type identifier was not given or given with an error"}), 400

        animal_type = AnimalTypes(animal_id=animal.id, type_id=animal_type_id)
        db.session.add(animal_type)
        db.session.commit()

    return jsonify({
            "id": animal.id,
            "animalTypes": [
                animal_types_result.type_id
                for animal_types_result in AnimalTypes.query.filter_by(animal_id=animal.id).all()
            ],
            "weight": animal.weight,
            "length": animal.length,
            "height": animal.height,
            "gender": animal.gender,
            "lifeStatus": animal.life_status,
            "chippingDateTime": animal.chipping_date_time,
            "chipperId": animal.chipper_id,
            "chippingLocationId": animal.chipper_location_id,
            "visitedLocations": [
                visited_locations.location_id
                for visited_locations in VisitedLocations.query.filter_by(animal_id=animal.id).all()
            ],
            "deathDateTime": animal.death_date_time
        }), 201


@app.route("/animals/search", methods=["GET"])
@authorized
def search_animals():
    start_date_time = request.args.get("startDateTime", None)
    end_date_time = request.args.get("endDateTime", None)
    weight = float(request.args.get("weight", 0))
    length = float(request.args.get("length", 0))
    height = float(request.args.get("height", 0))
    gender = request.args.get("gender", None)
    life_status = request.args.get("lifeStatus", None)
    chipper_id = int(request.args.get("chipperId", None))
    chipping_location_id = int(request.args.get("chippingLocationId", None))
    from_arg = int(request.args.get('from', 0))
    size = int(request.args.get('size', 10))

    if from_arg < 0 or from_arg is None:
        return jsonify({"error": "From argument is invalid"}), 400
    if size <= 0 or not size:
        return jsonify({"error": "Size argument is invalid"}), 400
    if not start_date_time:
        try:
            datetime.datetime.fromisoformat(start_date_time)
        except ValueError:
            return jsonify({"error": "Start datetime was not given or given with an error"}), 400
    if not end_date_time:
        try:
            datetime.datetime.fromisoformat(end_date_time)
        except ValueError:
            return jsonify({"error": "End datetime was not given or given with an error"}), 400
    if not gender or gender not in ["MALE", "FEMALE", "OTHER"]:
        return jsonify({"error": "Gender was not given or given with an error"}), 400
    if not chipper_id or chipper_id <= 0:
        return jsonify({"error": "Chipper identifier was not given or given with an error"}), 400
    if not chipping_location_id or chipping_location_id <= 0:
        return jsonify({"error": "Chipping location identifier was not given or given with an error"}), 400
    if not life_status or life_status not in ["ALIVE", "DEAD"]:
        return jsonify({"error": "Life status was not given or given with an error"}), 400

    filtered_animals = [
        animal for animal in Animal.query.all()
        if weight == animal.weight and
        length == animal.length and
        height == animal.height and
        gender == animal.gender and
        life_status == animal.life_status and
        datetime.datetime.fromisoformat(start_date_time) <=
        datetime.datetime.fromisoformat(animal.chipping_date_time) <=
        datetime.datetime.fromisoformat(end_date_time) and
        chipper_id == animal.chipper_id and
        chipping_location_id == animal.chipper_location_id
    ]
    filtered_animals = [
        {

            "id": animal.id,
            "animalTypes": [
                animal_types_result.type_id
                for animal_types_result in AnimalTypes.query.filter_by(animal_id=animal.id).all()
            ],
            "weight": animal.weight,
            "length": animal.length,
            "height": animal.height,
            "gender": animal.gender,
            "lifeStatus": animal.life_status,
            "chippingDateTime": animal.chipping_date_time,
            "chipperId": animal.chipper_id,
            "chippingLocationId": animal.chipper_location_id,
            "visitedLocations": [
                visited_locations.location_id
                for visited_locations in VisitedLocations.query.filter_by(animal_id=animal.id).all()
            ],
            "deathDateTime": animal.death_date_time

        }
        for animal_index, animal in enumerate(filtered_animals)
        if from_arg <= animal_index < from_arg + size
    ]

    return jsonify(filtered_animals), 201


@app.route("/animals/<int:animal_id>/types/<int:type_id>", methods=["POST"])
@authorized
def set_type_for_animal(animal_id, type_id):
    if not animal_id or animal_id <= 0:
        return jsonify({"error": "Invalid animal identifier"}), 400
    if not type_id or type_id <= 0:
        return jsonify({"error": "Invalid animal type identifier"}), 400

    animal = Animal.query.filter_by(animal_id=animal_id)
    if not animal:
        return jsonify({"error": "Such animal doesn't exist"}), 404

    if request.method == "POST":
        new_animal_type = AnimalTypes(animal_id=animal_id, type_id=type_id)
        db.session.add(new_animal_type)
        db.session.commit()

        return jsonify(
            {
                "id": animal.id,
                "animalTypes": [
                    animal_types_result.type_id
                    for animal_types_result in AnimalTypes.query.filter_by(animal_id=animal.id).all()
                ],
                "weight": animal.weight,
                "length": animal.length,
                "height": animal.height,
                "gender": animal.gender,
                "lifeStatus": animal.life_status,
                "chippingDateTime": animal.chipping_date_time,
                "chipperId": animal.chipper_id,
                "chippingLocationId": animal.chipper_location_id,
                "visitedLocations": [
                    visited_locations.location_id
                    for visited_locations in VisitedLocations.query.filter_by(animal_id=animal.id).all()
                ],
                "deathDateTime": animal.death_date_time
            }
        ), 200
    if request.method == "DELETE":
        deleting_animal_type = AnimalTypes.query.filter_by(animal_id=animal_id, type_id=type_id).first()
        if not deleting_animal_type:
            return jsonify({"error": "Such type of animal doesn't exist in animal types"}), 404
        if len(AnimalTypes.query.filter_by(animal_id=animal_id).all()) == 1 and \
                deleting_animal_type == AnimalTypes.query.filter_by(animal_id=animal_id).first():
            return jsonify({"error": "Cannot delete the last type of an animal"}), 400

        db.session.delete(deleting_animal_type)
        db.session.commit()
        return jsonify(
            {
                "id": animal.id,
                "animalTypes": [
                    animal_types_result.type_id
                    for animal_types_result in AnimalTypes.query.filter_by(animal_id=animal.id).all()
                ],
                "weight": animal.weight,
                "length": animal.length,
                "height": animal.height,
                "gender": animal.gender,
                "lifeStatus": animal.life_status,
                "chippingDateTime": animal.chipping_date_time,
                "chipperId": animal.chipper_id,
                "chippingLocationId": animal.chipper_location_id,
                "visitedLocations": [
                    visited_locations.location_id
                    for visited_locations in VisitedLocations.query.filter_by(animal_id=animal.id).all()
                ],
                "deathDateTime": animal.death_date_time
            }
        ), 200


@app.route("/animals/<int:animal_id>/types/", methods=["PUT"])
@authorized
def set_type_for_an_animal(animal_id):
    if not animal_id or animal_id <= 0:
        return jsonify({"error": "Invalid animal identifier"}), 400
    animal = Animal.query.filter_by(animal_id=animal_id)
    if not animal:
        return jsonify({"error": "Such animal doesn't exist"}), 404

    form_data = json.loads(request.data, strict=False)

    old_type_id = form_data.get("oldTypeId", None)
    new_type_id = form_data.get("newTypeId", None)

    if not old_type_id or old_type_id <= 0:
        return jsonify({"error": "Invalid old animal type identifier"}), 400
    if not new_type_id or new_type_id <= 0:
        return jsonify({"error": "Invalid new animal type identifier"}), 400

    if not AnimalType.query.filter_by(id=old_type_id):
        return jsonify({"error": "Old animal type doesn't exist"}), 404
    if not AnimalType.query.filter_by(id=new_type_id):
        return jsonify({"error": "New animal type doesn't exist"}), 404

    old_type_query = AnimalTypes.query.filter_by(animal_id=animal.id, type_id=old_type_id).first()
    new_type_query = AnimalTypes.query.filter_by(animal_id=animal.id, type_id=new_type_id).first()
    if not old_type_query:
        return jsonify({"error": "There is no animal type to change"}), 404

    if new_type_query:
        return jsonify({"error": "Such animal type already given"}), 409

    if old_type_query and new_type_query:
        return jsonify({"error": "Both animal types already given"}), 409


@app.route("/animals/<int:animal_id>/locations", methods=["GET", "PUT"])
def manage_animal_locations(animal_id):
    if not animal_id or animal_id <= 0:
        return jsonify({"error": "Invalid animal identifier"}), 400
    animal = Animal.query.filter_by(id=animal_id).first()
    if not animal:
        return jsonify({"error": "Invalid animal identifier"}), 404

    if request.method == "GET":
        start_date_time = request.args.get("startDateTime", None)
        end_date_time = request.args.get("endDateTime", None)
        from_arg = int(request.args.get('from', 0))
        size = int(request.args.get('size', 10))

        if from_arg < 0 or from_arg is None:
            return jsonify({"error": "From argument is invalid"}), 400
        if size <= 0 or not size:
            return jsonify({"error": "Size argument is invalid"}), 400
        if not start_date_time:
            try:
                datetime.datetime.fromisoformat(start_date_time)
            except ValueError:
                return jsonify({"error": "Start datetime was not given or given with an error"}), 400
        if not end_date_time:
            try:
                datetime.datetime.fromisoformat(end_date_time)
            except ValueError:
                return jsonify({"error": "End datetime was not given or given with an error"}), 400

        filtered_locations = [
            location for location in VisitedLocations.query.filter_by(animal_id=animal_id).all()
            if datetime.datetime.fromisoformat(start_date_time) <=
            datetime.datetime.fromisoformat(location.date_time_of_visiting) <=
            datetime.datetime.fromisoformat(end_date_time)

        ]
        filtered_locations = sorted(
            filtered_locations,
            key=lambda location: datetime.datetime.fromisoformat(location.date_time_of_visiting)
        )
        filtered_locations = [
            {
                "id": location.animal_id,
                "dateTimeOfVisitLocationPoint": location.date_time_of_visiting,
                "locationPointId": location.location_id
            }
            for location_index, location in enumerate(filtered_locations)
            if from_arg <= location_index < from_arg + size
        ]

        return jsonify(filtered_locations), 200

    if request.method == "PUT":
        form_data = json.loads(request.data, strict=False)

        visited_point = form_data.get("visitedLocationPointId", None)
        new_point = form_data.get("locationPointId", None)
        if visited_point <= 0 or not visited_point:
            return jsonify({"error": "Visited location point id argument is invalid"}), 400
        if new_point <= 0 or not new_point:
            return jsonify({"error": "Location point id argument is invalid"}), 400

        if visited_point == new_point:
            return jsonify({"error": "Same values were given"}), 400

        if not Location.query.filter_by(id=visited_point).first():
            return jsonify({"error": "Such visited location point does not exist"}), 404
        if not Location.query.filter_by(id=new_point).first():
            return jsonify({"error": "New location point does not exist"}), 404

        if VisitedLocations.query.filter_by(animal_id=animal_id).first().location_id == visited_point and \
            new_point == animal.chipper_location_id:
            return jsonify({"error": "Cannot set chipping location to be the first visited location"}), 400

        if new_point in [
            location.location_id for location in VisitedLocations.query.filter_by(animal_id=animal_id).all()
        ]:
            return jsonify({"error": "Cannot set an existing visited location for given animal"}), 400

        visited_location = VisitedLocations.query.filter_by(animal_id=animal_id, location_id=visited_point).first()
        if not visited_location:
            return jsonify({"error": "No such visited location"}), 404

        visited_location.location_id = new_point
        db.session.commit()

        return jsonify({
                "id": visited_location.animal_id,
                "dateTimeOfVisitLocationPoint": visited_location.date_time_of_visiting,
                "locationPointId": visited_location.location_id
            })


@app.route("/animals/<int:animal_id>/locations/<int:point_id>", methods=["POST", "DELETE"])
def set_or_delete_animal_location(animal_id, point_id):
    if not animal_id or animal_id <= 0:
        return jsonify({"error": "Invalid animal identifier"}), 400
    if not point_id or point_id <= 0:
        return jsonify({"error": "Invalid location identifier"}), 400

    animal = Animal.query.filter_by(id=animal_id).first()
    if not animal:
        return jsonify({"error": "No such animal found"}), 404
    if not Location.query.filter_by(id=point_id).first():
        return jsonify({"error": "No such location found"}), 404

    if request.method == "POST":

        if animal.life_status == "DEAD":
            return jsonify({"error": "Cannot change state of an animal with life status \"DEAD\""}), 400

        if point_id == animal.chipper_location_id:
            return jsonify({"error": "Cannot "}), 400

        visited_location = VisitedLocations(
            animal_id=animal_id,
            location_id=point_id,
            date_time_of_visiting=datetime.datetime.now().isoformat(" ")
        )
        db.session.add(visited_location)
        db.session.commit()

        return jsonify(
            {
                "id": visited_location.animal_id,
                "dateTimeOfVisitLocationPoint": visited_location.date_time_of_visiting ,
                "locationPointId": visited_location.location_id
            }
        ), 200

    if request.method == "DELETE":
        visited_location = VisitedLocations.query.filter_by(animal_id=animal_id, location_id=point_id).first()
        if not visited_location:
            return jsonify({"error": "No such visited location found"}), 404\

        db.session.delete(visited_location)
        db.session.commit()
        first_visited_location = VisitedLocations.query.filter_by(animal_id=animal_id).first()
        if first_visited_location.location_id == animal.chipper_location_id:
            db.session.delete(first_visited_location)
            db.session.commit()

        return "", 200


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")

from flask import Blueprint, request, jsonify
from models import db, AnimalType
import json
from authorized import authorized

animal_types = Blueprint("animal_types", __name__)


@animal_types.route("/animals/types/<int:type_id>", methods=["GET", "PUT", "DELETE"])
@authorized
def get_animals_type(type_id):
    if not type_id or type_id <= 0:
        return jsonify({"error": "Invalid type identifier"}), 400
    if not AnimalType.query.filter_by(id=type_id).first():
        return jsonify({"error": "No such animal type found"}), 404

    if request.method == "GET":
        animal_type = AnimalType.query.filter_by(id=type_id).first()

        return jsonify({
            "id": animal_type.id,
            "type": animal_type.type
        }), 200

    if request.method == "PUT":
        form_data = json.loads(request.data, strict=False)

        type_field = form_data.get("type", None)

        if not type_field or type_field.strip() == "":
            return jsonify({"error": "Type was not given or given with an error"}), 400

        animal_type = AnimalType.query.filter_by(id=type_id).first()
        animal_type.type = type_field
        db.session.commit()
        return jsonify({
            "id": animal_type.id,
            "type": animal_type.type
        }), 200

    if request.method == "DELETE":
        animal_type = AnimalType.query.filter_by(id=type_id).first()
        db.session.delete(animal_type)
        db.session.commit()
        return "", 200


@animal_types.route("/animals/types", methods=["POST"])
@authorized
def create_animal_type():
    if not request.data:
        return jsonify({"error": "No data in the request body"}), 400

    form_data = json.loads(request.data, strict=False)

    type_field = form_data.get("type", None)

    if not type_field or type_field.strip() == "":
        return jsonify({"error": "Type was not given or given with an error"}), 400

    if AnimalType.query.filter_by(type=type_field).first():
        return jsonify({"error": "Such animal type already exists"}), 409

    animal_type = AnimalType(type=type_field)
    db.session.add(animal_type)
    db.session.commit()
    return jsonify({
        "id": animal_type.id,
        "type": animal_type.type
    }), 200

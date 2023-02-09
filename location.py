from flask import Blueprint, request, jsonify
from models import db, Location
import json
from authorized import authorized

locations = Blueprint("locations", __name__)


@locations.route("/locations/", methods=["POST"])
@authorized
def create_location():
    if not request.data:
        return jsonify({"error": "No data in the request body"}), 400

    form_data = json.loads(request.data, strict=False)

    latitude = float(form_data.get("latitude", None))
    longitude = float(form_data.get("longitude", None))

    if not latitude or 90 < latitude < -90:
        return jsonify({"error": "Latitude is invalid"}), 400

    if not longitude or 180 < longitude < -180:
        return jsonify({"error": "Longitude is invalid"}), 400

    if Location.query.filter_by(latitude=latitude, longitude=longitude).first():
        return jsonify({"error": "Such location already exists"}), 409

    location = Location(latitude=latitude, longitude=longitude)
    db.session.add(location)
    db.session.commit()
    return jsonify({
        "id": location.id,
        "latitude": location.latitude,
        "longitude": location.longitude
    }), 200


@locations.route("/locations/<int:point_id>", methods=["GET", "PUT", "DELETE"])
@authorized
def get_location(point_id):
    if not point_id or point_id < 0:
        return jsonify({"error": "Invalid point identifier"}), 400

    if not Location.query.filter_by(id=point_id).first():
        return jsonify({"error": "No such location found"}), 404

    if request.method == "GET":
        location = Location.query.filter_by(id=point_id).first()
        return jsonify({
            "id": location.id,
            "latitude": location.latitude,
            "longitude": location.longitude
        }), 200

    if request.method == "PUT":
        form_data = json.loads(request.data, strict=False)

        latitude = form_data.get("latitude", None)
        longitude = form_data.get("longitude", None)

        if not latitude or 90 < latitude < -90:
            return jsonify({"error": "Latitude is invalid"}), 400

        if not longitude or 180 < longitude < -180:
            return jsonify({"error": "longitude is invalid"}), 400

        if Location.query.filter_by(latitude=latitude, longitude=longitude):
            return jsonify({"error": "Such location already exists"}), 409

        location = Location.query.filter_by(id=point_id).first()
        location.latitude = latitude
        location.longitude = longitude
        db.session.commit()

        return jsonify({
            "id": location.id,
            "latitude": location.latitude,
            "longitude": location.longitude
        }), 200

    if request.method == "DELETE":
        location = Location.query.filter_by(id=point_id).first()
        db.session.delete(location)
        db.session.commit()
        return "", 200



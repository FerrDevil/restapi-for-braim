from flask import request, jsonify
from models import db, User


def authorized(route_handler):
    def wrapper(*args, **kwargs):
        authorization_header = request.headers.get("Authorization")
        if not authorization_header:
            return jsonify({"error": "Account is not authorized"}), 401
        authorization_info = authorization_header.split(" ")[1].split(":")
        if not User.query.filter_by(email=authorization_info[0], password=authorization_info[1]).first():
            return jsonify({"error": "Such account doesnt exist"}), 401
        return route_handler(*args, **kwargs)

    wrapper.__name__ = route_handler.__name__
    return wrapper

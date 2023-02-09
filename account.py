from flask import Blueprint, request, jsonify
from models import db, User
import json
from authorized import authorized

account = Blueprint("account", __name__)


@account.route("/accounts/<int:account_id>", methods=["GET", "PUT", "DELETE"])
@authorized
def manage_account(account_id):
    if request.method == "GET":
        if not account_id or account_id < 0:
            return jsonify({"error": "Invalid account identifier"}), 400

        user = User.query.filter_by(id=account_id).first()

        if not user:
            return jsonify({"error": "No such user found"}), 404

        return jsonify({
            "id": user.id,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "email": user.email
        }), 200

    if request.method == "PUT":
        if not request.data:
            return jsonify({"error": "No data in the request body"}), 400

        if not account_id or account_id < 0:
            return jsonify({"error": "Invalid account identifier"}), 400

        form_data = json.loads(request.data, strict=False)

        first_name = form_data.get("firstName", None)
        last_name = form_data.get("lastName", None)
        email = form_data.get("email", None)
        password = form_data.get("password", None)

        if not first_name or first_name.strip() == "":
            return jsonify({"error": "First name was not given or given with an error"}), 400
        if not last_name or last_name.strip() == "":
            return jsonify({"error": "Last name was not given or given with an error"}), 400
        if not email or email.strip() == "":
            return jsonify({"error": "Email was not given or given with an error"}), 400
        if not password or password.strip() == "":
            return jsonify({"error": "Password was not given or given with an error"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email is already taken"}, 409)

        user = User.query.filter_by(id=account_id).first()
        if not user:
            return jsonify({"error": "No such user found"}, 403)

        authorization_info = request.headers.get("Authorization").split(" ")[1].split(":")
        authenticated_user = User.query.filter_by(email=authorization_info[0], password=authorization_info[1]).first()
        if user.email != authenticated_user.email:
            return jsonify({"error": "Cannot update another user's account"}), 403

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.password = password
        db.session.commit()

        return jsonify({
            "id": user.id,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "email": user.email
        }), 201

    if request.method == "DELETE":
        if not account_id or account_id < 0:
            return jsonify({"error": "Invalid account identifier"}), 400

        user = User.query.filter_by(id=account_id).first()
        if not user:
            return jsonify({"error": "No such user found"}), 400

        authorization_info = request.headers.get("Authorization").split(" ")[1].split(":")
        authenticated_user = User.query.filter_by(email=authorization_info[0], password=authorization_info[1]).first()
        if user.email != authenticated_user.email:
            return jsonify({"error": "Cannot delete another user's account"}), 403

        db.session.delete(user)
        db.session.commit()
        return "", 200


@account.route("/accounts/search", methods=["GET"])
@authorized
def search_account():
    first_name = request.args.get('firstName', "")
    last_name = request.args.get('lastName', "")
    email = request.args.get('email', "")
    from_arg = int(request.args.get('from', 0))
    size = int(request.args.get('size', 10))

    if from_arg < 0 or from_arg is None:
        return jsonify({"error": "From argument is invalid"}), 400
    if size <= 0 or not size:
        return jsonify({"error": "Size argument is invalid"}), 400

    filtered_users = [
        user for user in User.query.all()
        if first_name.lower() in user.first_name.lower() and
        last_name.lower() in user.last_name.lower()
        and email.lower() in user.email.lower()
    ]
    filtered_users = [
        {
            "id": user.id,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "email": user.email
        }
        for user_index, user in enumerate(filtered_users)
        if from_arg <= user_index < from_arg + size
    ]

    return jsonify(filtered_users), 200


@account.route("/registration", methods=["POST"])
def registration():
    authorization_header = request.headers.get("Authorization")
    if authorization_header:
        return jsonify({"error": "Account should not be authorized"}), 403

    if not request.data:
        return jsonify({"error": "No data in the request body"}), 400

    form_data = json.loads(request.data, strict=False)

    first_name = form_data.get("firstName", None)
    last_name = form_data.get("lastName", None)
    email = form_data.get("email", None)
    password = form_data.get("password", None)

    if not first_name or first_name.strip() == "" :
        return jsonify({"error": "First name was not given or given with an error"}), 400
    if not last_name or last_name.strip() == "" :
        return jsonify({"error": "Last name was not given or given with an error"}), 400
    if not email or email.strip() == "":
        return jsonify({"error": "Email was not given or given with an error"}), 400
    if not password or password.strip() == "":
        return jsonify({"error": "Password was not given or given with an error"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "User already exists"}), 409

    user = User(first_name=first_name, last_name=last_name, email=email, password=password)
    db.session.add(user)
    db.session.commit()
    return jsonify({
        "id": user.id,
        "firstName": first_name,
        "lastName": last_name,
        "email": email
    }), 201

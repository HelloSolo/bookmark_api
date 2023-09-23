from flask import Blueprint, request, jsonify
from python_usernames import is_safe_username
from werkzeug.security import generate_password_hash
import validators
from .constants import http_status_codes
from .utils import passwordValidator
from src.database import User, db

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth.post("/register")
def register():
    username = request.json["username"]
    email = request.json["email"]
    password = request.json["password"]

    if (validator_resp := passwordValidator.validate(password)) != True:
        return (
            jsonify({"message": validator_resp}),
            http_status_codes.HTTP_400_BAD_REQUEST,
        )

    if validator_resp := is_safe_username(username, max_length=5) != True:
        return (
            jsonify(
                {
                    "message": "Username should contain at least 5 characters and without space"
                }
            ),
            http_status_codes.HTTP_400_BAD_REQUEST,
        )

    if not validators.email(email):
        return (
            jsonify({"message": "Invalid email"}),
            http_status_codes.HTTP_400_BAD_REQUEST,
        )

    if User.query.filter_by(username=username).first() is not None:
        return (
            jsonify({"message": "Username name has already been used"}),
            http_status_codes.HTTP_409_CONFLICT,
        )

    if User.query.filter_by(email=email).first() is not None:
        return (
            jsonify({"message": "email name has already been used"}),
            http_status_codes.HTTP_409_CONFLICT,
        )

    pwd_hash = generate_password_hash(password)

    user = User(username=username, password=pwd_hash, email=email)

    db.session.add(user)
    db.session.commit()

    return (
        jsonify(
            {"message": "user created", "user": {"username": username, "email": email}}
        ),
        http_status_codes.HTTP_201_CREATED,
    )


@auth.get("/me")
def me():
    return {"user": "me"}

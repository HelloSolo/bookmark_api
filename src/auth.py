from flask import Blueprint, request, jsonify
from python_usernames import is_safe_username
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from flasgger import swag_from
import validators
from .constants import http_status_codes
from .utils import passwordValidator
from src.database import User, db

auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth.post("/register")
@swag_from("./docs/auth/register.yml")
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


@auth.post("/login")
@swag_from("./docs/auth/login.yml")
def login():
    email = request.json.get("email", "")
    pwd = request.json.get("password", "")

    user = User.query.filter_by(email=email).first()

    if user:
        pwd_is_correct = check_password_hash(pwhash=user.password, password=pwd)

        if pwd_is_correct:
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            return (
                jsonify(
                    {
                        "token": {"access": access_token, "refresh": refresh_token},
                        "user": {"username": user.username, "email": user.email},
                    }
                ),
                http_status_codes.HTTP_200_OK,
            )

    return (
        jsonify({"message": "Invalid Credentials"}),
        http_status_codes.HTTP_401_UNAUTHORIZED,
    )


@auth.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    return (
        jsonify({"user": {"username": user.username, "email": user.email}}),
        http_status_codes.HTTP_200_OK,
    )


@auth.get("/token/refresh")
@jwt_required(refresh=True)
def refresh_access_token():
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)

    return jsonify({"access": access_token}), http_status_codes.HTTP_200_OK

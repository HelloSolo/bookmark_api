import os
from flask import Flask, redirect, jsonify
from flask_jwt_extended import JWTManager
from flasgger import Swagger, swag_from
from src.config.swagger import template, swagger_config
from src.auth import auth
from src.bookmarks import bookmarks
from src.database import db, Bookmark
from src.constants import http_status_codes


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DATABASE_URI"),
            JWT_SECRET_KEY=os.environ.get("JWT_SECRET_KEY"),
            SWAGGER={"title": "Bookmark API", "uiversion": 3},
        )
    else:
        app.config.from_mapping(test_config)

    db.app = app
    db.init_app(app)

    JWTManager(app)
    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)

    Swagger(app, config=swagger_config, template=template)

    @app.get("/<short_url>")
    @swag_from("./docs/short_url.yml")
    def redirect_short_url_to_url(short_url):
        bookmark: Bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404(
            "Item not found"
        )

        bookmark.visits += 1

        db.session.commit()

        return redirect(bookmark.url)

    @app.errorhandler(http_status_codes.HTTP_404_NOT_FOUND)
    def handle_404(e):
        return (
            jsonify({"message": "resource not found"}),
            http_status_codes.HTTP_404_NOT_FOUND,
        )

    @app.errorhandler(http_status_codes.HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return (
            jsonify({"message": "server is busy, we are working on it"}),
            http_status_codes.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return app

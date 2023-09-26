from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
import validators
from .constants import http_status_codes
from .database import Bookmark, db

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")


@bookmarks.route("/", methods=["GET", "POST"])
@jwt_required()
def handle_bookmarks():
    current_user = get_jwt_identity()

    if request.method == "POST":
        body = request.get_json().get("body", "")
        url = request.get_json().get("url", "")

        if not validators.url(url):
            return (
                jsonify({"message": "Invalid url, enter a valid on"}),
                http_status_codes.HTTP_400_BAD_REQUEST,
            )

        if Bookmark.query.filter_by(url=url).first():
            return (
                jsonify({"message": "url already exists"}),
                http_status_codes.HTTP_409_CONFLICT,
            )

        bookmark = Bookmark(url=url, body=body, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()

        return (
            jsonify(
                {
                    "id": bookmark.id,
                    "url": bookmark.url,
                    "short_url": bookmark.short_url,
                    "body": bookmark.body,
                    "visits": bookmark.visits,
                    "created_at": bookmark.created_at,
                    "updated_at": bookmark.updated_at,
                }
            ),
            http_status_codes.HTTP_201_CREATED,
        )

    else:
        bookmarks = Bookmark.query.filter_by(user_id=current_user)

        data = []

        for bookmark in bookmarks:
            data.append(
                {
                    "id": bookmark.id,
                    "url": bookmark.url,
                    "short_url": bookmark.short_url,
                    "body": bookmark.body,
                    "visits": bookmark.visits,
                    "created_at": bookmark.created_at,
                    "updated_at": bookmark.updated_at,
                }
            )

        return (
            jsonify({"data": data}),
            http_status_codes.HTTP_200_OK,
        )

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
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 5, type=int)

        bookmarks = Bookmark.query.filter_by(user_id=current_user).paginate(
            page=page, per_page=per_page
        )

        data = []

        for bookmark in bookmarks.items:
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

        meta = {
            "page": bookmarks.page,
            "pages": bookmarks.pages,
            "total_count": bookmarks.total,
            "prev_page": bookmarks.prev_num,
            "next_page": bookmarks.has_next,
            "has_next": bookmarks.has_next,
            "prev_next": bookmarks.has_prev,
        }

        return (
            jsonify({"data": data, "meta": meta}),
            http_status_codes.HTTP_200_OK,
        )


@bookmarks.get("/<int:id>")
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(user_id=current_user, id=id).first_or_404(
        "Item not found"
    )

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
        http_status_codes.HTTP_200_OK,
    )


@bookmarks.patch("/<int:id>")
@jwt_required()
def edit_bookmark(id):
    current_user = get_jwt_identity()

    bookmark: Bookmark = Bookmark.query.filter_by(
        user_id=current_user, id=id
    ).first_or_404("Item not found")

    url = request.get_json().get("url", bookmark.url)
    body = request.get_json().get("body", bookmark.body)

    if not validators.url(url):
        return (
            jsonify({"message": "invalid url"}),
            http_status_codes.HTTP_400_BAD_REQUEST,
        )

    bookmark.url = url
    bookmark.body = body

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
        http_status_codes.HTTP_200_OK,
    )

from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity, jwt_required
from flasgger import swag_from
import validators
from .constants import http_status_codes
from .database import Bookmark, db

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")


@bookmarks.route("/", methods=["GET", "POST"])
@jwt_required()
@swag_from("./docs/bookmarks/create_get_bookmarks.yml")
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
        )  # The data fetched from the response is an object so we still need to extract the data

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
@swag_from("./docs/bookmarks/get_bookmark.yml")
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


@bookmarks.put("/<int:id>")
@bookmarks.patch("/<int:id>")
@jwt_required()
@swag_from("./docs/bookmarks/edit_bookmark.yml")
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


@bookmarks.delete("/<int:id>")
@jwt_required()
@swag_from("./docs/bookmarks/delete_bookmark.yml")
def delete_bookmark(id):
    current_user = get_jwt_identity()

    bookmark: Bookmark = Bookmark.query.filter_by(
        user_id=current_user, id=id
    ).first_or_404("Item not found")

    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({"message": "item deleted"}), http_status_codes.HTTP_204_NO_CONTENT


@bookmarks.get("/stats")
@jwt_required()
@swag_from("./docs/bookmarks/stats.yml")
def get_stats():
    current_user = get_jwt_identity()

    bookmarks: Bookmark = Bookmark.query.filter_by(user_id=current_user).all()

    data = []

    for bookmark in bookmarks:
        data.append(
            {
                "visits": bookmark.visits,
                "url": bookmark.url,
                "short_url": bookmark.short_url,
                "id": bookmark.id,
            }
        )

    return jsonify({"data": data}), http_status_codes.HTTP_200_OK

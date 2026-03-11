from typing import TypedDict

from bafser import JsonObj, doc_api, protected_route, response_msg, abort_if_none
from flask import Blueprint, Response

from data._operations import Operations
from data.rating import Rating, RatingDict
from data.recipe import Recipe
from data.user import User

bp = Blueprint("rating", __name__)


class CreateOrUpdateRatingJson(JsonObj):
    rating: int  # 1-5


class RatingStatsDict(TypedDict):
    recipe_id: int
    average: float
    count: int
    distribution: dict[str, int]


@bp.get("/api/recipes/<int:recipe_id>/ratings")
@doc_api(res=RatingStatsDict, desc="Get rating statistics for a recipe")
def get_ratings_stats(recipe_id: int) -> RatingStatsDict | Response:
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    avg, count, distribution = Rating.get_stats(recipe_id)
    return {
        "recipe_id": recipe_id,
        "average": round(avg, 2),
        "count": count,
        "distribution": distribution,
    }


@bp.get("/api/recipes/<int:recipe_id>/ratings/me")
@doc_api(res=RatingDict, desc="Get current user's rating for a recipe")
@protected_route(perms=Operations.rating_view)
def get_my_rating(recipe_id: int):
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    rating = abort_if_none(Rating.get_by_user_and_recipe(User.current.id, recipe_id), msg="Not rated")
    return rating.get_dict()


@bp.post("/api/recipes/<int:recipe_id>/ratings")
@doc_api(req=CreateOrUpdateRatingJson, res=RatingDict, desc="Rate a recipe (create or update)")
@protected_route(perms=Operations.rating_create)
def rate_recipe(recipe_id: int):
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    req = CreateOrUpdateRatingJson.get_from_req()
    if not (1 <= req.rating <= 5):
        return response_msg("Rating must be between 1 and 5", 400)
    # Check if already rated
    existing = Rating.get_by_user_and_recipe(User.current.id, recipe_id)
    if existing:
        # Update
        existing.update(rating=req.rating)
        return existing.get_dict()
    else:
        # Create
        rating = Rating.new(
            user_id=User.current.id,
            recipe_id=recipe_id,
            rating=req.rating,
        )
        return rating.get_dict()


@bp.delete("/api/recipes/<int:recipe_id>/ratings")
@doc_api(res=None, desc="Remove current user's rating for a recipe")
@protected_route(perms=Operations.rating_delete)
def delete_rating(recipe_id: int):
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    rating = abort_if_none(Rating.get_by_user_and_recipe(User.current.id, recipe_id), msg="Rating not found")
    rating.db_sess.delete(rating)
    rating.db_sess.commit()
    return "", 204

from typing import TypedDict

from bafser import JsonObj, abort_if_none, doc_api, protected_route, response_msg, use_db_sess
from flask import Blueprint, Response
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from data._operations import Operations
from data.rating import Rating, RatingDict
from data.recipe import Recipe
from data.user import User

bp = Blueprint("rating", __name__)


class CreateOrUpdateRatingJson(JsonObj):
    """JSON schema for creating or updating a rating.

    Attributes:
        rating: Integer rating value between 1 and 5 inclusive.
    """

    rating: int  # 1-5


class RatingStatsDict(TypedDict):
    """Dictionary containing rating statistics for a recipe.

    Attributes:
        recipe_id: ID of the recipe.
        average: Average rating (rounded to 2 decimal places).
        count: Total number of ratings.
        distribution: Mapping from rating value (as string) to count.
    """

    recipe_id: int
    average: float
    count: int
    distribution: dict[str, int]


@bp.get("/api/recipes/<int:recipe_id>/ratings")
@doc_api(res=RatingStatsDict, desc="Get rating statistics for a recipe")
def get_ratings_stats(recipe_id: int) -> RatingStatsDict | Response:
    """Retrieve rating statistics for a specific recipe.

    Args:
        recipe_id: ID of the recipe.

    Returns:
        RatingStatsDict: Dictionary with average, count, and distribution of ratings.

    Raises:
        HTTPException: 404 if recipe not found.
    """
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
def get_my_rating(recipe_id: int) -> RatingDict:
    """Retrieve the current user's rating for a specific recipe.

    Requires authentication and the `rating_view` permission.

    Args:
        recipe_id: ID of the recipe.

    Returns:
        dict: The rating object as JSON.

    Raises:
        HTTPException: 404 if recipe not found or user hasn't rated it.
        HTTPException: 403 if user lacks permission.
    """
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    rating = abort_if_none(Rating.get_by_user_and_recipe(User.current.id, recipe_id), msg="Not rated")
    return rating.get_dict()


@bp.post("/api/recipes/<int:recipe_id>/ratings")
@doc_api(req=CreateOrUpdateRatingJson, res=RatingDict, desc="Rate a recipe (create or update)")
@protected_route(perms=Operations.rating_create)
@use_db_sess
def rate_recipe(db_sess: Session, recipe_id: int) -> RatingDict | Response:
    """Create or update the current user's rating for a recipe.

    Requires authentication and the `rating_create` permission.
    If the user already rated the recipe, the rating is updated.
    Rating value must be between 1 and 5 inclusive.

    Args:
        db_sess: Database session (injected by @use_db_sess).
        recipe_id: ID of the recipe to rate.

    Returns:
        dict: The rating object as JSON (new or updated).

    Raises:
        HTTPException: 404 if recipe not found.
        HTTPException: 400 if rating is out of range.
        HTTPException: 403 if user lacks permission.
        HTTPException: 409 on concurrent conflict (rare).
    """
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    req = CreateOrUpdateRatingJson.get_from_req()
    if not (1 <= req.rating <= 5):
        return response_msg("Rating must be between 1 and 5", 400)

    # Try to find existing rating
    existing = Rating.get_by_user_and_recipe(User.current.id, recipe_id)
    if existing:
        existing.update(rating=req.rating)
        Rating.recalculate_recipe_stats(recipe_id)
        return existing.get_dict()
    # Attempt to create new rating
    try:
        rating = Rating.new(
            user_id=User.current.id,
            recipe_id=recipe_id,
            rating=req.rating,
        )
        Rating.recalculate_recipe_stats(recipe_id)
        return rating.get_dict()
    except IntegrityError:
        db_sess.rollback()
        # Race condition: another request inserted concurrently
        existing = Rating.get_by_user_and_recipe(User.current.id, recipe_id)
        if existing:
            existing.update(rating=req.rating)
            Rating.recalculate_recipe_stats(recipe_id)
            return existing.get_dict()
        else:
            return response_msg("Conflict", 409)


@bp.delete("/api/recipes/<int:recipe_id>/ratings")
@doc_api(res=None, desc="Remove current user's rating for a recipe")
@protected_route(perms=Operations.rating_delete)
@use_db_sess
def delete_rating(db_sess: Session, recipe_id: int) -> tuple[str, int]:
    """Delete the current user's rating for a recipe.

    Requires authentication and the `rating_delete` permission.

    Args:
        db_sess: Database session (injected by @use_db_sess).
        recipe_id: ID of the recipe.

    Returns:
        tuple: Empty response with status 204 on success.

    Raises:
        HTTPException: 404 if recipe not found or user hasn't rated it.
        HTTPException: 403 if user lacks permission.
    """
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    rating = abort_if_none(Rating.get_by_user_and_recipe(User.current.id, recipe_id), "rating")
    db_sess.delete(rating)
    db_sess.commit()
    Rating.recalculate_recipe_stats(recipe_id)
    return "", 204

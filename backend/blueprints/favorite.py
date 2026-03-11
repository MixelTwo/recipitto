from typing import TypedDict

from bafser import doc_api, jsonify_list, protected_route, response_msg, abort_if_none, use_db_sess
from flask import Blueprint, Response
from sqlalchemy.orm import Session

from data._operations import Operations
from data.favorite import Favorite, FavoriteDict
from data.recipe import Recipe
from data.user import User

bp = Blueprint("favorite", __name__)


class FavoriteCheckDict(TypedDict):
    favorited: bool
    favorite: FavoriteDict | None


@bp.get("/api/favorites")
@doc_api(res=list[FavoriteDict], desc="List current user's favorite recipes")
@protected_route(perms=Operations.favorite_view)
@use_db_sess
def list_favorites(db_sess: Session):
    favorites = Favorite.get_by_user(db_sess, User.current.id)
    return jsonify_list(favorites)


@bp.get("/api/recipes/<int:recipe_id>/favorite")
@doc_api(res=FavoriteCheckDict, desc="Check if recipe is favorited by current user")
@protected_route(perms=Operations.favorite_view)
@use_db_sess
def check_favorite(db_sess: Session, recipe_id: int) -> FavoriteCheckDict | Response:
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    favorite = Favorite.get_by_user_and_recipe(db_sess, User.current.id, recipe_id)
    return {
        "favorited": favorite is not None,
        "favorite": favorite.get_dict() if favorite else None,
    }


@bp.post("/api/recipes/<int:recipe_id>/favorite")
@doc_api(res=FavoriteDict, desc="Add recipe to favorites")
@protected_route(perms=Operations.favorite_create)
@use_db_sess
def add_favorite(db_sess: Session, recipe_id: int):
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    # Check if already favorited
    if Favorite.exists(db_sess, User.current.id, recipe_id):
        return response_msg("Already in favorites", 400)
    favorite = Favorite.new(
        user_id=User.current.id,
        recipe_id=recipe_id,
    )
    db_sess.add(favorite)
    return favorite.get_dict()


@bp.delete("/api/recipes/<int:recipe_id>/favorite")
@doc_api(res=None, desc="Remove recipe from favorites")
@protected_route(perms=Operations.favorite_delete)
@use_db_sess
def remove_favorite(db_sess: Session, recipe_id: int):
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    favorite = abort_if_none(Favorite.get_by_user_and_recipe(db_sess, User.current.id, recipe_id), msg="Not in favorites")
    db_sess.delete(favorite)
    db_sess.commit()
    return "", 204

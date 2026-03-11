from typing import TypedDict

from bafser import doc_api, jsonify_list, protected_route, response_msg, abort_if_none
from flask import Blueprint, Response

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
def list_favorites():
    favorites = Favorite.get_by_user(User.current.id)
    return jsonify_list(favorites)


@bp.get("/api/recipes/<int:recipe_id>/favorite")
@doc_api(res=FavoriteCheckDict, desc="Check if recipe is favorited by current user")
@protected_route(perms=Operations.favorite_view)
def check_favorite(recipe_id: int) -> FavoriteCheckDict | Response:
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    favorite = Favorite.get_by_user_and_recipe(User.current.id, recipe_id)
    return {
        "favorited": favorite is not None,
        "favorite": favorite.get_dict() if favorite else None,
    }


@bp.post("/api/recipes/<int:recipe_id>/favorite")
@doc_api(res=FavoriteDict, desc="Add recipe to favorites")
@protected_route(perms=Operations.favorite_create)
def add_favorite(recipe_id: int):
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    if Favorite.exists(User.current.id, recipe_id):
        return response_msg("Already in favorites", 400)
    favorite = Favorite.new(
        user_id=User.current.id,
        recipe_id=recipe_id,
    )
    return favorite.get_dict()


@bp.delete("/api/recipes/<int:recipe_id>/favorite")
@doc_api(res=None, desc="Remove recipe from favorites")
@protected_route(perms=Operations.favorite_delete)
def remove_favorite(recipe_id: int):
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    favorite = abort_if_none(Favorite.get_by_user_and_recipe(User.current.id, recipe_id), msg="Not in favorites")
    favorite.db_sess.delete(favorite)
    favorite.db_sess.commit()
    return "", 204

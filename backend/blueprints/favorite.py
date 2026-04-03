from typing import TypedDict

from bafser import abort_if_none, doc_api, protected_route, response_msg, use_db_sess
from flask import Blueprint, Response, jsonify
from sqlalchemy.orm import Session, joinedload

from data._operations import Operations
from data.favorite import Favorite, FavoriteDict
from data.recipe import Recipe, RecipeDict
from data.user import User

bp = Blueprint("favorite", __name__)


class FavoriteCheckDict(TypedDict):
    favorited: bool
    favorite: FavoriteDict | None


class FavoriteWithRecipeDict(TypedDict):
    recipe: RecipeDict
    added_at: str


@bp.get("/api/favorites")
@doc_api(res=list[FavoriteWithRecipeDict], desc="List current user's favorite recipes")
@protected_route(perms=Operations.favorite_view)
@use_db_sess
def list_favorites(db_sess: Session):
    favorites = (
        db_sess.query(Favorite).options(joinedload(Favorite.recipe)).filter_by(user_id=User.current.id).order_by(Favorite.added_at.desc()).all()
    )
    result: list[FavoriteWithRecipeDict] = []
    for fav in favorites:
        result.append(
            {
                "recipe": fav.recipe.get_dict(),
                "added_at": fav.added_at.isoformat(),
            }
        )
    return jsonify(result)


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
@use_db_sess
def add_favorite(db_sess: Session, recipe_id: int):
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    from sqlalchemy.exc import IntegrityError

    try:
        favorite = Favorite.new(
            user_id=User.current.id,
            recipe_id=recipe_id,
        )
        db_sess.commit()
    except IntegrityError:
        db_sess.rollback()
        return response_msg("Already in favorites", 400)
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

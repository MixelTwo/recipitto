from bafser import Image, JsonObj, doc_api, jsonify_list, protected_route, response_msg, abort_if_none, use_db_sess
from flask import Blueprint
from sqlalchemy.orm import Session

from data._operations import Operations
from data.recipe import Recipe
from data.recipe_image import RecipeImage, RecipeImageDict
from data.user import User

bp = Blueprint("recipe_image", __name__)


class CreateRecipeImageJson(JsonObj):
    image_id: int


@bp.get("/api/recipes/<int:recipe_id>/images")
@doc_api(res=list[RecipeImageDict], desc="List images of a recipe")
def list_images(recipe_id: int):
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    images = RecipeImage.query2().filter_by(recipe_id=recipe_id).all()
    return jsonify_list(images)


@bp.get("/api/recipes/<int:recipe_id>/images/<int:image_id>")
@doc_api(res=RecipeImageDict, desc="Get a recipe image by ID")
def get_image(recipe_id: int, image_id: int):
    recipe_image = abort_if_none(RecipeImage.query2().filter_by(recipe_id=recipe_id, image_id=image_id).first(), msg="Image not found in recipe")
    return recipe_image.get_dict()


@bp.post("/api/recipes/<int:recipe_id>/images")
@doc_api(req=CreateRecipeImageJson, res=RecipeImageDict, desc="Add an image to a recipe")
@protected_route(perms=Operations.recipe_image_create)
@use_db_sess
def create_image(db_sess: Session, recipe_id: int):
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_moderate_recipes) and recipe.author_id != User.current.id:
        return response_msg("You can only edit your own recipes", 403)
    req = CreateRecipeImageJson.get_from_req()
    # Check if image exists
    abort_if_none(Image.get2(req.image_id), "image")
    # Check if already associated
    existing = RecipeImage.query2().filter_by(recipe_id=recipe_id, image_id=req.image_id).first()
    if existing:
        return response_msg("Image already added to recipe", 400)
    recipe_image = RecipeImage.new(
        recipe_id=recipe_id,
        image_id=req.image_id,
        creator=User.current,
    )
    return recipe_image.get_dict()


@bp.delete("/api/recipes/<int:recipe_id>/images/<int:image_id>")
@doc_api(res=None, desc="Remove an image from a recipe")
@protected_route(perms=Operations.recipe_image_delete)
@use_db_sess
def delete_image(db_sess: Session, recipe_id: int, image_id: int):
    recipe_image = abort_if_none(RecipeImage.query2().filter_by(recipe_id=recipe_id, image_id=image_id).first(), msg="Image not found in recipe")
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_moderate_recipes) and recipe.author_id != User.current.id:
        return response_msg("You can only edit your own recipes", 403)
    recipe_image.delete2()
    return "", 204

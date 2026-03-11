from bafser import JsonObj, JsonOpt, Undefined, abort_if_none, doc_api, jsonify_list, protected_route, response_msg, use_db_sess
from flask import Blueprint
from sqlalchemy.orm import Session

from data._operations import Operations
from data.recipe import Recipe
from data.recipe_ingredient import RecipeIngredient, RecipeIngredientDict
from data.user import User

bp = Blueprint("recipe_ingredient", __name__)


class CreateRecipeIngredientJson(JsonObj):
    ingredient_id: int
    quantity: float
    unit: str


class UpdateRecipeIngredientJson(JsonObj):
    quantity: JsonOpt[float] = Undefined
    unit: JsonOpt[str] = Undefined


@bp.get("/api/recipes/<int:recipe_id>/ingredients")
@doc_api(res=list[RecipeIngredientDict], desc="List ingredients of a recipe")
@use_db_sess
def list_ingredients(db_sess: Session, recipe_id: int):
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    ingredients = RecipeIngredient.get_by_recipe(db_sess, recipe_id)
    return jsonify_list(ingredients)


@bp.get("/api/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>")
@doc_api(res=RecipeIngredientDict, desc="Get a recipe ingredient by IDs")
@use_db_sess
def get_ingredient(db_sess: Session, recipe_id: int, ingredient_id: int):
    ingredient = abort_if_none(
        RecipeIngredient.get_by_recipe_and_ingredient(db_sess, recipe_id, ingredient_id),
        msg="Ingredient not found in recipe",
    )
    return ingredient.get_dict()


@bp.post("/api/recipes/<int:recipe_id>/ingredients")
@doc_api(req=CreateRecipeIngredientJson, res=RecipeIngredientDict, desc="Add an ingredient to a recipe")
@protected_route(perms=Operations.recipe_ingredient_create)
@use_db_sess
def create_ingredient(db_sess: Session, recipe_id: int):
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_moderate_recipes) and recipe.author_id != User.current.id:
        return response_msg("You can only edit your own recipes", 403)
    req = CreateRecipeIngredientJson.get_from_req()
    # Check if ingredient already exists
    existing = RecipeIngredient.get_by_recipe_and_ingredient(db_sess, recipe_id, req.ingredient_id)
    if existing:
        return response_msg("Ingredient already added to recipe", 400)
    ingredient = RecipeIngredient.new(
        recipe_id=recipe_id,
        ingredient_id=req.ingredient_id,
        quantity=req.quantity,
        unit=req.unit,
    )
    return ingredient.get_dict()


@bp.patch("/api/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>")
@doc_api(req=UpdateRecipeIngredientJson, res=RecipeIngredientDict, desc="Update a recipe ingredient")
@protected_route(perms=Operations.recipe_ingredient_update)
@use_db_sess
def update_ingredient(db_sess: Session, recipe_id: int, ingredient_id: int):
    ingredient = abort_if_none(
        RecipeIngredient.get_by_recipe_and_ingredient(db_sess, recipe_id, ingredient_id), msg="Ingredient not found in recipe"
    )
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_moderate_recipes) and recipe.author_id != User.current.id:
        return response_msg("You can only edit your own recipes", 403)
    req = UpdateRecipeIngredientJson.get_from_req()
    ingredient.update(
        quantity=Undefined.default(req.quantity, None),
        unit=Undefined.default(req.unit, None),
    )
    return ingredient.get_dict()


@bp.delete("/api/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>")
@doc_api(res=None, desc="Remove an ingredient from a recipe")
@protected_route(perms=Operations.recipe_ingredient_delete)
@use_db_sess
def delete_ingredient(db_sess: Session, recipe_id: int, ingredient_id: int):
    ingredient = abort_if_none(
        RecipeIngredient.get_by_recipe_and_ingredient(db_sess, recipe_id, ingredient_id), msg="Ingredient not found in recipe"
    )
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_moderate_recipes) and recipe.author_id != User.current.id:
        return response_msg("You can only edit your own recipes", 403)
    db_sess.delete(ingredient)
    db_sess.commit()
    return "", 204

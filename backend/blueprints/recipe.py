from bafser import JsonObj, JsonOpt, Undefined, doc_api, jsonify_list, protected_route, response_msg, abort_if_none, use_db_sess
from flask import Blueprint
from sqlalchemy.orm import Session

from data._operations import Operations
from data.recipe import Recipe, RecipeDict, RecipeStatus, TRecipeStatus
from data.user import User

bp = Blueprint("recipe", __name__)


class CreateRecipeJson(JsonObj):
    title: str
    description: str
    active_time: int
    total_time: int
    difficulty: int
    category_id: int
    main_image_id: JsonOpt[int] = Undefined
    status: JsonOpt[TRecipeStatus] = Undefined


class UpdateRecipeJson(JsonObj):
    title: JsonOpt[str] = Undefined
    description: JsonOpt[str] = Undefined
    active_time: JsonOpt[int] = Undefined
    total_time: JsonOpt[int] = Undefined
    difficulty: JsonOpt[int] = Undefined
    category_id: JsonOpt[int] = Undefined
    main_image_id: JsonOpt[int] = Undefined
    status: JsonOpt[TRecipeStatus] = Undefined


@bp.get("/api/recipes")
@doc_api(res=list[RecipeDict], desc="List recipes with optional filtering")
def list_recipes():
    # TODO: implement filtering, sorting, pagination
    recipes = Recipe.all2()
    return jsonify_list(recipes)


@bp.get("/api/recipes/<int:recipe_id>")
@doc_api(res=RecipeDict, desc="Get a recipe by ID")
def get_recipe(recipe_id: int):
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    return recipe.get_dict()


@bp.post("/api/recipes")
@doc_api(req=CreateRecipeJson, res=RecipeDict, desc="Create a new recipe")
@protected_route(perms=Operations.recipe_create)
@use_db_sess
def create_recipe(db_sess: Session):
    req = CreateRecipeJson.get_from_req()
    # Validate status
    status = None
    if Undefined.defined(req.status):
        try:
            status = RecipeStatus(req.status)
        except ValueError:
            return response_msg("Invalid status", 400)
    recipe = Recipe.new(
        title=req.title,
        description=req.description,
        active_time=req.active_time,
        total_time=req.total_time,
        difficulty=req.difficulty,
        author=User.current,
        category_id=req.category_id,
        main_image_id=Undefined.default(req.main_image_id),
        status=status or RecipeStatus.DRAFT,
    )
    return recipe.get_dict()


@bp.patch("/api/recipes/<int:recipe_id>")
@doc_api(req=UpdateRecipeJson, res=RecipeDict, desc="Update a recipe")
@protected_route(perms=Operations.recipe_update)
@use_db_sess
def update_recipe(db_sess: Session, recipe_id: int):
    req = UpdateRecipeJson.get_from_req()
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_moderate_recipes) and recipe.author_id != User.current.id:
        return response_msg("You can only edit your own recipes", 403)
    # Prepare update parameters
    status = None
    if Undefined.defined(req.status):
        try:
            status = RecipeStatus(req.status)
        except ValueError:
            return response_msg("Invalid status", 400)
    recipe.update(
        title=Undefined.default(req.title, None),
        description=Undefined.default(req.description, None),
        active_time=Undefined.default(req.active_time, None),
        total_time=Undefined.default(req.total_time, None),
        difficulty=Undefined.default(req.difficulty, None),
        category_id=Undefined.default(req.category_id, None),
        main_image_id=Undefined.default(req.main_image_id, None),
        status=status,
    )
    return recipe.get_dict()


@bp.delete("/api/recipes/<int:recipe_id>")
@doc_api(res=None, desc="Delete a recipe")
@protected_route(perms=Operations.recipe_delete)
@use_db_sess
def delete_recipe(db_sess: Session, recipe_id: int):
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_moderate_recipes) and recipe.author_id != User.current.id:
        return response_msg("You can only delete your own recipes", 403)
    recipe.delete2()
    return "", 204

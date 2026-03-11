from bafser import JsonObj, JsonOpt, Undefined, doc_api, jsonify_list, protected_route, response_msg, abort_if_none, use_db_sess
from flask import Blueprint
from sqlalchemy.orm import Session

from data._operations import Operations
from data.recipe import Recipe
from data.recipe_step import RecipeStep, RecipeStepDict
from data.user import User

bp = Blueprint("recipe_step", __name__)


class CreateRecipeStepJson(JsonObj):
    step_number: int
    text: str
    image_id: JsonOpt[int] = Undefined


class UpdateRecipeStepJson(JsonObj):
    step_number: JsonOpt[int] = Undefined
    text: JsonOpt[str] = Undefined
    image_id: JsonOpt[int] = Undefined


@bp.get("/api/recipes/<int:recipe_id>/steps")
@doc_api(res=list[RecipeStepDict], desc="List steps of a recipe")
@use_db_sess
def list_steps(db_sess: Session, recipe_id: int):
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    steps = RecipeStep.get_by_recipe(db_sess, recipe_id)
    return jsonify_list(steps)


@bp.get("/api/recipes/<int:recipe_id>/steps/<int:step_id>")
@doc_api(res=RecipeStepDict, desc="Get a recipe step by ID")
def get_step(recipe_id: int, step_id: int):
    step = abort_if_none(RecipeStep.get2(step_id), "step")
    if step.recipe_id != recipe_id:
        return response_msg("Step not found", 404)
    return step.get_dict()


@bp.post("/api/recipes/<int:recipe_id>/steps")
@doc_api(req=CreateRecipeStepJson, res=RecipeStepDict, desc="Add a step to a recipe")
@protected_route(perms=Operations.recipe_step_create)
def create_step(recipe_id: int):
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_moderate_recipes) and recipe.author_id != User.current.id:
        return response_msg("You can only edit your own recipes", 403)
    req = CreateRecipeStepJson.get_from_req()
    step = RecipeStep.new(
        recipe_id=recipe_id,
        step_number=req.step_number,
        text=req.text,
        image_id=Undefined.default(req.image_id, None),
    )
    return step.get_dict()


@bp.patch("/api/recipes/<int:recipe_id>/steps/<int:step_id>")
@doc_api(req=UpdateRecipeStepJson, res=RecipeStepDict, desc="Update a recipe step")
@protected_route(perms=Operations.recipe_step_update)
def update_step(recipe_id: int, step_id: int):
    step = abort_if_none(RecipeStep.get2(step_id), "step")
    if step.recipe_id != recipe_id:
        return response_msg("Step not found", 404)
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_moderate_recipes) and recipe.author_id != User.current.id:
        return response_msg("You can only edit your own recipes", 403)
    req = UpdateRecipeStepJson.get_from_req()
    step.update(
        step_number=Undefined.default(req.step_number, None),
        text=Undefined.default(req.text, None),
        image_id=Undefined.default(req.image_id, None),
    )
    return step.get_dict()


@bp.delete("/api/recipes/<int:recipe_id>/steps/<int:step_id>")
@doc_api(res=None, desc="Delete a recipe step")
@protected_route(perms=Operations.recipe_step_delete)
def delete_step(recipe_id: int, step_id: int):
    step = abort_if_none(RecipeStep.get2(step_id), "step")
    if step.recipe_id != recipe_id:
        return response_msg("Step not found", 404)
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_moderate_recipes) and recipe.author_id != User.current.id:
        return response_msg("You can only edit your own recipes", 403)
    step.delete2()
    return "", 204

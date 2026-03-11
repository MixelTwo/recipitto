from bafser import JsonObj, JsonOpt, Undefined, doc_api, jsonify_list, protected_route, abort_if_none
from flask import Blueprint

from data._operations import Operations
from data.ingredient import Ingredient, IngredientDict

bp = Blueprint("ingredient", __name__)


class CreateIngredientJson(JsonObj):
    name: str
    category_id: int


class UpdateIngredientJson(JsonObj):
    name: JsonOpt[str] = Undefined
    category_id: JsonOpt[int] = Undefined


@bp.get("/api/ingredients")
@doc_api(res=list[IngredientDict], desc="List all ingredients")
def list_ingredients():
    ingredients = Ingredient.all2()
    return jsonify_list(ingredients)


@bp.get("/api/ingredients/<int:ingredient_id>")
@doc_api(res=IngredientDict, desc="Get an ingredient by ID")
def get_ingredient(ingredient_id: int):
    ingredient = abort_if_none(Ingredient.get2(ingredient_id), "ingredient")
    return ingredient.get_dict()


@bp.post("/api/ingredients")
@doc_api(req=CreateIngredientJson, res=IngredientDict, desc="Create a new ingredient")
@protected_route(perms=Operations.ingredient_create)
def create_ingredient():
    req = CreateIngredientJson.get_from_req()
    ingredient = Ingredient.new(req.name, req.category_id)
    return ingredient.get_dict()


@bp.patch("/api/ingredients/<int:ingredient_id>")
@doc_api(req=UpdateIngredientJson, res=IngredientDict, desc="Update an ingredient")
@protected_route(perms=Operations.ingredient_update)
def update_ingredient(ingredient_id: int):
    req = UpdateIngredientJson.get_from_req()
    ingredient = abort_if_none(Ingredient.get2(ingredient_id), "ingredient")
    ingredient.update(
        name=Undefined.default(req.name, None),
        category_id=Undefined.default(req.category_id, None),
    )
    return ingredient.get_dict()


@bp.delete("/api/ingredients/<int:ingredient_id>")
@doc_api(res=None, desc="Delete an ingredient")
@protected_route(perms=Operations.ingredient_delete)
def delete_ingredient(ingredient_id: int):
    ingredient = abort_if_none(Ingredient.get2(ingredient_id), "ingredient")
    ingredient.delete2()
    return "", 204

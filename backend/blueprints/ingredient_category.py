from bafser import JsonObj, JsonOpt, Undefined, abort_if_none, doc_api, jsonify_list, protected_route
from flask import Blueprint

from data._operations import Operations
from data.ingredient_category import IngredientCategory, IngredientCategoryDict

bp = Blueprint("ingredient_category", __name__)


class CreateIngredientCategoryJson(JsonObj):
    name: str


class UpdateIngredientCategoryJson(JsonObj):
    name: JsonOpt[str] = Undefined


@bp.get("/api/ingredient-categories")
@doc_api(res=list[IngredientCategoryDict], desc="List all ingredient categories")
def list_categories():
    categories = IngredientCategory.all2()
    return jsonify_list(categories)


@bp.get("/api/ingredient-categories/<int:category_id>")
@doc_api(res=IngredientCategoryDict, desc="Get an ingredient category by ID")
def get_category(category_id: int):
    category = abort_if_none(IngredientCategory.get2(category_id), "category")
    return category.get_dict()


@bp.post("/api/ingredient-categories")
@doc_api(req=CreateIngredientCategoryJson, res=IngredientCategoryDict, desc="Create a new ingredient category")
@protected_route(perms=Operations.ingredient_category_create)
def create_category():
    req = CreateIngredientCategoryJson.get_from_req()
    category = IngredientCategory.new(req.name)
    return category.get_dict()


@bp.patch("/api/ingredient-categories/<int:category_id>")
@doc_api(req=UpdateIngredientCategoryJson, res=IngredientCategoryDict, desc="Update an ingredient category")
@protected_route(perms=Operations.ingredient_category_update)
def update_category(category_id: int):
    req = UpdateIngredientCategoryJson.get_from_req()
    category = abort_if_none(IngredientCategory.get2(category_id), "category")
    category.update(name=Undefined.default(req.name, None))
    return category.get_dict()


@bp.delete("/api/ingredient-categories/<int:category_id>")
@doc_api(res=None, desc="Delete an ingredient category")
@protected_route(perms=Operations.ingredient_category_delete)
def delete_category(category_id: int):
    category = abort_if_none(IngredientCategory.get2(category_id), "category")
    category.delete2()
    return "", 204

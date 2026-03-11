from bafser import JsonObj, JsonOpt, Undefined, doc_api, jsonify_list, protected_route, abort_if_none, use_db_sess
from flask import Blueprint
from sqlalchemy.orm import Session

from data._operations import Operations
from data.recipe_category import RecipeCategory, RecipeCategoryDict

bp = Blueprint("recipe_category", __name__)


class CreateRecipeCategoryJson(JsonObj):
    name: str


class UpdateRecipeCategoryJson(JsonObj):
    name: JsonOpt[str] = Undefined


@bp.get("/api/recipe-categories")
@doc_api(res=list[RecipeCategoryDict], desc="List all recipe categories")
def list_categories():
    categories = RecipeCategory.all2()
    return jsonify_list(categories)


@bp.get("/api/recipe-categories/<int:category_id>")
@doc_api(res=RecipeCategoryDict, desc="Get a recipe category by ID")
def get_category(category_id: int):
    category = abort_if_none(RecipeCategory.get2(category_id), "category")
    return category.get_dict()


@bp.post("/api/recipe-categories")
@doc_api(req=CreateRecipeCategoryJson, res=RecipeCategoryDict, desc="Create a new recipe category")
@protected_route(perms=Operations.recipe_category_create)
@use_db_sess
def create_category(db_sess: Session):
    req = CreateRecipeCategoryJson.get_from_req()
    category = RecipeCategory.new(req.name)
    return category.get_dict()


@bp.patch("/api/recipe-categories/<int:category_id>")
@doc_api(req=UpdateRecipeCategoryJson, res=RecipeCategoryDict, desc="Update a recipe category")
@protected_route(perms=Operations.recipe_category_update)
@use_db_sess
def update_category(db_sess: Session, category_id: int):
    req = UpdateRecipeCategoryJson.get_from_req()
    category = abort_if_none(RecipeCategory.get2(category_id), "category")
    category.update(name=Undefined.default(req.name, None))
    return category.get_dict()


@bp.delete("/api/recipe-categories/<int:category_id>")
@doc_api(res=None, desc="Delete a recipe category")
@protected_route(perms=Operations.recipe_category_delete)
@use_db_sess
def delete_category(db_sess: Session, category_id: int):
    category = abort_if_none(RecipeCategory.get2(category_id), "category")
    category.delete2()
    return "", 204

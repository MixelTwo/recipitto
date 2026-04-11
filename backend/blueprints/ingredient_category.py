from bafser import JsonObj, JsonOpt, Undefined, abort_if_none, doc_api, jsonify_list, protected_route
from flask import Blueprint

from data._operations import Operations
from data.ingredient_category import IngredientCategory, IngredientCategoryDict

bp = Blueprint("ingredient_category", __name__)


class CreateIngredientCategoryJson(JsonObj):
    """JSON schema for creating an ingredient category.

    Attributes:
        name: Category name.
    """

    name: str


class UpdateIngredientCategoryJson(JsonObj):
    """JSON schema for updating an ingredient category.

    Attributes:
        name: New category name (optional).
    """

    name: JsonOpt[str] = Undefined


@bp.get("/api/ingredient-categories")
@doc_api(res=list[IngredientCategoryDict], desc="List all ingredient categories")
def list_categories():
    """Retrieve all ingredient categories.

    Returns:
        Response: JSON array of ingredient category objects.
    """
    categories = IngredientCategory.all2()
    return jsonify_list(categories)


@bp.get("/api/ingredient-categories/<int:category_id>")
@doc_api(res=IngredientCategoryDict, desc="Get an ingredient category by ID")
def get_category(category_id: int):
    """Retrieve a single ingredient category by its ID.

    Args:
        category_id: ID of the ingredient category.

    Returns:
        dict: The ingredient category object as JSON.

    Raises:
        HTTPException: 404 if category not found.
    """
    category = abort_if_none(IngredientCategory.get2(category_id), "category")
    return category.get_dict()


@bp.post("/api/ingredient-categories")
@doc_api(req=CreateIngredientCategoryJson, res=IngredientCategoryDict, desc="Create a new ingredient category")
@protected_route(perms=Operations.ingredient_category_create)
def create_category():
    """Create a new ingredient category.

    Requires authentication and the `ingredient_category_create` permission.

    Returns:
        dict: The newly created ingredient category object.

    Raises:
        HTTPException: 403 if user lacks permission.
    """
    req = CreateIngredientCategoryJson.get_from_req()
    category = IngredientCategory.new(req.name)
    return category.get_dict()


@bp.patch("/api/ingredient-categories/<int:category_id>")
@doc_api(req=UpdateIngredientCategoryJson, res=IngredientCategoryDict, desc="Update an ingredient category")
@protected_route(perms=Operations.ingredient_category_update)
def update_category(category_id: int):
    """Update an existing ingredient category.

    Requires authentication and the `ingredient_category_update` permission.

    Args:
        category_id: ID of the ingredient category to update.

    Returns:
        dict: The updated ingredient category object.

    Raises:
        HTTPException: 404 if category not found.
        HTTPException: 403 if user lacks permission.
    """
    req = UpdateIngredientCategoryJson.get_from_req()
    category = abort_if_none(IngredientCategory.get2(category_id), "category")
    category.update(name=Undefined.default(req.name, None))
    return category.get_dict()


@bp.delete("/api/ingredient-categories/<int:category_id>")
@doc_api(res=None, desc="Delete an ingredient category")
@protected_route(perms=Operations.ingredient_category_delete)
def delete_category(category_id: int):
    """Delete an ingredient category.

    Requires authentication and the `ingredient_category_delete` permission.

    Args:
        category_id: ID of the ingredient category to delete.

    Returns:
        tuple: Empty response with status 204 on success.

    Raises:
        HTTPException: 404 if category not found.
        HTTPException: 403 if user lacks permission.
    """
    category = abort_if_none(IngredientCategory.get2(category_id), "category")
    category.delete2()
    return "", 204

from bafser import JsonObj, JsonOpt, Undefined, abort_if_none, doc_api, jsonify_list, protected_route
from flask import Blueprint

from data._operations import Operations
from data.recipe_category import RecipeCategory, RecipeCategoryDict

bp = Blueprint("recipe_category", __name__)


class CreateRecipeCategoryJson(JsonObj):
    """JSON schema for creating a recipe category.

    Attributes:
        name: Category name.
    """

    name: str


class UpdateRecipeCategoryJson(JsonObj):
    """JSON schema for updating a recipe category.

    Attributes:
        name: New category name (optional).
    """

    name: JsonOpt[str] = Undefined


@bp.get("/api/recipe-categories")
@doc_api(res=list[RecipeCategoryDict], desc="List all recipe categories")
def list_categories():
    """Retrieve all recipe categories.

    Returns:
        Response: JSON array of recipe category objects.
    """
    categories = RecipeCategory.all2()
    return jsonify_list(categories)


@bp.get("/api/recipe-categories/<int:category_id>")
@doc_api(res=RecipeCategoryDict, desc="Get a recipe category by ID")
def get_category(category_id: int):
    """Retrieve a single recipe category by its ID.

    Args:
        category_id: ID of the recipe category.

    Returns:
        dict: The recipe category object as JSON.

    Raises:
        HTTPException: 404 if category not found.
    """
    category = abort_if_none(RecipeCategory.get2(category_id), "category")
    return category.get_dict()


@bp.post("/api/recipe-categories")
@doc_api(req=CreateRecipeCategoryJson, res=RecipeCategoryDict, desc="Create a new recipe category")
@protected_route(perms=Operations.recipe_category_create)
def create_category():
    """Create a new recipe category.

    Requires authentication and the `recipe_category_create` permission.

    Returns:
        dict: The newly created recipe category object.

    Raises:
        HTTPException: 403 if user lacks permission.
    """
    req = CreateRecipeCategoryJson.get_from_req()
    category = RecipeCategory.new(req.name)
    return category.get_dict()


@bp.patch("/api/recipe-categories/<int:category_id>")
@doc_api(req=UpdateRecipeCategoryJson, res=RecipeCategoryDict, desc="Update a recipe category")
@protected_route(perms=Operations.recipe_category_update)
def update_category(category_id: int):
    """Update an existing recipe category.

    Requires authentication and the `recipe_category_update` permission.

    Args:
        category_id: ID of the recipe category to update.

    Returns:
        dict: The updated recipe category object.

    Raises:
        HTTPException: 404 if category not found.
        HTTPException: 403 if user lacks permission.
    """
    req = UpdateRecipeCategoryJson.get_from_req()
    category = abort_if_none(RecipeCategory.get2(category_id), "category")
    category.update(name=Undefined.default(req.name, None))
    return category.get_dict()


@bp.delete("/api/recipe-categories/<int:category_id>")
@doc_api(res=None, desc="Delete a recipe category")
@protected_route(perms=Operations.recipe_category_delete)
def delete_category(category_id: int):
    """Delete a recipe category.

    Requires authentication and the `recipe_category_delete` permission.

    Args:
        category_id: ID of the recipe category to delete.

    Returns:
        tuple: Empty response with status 204 on success.

    Raises:
        HTTPException: 404 if category not found.
        HTTPException: 403 if user lacks permission.
    """
    category = abort_if_none(RecipeCategory.get2(category_id), "category")
    category.delete2()
    return "", 204

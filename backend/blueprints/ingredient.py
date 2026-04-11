from bafser import JsonObj, JsonOpt, Undefined, abort_if_none, doc_api, jsonify_list, protected_route
from flask import Blueprint

from data._operations import Operations
from data.ingredient import Ingredient, IngredientDict

bp = Blueprint("ingredient", __name__)


class CreateIngredientJson(JsonObj):
    """JSON schema for creating an ingredient.

    Attributes:
        name: Ingredient name.
        category_id: ID of the ingredient category.
    """

    name: str
    category_id: int


class UpdateIngredientJson(JsonObj):
    """JSON schema for updating an ingredient.

    Attributes:
        name: New ingredient name (optional).
        category_id: New category ID (optional).
    """

    name: JsonOpt[str] = Undefined
    category_id: JsonOpt[int] = Undefined


@bp.get("/api/ingredients")
@doc_api(res=list[IngredientDict], desc="List all ingredients")
def list_ingredients():
    """Retrieve all ingredients.

    Returns:
        Response: JSON array of ingredient objects.
    """
    ingredients = Ingredient.all2()
    return jsonify_list(ingredients)


@bp.get("/api/ingredients/<int:ingredient_id>")
@doc_api(res=IngredientDict, desc="Get an ingredient by ID")
def get_ingredient(ingredient_id: int):
    """Retrieve a single ingredient by its ID.

    Args:
        ingredient_id: ID of the ingredient.

    Returns:
        dict: The ingredient object as JSON.

    Raises:
        HTTPException: 404 if ingredient not found.
    """
    ingredient = abort_if_none(Ingredient.get2(ingredient_id), "ingredient")
    return ingredient.get_dict()


@bp.post("/api/ingredients")
@doc_api(req=CreateIngredientJson, res=IngredientDict, desc="Create a new ingredient")
@protected_route(perms=Operations.ingredient_create)
def create_ingredient():
    """Create a new ingredient.

    Requires authentication and the `ingredient_create` permission.

    Returns:
        dict: The newly created ingredient object.

    Raises:
        HTTPException: 403 if user lacks permission.
    """
    req = CreateIngredientJson.get_from_req()
    ingredient = Ingredient.new(req.name, req.category_id)
    return ingredient.get_dict()


@bp.patch("/api/ingredients/<int:ingredient_id>")
@doc_api(req=UpdateIngredientJson, res=IngredientDict, desc="Update an ingredient")
@protected_route(perms=Operations.ingredient_update)
def update_ingredient(ingredient_id: int):
    """Update an existing ingredient.

    Requires authentication and the `ingredient_update` permission.

    Args:
        ingredient_id: ID of the ingredient to update.

    Returns:
        dict: The updated ingredient object.

    Raises:
        HTTPException: 404 if ingredient not found.
        HTTPException: 403 if user lacks permission.
    """
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
    """Delete an ingredient.

    Requires authentication and the `ingredient_delete` permission.

    Args:
        ingredient_id: ID of the ingredient to delete.

    Returns:
        tuple: Empty response with status 204 on success.

    Raises:
        HTTPException: 404 if ingredient not found.
        HTTPException: 403 if user lacks permission.
    """
    ingredient = abort_if_none(Ingredient.get2(ingredient_id), "ingredient")
    ingredient.delete2()
    return "", 204

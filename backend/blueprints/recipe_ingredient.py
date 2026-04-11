from bafser import JsonObj, JsonOpt, Undefined, abort_if_none, doc_api, jsonify_list, protected_route, response_msg
from flask import Blueprint

from data._operations import Operations
from data.recipe import Recipe
from data.recipe_ingredient import RecipeIngredient, RecipeIngredientDict
from data.user import User

bp = Blueprint("recipe_ingredient", __name__)


class CreateRecipeIngredientJson(JsonObj):
    """JSON schema for adding an ingredient to a recipe.

    Attributes:
        ingredient_id: ID of the ingredient.
        quantity: Amount of the ingredient.
        unit: Unit of measurement (e.g., 'g', 'ml', 'pieces').
    """

    ingredient_id: int
    quantity: float
    unit: str


class UpdateRecipeIngredientJson(JsonObj):
    """JSON schema for updating a recipe ingredient.

    Attributes:
        quantity: New quantity (optional).
        unit: New unit (optional).
    """

    quantity: JsonOpt[float] = Undefined
    unit: JsonOpt[str] = Undefined


@bp.get("/api/recipes/<int:recipe_id>/ingredients")
@doc_api(res=list[RecipeIngredientDict], desc="List ingredients of a recipe")
def list_ingredients(recipe_id: int):
    """Retrieve all ingredients associated with a recipe.

    Args:
        recipe_id: ID of the recipe.

    Returns:
        Response: JSON array of recipe ingredient objects.

    Raises:
        HTTPException: 404 if recipe not found.
    """
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    ingredients = RecipeIngredient.get_by_recipe(recipe_id)
    return jsonify_list(ingredients)


@bp.get("/api/recipes/<int:recipe_id>/ingredients/<int:ingredient_id>")
@doc_api(res=RecipeIngredientDict, desc="Get a recipe ingredient by IDs")
def get_ingredient(recipe_id: int, ingredient_id: int):
    """Retrieve a specific ingredient of a recipe.

    Args:
        recipe_id: ID of the recipe.
        ingredient_id: ID of the ingredient.

    Returns:
        dict: The recipe ingredient object as JSON.

    Raises:
        HTTPException: 404 if recipe or ingredient not found, or ingredient not associated with recipe.
    """
    ingredient = abort_if_none(
        RecipeIngredient.get_by_recipe_and_ingredient(recipe_id, ingredient_id),
        msg="Ingredient not found in recipe",
    )
    return ingredient.get_dict()


@bp.post("/api/recipes/<int:recipe_id>/ingredients")
@doc_api(req=CreateRecipeIngredientJson, res=RecipeIngredientDict, desc="Add an ingredient to a recipe")
@protected_route(perms=Operations.recipe_ingredient_create)
def create_ingredient(recipe_id: int):
    """Add a new ingredient to a recipe.

    Requires authentication and the `recipe_ingredient_create` permission.
    Only the recipe author or an admin can add ingredients.
    The ingredient must not already be present in the recipe.

    Args:
        recipe_id: ID of the recipe.

    Returns:
        dict: The newly created recipe ingredient object.

    Raises:
        HTTPException: 404 if recipe not found.
        HTTPException: 403 if user lacks permission or is not the author/admin.
        HTTPException: 400 if ingredient already added.
    """
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_moderate_recipes) and recipe.author_id != User.current.id:
        return response_msg("You can only edit your own recipes", 403)
    req = CreateRecipeIngredientJson.get_from_req()
    # Check if ingredient already exists
    existing = RecipeIngredient.get_by_recipe_and_ingredient(recipe_id, req.ingredient_id)
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
def update_ingredient(recipe_id: int, ingredient_id: int):
    """Update an existing recipe ingredient.

    Requires authentication and the `recipe_ingredient_update` permission.
    Only the recipe author or an admin can update ingredients.

    Args:
        recipe_id: ID of the recipe.
        ingredient_id: ID of the ingredient.

    Returns:
        dict: The updated recipe ingredient object.

    Raises:
        HTTPException: 404 if recipe or ingredient not found, or ingredient not associated with recipe.
        HTTPException: 403 if user lacks permission or is not the author/admin.
    """
    ingredient = abort_if_none(RecipeIngredient.get_by_recipe_and_ingredient(recipe_id, ingredient_id), msg="Ingredient not found in recipe")
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
def delete_ingredient(recipe_id: int, ingredient_id: int):
    """Remove an ingredient from a recipe.

    Requires authentication and the `recipe_ingredient_delete` permission.
    Only the recipe author or an admin can delete ingredients.

    Args:
        recipe_id: ID of the recipe.
        ingredient_id: ID of the ingredient.

    Returns:
        tuple: Empty response with status 204 on success.

    Raises:
        HTTPException: 404 if recipe or ingredient not found, or ingredient not associated with recipe.
        HTTPException: 403 if user lacks permission or is not the author/admin.
    """
    ingredient = abort_if_none(RecipeIngredient.get_by_recipe_and_ingredient(recipe_id, ingredient_id), msg="Ingredient not found in recipe")
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_moderate_recipes) and recipe.author_id != User.current.id:
        return response_msg("You can only edit your own recipes", 403)
    ingredient.db_sess.delete(ingredient)
    ingredient.db_sess.commit()
    return "", 204

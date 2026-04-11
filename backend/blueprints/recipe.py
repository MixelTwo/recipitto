from bafser import Image, ImageJson, JsonObj, JsonOpt, Undefined, abort_if_none, doc_api, jsonify_list, protected_route, response_msg
from flask import Blueprint, Response

from data._operations import Operations
from data.recipe import Recipe, RecipeDict, RecipeStatus, TRecipeStatus
from data.user import User

bp = Blueprint("recipe", __name__)


class CreateRecipeJson(JsonObj):
    """JSON schema for creating a new recipe.

    Attributes:
        title: Recipe title (max 128 characters).
        description: Recipe description.
        active_time: Active preparation time in minutes.
        total_time: Total time including waiting/cooking in minutes.
        difficulty: Difficulty level from 1 (easiest) to 5 (hardest).
        category_id: ID of the recipe category.
        main_image: Optional image data for the main recipe image.
        status: Optional recipe status (draft, published, deleted). Defaults to draft.
    """

    title: str
    description: str
    active_time: int
    total_time: int
    difficulty: int
    category_id: int
    main_image: JsonOpt[ImageJson | None] = Undefined
    status: JsonOpt[TRecipeStatus] = Undefined


class UpdateRecipeJson(JsonObj):
    """JSON schema for updating an existing recipe.

    All fields are optional. Only provided fields will be updated.

    Attributes:
        title: New recipe title (max 128 characters).
        description: New recipe description.
        active_time: New active preparation time in minutes.
        total_time: New total time in minutes.
        difficulty: New difficulty level (1-5).
        category_id: New category ID.
        main_image: New image data for the main recipe image (or null to remove).
        status: New recipe status (draft, published, deleted).
    """

    title: JsonOpt[str] = Undefined
    description: JsonOpt[str] = Undefined
    active_time: JsonOpt[int] = Undefined
    total_time: JsonOpt[int] = Undefined
    difficulty: JsonOpt[int] = Undefined
    category_id: JsonOpt[int] = Undefined
    main_image: JsonOpt[ImageJson | None] = Undefined
    status: JsonOpt[TRecipeStatus] = Undefined


@bp.get("/api/recipes")
@doc_api(res=list[RecipeDict], desc="List recipes with optional filtering")
def list_recipes() -> Response:
    """Retrieve a list of recipes.

    Returns:
        Response: JSON array of recipe objects.

    Note:
        Filtering, sorting, and pagination are not yet implemented.
    """
    # TODO: implement filtering, sorting, pagination
    recipes = Recipe.all2()
    return jsonify_list(recipes)


@bp.get("/api/recipes/<int:recipe_id>")
@doc_api(res=RecipeDict, desc="Get a recipe by ID")
def get_recipe(recipe_id: int) -> RecipeDict:
    """Retrieve a single recipe by its ID.

    Args:
        recipe_id: The ID of the recipe to retrieve.

    Returns:
        dict: The recipe object as JSON.

    Raises:
        HTTPException: 404 error if recipe not found.
    """
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    return recipe.get_dict()


@bp.post("/api/recipes")
@doc_api(req=CreateRecipeJson, res=RecipeDict, desc="Create a new recipe")
@protected_route(perms=Operations.recipe_create)
def create_recipe() -> RecipeDict | Response:
    """Create a new recipe.

    Requires authentication and the `recipe_create` permission.

    Request body must conform to CreateRecipeJson schema.

    Returns:
        dict: The newly created recipe object.

    Raises:
        HTTPException: 400 if validation fails (invalid status, image upload error).
        HTTPException: 403 if user lacks permission.
    """
    req = CreateRecipeJson.get_from_req()
    # Validate status
    status = None
    if Undefined.defined(req.status):
        try:
            status = RecipeStatus(req.status)
        except ValueError:
            return response_msg("Invalid status", 400)
    main_image_id = None
    if Undefined.defined(req.main_image):
        value = req.main_image
        if value is not None:
            image, error = Image.new(User.current, value)
            if error:
                return response_msg(f"Image upload failed: {error}", 400)
            assert image is not None
            main_image_id = image.id
    recipe = Recipe.new(
        title=req.title,
        description=req.description,
        active_time=req.active_time,
        total_time=req.total_time,
        difficulty=req.difficulty,
        author=User.current,
        category_id=req.category_id,
        main_image_id=main_image_id,
        status=status or RecipeStatus.DRAFT,
    )
    return recipe.get_dict()


@bp.patch("/api/recipes/<int:recipe_id>")
@doc_api(req=UpdateRecipeJson, res=RecipeDict, desc="Update a recipe")
@protected_route(perms=Operations.recipe_update)
def update_recipe(recipe_id: int) -> RecipeDict | Response:
    """Update an existing recipe.

    Requires authentication and the `recipe_update` permission.
    Users can only update their own recipes unless they have admin moderation rights.

    Args:
        recipe_id: The ID of the recipe to update.

    Returns:
        dict: The updated recipe object.

    Raises:
        HTTPException: 400 if validation fails (invalid status, image upload error).
        HTTPException: 403 if user lacks permission or is not the author/admin.
        HTTPException: 404 if recipe not found.
    """
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
    main_image_id = None
    if Undefined.defined(req.main_image):
        value = req.main_image
        if value is not None:
            image, error = Image.new(User.current, value)
            if error:
                return response_msg(f"Image upload failed: {error}", 400)
            assert image is not None
            main_image_id = image.id
    recipe.update(
        title=Undefined.default(req.title, None),
        description=Undefined.default(req.description, None),
        active_time=Undefined.default(req.active_time, None),
        total_time=Undefined.default(req.total_time, None),
        difficulty=Undefined.default(req.difficulty, None),
        category_id=Undefined.default(req.category_id, None),
        main_image_id=main_image_id,
        status=status,
    )
    return recipe.get_dict()


@bp.delete("/api/recipes/<int:recipe_id>")
@doc_api(res=None, desc="Delete a recipe")
@protected_route(perms=Operations.recipe_delete)
def delete_recipe(recipe_id: int) -> tuple[str, int] | Response:
    """Delete a recipe.

    Requires authentication and the `recipe_delete` permission.
    Users can only delete their own recipes unless they have admin moderation rights.

    Args:
        recipe_id: The ID of the recipe to delete.

    Returns:
        tuple: Empty response with status 204 on success.

    Raises:
        HTTPException: 403 if user lacks permission or is not the author/admin.
        HTTPException: 404 if recipe not found.
    """
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_moderate_recipes) and recipe.author_id != User.current.id:
        return response_msg("You can only delete your own recipes", 403)
    recipe.delete2()
    return "", 204

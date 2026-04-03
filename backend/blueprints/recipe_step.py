from bafser import Image, ImageJson, JsonObj, JsonOpt, Undefined, abort_if_none, doc_api, jsonify_list, protected_route, response_msg
from flask import Blueprint

from data._operations import Operations
from data.recipe import Recipe
from data.recipe_step import RecipeStep, RecipeStepDict
from data.user import User

bp = Blueprint("recipe_step", __name__)


class CreateRecipeStepJson(JsonObj):
    """JSON schema for adding a step to a recipe.

    Attributes:
        step_number: Sequential number of the step (starting from 1).
        text: Description of the step.
        image: Optional image metadata (base64‑encoded data, filename, etc.).
    """

    step_number: int
    text: str
    image: JsonOpt[ImageJson | None] = Undefined


class UpdateRecipeStepJson(JsonObj):
    """JSON schema for updating a recipe step.

    Attributes:
        step_number: New step number (optional).
        text: New description (optional).
        image: New image metadata (optional; None to remove image).
    """

    step_number: JsonOpt[int] = Undefined
    text: JsonOpt[str] = Undefined
    image: JsonOpt[ImageJson | None] = Undefined


@bp.get("/api/recipes/<int:recipe_id>/steps")
@doc_api(res=list[RecipeStepDict], desc="List steps of a recipe")
def list_steps(recipe_id: int):
    """Retrieve all steps of a recipe.

    Args:
        recipe_id: ID of the recipe.

    Returns:
        Response: JSON array of recipe step objects.

    Raises:
        HTTPException: 404 if recipe not found.
    """
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    steps = RecipeStep.get_by_recipe(recipe_id)
    return jsonify_list(steps)


@bp.get("/api/recipes/<int:recipe_id>/steps/<int:step_id>")
@doc_api(res=RecipeStepDict, desc="Get a recipe step by ID")
def get_step(recipe_id: int, step_id: int):
    """Retrieve a specific step of a recipe.

    Args:
        recipe_id: ID of the recipe.
        step_id: ID of the step.

    Returns:
        dict: The recipe step object as JSON.

    Raises:
        HTTPException: 404 if step not found or step does not belong to the recipe.
    """
    step = abort_if_none(RecipeStep.get2(step_id), "step")
    if step.recipe_id != recipe_id:
        return response_msg("Step not found", 404)
    return step.get_dict()


@bp.post("/api/recipes/<int:recipe_id>/steps")
@doc_api(req=CreateRecipeStepJson, res=RecipeStepDict, desc="Add a step to a recipe")
@protected_route(perms=Operations.recipe_step_create)
def create_step(recipe_id: int):
    """Add a new step to a recipe.

    Requires authentication and the `recipe_step_create` permission.
    Only the recipe author or an admin can add steps.
    An optional image can be attached to the step.

    Args:
        recipe_id: ID of the recipe.

    Returns:
        dict: The newly created recipe step object.

    Raises:
        HTTPException: 404 if recipe not found.
        HTTPException: 403 if user lacks permission or is not the author/admin.
        HTTPException: 400 if image upload fails.
    """
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_moderate_recipes) and recipe.author_id != User.current.id:
        return response_msg("You can only edit your own recipes", 403)
    req = CreateRecipeStepJson.get_from_req()
    image_id = None
    if Undefined.defined(req.image):
        value = req.image
        if value is None:
            image_id = None
        else:
            image, error = Image.new(User.current, value)
            if error:
                return response_msg(f"Image upload failed: {error}", 400)
            assert image is not None
            image_id = image.id
    step = RecipeStep.new(
        recipe_id=recipe_id,
        step_number=req.step_number,
        text=req.text,
        image_id=image_id,
    )
    return step.get_dict()


@bp.patch("/api/recipes/<int:recipe_id>/steps/<int:step_id>")
@doc_api(req=UpdateRecipeStepJson, res=RecipeStepDict, desc="Update a recipe step")
@protected_route(perms=Operations.recipe_step_update)
def update_step(recipe_id: int, step_id: int):
    """Update an existing recipe step.

    Requires authentication and the `recipe_step_update` permission.
    Only the recipe author or an admin can update steps.
    The image can be replaced, removed (by sending null), or left unchanged.

    Args:
        recipe_id: ID of the recipe.
        step_id: ID of the step.

    Returns:
        dict: The updated recipe step object.

    Raises:
        HTTPException: 404 if recipe or step not found, or step does not belong to recipe.
        HTTPException: 403 if user lacks permission or is not the author/admin.
        HTTPException: 400 if image upload fails.
    """
    step = abort_if_none(RecipeStep.get2(step_id), "step")
    if step.recipe_id != recipe_id:
        return response_msg("Step not found", 404)
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_moderate_recipes) and recipe.author_id != User.current.id:
        return response_msg("You can only edit your own recipes", 403)
    req = UpdateRecipeStepJson.get_from_req()
    image_id = None
    if Undefined.defined(req.image):
        value = req.image
        if value is not None:
            image, error = Image.new(User.current, value)
            if error:
                return response_msg(f"Image upload failed: {error}", 400)
            assert image is not None
            image_id = image.id
    step.update(
        step_number=Undefined.default(req.step_number, None),
        text=Undefined.default(req.text, None),
        image_id=image_id,
    )
    return step.get_dict()


@bp.delete("/api/recipes/<int:recipe_id>/steps/<int:step_id>")
@doc_api(res=None, desc="Delete a recipe step")
@protected_route(perms=Operations.recipe_step_delete)
def delete_step(recipe_id: int, step_id: int):
    """Delete a recipe step.

    Requires authentication and the `recipe_step_delete` permission.
    Only the recipe author or an admin can delete steps.

    Args:
        recipe_id: ID of the recipe.
        step_id: ID of the step.

    Returns:
        tuple: Empty response with status 204 on success.

    Raises:
        HTTPException: 404 if recipe or step not found, or step does not belong to recipe.
        HTTPException: 403 if user lacks permission or is not the author/admin.
    """
    step = abort_if_none(RecipeStep.get2(step_id), "step")
    if step.recipe_id != recipe_id:
        return response_msg("Step not found", 404)
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_moderate_recipes) and recipe.author_id != User.current.id:
        return response_msg("You can only edit your own recipes", 403)
    step.delete2()
    return "", 204

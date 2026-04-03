from bafser import Image, ImageJson, JsonObj, abort_if_none, doc_api, jsonify_list, protected_route, response_msg
from flask import Blueprint

from data._operations import Operations
from data.recipe import Recipe
from data.recipe_image import RecipeImage, RecipeImageDict
from data.user import User

bp = Blueprint("recipe_image", __name__)


class CreateRecipeImageJson(JsonObj):
    """JSON schema for adding an image to a recipe.

    Attributes:
        image: Image metadata (base64‑encoded data, filename, etc.).
    """

    image: ImageJson


@bp.get("/api/recipes/<int:recipe_id>/images")
@doc_api(res=list[RecipeImageDict], desc="List images of a recipe")
def list_images(recipe_id: int):
    """Retrieve all images associated with a recipe.

    Args:
        recipe_id: ID of the recipe.

    Returns:
        Response: JSON array of recipe image objects.

    Raises:
        HTTPException: 404 if recipe not found.
    """
    abort_if_none(Recipe.get2(recipe_id), "recipe")
    images = RecipeImage.get_by_recipe(recipe_id)
    return jsonify_list(images)


@bp.get("/api/recipes/<int:recipe_id>/images/<int:image_id>")
@doc_api(res=RecipeImageDict, desc="Get a recipe image by ID")
def get_image(recipe_id: int, image_id: int):
    """Retrieve a specific image of a recipe.

    Args:
        recipe_id: ID of the recipe.
        image_id: ID of the image.

    Returns:
        dict: The recipe image object as JSON.

    Raises:
        HTTPException: 404 if recipe or image not found, or image not associated with recipe.
    """
    recipe_image = abort_if_none(RecipeImage.get_by_recipe_and_image(recipe_id, image_id), msg="Image not found in recipe")
    return recipe_image.get_dict()


@bp.post("/api/recipes/<int:recipe_id>/images")
@doc_api(req=CreateRecipeImageJson, res=RecipeImageDict, desc="Add an image to a recipe")
@protected_route(perms=Operations.recipe_image_create)
def create_image(recipe_id: int):
    """Add a new image to a recipe.

    Requires authentication and the `recipe_image_create` permission.
    Only the recipe author or an admin can add images.

    Args:
        recipe_id: ID of the recipe.

    Returns:
        dict: The newly created recipe image object.

    Raises:
        HTTPException: 404 if recipe not found.
        HTTPException: 403 if user lacks permission or is not the author/admin.
        HTTPException: 400 if image upload fails.
    """
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_moderate_recipes) and recipe.author_id != User.current.id:
        return response_msg("You can only edit your own recipes", 403)
    req = CreateRecipeImageJson.get_from_req()
    # Create new image
    image, error = Image.new(User.current, req.image)
    if error:
        return response_msg(f"Image upload failed: {error}", 400)
    assert image is not None
    recipe_image = RecipeImage.new(
        recipe_id=recipe_id,
        image_id=image.id,
        creator=User.current,
    )
    return recipe_image.get_dict()


@bp.delete("/api/recipes/<int:recipe_id>/images/<int:image_id>")
@doc_api(res=None, desc="Remove an image from a recipe")
@protected_route(perms=Operations.recipe_image_delete)
def delete_image(recipe_id: int, image_id: int):
    """Remove an image from a recipe.

    Requires authentication and the `recipe_image_delete` permission.
    Only the recipe author or an admin can delete images.

    Args:
        recipe_id: ID of the recipe.
        image_id: ID of the image.

    Returns:
        tuple: Empty response with status 204 on success.

    Raises:
        HTTPException: 404 if recipe or image not found, or image not associated with recipe.
        HTTPException: 403 if user lacks permission or is not the author/admin.
    """
    recipe_image = abort_if_none(RecipeImage.get_by_recipe_and_image(recipe_id, image_id), msg="Image not found in recipe")
    recipe = abort_if_none(Recipe.get2(recipe_id), "recipe")
    # Check ownership: if user is not admin and not author, deny
    if not User.current.has_operation(Operations.admin_moderate_recipes) and recipe.author_id != User.current.id:
        return response_msg("You can only edit your own recipes", 403)
    recipe_image.delete2()
    return "", 204

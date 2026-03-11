from bafser import RolesBase

from data._operations import Operations


class Roles(RolesBase):
    user = 2
    guest = 3


Roles.ROLES = {
    Roles.user: {
        "name": "User",
        "operations": [
            Operations.recipe_view,
            Operations.recipe_create,
            Operations.recipe_manage_own,
            Operations.recipe_step_view,
            Operations.recipe_step_create,
            Operations.recipe_step_update,
            Operations.recipe_step_delete,
            Operations.recipe_ingredient_view,
            Operations.recipe_ingredient_create,
            Operations.recipe_ingredient_update,
            Operations.recipe_ingredient_delete,
            Operations.recipe_image_view,
            Operations.recipe_image_create,
            Operations.recipe_image_delete,
            Operations.comment_view,
            Operations.comment_create,
            Operations.comment_update,
            Operations.comment_delete,
            Operations.rating_view,
            Operations.rating_create,
            Operations.rating_update,
            Operations.rating_delete,
            Operations.favorite_view,
            Operations.favorite_create,
            Operations.favorite_delete,
            Operations.search_recipes,
            Operations.recipe_category_view,
            Operations.ingredient_category_view,
            Operations.ingredient_view,
        ],
    },
    Roles.guest: {
        "name": "Guest",
        "operations": [
            Operations.recipe_view,
            Operations.recipe_step_view,
            Operations.recipe_ingredient_view,
            Operations.recipe_image_view,
            Operations.comment_view,
            Operations.rating_view,
            Operations.favorite_view,
            Operations.search_recipes,
            Operations.recipe_category_view,
            Operations.ingredient_category_view,
            Operations.ingredient_view,
        ],
    },
}

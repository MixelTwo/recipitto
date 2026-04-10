from bafser import OperationsBase


class Operations(OperationsBase):
    # Recipe categories
    recipe_category_view = ("recipe_category_view", "Can view recipe categories")
    recipe_category_create = ("recipe_category_create", "Can create recipe categories")
    recipe_category_update = ("recipe_category_update", "Can update recipe categories")
    recipe_category_delete = ("recipe_category_delete", "Can delete recipe categories")

    # Ingredient categories
    ingredient_category_view = ("ingredient_category_view", "Can view ingredient categories")
    ingredient_category_create = ("ingredient_category_create", "Can create ingredient categories")
    ingredient_category_update = ("ingredient_category_update", "Can update ingredient categories")
    ingredient_category_delete = ("ingredient_category_delete", "Can delete ingredient categories")

    # Ingredients
    ingredient_view = ("ingredient_view", "Can view ingredients")
    ingredient_create = ("ingredient_create", "Can create ingredients")
    ingredient_update = ("ingredient_update", "Can update ingredients")
    ingredient_delete = ("ingredient_delete", "Can delete ingredients")

    # Recipes
    recipe_view = ("recipe_view", "Can view recipes")
    recipe_create = ("recipe_create", "Can create recipes")
    recipe_update = ("recipe_update", "Can update recipes")
    recipe_delete = ("recipe_delete", "Can delete recipes")
    recipe_manage_own = ("recipe_manage_own", "Can manage own recipes (edit/delete)")

    # Recipe steps
    recipe_step_view = ("recipe_step_view", "Can view recipe steps")
    recipe_step_create = ("recipe_step_create", "Can create recipe steps")
    recipe_step_update = ("recipe_step_update", "Can update recipe steps")
    recipe_step_delete = ("recipe_step_delete", "Can delete recipe steps")

    # Recipe ingredients (junction)
    recipe_ingredient_view = ("recipe_ingredient_view", "Can view recipe ingredients")
    recipe_ingredient_create = ("recipe_ingredient_create", "Can create recipe ingredients")
    recipe_ingredient_update = ("recipe_ingredient_update", "Can update recipe ingredients")
    recipe_ingredient_delete = ("recipe_ingredient_delete", "Can delete recipe ingredients")

    # Recipe images
    recipe_image_view = ("recipe_image_view", "Can view recipe images")
    recipe_image_create = ("recipe_image_create", "Can upload recipe images")
    recipe_image_delete = ("recipe_image_delete", "Can delete recipe images")

    # Comments
    comment_view = ("comment_view", "Can view comments")
    comment_create = ("comment_create", "Can create comments")
    comment_update = ("comment_update", "Can update comments")
    comment_delete = ("comment_delete", "Can delete comments")

    # Ratings
    rating_view = ("rating_view", "Can view ratings")
    rating_create = ("rating_create", "Can rate recipes")
    rating_update = ("rating_update", "Can update own ratings")
    rating_delete = ("rating_delete", "Can delete ratings")

    # Favorites
    favorite_view = ("favorite_view", "Can view favorites")
    favorite_create = ("favorite_create", "Can add to favorites")
    favorite_delete = ("favorite_delete", "Can remove from favorites")

    # Search
    search_recipes = ("search_recipes", "Can search recipes")

    # Admin operations
    admin_page = ("admin_page", "Can see admin page")
    admin_manage_users = ("admin_manage_users", "Can manage users")
    admin_view_statistics = ("admin_view_statistics", "Can view statistics")
    admin_moderate_recipes = ("admin_moderate_recipes", "Can moderate recipes")
    admin_manage_comments = ("admin_manage_comments", "Can manage comments")

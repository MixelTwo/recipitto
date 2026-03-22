import random
import shutil

# datetime not used
from bafser import AppConfig, Image, get_datetime_now
from sqlalchemy.orm import Session

import bafser_config
from data._roles import Roles
from data.comment import Comment
from data.favorite import Favorite
from data.ingredient import Ingredient
from data.ingredient_category import IngredientCategory
from data.rating import Rating
from data.recipe import Recipe, RecipeStatus
from data.recipe_category import RecipeCategory
from data.recipe_image import RecipeImage
from data.recipe_ingredient import RecipeIngredient
from data.recipe_step import RecipeStep
from data.user import User


def init_db_dev(db_sess: Session, config: AppConfig):
    # user to pass in Model.new method
    admin = User.get_by_login(db_sess, "admin")
    assert admin
    now = get_datetime_now()

    # ------------------------------------------------------------
    # 1. Copy mock images and create Image records
    # ------------------------------------------------------------
    mock_images = [
        "avocado-toast.jpg",
        "beef_bourguignon.jpg",
        "category-breakfast.jpg",
        "category-dessert.jpg",
        "category-italian.jpg",
        "category-quick-easy.jpg",
        "chocolate_walnut_ganache.jpg",
        "chocolate-souffle.jpg",
        "empty-search-state.jpg",
        "folding-ganache_and_walnuts.jpg",
        "margherita-pizza.jpg",
        "peeling_a_roasted_potato.jpg",
        "plating-garnish.jpg",
        "prep-chopping-onions.jpg",
        "quinoa-salad.jpg",
        "roasted_tomato_soup.jpg",
        "stove-boiling-water.jpg",
        "thai-green-curry.jpg",
        "whisking_soup_and_cream.jpg",
    ]

    images: list[Image] = []  # list of Image objects
    next_img_id = 1
    for filename in mock_images:
        img_ext = "jpg"
        shutil.copy(f"mocks/{filename}", f"{bafser_config.images_folder}/{next_img_id}.{img_ext}")
        img = Image(
            name=filename.replace("-", " ").replace("_", " ").replace(".jpg", ""),
            type=img_ext,
            creationDate=now,
            createdById=admin.id,
        )
        img.id = next_img_id
        db_sess.add(img)
        images.append(img)
        next_img_id += 1

    db_sess.commit()
    print(f"Created {len(images)} images")

    # ------------------------------------------------------------
    # 2. Ingredient categories
    # ------------------------------------------------------------
    ingredient_category_names = [
        "Vegetables",
        "Fruits",
        "Dairy",
        "Meat",
        "Grains",
        "Spices",
    ]
    ingredient_categories: list[IngredientCategory] = []
    for name in ingredient_category_names:
        cat = IngredientCategory.new(name=name, creator=admin)
        ingredient_categories.append(cat)
    db_sess.commit()
    print(f"Created {len(ingredient_categories)} ingredient categories")

    # ------------------------------------------------------------
    # 3. Ingredients
    # ------------------------------------------------------------
    ingredient_data = [
        ("Tomato", "Vegetables"),
        ("Cucumber", "Vegetables"),
        ("Carrot", "Vegetables"),
        ("Bell Pepper", "Vegetables"),
        ("Spinach", "Vegetables"),
        ("Apple", "Fruits"),
        ("Banana", "Fruits"),
        ("Orange", "Fruits"),
        ("Strawberry", "Fruits"),
        ("Grapes", "Fruits"),
        ("Milk", "Dairy"),
        ("Cheese", "Dairy"),
        ("Yogurt", "Dairy"),
        ("Butter", "Dairy"),
        ("Cream", "Dairy"),
        ("Chicken Breast", "Meat"),
        ("Beef Steak", "Meat"),
        ("Pork Chop", "Meat"),
        ("Salmon", "Meat"),
        ("Bacon", "Meat"),
        ("Rice", "Grains"),
        ("Pasta", "Grains"),
        ("Bread", "Grains"),
        ("Flour", "Grains"),
        ("Oats", "Grains"),
        ("Salt", "Spices"),
        ("Black Pepper", "Spices"),
        ("Cumin", "Spices"),
        ("Paprika", "Spices"),
        ("Cinnamon", "Spices"),
        ("Garlic", "Vegetables"),
        ("Onion", "Vegetables"),
        ("Potato", "Vegetables"),
        ("Lemon", "Fruits"),
        ("Lime", "Fruits"),
        ("Egg", "Dairy"),
        ("Sugar", "Spices"),
        ("Olive Oil", "Spices"),
        ("Vinegar", "Spices"),
        ("Honey", "Spices"),
    ]
    ingredients: list[Ingredient] = []
    for name, cat_name in ingredient_data:
        cat = next(c for c in ingredient_categories if c.name == cat_name)
        ing = Ingredient.new(name=name, category_id=cat.id, creator=admin)
        ingredients.append(ing)
    db_sess.commit()
    print(f"Created {len(ingredients)} ingredients")

    # ------------------------------------------------------------
    # 4. Recipe categories
    # ------------------------------------------------------------
    recipe_category_names = [
        "Breakfast",
        "Lunch",
        "Dinner",
        "Dessert",
        "Snack",
    ]
    recipe_categories: list[RecipeCategory] = []
    for name in recipe_category_names:
        cat = RecipeCategory.new(name=name, creator=admin)
        recipe_categories.append(cat)
    db_sess.commit()
    print(f"Created {len(recipe_categories)} recipe categories")

    # ------------------------------------------------------------
    # 5. Additional users
    # ------------------------------------------------------------
    user_names = [
        ("alice", "Alice Smith"),
        ("bob", "Bob Johnson"),
        ("charlie", "Charlie Brown"),
        ("diana", "Diana Prince"),
        ("eve", "Eve Adams"),
        ("frank", "Frank Miller"),
        ("grace", "Grace Lee"),
        ("henry", "Henry Ford"),
        ("ivy", "Ivy Chen"),
        ("jack", "Jack Sparrow"),
    ]
    users = [admin]
    for login, name in user_names:
        user = User.new(creator=admin, login=login, password="password", name=name, roles=[Roles.user])
        users.append(user)
    db_sess.commit()
    print(f"Created {len(users)} users (including admin)")

    # ------------------------------------------------------------
    # 6. Recipes
    # ------------------------------------------------------------
    recipe_titles = [
        "Avocado Toast",
        "Beef Bourguignon",
        "Chocolate Souffle",
        "Margherita Pizza",
        "Quinoa Salad",
        "Thai Green Curry",
        "Roasted Tomato Soup",
        "Chocolate Walnut Ganache",
        "Folding Ganache and Walnuts",
        "Peeling a Roasted Potato",
        "Plating Garnish",
        "Prep Chopping Onions",
        "Stove Boiling Water",
        "Whisking Soup and Cream",
        "Classic Pancakes",
        "Vegetable Stir Fry",
        "Spaghetti Carbonara",
        "Chicken Tikka Masala",
        "Beef Tacos",
        "Greek Salad",
        "Banana Bread",
        "Apple Pie",
        "Chocolate Chip Cookies",
        "French Onion Soup",
        "Grilled Cheese Sandwich",
        "Caesar Salad",
        "Beef Burger",
        "Fish and Chips",
        "Mushroom Risotto",
        "Tiramisu",
    ]
    # Ensure we have at least 30 recipes
    recipes: list[Recipe] = []
    for i, title in enumerate(recipe_titles):
        # pick random author (excluding admin sometimes)
        author = random.choice(users)
        category = random.choice(recipe_categories)
        # decide status: mostly published, some drafts
        if i < 2:  # first two are drafts
            status = RecipeStatus.DRAFT
        else:
            status = RecipeStatus.PUBLISHED
        # random times
        active_time = random.randint(10, 60)
        total_time = active_time + random.randint(0, 30)
        difficulty = random.randint(1, 5)
        description = f"A delicious recipe for {title}. " + " ".join(["This is a test description."] * random.randint(2, 5))
        # pick a main image from images (some recipes may have none)
        main_image = random.choice(images) if random.random() < 0.8 else None
        recipe = Recipe.new(
            title=title,
            description=description,
            active_time=active_time,
            total_time=total_time,
            difficulty=difficulty,
            author=author,
            category_id=category.id,
            status=status,
            main_image_id=main_image.id if main_image else None,
            creator=admin,
        )
        recipes.append(recipe)
    db_sess.commit()
    print(f"Created {len(recipes)} recipes")

    # ------------------------------------------------------------
    # 7. Recipe steps
    # ------------------------------------------------------------
    step_texts = [
        "Prepare all ingredients.",
        "Chop vegetables finely.",
        "Heat oil in a pan.",
        "Add onions and sauté until golden.",
        "Add main ingredient and cook for 10 minutes.",
        "Season with salt and pepper.",
        "Simmer for another 5 minutes.",
        "Garnish with herbs.",
        "Serve hot.",
    ]
    for recipe in recipes:
        num_steps = random.randint(3, 8)
        for step_num in range(1, num_steps + 1):
            text = random.choice(step_texts)
            # maybe add an image for some steps
            step_image = random.choice(images) if random.random() < 0.3 else None
            RecipeStep.new(
                recipe_id=recipe.id,
                step_number=step_num,
                text=text,
                image_id=step_image.id if step_image else None,
                creator=admin,
            )
    db_sess.commit()
    print("Created steps for recipes")

    # ------------------------------------------------------------
    # 8. Recipe images (additional images besides main)
    # ------------------------------------------------------------
    for recipe in recipes:
        # each recipe gets 0-2 extra images
        num_extra = random.randint(0, 2)
        for _ in range(num_extra):
            img = random.choice(images)
            # ensure not already used as main image (optional)
            RecipeImage.new(recipe_id=recipe.id, image_id=img.id, creator=admin)
    db_sess.commit()
    print("Created extra recipe images")

    # ------------------------------------------------------------
    # 9. Recipe ingredients
    # ------------------------------------------------------------
    units = ["g", "kg", "ml", "L", "tsp", "tbsp", "cup", "piece", "slice"]
    for recipe in recipes:
        # pick 5-15 ingredients
        num_ing = random.randint(5, 15)
        selected = random.sample(ingredients, min(num_ing, len(ingredients)))
        for ing in selected:
            quantity = round(random.uniform(0.5, 500.0), 2)
            unit = random.choice(units)
            RecipeIngredient.new(
                recipe_id=recipe.id,
                ingredient_id=ing.id,
                quantity=quantity,
                unit=unit,
                creator=admin,
            )
    db_sess.commit()
    print("Created recipe ingredients")

    # ------------------------------------------------------------
    # 10. Comments
    # ------------------------------------------------------------
    comment_texts = [
        "Great recipe!",
        "I loved it!",
        "Could use more salt.",
        "Easy to follow.",
        "My family enjoyed this.",
        "Will make again.",
        "Not bad, but needs improvement.",
        "Perfect for a weekday dinner.",
        "Too spicy for me.",
        "Delicious!",
    ]
    for recipe in recipes:
        num_comments = random.randint(0, 5)
        commenters = random.sample(users, min(num_comments, len(users)))
        for user in commenters:
            text = random.choice(comment_texts)
            Comment.new(user_id=user.id, recipe_id=recipe.id, text=text, creator=admin)
    db_sess.commit()
    print("Created comments")

    # ------------------------------------------------------------
    # 11. Ratings
    # ------------------------------------------------------------
    for recipe in recipes:
        # each recipe gets 5-20 ratings from distinct users
        num_ratings = random.randint(5, 20)
        raters = random.sample(users, min(num_ratings, len(users)))
        for user in raters:
            rating_value = random.randint(1, 5)
            Rating.new(user_id=user.id, recipe_id=recipe.id, rating=rating_value, creator=admin)
    # Recalculate recipe stats
    for recipe in recipes:
        Rating.recalculate_recipe_stats(recipe.id, db_sess=db_sess)
    db_sess.commit()
    print("Created ratings and updated stats")

    # ------------------------------------------------------------
    # 12. Favorites
    # ------------------------------------------------------------
    for user in users:
        num_favs = random.randint(0, 10)
        fav_recipes = random.sample(recipes, min(num_favs, len(recipes)))
        for recipe in fav_recipes:
            Favorite.new(user_id=user.id, recipe_id=recipe.id, creator=admin)
    db_sess.commit()
    print("Created favorites")

    print("Database population completed successfully.")

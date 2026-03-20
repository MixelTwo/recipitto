"""
Unit tests for data models.
"""

from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from bafser import UserBase

from data._roles import Roles
from data.ingredient import Ingredient
from data.ingredient_category import IngredientCategory
from data.recipe import Recipe, RecipeStatus
from data.recipe_category import RecipeCategory
from data.recipe_image import RecipeImage
from data.recipe_ingredient import RecipeIngredient
from data.recipe_step import RecipeStep
from data.user import User


class TestUser:
    """Test User model."""

    def test_create_user(self, db_sess: "Session") -> None:
        """Test creating a user."""
        fake_creator = UserBase.get_fake_system()
        user = User.new(creator=fake_creator, login="unit_testuser", password="testpass", name="Test User", roles=[Roles.user], db_sess=db_sess)
        # User.new already commits

        assert user.id is not None
        assert user.login == "unit_testuser"
        assert user.name == "Test User"
        assert user.check_password("testpass")
        assert not user.check_password("wrong")
        assert user.has_role(Roles.user)
        assert not user.has_role(Roles.admin)

    def test_user_get_by_login(self, db_sess: "Session") -> None:
        fake_creator = UserBase.get_fake_system()
        user = User.new(creator=fake_creator, login="unit_alice", password="secret", name="Alice", roles=[Roles.user], db_sess=db_sess)
        # User.new already commits
        found = User.get_by_login(db_sess, "unit_alice")
        assert found is not None
        assert found.id == user.id
        assert found.login == "unit_alice"

    def test_user_update_password(self, db_sess: "Session") -> None:
        fake_creator = UserBase.get_fake_system()
        user = User.new(creator=fake_creator, login="unit_bob", password="old", name="Bob", roles=[Roles.user], db_sess=db_sess)
        # User.new already commits
        user.update_password(fake_creator, "newpassword")
        db_sess.commit()

        assert user.check_password("newpassword")
        assert not user.check_password("old")

    def test_user_roles(self, db_sess: "Session") -> None:
        fake_creator = UserBase.get_fake_system()
        user = User.new(
            creator=fake_creator, login="unit_roleuser", password="pass", name="Role User", roles=[Roles.user, Roles.guest], db_sess=db_sess
        )
        # User.new already commits
        assert user.has_role(Roles.user)
        assert user.has_role(Roles.guest)
        assert not user.has_role(Roles.admin)


class TestRecipe:
    """Test Recipe model."""

    def test_create_recipe(self, db_sess: "Session") -> None:
        # Create author and category first
        fake_creator = UserBase.get_fake_system()
        author = User.new(creator=fake_creator, login="unit_author1", password="pass", name="Author One", roles=[Roles.user], db_sess=db_sess)
        # User.new already commits
        category = RecipeCategory.new(name="Dessert", creator=None)
        db_sess.add(category)
        db_sess.commit()

        recipe = Recipe.new(
            title="Chocolate Cake",
            description="Delicious cake",
            active_time=30,
            total_time=60,
            difficulty=3,
            author=author,
            category_id=category.id,
            status=RecipeStatus.DRAFT,
            creator=None,
        )
        db_sess.add(recipe)
        db_sess.commit()

        assert recipe.id is not None
        assert recipe.title == "Chocolate Cake"
        assert recipe.title_normalized == "chocolate cake"
        assert recipe.description == "Delicious cake"
        assert recipe.active_time == 30
        assert recipe.total_time == 60
        assert recipe.difficulty == 3
        assert recipe.author_id == author.id
        assert recipe.category_id == category.id
        assert recipe.status == RecipeStatus.DRAFT
        assert recipe.published_at is None
        assert recipe.rating == 0.0
        assert recipe.vote_count == 0

    def test_recipe_update(self, db_sess: "Session") -> None:
        fake_creator = UserBase.get_fake_system()
        author = User.new(creator=fake_creator, login="unit_author2", password="pass", name="Author Two", roles=[Roles.user], db_sess=db_sess)
        # User.new already commits
        category = RecipeCategory.new(name="Main Course", creator=None)
        db_sess.add(category)
        db_sess.commit()

        recipe = Recipe.new(
            title="Old Title",
            description="Old desc",
            active_time=10,
            total_time=20,
            difficulty=2,
            author=author,
            category_id=category.id,
            creator=None,
        )
        db_sess.add(recipe)
        db_sess.commit()

        recipe.update(
            title="New Title",
            description="New desc",
            active_time=15,
            total_time=25,
            difficulty=4,
            category_id=category.id,
            actor=None,
        )
        db_sess.commit()

        assert recipe.title == "New Title"
        assert recipe.description == "New desc"
        assert recipe.active_time == 15
        assert recipe.total_time == 25
        assert recipe.difficulty == 4

    def test_recipe_publish(self, db_sess: "Session") -> None:
        fake_creator = UserBase.get_fake_system()
        author = User.new(creator=fake_creator, login="unit_author3", password="pass", name="Author Three", roles=[Roles.user], db_sess=db_sess)
        # User.new already commits
        category = RecipeCategory.new(name="Snack", creator=None)
        db_sess.add(category)
        db_sess.commit()

        recipe = Recipe.new(
            title="Snack Recipe",
            description="Yummy",
            active_time=5,
            total_time=10,
            difficulty=1,
            author=author,
            category_id=category.id,
            creator=None,
        )
        db_sess.add(recipe)
        db_sess.commit()

        recipe.update(status=RecipeStatus.PUBLISHED, actor=None)
        db_sess.commit()

        assert recipe.status == RecipeStatus.PUBLISHED
        assert recipe.published_at is not None
        assert isinstance(recipe.published_at, datetime)


class TestRecipeCategory:
    """Test RecipeCategory model."""

    def test_create_category(self, db_sess: "Session") -> None:
        category = RecipeCategory.new(name="Dessert", creator=None)
        db_sess.add(category)
        db_sess.commit()

        assert category.id is not None
        assert category.name == "Dessert"
        assert category.deleted is False

    def test_category_delete(self, db_sess: "Session") -> None:
        # Create a real user to act as actor
        fake_creator = UserBase.get_fake_system()
        actor = User.new(creator=fake_creator, login="unit_actoruser", password="pass", name="Actor User", roles=[Roles.user], db_sess=db_sess)
        # User.new already commits

        category = RecipeCategory.new(name="ToDelete", creator=None)
        db_sess.add(category)
        db_sess.commit()

        category.delete(actor, db_sess=db_sess)
        db_sess.commit()

        assert category.deleted is True


class TestIngredient:
    """Test Ingredient model."""

    def test_create_ingredient(self, db_sess: "Session") -> None:
        cat = IngredientCategory.new(name="Vegetables", creator=None)
        db_sess.add(cat)
        db_sess.commit()

        ingredient = Ingredient.new(
            name="Carrot",
            category_id=cat.id,
            creator=None,
        )
        db_sess.add(ingredient)
        db_sess.commit()

        assert ingredient.id is not None
        assert ingredient.name == "Carrot"
        assert ingredient.category_id == cat.id


class TestRecipeIngredient:
    """Test RecipeIngredient model."""

    def test_create_recipe_ingredient(self, db_sess: "Session") -> None:
        fake_creator = UserBase.get_fake_system()
        author = User.new(creator=fake_creator, login="unit_author4", password="pass", name="Author Four", roles=[Roles.user], db_sess=db_sess)
        # User.new already commits
        # Create IngredientCategory for ingredient
        ingredient_category = IngredientCategory.new(name="Grains", creator=None)
        db_sess.add(ingredient_category)
        # Create RecipeCategory for recipe
        recipe_category = RecipeCategory.new(name="Test", creator=None)
        db_sess.add(recipe_category)
        db_sess.commit()  # ensure ids are assigned
        ingredient = Ingredient.new(name="Flour", category_id=ingredient_category.id, creator=None)
        db_sess.add(ingredient)
        recipe = Recipe.new(
            title="Test Recipe",
            description="Test",
            active_time=5,
            total_time=5,
            difficulty=1,
            author=author,
            category_id=recipe_category.id,
            creator=None,
        )
        db_sess.add(recipe)
        db_sess.commit()

        ri = RecipeIngredient.new(
            recipe_id=recipe.id,
            ingredient_id=ingredient.id,
            quantity=200,
            unit="g",
            creator=None,
        )
        db_sess.add(ri)
        db_sess.commit()

        assert ri.recipe_id == recipe.id
        assert ri.ingredient_id == ingredient.id
        assert ri.quantity == 200
        assert ri.unit == "g"


class TestRecipeStep:
    """Test RecipeStep model."""

    def test_create_recipe_step(self, db_sess: "Session") -> None:
        fake_creator = UserBase.get_fake_system()
        author = User.new(creator=fake_creator, login="unit_author5", password="pass", name="Author Five", roles=[Roles.user], db_sess=db_sess)
        # User.new already commits
        category = RecipeCategory.new(name="Test", creator=None)
        db_sess.add(category)
        recipe = Recipe.new(
            title="Test Recipe",
            description="Test",
            active_time=5,
            total_time=5,
            difficulty=1,
            author=author,
            category_id=category.id,
            creator=None,
        )
        db_sess.add(recipe)
        db_sess.commit()

        step = RecipeStep.new(
            recipe_id=recipe.id,
            step_number=1,
            text="Mix ingredients",
            creator=None,
        )
        db_sess.add(step)
        db_sess.commit()

        assert step.id is not None
        assert step.recipe_id == recipe.id
        assert step.step_number == 1
        assert step.text == "Mix ingredients"


class TestRecipeImage:
    """Test RecipeImage model."""

    def test_create_recipe_image(self, db_sess: "Session") -> None:
        fake_creator = UserBase.get_fake_system()
        author = User.new(creator=fake_creator, login="unit_author6", password="pass", name="Author Six", roles=[Roles.user], db_sess=db_sess)
        # User.new already commits
        category = RecipeCategory.new(name="Test", creator=None)
        db_sess.add(category)
        recipe = Recipe.new(
            title="Test Recipe",
            description="Test",
            active_time=5,
            total_time=5,
            difficulty=1,
            author=author,
            category_id=category.id,
            creator=None,
        )
        db_sess.add(recipe)
        db_sess.commit()

        # Create an image (mock) using direct constructor
        from bafser import get_datetime_now
        from bafser.data.image import Image

        image = Image(
            name="test.jpg",
            type="jpg",
            creationDate=get_datetime_now(),
            createdById=author.id,
        )
        db_sess.add(image)
        db_sess.commit()

        ri = RecipeImage.new(
            recipe_id=recipe.id,
            image_id=image.id,
            creator=None,
        )
        db_sess.add(ri)
        db_sess.commit()

        assert ri.id is not None
        assert ri.recipe_id == recipe.id
        assert ri.image_id == image.id

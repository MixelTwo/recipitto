"""
Unit tests for data models.
"""

from datetime import datetime
from data.user import User
from data.recipe import Recipe, RecipeStatus
from data.recipe_category import RecipeCategory
from data.ingredient import Ingredient
from data.ingredient_category import IngredientCategory
from data.recipe_ingredient import RecipeIngredient
from data.recipe_step import RecipeStep
from data.recipe_image import RecipeImage
from data.comment import Comment
from data.rating import Rating
from data.favorite import Favorite
from data._roles import Roles
from bafser import UserBase


class TestUser:
    """Test User model."""

    def test_create_user(self, db_sess):
        """Test creating a user."""
        fake_creator = UserBase.get_fake_system()
        user = User.new(
            creator=fake_creator,
            login="unit_testuser",
            password="testpass",
            name="Test User",
            roles=[Roles.user],
            db_sess=db_sess
        )
        # User.new already commits

        assert user.id is not None
        assert user.login == "unit_testuser"
        assert user.name == "Test User"
        assert user.check_password("testpass")
        assert not user.check_password("wrong")
        assert user.has_role(Roles.user)
        assert not user.has_role(Roles.admin)

    def test_user_get_by_login(self, db_sess):
        fake_creator = UserBase.get_fake_system()
        user = User.new(
            creator=fake_creator,
            login="unit_alice",
            password="secret",
            name="Alice",
            roles=[Roles.user],
            db_sess=db_sess
        )
        # User.new already commits
        found = User.get_by_login(db_sess, "unit_alice")
        assert found is not None
        assert found.id == user.id
        assert found.login == "unit_alice"

    def test_user_update_password(self, db_sess):
        fake_creator = UserBase.get_fake_system()
        user = User.new(
            creator=fake_creator,
            login="unit_bob",
            password="old",
            name="Bob",
            roles=[Roles.user],
            db_sess=db_sess
        )
        # User.new already commits
        user.update_password(fake_creator, "newpassword")
        db_sess.commit()

        assert user.check_password("newpassword")
        assert not user.check_password("old")

    def test_user_roles(self, db_sess):
        fake_creator = UserBase.get_fake_system()
        user = User.new(
            creator=fake_creator,
            login="unit_roleuser",
            password="pass",
            name="Role User",
            roles=[Roles.user, Roles.guest],
            db_sess=db_sess
        )
        # User.new already commits
        assert user.has_role(Roles.user)
        assert user.has_role(Roles.guest)
        assert not user.has_role(Roles.admin)


class TestRecipe:
    """Test Recipe model."""

    def test_create_recipe(self, db_sess):
        # Create author and category first
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="unit_author1",
            password="pass",
            name="Author One",
            roles=[Roles.user],
            db_sess=db_sess
        )
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

    def test_recipe_update(self, db_sess):
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="unit_author2",
            password="pass",
            name="Author Two",
            roles=[Roles.user],
            db_sess=db_sess
        )
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

    def test_recipe_publish(self, db_sess):
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="unit_author3",
            password="pass",
            name="Author Three",
            roles=[Roles.user],
            db_sess=db_sess
        )
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

    def test_create_category(self, db_sess):
        category = RecipeCategory.new(name="Dessert", creator=None)
        db_sess.add(category)
        db_sess.commit()

        assert category.id is not None
        assert category.name == "Dessert"
        assert category.deleted is False

    def test_category_delete(self, db_sess):
        # Create a real user to act as actor
        fake_creator = UserBase.get_fake_system()
        actor = User.new(
            creator=fake_creator,
            login="unit_actoruser",
            password="pass",
            name="Actor User",
            roles=[Roles.user],
            db_sess=db_sess
        )
        # User.new already commits

        category = RecipeCategory.new(name="ToDelete", creator=None)
        db_sess.add(category)
        db_sess.commit()

        category.delete(actor, db_sess=db_sess)
        db_sess.commit()

        assert category.deleted is True


class TestIngredient:
    """Test Ingredient model."""

    def test_create_ingredient(self, db_sess):
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

    def test_create_recipe_ingredient(self, db_sess):
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="unit_author4",
            password="pass",
            name="Author Four",
            roles=[Roles.user],
            db_sess=db_sess
        )
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

    def test_create_recipe_step(self, db_sess):
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="unit_author5",
            password="pass",
            name="Author Five",
            roles=[Roles.user],
            db_sess=db_sess
        )
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

    def test_create_recipe_image(self, db_sess):
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="unit_author6",
            password="pass",
            name="Author Six",
            roles=[Roles.user],
            db_sess=db_sess
        )
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
        from bafser.data.image import Image
        from bafser import get_datetime_now
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


class TestComment:
    """Test Comment model."""

    def test_create_comment(self, db_sess):
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="unit_author7",
            password="pass",
            name="Author Seven",
            roles=[Roles.user],
            db_sess=db_sess
        )
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

        comment = Comment.new(
            recipe_id=recipe.id,
            user_id=author.id,
            text="Great recipe!",
            creator=None,
        )
        db_sess.add(comment)
        db_sess.commit()

        assert comment.id is not None
        assert comment.recipe_id == recipe.id
        assert comment.user_id == author.id
        assert comment.text == "Great recipe!"

    def test_comment_update(self, db_sess):
        """Test updating a comment."""
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="unit_author_update",
            password="pass",
            name="Author Update",
            roles=[Roles.user],
            db_sess=db_sess
        )
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

        comment = Comment.new(
            recipe_id=recipe.id,
            user_id=author.id,
            text="Original text",
            creator=None,
        )
        db_sess.add(comment)
        db_sess.commit()

        # Update text
        comment.update(text="Updated text", actor=None)
        db_sess.commit()

        assert comment.text == "Updated text"
        # Ensure updated_at changed (should be auto-updated)
        assert comment.updated_at is not None

    def test_comment_get_by_recipe(self, db_sess):
        """Test retrieving comments by recipe."""
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="unit_author_get",
            password="pass",
            name="Author Get",
            roles=[Roles.user],
            db_sess=db_sess
        )
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

        # Create two comments
        comment1 = Comment.new(
            recipe_id=recipe.id,
            user_id=author.id,
            text="First comment",
            creator=None,
        )
        db_sess.add(comment1)
        comment2 = Comment.new(
            recipe_id=recipe.id,
            user_id=author.id,
            text="Second comment",
            creator=None,
        )
        db_sess.add(comment2)
        db_sess.commit()

        # Retrieve
        comments = Comment.get_by_recipe(recipe.id, db_sess=db_sess)
        assert len(comments) == 2
        # Should be ordered by created_at descending (newest first)
        # Since they were created sequentially, comment2 is newer
        assert comments[0].id == comment2.id
        assert comments[1].id == comment1.id
        assert {c.text for c in comments} == {"First comment", "Second comment"}

    def test_comment_get_dict(self, db_sess):
        """Test serialization to dict."""
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="unit_author_dict",
            password="pass",
            name="Author Dict",
            roles=[Roles.user],
            db_sess=db_sess
        )
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

        comment = Comment.new(
            recipe_id=recipe.id,
            user_id=author.id,
            text="Test dict",
            creator=None,
        )
        db_sess.add(comment)
        db_sess.commit()

        d = comment.get_dict()
        assert d["id"] == comment.id
        assert d["user_id"] == author.id
        assert d["recipe_id"] == recipe.id
        assert d["text"] == "Test dict"
        assert "created_at" in d
        # ISO format string
        import datetime
        datetime.datetime.fromisoformat(d["created_at"])  # should not raise


class TestRating:
    """Test Rating model."""

    def test_create_rating(self, db_sess):
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="unit_author8",
            password="pass",
            name="Author Eight",
            roles=[Roles.user],
            db_sess=db_sess
        )
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

        rating = Rating.new(
            recipe_id=recipe.id,
            user_id=author.id,
            rating=5,
            creator=None,
        )
        db_sess.add(rating)
        db_sess.commit()

        # Rating uses composite primary key (user_id, recipe_id), no id column
        assert rating.recipe_id == recipe.id
        assert rating.user_id == author.id
        assert rating.rating == 5

    def test_rating_update(self, db_sess):
        """Test updating a rating."""
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="unit_rating_update",
            password="pass",
            name="Rating Update",
            roles=[Roles.user],
            db_sess=db_sess
        )
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

        rating = Rating.new(
            recipe_id=recipe.id,
            user_id=author.id,
            rating=3,
            creator=None,
        )
        db_sess.add(rating)
        db_sess.commit()

        # Update rating
        rating.update(rating=5, actor=None)
        db_sess.commit()

        assert rating.rating == 5
        # Ensure rating is updated in database
        db_sess.refresh(rating)
        assert rating.rating == 5

    def test_rating_get_stats(self, db_sess):
        """Test retrieving rating statistics."""
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="unit_rating_stats",
            password="pass",
            name="Rating Stats",
            roles=[Roles.user],
            db_sess=db_sess
        )
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

        # Create three ratings
        rating1 = Rating.new(
            recipe_id=recipe.id,
            user_id=author.id,
            rating=4,
            creator=None,
        )
        db_sess.add(rating1)
        # Need another user for second rating (same user can't have two ratings for same recipe)
        user2 = User.new(
            creator=fake_creator,
            login="unit_rating_stats2",
            password="pass",
            name="User Two",
            roles=[Roles.user],
            db_sess=db_sess
        )
        rating2 = Rating.new(
            recipe_id=recipe.id,
            user_id=user2.id,
            rating=2,
            creator=None,
        )
        db_sess.add(rating2)
        db_sess.commit()

        avg, count, distribution = Rating.get_stats(recipe.id, db_sess=db_sess)
        # Average of 4 and 2 is 3.0
        assert avg == 3.0
        assert count == 2
        assert distribution == {"1": 0, "2": 1, "3": 0, "4": 1, "5": 0}

    def test_rating_recalculate_recipe_stats(self, db_sess):
        """Test recalculating recipe rating and vote count."""
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="unit_rating_recalc",
            password="pass",
            name="Rating Recalc",
            roles=[Roles.user],
            db_sess=db_sess
        )
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

        # Initially recipe rating is 0.0, vote_count 0
        assert recipe.rating == 0.0
        assert recipe.vote_count == 0

        # Add a rating
        rating = Rating.new(
            recipe_id=recipe.id,
            user_id=author.id,
            rating=5,
            creator=None,
        )
        db_sess.add(rating)
        db_sess.commit()

        # Recalculate
        Rating.recalculate_recipe_stats(recipe.id, db_sess=db_sess)
        db_sess.refresh(recipe)
        assert recipe.rating == 5.0
        assert recipe.vote_count == 1

        # Add another rating from different user
        user2 = User.new(
            creator=fake_creator,
            login="unit_rating_recalc2",
            password="pass",
            name="User Two",
            roles=[Roles.user],
            db_sess=db_sess
        )
        rating2 = Rating.new(
            recipe_id=recipe.id,
            user_id=user2.id,
            rating=3,
            creator=None,
        )
        db_sess.add(rating2)
        db_sess.commit()

        Rating.recalculate_recipe_stats(recipe.id, db_sess=db_sess)
        db_sess.refresh(recipe)
        assert recipe.rating == 4.0  # (5+3)/2
        assert recipe.vote_count == 2

    def test_rating_get_by_user_and_recipe(self, db_sess):
        """Test retrieving rating by user and recipe."""
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="unit_rating_get",
            password="pass",
            name="Rating Get",
            roles=[Roles.user],
            db_sess=db_sess
        )
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

        rating = Rating.new(
            recipe_id=recipe.id,
            user_id=author.id,
            rating=4,
            creator=None,
        )
        db_sess.add(rating)
        db_sess.commit()

        found = Rating.get_by_user_and_recipe(author.id, recipe.id, db_sess=db_sess)
        assert found is not None
        assert found.rating == 4
        assert found.user_id == author.id
        assert found.recipe_id == recipe.id

        # Non-existent rating
        not_found = Rating.get_by_user_and_recipe(999, recipe.id, db_sess=db_sess)
        assert not_found is None

    def test_rating_exists(self, db_sess):
        """Test checking if a rating exists."""
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="unit_rating_exists",
            password="pass",
            name="Rating Exists",
            roles=[Roles.user],
            db_sess=db_sess
        )
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

        # Initially does not exist
        assert Rating.exists(author.id, recipe.id, db_sess=db_sess) is False

        rating = Rating.new(
            recipe_id=recipe.id,
            user_id=author.id,
            rating=5,
            creator=None,
        )
        db_sess.add(rating)
        db_sess.commit()

        assert Rating.exists(author.id, recipe.id, db_sess=db_sess) is True
        assert Rating.exists(999, recipe.id, db_sess=db_sess) is False

    def test_rating_get_dict(self, db_sess):
        """Test serialization to dict."""
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="unit_rating_dict",
            password="pass",
            name="Rating Dict",
            roles=[Roles.user],
            db_sess=db_sess
        )
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

        rating = Rating.new(
            recipe_id=recipe.id,
            user_id=author.id,
            rating=5,
            creator=None,
        )
        db_sess.add(rating)
        db_sess.commit()

        d = rating.get_dict()
        assert d["user_id"] == author.id
        assert d["recipe_id"] == recipe.id
        assert d["rating"] == 5


class TestFavorite:
    """Test Favorite model."""

    def test_create_favorite(self, db_sess):
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="unit_author9",
            password="pass",
            name="Author Nine",
            roles=[Roles.user],
            db_sess=db_sess
        )
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

        favorite = Favorite.new(
            recipe_id=recipe.id,
            user_id=author.id,
            creator=None,
        )
        db_sess.add(favorite)
        db_sess.commit()

        # Favorite uses composite primary key (user_id, recipe_id), no id column
        assert favorite.recipe_id == recipe.id
        assert favorite.user_id == author.id

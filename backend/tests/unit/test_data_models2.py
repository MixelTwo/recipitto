"""
Unit tests for data models.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from bafser import UserBase

from data._roles import Roles
from data.rating import Rating
from data.recipe import Recipe
from data.recipe_category import RecipeCategory
from data.user import User


class TestRating:
    """Test Rating model."""

    def test_create_rating(self, db_sess: "Session") -> None:
        fake_creator = UserBase.get_fake_system()
        author = User.new(creator=fake_creator, login="unit_author8", password="pass", name="Author Eight", roles=[Roles.user], db_sess=db_sess)
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

    def test_rating_update(self, db_sess: "Session") -> None:
        """Test updating a rating."""
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator, login="unit_rating_update", password="pass", name="Rating Update", roles=[Roles.user], db_sess=db_sess
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

    def test_rating_get_stats(self, db_sess: "Session") -> None:
        """Test retrieving rating statistics."""
        fake_creator = UserBase.get_fake_system()
        author = User.new(creator=fake_creator, login="unit_rating_stats", password="pass", name="Rating Stats", roles=[Roles.user], db_sess=db_sess)
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
        user2 = User.new(creator=fake_creator, login="unit_rating_stats2", password="pass", name="User Two", roles=[Roles.user], db_sess=db_sess)
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

    def test_rating_recalculate_recipe_stats(self, db_sess: "Session") -> None:
        """Test recalculating recipe rating and vote count."""
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator, login="unit_rating_recalc", password="pass", name="Rating Recalc", roles=[Roles.user], db_sess=db_sess
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
        user2 = User.new(creator=fake_creator, login="unit_rating_recalc2", password="pass", name="User Two", roles=[Roles.user], db_sess=db_sess)
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

    def test_rating_get_by_user_and_recipe(self, db_sess: "Session") -> None:
        """Test retrieving rating by user and recipe."""
        fake_creator = UserBase.get_fake_system()
        author = User.new(creator=fake_creator, login="unit_rating_get", password="pass", name="Rating Get", roles=[Roles.user], db_sess=db_sess)
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

    def test_rating_exists(self, db_sess: "Session") -> None:
        """Test checking if a rating exists."""
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator, login="unit_rating_exists", password="pass", name="Rating Exists", roles=[Roles.user], db_sess=db_sess
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

    def test_rating_get_dict(self, db_sess: "Session") -> None:
        """Test serialization to dict."""
        fake_creator = UserBase.get_fake_system()
        author = User.new(creator=fake_creator, login="unit_rating_dict", password="pass", name="Rating Dict", roles=[Roles.user], db_sess=db_sess)
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

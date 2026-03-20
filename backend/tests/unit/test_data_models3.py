"""
Unit tests for data models.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from bafser import UserBase

from data._roles import Roles
from data.comment import Comment
from data.favorite import Favorite
from data.recipe import Recipe
from data.recipe_category import RecipeCategory
from data.user import User


class TestComment:
    """Test Comment model."""

    def test_create_comment(self, db_sess: "Session") -> None:
        fake_creator = UserBase.get_fake_system()
        author = User.new(creator=fake_creator, login="unit_author7", password="pass", name="Author Seven", roles=[Roles.user], db_sess=db_sess)
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

    def test_comment_update(self, db_sess: "Session") -> None:
        """Test updating a comment."""
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator, login="unit_author_update", password="pass", name="Author Update", roles=[Roles.user], db_sess=db_sess
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

    def test_comment_get_by_recipe(self, db_sess: "Session") -> None:
        """Test retrieving comments by recipe."""
        fake_creator = UserBase.get_fake_system()
        author = User.new(creator=fake_creator, login="unit_author_get", password="pass", name="Author Get", roles=[Roles.user], db_sess=db_sess)
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

    def test_comment_get_dict(self, db_sess: "Session") -> None:
        """Test serialization to dict."""
        fake_creator = UserBase.get_fake_system()
        author = User.new(creator=fake_creator, login="unit_author_dict", password="pass", name="Author Dict", roles=[Roles.user], db_sess=db_sess)
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


class TestFavorite:
    """Test Favorite model."""

    def test_create_favorite(self, db_sess: "Session") -> None:
        fake_creator = UserBase.get_fake_system()
        author = User.new(creator=fake_creator, login="unit_author9", password="pass", name="Author Nine", roles=[Roles.user], db_sess=db_sess)
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

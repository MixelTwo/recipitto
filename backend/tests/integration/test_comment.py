"""
Integration tests for comment blueprint.
"""

from typing import TYPE_CHECKING

from data._roles import Roles
from data.comment import Comment
from data.recipe import Recipe, RecipeStatus
from data.recipe_category import RecipeCategory
from data.user import User

if TYPE_CHECKING:
    from flask.testing import FlaskClient
    from sqlalchemy.orm import Session


class TestCommentEndpoints:
    """Test comment endpoints."""

    def test_list_comments(self, client: "FlaskClient", db_sess: "Session") -> None:
        """GET /api/recipes/<id>/comments returns list."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(creator=admin, login="test_author_comment1", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
        recipe = Recipe.new(
            title="Test Recipe for Comments",
            description="Desc",
            active_time=30,
            total_time=60,
            difficulty=3,
            author=author,
            category_id=category.id,
            status=RecipeStatus.DRAFT,
            creator=admin,
        )
        db_sess.add(recipe)
        db_sess.commit()
        # Create a comment
        commenter = User.new(creator=admin, login="test_commenter1", password="pass", name="Commenter", roles=[Roles.user], db_sess=db_sess)
        comment = Comment.new(user_id=commenter.id, recipe_id=recipe.id, text="Great recipe!", creator=admin)
        db_sess.add(comment)
        db_sess.commit()

        response = client.get(f"/api/recipes/{recipe.id}/comments")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1  # pyright: ignore[reportUnknownArgumentType]
        found = next((c for c in data if c["id"] == comment.id), None)  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]
        assert found is not None
        assert found["text"] == "Great recipe!"
        assert found["user_id"] == commenter.id

    def test_get_comment(self, client: "FlaskClient", db_sess: "Session") -> None:
        """GET /api/comments/<id> returns comment."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category 2", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(creator=admin, login="test_author_comment2", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
        recipe = Recipe.new(
            title="Recipe",
            description="Desc",
            active_time=30,
            total_time=60,
            difficulty=3,
            author=author,
            category_id=category.id,
            status=RecipeStatus.DRAFT,
            creator=admin,
        )
        db_sess.add(recipe)
        db_sess.commit()
        commenter = User.new(creator=admin, login="test_commenter2", password="pass", name="Commenter", roles=[Roles.user], db_sess=db_sess)
        comment = Comment.new(user_id=commenter.id, recipe_id=recipe.id, text="Nice", creator=admin)
        db_sess.add(comment)
        db_sess.commit()

        response = client.get(f"/api/comments/{comment.id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == comment.id
        assert data["text"] == "Nice"
        assert data["recipe_id"] == recipe.id

    def test_create_comment(self, authenticated_client: "FlaskClient", db_sess: "Session") -> None:
        """POST /api/recipes/<id>/comments creates comment."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category 3", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(creator=admin, login="test_author_comment3", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
        recipe = Recipe.new(
            title="Recipe",
            description="Desc",
            active_time=30,
            total_time=60,
            difficulty=3,
            author=author,
            category_id=category.id,
            status=RecipeStatus.DRAFT,
            creator=admin,
        )
        db_sess.add(recipe)
        db_sess.commit()

        response = authenticated_client.post(f"/api/recipes/{recipe.id}/comments", json={"text": "This is a comment"})
        assert response.status_code == 200
        data = response.get_json()
        assert data["text"] == "This is a comment"
        assert data["recipe_id"] == recipe.id
        # Verify in DB
        user = User.get_by_login(db_sess, "authuser")
        assert user
        comments = Comment.get_by_recipe(recipe.id)
        found = next((c for c in comments if c.user_id == user.id), None)
        assert found is not None
        assert found.text == "This is a comment"

    def test_update_comment_as_owner(self, authenticated_client: "FlaskClient", db_sess: "Session") -> None:
        """PATCH /api/comments/<id> updates comment if user is author."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category 4", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(creator=admin, login="test_author_comment4", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
        recipe = Recipe.new(
            title="Recipe",
            description="Desc",
            active_time=30,
            total_time=60,
            difficulty=3,
            author=author,
            category_id=category.id,
            status=RecipeStatus.DRAFT,
            creator=admin,
        )
        db_sess.add(recipe)
        db_sess.commit()
        user = User.get_by_login(db_sess, "authuser")
        assert user
        comment = Comment.new(user_id=user.id, recipe_id=recipe.id, text="Old text", creator=admin)
        db_sess.add(comment)
        db_sess.commit()

        response = authenticated_client.patch(f"/api/comments/{comment.id}", json={"text": "Updated text"})
        assert response.status_code == 200
        data = response.get_json()
        assert data["text"] == "Updated text"
        # Verify update
        updated = Comment.get2(comment.id)
        assert updated
        assert updated.text == "Updated text"

    def test_update_comment_as_admin(self, admin_client: "FlaskClient", db_sess: "Session") -> None:
        """Admin can update any comment."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category 5", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(creator=admin, login="test_author_comment5", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
        recipe = Recipe.new(
            title="Recipe",
            description="Desc",
            active_time=30,
            total_time=60,
            difficulty=3,
            author=author,
            category_id=category.id,
            status=RecipeStatus.DRAFT,
            creator=admin,
        )
        db_sess.add(recipe)
        db_sess.commit()
        commenter = User.new(creator=admin, login="test_commenter5", password="pass", name="Commenter", roles=[Roles.user], db_sess=db_sess)
        comment = Comment.new(user_id=commenter.id, recipe_id=recipe.id, text="Original", creator=admin)
        db_sess.add(comment)
        db_sess.commit()

        response = admin_client.patch(f"/api/comments/{comment.id}", json={"text": "Admin edited"})
        assert response.status_code == 200
        data = response.get_json()
        assert data["text"] == "Admin edited"

    def test_update_comment_forbidden(self, authenticated_client: "FlaskClient", db_sess: "Session") -> None:
        """User cannot update another user's comment."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category 6", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(creator=admin, login="test_author_comment6", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
        recipe = Recipe.new(
            title="Recipe",
            description="Desc",
            active_time=30,
            total_time=60,
            difficulty=3,
            author=author,
            category_id=category.id,
            status=RecipeStatus.DRAFT,
            creator=admin,
        )
        db_sess.add(recipe)
        db_sess.commit()
        other_user = User.new(creator=admin, login="other_user_comment6", password="pass", name="Other", roles=[Roles.user], db_sess=db_sess)
        comment = Comment.new(user_id=other_user.id, recipe_id=recipe.id, text="Not yours", creator=admin)
        db_sess.add(comment)
        db_sess.commit()

        response = authenticated_client.patch(f"/api/comments/{comment.id}", json={"text": "Trying to edit"})
        assert response.status_code == 403
        data = response.get_json()
        assert "own comments" in data.get("msg", "")

    def test_delete_comment_as_owner(self, authenticated_client: "FlaskClient", db_sess: "Session") -> None:
        """DELETE /api/comments/<id> deletes comment if user is author."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category 7", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(creator=admin, login="test_author_comment7", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
        recipe = Recipe.new(
            title="Recipe",
            description="Desc",
            active_time=30,
            total_time=60,
            difficulty=3,
            author=author,
            category_id=category.id,
            status=RecipeStatus.DRAFT,
            creator=admin,
        )
        db_sess.add(recipe)
        db_sess.commit()
        user = User.get_by_login(db_sess, "authuser")
        assert user
        comment = Comment.new(user_id=user.id, recipe_id=recipe.id, text="To delete", creator=admin)
        db_sess.add(comment)
        db_sess.commit()

        response = authenticated_client.delete(f"/api/comments/{comment.id}")
        assert response.status_code == 204
        # Verify soft delete
        deleted = Comment.get2(comment.id, includeDeleted=True)
        assert deleted
        assert deleted.deleted is True

    def test_delete_comment_as_admin(self, admin_client: "FlaskClient", db_sess: "Session") -> None:
        """Admin can delete any comment."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category 8", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(creator=admin, login="test_author_comment8", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
        recipe = Recipe.new(
            title="Recipe",
            description="Desc",
            active_time=30,
            total_time=60,
            difficulty=3,
            author=author,
            category_id=category.id,
            status=RecipeStatus.DRAFT,
            creator=admin,
        )
        db_sess.add(recipe)
        db_sess.commit()
        commenter = User.new(creator=admin, login="test_commenter8", password="pass", name="Commenter", roles=[Roles.user], db_sess=db_sess)
        comment = Comment.new(user_id=commenter.id, recipe_id=recipe.id, text="Admin delete", creator=admin)
        db_sess.add(comment)
        db_sess.commit()

        response = admin_client.delete(f"/api/comments/{comment.id}")
        assert response.status_code == 204
        deleted = Comment.get2(comment.id, includeDeleted=True)
        assert deleted
        assert deleted.deleted is True

    def test_delete_comment_forbidden(self, authenticated_client: "FlaskClient", db_sess: "Session") -> None:
        """User cannot delete another user's comment."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category 9", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(creator=admin, login="test_author_comment9", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
        recipe = Recipe.new(
            title="Recipe",
            description="Desc",
            active_time=30,
            total_time=60,
            difficulty=3,
            author=author,
            category_id=category.id,
            status=RecipeStatus.DRAFT,
            creator=admin,
        )
        db_sess.add(recipe)
        db_sess.commit()
        other_user = User.new(creator=admin, login="other_user_comment9", password="pass", name="Other", roles=[Roles.user], db_sess=db_sess)
        comment = Comment.new(user_id=other_user.id, recipe_id=recipe.id, text="Not yours", creator=admin)
        db_sess.add(comment)
        db_sess.commit()

        response = authenticated_client.delete(f"/api/comments/{comment.id}")
        assert response.status_code == 403
        data = response.get_json()
        assert "own comments" in data.get("msg", "")

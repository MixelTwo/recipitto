"""
Integration tests for rating blueprint.
"""

from typing import TYPE_CHECKING
from unittest.mock import patch

from sqlalchemy.exc import IntegrityError

from data._roles import Roles
from data.rating import Rating
from data.recipe import Recipe, RecipeStatus
from data.recipe_category import RecipeCategory
from data.user import User

if TYPE_CHECKING:
    from flask.testing import FlaskClient
    from sqlalchemy.orm import Session


class TestRatingEndpoints:
    """Test rating endpoints."""

    def test_get_rating_stats(self, client: "FlaskClient", db_sess: "Session") -> None:
        """GET /api/recipes/<id>/ratings returns stats."""
        # Get admin user as creator
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        # Create a recipe category
        category = RecipeCategory.new(name="Test Category", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        # Create author
        author = User.new(creator=admin, login="test_author_rating1", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
        # Create recipe
        recipe = Recipe.new(
            title="Test Recipe for Rating",
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
        # Add a rating
        rater = User.new(creator=admin, login="test_rater1", password="pass", name="Rater", roles=[Roles.user], db_sess=db_sess)
        rating = Rating.new(user_id=rater.id, recipe_id=recipe.id, rating=4, creator=admin)
        db_sess.add(rating)
        db_sess.commit()

        response = client.get(f"/api/recipes/{recipe.id}/ratings")
        assert response.status_code == 200
        data = response.get_json()
        assert data["recipe_id"] == recipe.id
        assert data["average"] == 4.0
        assert data["count"] == 1
        assert data["distribution"] == {"1": 0, "2": 0, "3": 0, "4": 1, "5": 0}

    def test_get_rating_stats_no_ratings(self, client: "FlaskClient", db_sess: "Session") -> None:
        """GET stats for recipe with no ratings."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category 2", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(creator=admin, login="test_author_rating2", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
        recipe = Recipe.new(
            title="No Rating Recipe",
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

        response = client.get(f"/api/recipes/{recipe.id}/ratings")
        assert response.status_code == 200
        data = response.get_json()
        assert data["recipe_id"] == recipe.id
        assert data["average"] == 0.0
        assert data["count"] == 0
        assert data["distribution"] == {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}

    def test_get_my_rating_unauthenticated(self, client: "FlaskClient", db_sess: "Session") -> None:
        """GET /api/recipes/<id>/ratings/me without auth returns 401."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category 3", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(creator=admin, login="test_author_rating3", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
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

        response = client.get(f"/api/recipes/{recipe.id}/ratings/me")
        assert response.status_code == 401

    def test_get_my_rating_not_rated(self, authenticated_client: "FlaskClient", db_sess: "Session") -> None:
        """GET my rating when user hasn't rated returns 404."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category 4", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(creator=admin, login="test_author_rating4", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
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

        response = authenticated_client.get(f"/api/recipes/{recipe.id}/ratings/me")
        assert response.status_code == 404
        data = response.get_json()
        assert "Not rated" in data.get("msg", "")

    def test_get_my_rating_exists(self, authenticated_client: "FlaskClient", db_sess: "Session") -> None:
        """GET my rating returns existing rating."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category 5", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(creator=admin, login="test_author_rating5", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
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
        # Get the authenticated user (the one created by authenticated_client fixture)
        user = User.get_by_login(db_sess, "authuser")
        assert user
        rating = Rating.new(user_id=user.id, recipe_id=recipe.id, rating=5, creator=admin)
        db_sess.add(rating)
        db_sess.commit()

        response = authenticated_client.get(f"/api/recipes/{recipe.id}/ratings/me")
        assert response.status_code == 200
        data = response.get_json()
        assert data["rating"] == 5
        assert data["user_id"] == user.id
        assert data["recipe_id"] == recipe.id

    def test_rate_recipe_create(self, authenticated_client: "FlaskClient", db_sess: "Session") -> None:
        """POST /api/recipes/<id>/ratings creates a new rating."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category 6", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(creator=admin, login="test_author_rating6", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
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

        response = authenticated_client.post(f"/api/recipes/{recipe.id}/ratings", json={"rating": 3})
        assert response.status_code == 200
        data = response.get_json()
        assert data["rating"] == 3
        assert data["recipe_id"] == recipe.id
        # Verify in DB
        user = User.get_by_login(db_sess, "authuser")
        assert user
        rating = Rating.get_by_user_and_recipe(user.id, recipe.id)
        assert rating is not None
        assert rating.rating == 3

    def test_rate_recipe_update(self, authenticated_client: "FlaskClient", db_sess: "Session") -> None:
        """POST updates existing rating."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category 7", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(creator=admin, login="test_author_rating7", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
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
        rating = Rating.new(user_id=user.id, recipe_id=recipe.id, rating=2, creator=admin)
        db_sess.add(rating)
        db_sess.commit()

        response = authenticated_client.post(f"/api/recipes/{recipe.id}/ratings", json={"rating": 5})
        assert response.status_code == 200
        data = response.get_json()
        assert data["rating"] == 5
        # Verify updated
        rating = Rating.get_by_user_and_recipe(user.id, recipe.id)
        assert rating
        assert rating.rating == 5

    def test_rate_recipe_invalid_rating(self, authenticated_client: "FlaskClient", db_sess: "Session") -> None:
        """POST with rating out of range returns 400."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category 8", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(creator=admin, login="test_author_rating8", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
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

        response = authenticated_client.post(f"/api/recipes/{recipe.id}/ratings", json={"rating": 0})
        assert response.status_code == 400
        response = authenticated_client.post(f"/api/recipes/{recipe.id}/ratings", json={"rating": 6})
        assert response.status_code == 400

    def test_delete_rating(self, authenticated_client: "FlaskClient", db_sess: "Session") -> None:
        """DELETE removes rating."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category 9", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(creator=admin, login="test_author_rating9", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
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
        rating = Rating.new(user_id=user.id, recipe_id=recipe.id, rating=4, creator=admin)
        db_sess.add(rating)
        db_sess.commit()

        response = authenticated_client.delete(f"/api/recipes/{recipe.id}/ratings")
        assert response.status_code == 204
        # Verify deleted
        rating = Rating.get_by_user_and_recipe(user.id, recipe.id)
        assert rating is None

    def test_delete_rating_not_found(self, authenticated_client: "FlaskClient", db_sess: "Session") -> None:
        """DELETE when rating doesn't exist returns 404."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category 10", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(creator=admin, login="test_author_rating10", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
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

        response = authenticated_client.delete(f"/api/recipes/{recipe.id}/ratings")
        assert response.status_code == 404

    def test_rate_recipe_race_condition_conflict(self, authenticated_client: "FlaskClient", db_sess: "Session") -> None:
        """POST /api/recipes/<id>/ratings handles IntegrityError race condition with no existing rating after rollback."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category Race Conflict", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(
            creator=admin, login="test_author_rating_race_conflict", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess
        )
        recipe = Recipe.new(
            title="Recipe Race Conflict",
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

        # Mock Rating.new to raise IntegrityError and Rating.get_by_user_and_recipe to return None
        with (
            patch("data.rating.Rating.new", side_effect=IntegrityError("duplicate", None, Exception())),
            patch("data.rating.Rating.get_by_user_and_recipe", return_value=None),
        ):
            response = authenticated_client.post(f"/api/recipes/{recipe.id}/ratings", json={"rating": 4})
            # Should return 409 Conflict because no rating found after rollback
            assert response.status_code == 409
            data = response.get_json()
            assert "Conflict" in data.get("msg", "")

    def test_rate_recipe_race_condition_update(self, authenticated_client: "FlaskClient", db_sess: "Session") -> None:
        """POST /api/recipes/<id>/ratings handles IntegrityError race condition with existing rating after rollback."""
        admin = User.get_by_login(db_sess, "admin")
        assert admin
        category = RecipeCategory.new(name="Test Category Race Update", creator=admin)
        db_sess.add(category)
        db_sess.commit()
        author = User.new(creator=admin, login="test_author_rating_race_update", password="pass", name="Author", roles=[Roles.user], db_sess=db_sess)
        recipe = Recipe.new(
            title="Recipe Race Update",
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

        # Create a rating that will be found after the IntegrityError
        user = User.get_by_login(db_sess, "authuser")
        assert user
        existing_rating = Rating.new(user_id=user.id, recipe_id=recipe.id, rating=2, creator=admin)
        db_sess.add(existing_rating)
        db_sess.commit()

        # Mock Rating.new to raise IntegrityError, but Rating.get_by_user_and_recipe returns the existing rating
        with patch("data.rating.Rating.new", side_effect=IntegrityError("duplicate", None, Exception())):
            # Ensure get_by_user_and_recipe returns the existing rating (it will because we didn't mock it)
            response = authenticated_client.post(f"/api/recipes/{recipe.id}/ratings", json={"rating": 4})
            # Should still succeed because existing rating is found after rollback
            assert response.status_code == 200
            data = response.get_json()
            assert data["rating"] == 4
            # Verify the existing rating was updated
            db_sess.refresh(existing_rating)
            assert existing_rating.rating == 4

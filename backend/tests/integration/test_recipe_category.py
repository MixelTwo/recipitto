"""
Integration tests for recipe_category blueprint.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask.testing import FlaskClient
    from sqlalchemy.orm import Session

from data.recipe_category import RecipeCategory
from data.user import User


class TestRecipeCategoryEndpoints:
    """Test recipe category CRUD endpoints."""

    def test_list_categories(self, client: "FlaskClient", db_sess: "Session") -> None:
        """GET /api/recipe-categories returns list."""
        admin = User.get_by_login(db_sess, "admin")
        category = RecipeCategory.new(name="Vegetables", creator=admin)
        db_sess.add(category)
        db_sess.commit()

        response = client.get("/api/recipe-categories")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1  # pyright: ignore[reportUnknownArgumentType]
        found = next((c for c in data if c["id"] == category.id), None)  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]
        assert found is not None
        assert found["name"] == "Vegetables"

    def test_get_category(self, client: "FlaskClient", db_sess: "Session") -> None:
        admin = User.get_by_login(db_sess, "admin")
        category = RecipeCategory.new(name="Fruits", creator=admin)
        db_sess.add(category)
        db_sess.commit()

        response = client.get(f"/api/recipe-categories/{category.id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == category.id
        assert data["name"] == "Fruits"

    def test_create_category_as_user(self, authenticated_client: "FlaskClient", db_sess: "Session") -> None:
        """POST /api/recipe-categories with user permissions."""
        response = authenticated_client.post(
            "/api/recipe-categories",
            json={
                "name": "Grains",
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "Grains"
        assert data["id"] is not None

        # Verify in database
        created = RecipeCategory.get2(data["id"])
        assert created
        assert created.name == "Grains"

    def test_update_category_as_user(self, authenticated_client: "FlaskClient", db_sess: "Session") -> None:
        admin = User.get_by_login(db_sess, "admin")
        category = RecipeCategory.new(name="Old Name", creator=admin)
        db_sess.add(category)
        db_sess.commit()

        response = authenticated_client.patch(
            f"/api/recipe-categories/{category.id}",
            json={
                "name": "New Name",
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "New Name"

        # Verify update
        updated = RecipeCategory.get2(category.id)
        assert updated
        assert updated.name == "New Name"

    def test_delete_category_as_user(self, authenticated_client: "FlaskClient", db_sess: "Session") -> None:
        admin = User.get_by_login(db_sess, "admin")
        category = RecipeCategory.new(name="To Delete", creator=admin)
        db_sess.add(category)
        db_sess.commit()

        response = authenticated_client.delete(f"/api/recipe-categories/{category.id}")
        assert response.status_code == 204

        # Verify soft delete
        deleted = RecipeCategory.get2(category.id, includeDeleted=True)
        assert deleted
        assert deleted.deleted is True

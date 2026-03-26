"""
Integration tests for ingredient_category blueprint.
"""

from typing import TYPE_CHECKING

from bafser import UserBase

from data._roles import Roles
from data.ingredient_category import IngredientCategory
from data.user import User

if TYPE_CHECKING:
    from flask.testing import FlaskClient
    from sqlalchemy.orm import Session


class TestIngredientCategoryEndpoints:
    """Test ingredient category CRUD endpoints."""

    def test_list_categories(self, client: "FlaskClient", db_sess: "Session") -> None:
        """GET /api/ingredient-categories returns list."""
        # Create a user as creator
        fake_creator = UserBase.get_fake_system()
        creator = User.new(creator=fake_creator, login="test_creator1", password="pass", name="Test Creator", roles=[Roles.user], db_sess=db_sess)
        # User.new already commits
        category = IngredientCategory.new(name="Vegetables", creator=creator)
        db_sess.add(category)
        db_sess.commit()

        response = client.get("/api/ingredient-categories")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1  # pyright: ignore[reportUnknownArgumentType]
        found = next((c for c in data if c["id"] == category.id), None)  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]
        assert found is not None
        assert found["name"] == "Vegetables"

    def test_get_category(self, client: "FlaskClient", db_sess: "Session") -> None:
        fake_creator = UserBase.get_fake_system()
        creator = User.new(creator=fake_creator, login="test_creator2", password="pass", name="Test Creator", roles=[Roles.user], db_sess=db_sess)
        category = IngredientCategory.new(name="Fruits", creator=creator)
        db_sess.add(category)
        db_sess.commit()

        response = client.get(f"/api/ingredient-categories/{category.id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == category.id
        assert data["name"] == "Fruits"

    def test_create_category_as_admin(self, admin_client: "FlaskClient", db_sess: "Session") -> None:
        """POST /api/ingredient-categories with user permissions."""
        response = admin_client.post(
            "/api/ingredient-categories",
            json={
                "name": "Grains",
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "Grains"
        assert data["id"] is not None

        # Verify in database
        created = IngredientCategory.get2(data["id"])
        assert created
        assert created.name == "Grains"

    def test_update_category_as_admin(self, admin_client: "FlaskClient", db_sess: "Session") -> None:
        fake_creator = UserBase.get_fake_system()
        creator = User.new(creator=fake_creator, login="test_creator3", password="pass", name="Test Creator", roles=[Roles.user], db_sess=db_sess)
        category = IngredientCategory.new(name="Old Name", creator=creator)
        db_sess.add(category)
        db_sess.commit()

        response = admin_client.patch(
            f"/api/ingredient-categories/{category.id}",
            json={
                "name": "New Name",
            },
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["name"] == "New Name"

        # Verify update
        updated = IngredientCategory.get2(category.id)
        assert updated
        assert updated.name == "New Name"

    def test_delete_category_as_admin(self, admin_client: "FlaskClient", db_sess: "Session") -> None:
        fake_creator = UserBase.get_fake_system()
        creator = User.new(creator=fake_creator, login="test_creator4", password="pass", name="Test Creator", roles=[Roles.user], db_sess=db_sess)
        category = IngredientCategory.new(name="To Delete", creator=creator)
        db_sess.add(category)
        db_sess.commit()

        response = admin_client.delete(f"/api/ingredient-categories/{category.id}")
        assert response.status_code == 204

        # Verify soft delete
        deleted = IngredientCategory.get2(category.id, includeDeleted=True)
        assert deleted
        assert deleted.deleted is True

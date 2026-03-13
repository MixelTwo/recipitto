"""
Integration tests for recipe blueprint.
"""
import pytest
from data.user import User
from data.recipe import Recipe, RecipeStatus
from data.recipe_category import RecipeCategory
from data._roles import Roles
from bafser import UserBase


class TestRecipeEndpoints:
    """Test recipe CRUD endpoints."""

    def test_list_recipes(self, client, db_sess):
        """GET /api/recipes returns list."""
        # Create a recipe
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="author1",
            password="pass",
            name="Author One",
            roles=[Roles.user],
            db_sess=db_sess
        )
        # User.new already commits
        category = RecipeCategory.new(name="Test Category", creator=author)
        db_sess.add(category)
        db_sess.commit()

        recipe = Recipe.new(
            title="Test Recipe",
            description="Test",
            active_time=10,
            total_time=20,
            difficulty=2,
            author=author,
            category_id=category.id,
            creator=author,
        )
        db_sess.add(recipe)
        db_sess.commit()

        response = client.get("/api/recipes")
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Find our recipe
        found = next((r for r in data if r["id"] == recipe.id), None)
        assert found is not None
        assert found["title"] == "Test Recipe"

    def test_get_recipe(self, client, db_sess):
        fake_creator = UserBase.get_fake_system()
        author = User.new(
            creator=fake_creator,
            login="author2",
            password="pass",
            name="Author Two",
            roles=[Roles.user],
            db_sess=db_sess
        )
        # User.new already commits
        category = RecipeCategory.new(name="Test Category", creator=author)
        db_sess.add(category)
        db_sess.commit()

        recipe = Recipe.new(
            title="Single Recipe",
            description="Desc",
            active_time=5,
            total_time=10,
            difficulty=1,
            author=author,
            category_id=category.id,
            creator=author,
        )
        db_sess.add(recipe)
        db_sess.commit()

        response = client.get(f"/api/recipes/{recipe.id}")
        assert response.status_code == 200
        data = response.get_json()
        assert data["id"] == recipe.id
        assert data["title"] == "Single Recipe"

    def test_create_recipe_authenticated(self, authenticated_client, db_sess):
        """POST /api/recipes with authenticated user."""
        # Need a category
        admin = User.get_by_login(db_sess, "admin")
        if not admin:
            admin = User.create_admin(db_sess)
        category = RecipeCategory.new(name="Dinner", creator=admin)
        db_sess.add(category)
        db_sess.commit()

        response = authenticated_client.post("/api/recipes", json={
            "title": "New Recipe",
            "description": "A delicious dish",
            "active_time": 30,
            "total_time": 60,
            "difficulty": 3,
            "category_id": category.id,
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data["title"] == "New Recipe"
        assert data["author"] == "authuser"  # from authenticated_client fixture
        assert data["status"] == "draft"

    def test_update_recipe_as_author(self, authenticated_client, db_sess):
        # Create a recipe owned by the authenticated user
        fake_creator = UserBase.get_fake_system()
        # Get the user from the fixture (we need its id)
        # Since authenticated_client creates a user with login "authuser", we can fetch it
        user = User.get_by_login(db_sess, "authuser")
        if not user:
            # create it (should not happen because fixture creates it)
            user = User.new(
                creator=fake_creator,
                login="authuser",
                password="testpass",
                name="Auth User",
                roles=[Roles.user],
                db_sess=db_sess
            )
            # User.new already commits
        category = RecipeCategory.new(name="Lunch", creator=user)
        db_sess.add(category)
        db_sess.commit()

        recipe = Recipe.new(
            title="Old Title",
            description="Old",
            active_time=5,
            total_time=5,
            difficulty=1,
            author=user,
            category_id=category.id,
            creator=user,
        )
        db_sess.add(recipe)
        db_sess.commit()

        response = authenticated_client.patch(f"/api/recipes/{recipe.id}", json={
            "title": "Updated Title",
            "difficulty": 5,
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data["title"] == "Updated Title"
        assert data["difficulty"] == 5

        # Verify in database
        updated = Recipe.get2(recipe.id)
        assert updated.title == "Updated Title"
        assert updated.difficulty == 5

    def test_update_recipe_as_admin(self, admin_client, db_sess):
        # Create a recipe owned by a different user
        fake_creator = UserBase.get_fake_system()
        other_user = User.new(
            creator=fake_creator,
            login="otheruser",
            password="pass",
            name="Other User",
            roles=[Roles.user],
            db_sess=db_sess
        )
        # User.new already commits
        category = RecipeCategory.new(name="Breakfast", creator=other_user)
        db_sess.add(category)
        db_sess.commit()

        recipe = Recipe.new(
            title="Other's Recipe",
            description="Other",
            active_time=10,
            total_time=20,
            difficulty=2,
            author=other_user,
            category_id=category.id,
            creator=other_user,
        )
        db_sess.add(recipe)
        db_sess.commit()

        # Admin can update any recipe
        response = admin_client.patch(f"/api/recipes/{recipe.id}", json={
            "title": "Admin Updated",
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data["title"] == "Admin Updated"

    def test_delete_recipe_as_author(self, authenticated_client, db_sess):
        fake_creator = UserBase.get_fake_system()
        user = User.get_by_login(db_sess, "authuser")
        if not user:
            user = User.new(
                creator=fake_creator,
                login="authuser",
                password="testpass",
                name="Auth User",
                roles=[Roles.user],
                db_sess=db_sess
            )
            # User.new already commits
        category = RecipeCategory.new(name="Dessert", creator=user)
        db_sess.add(category)
        db_sess.commit()

        recipe = Recipe.new(
            title="To Delete",
            description="Delete me",
            active_time=1,
            total_time=1,
            difficulty=1,
            author=user,
            category_id=category.id,
            creator=user,
        )
        db_sess.add(recipe)
        db_sess.commit()

        response = authenticated_client.delete(f"/api/recipes/{recipe.id}")
        assert response.status_code == 204

        # Verify soft delete
        deleted_recipe = Recipe.get2(recipe.id, includeDeleted=True)
        assert deleted_recipe.deleted is True

    def test_delete_recipe_as_admin(self, admin_client, db_sess):
        fake_creator = UserBase.get_fake_system()
        other_user = User.new(
            creator=fake_creator,
            login="otheruser2",
            password="pass",
            name="Other User",
            roles=[Roles.user],
            db_sess=db_sess
        )
        # User.new already commits
        category = RecipeCategory.new(name="Snack", creator=other_user)
        db_sess.add(category)
        db_sess.commit()

        recipe = Recipe.new(
            title="Other's Recipe To Delete",
            description="Delete",
            active_time=5,
            total_time=5,
            difficulty=1,
            author=other_user,
            category_id=category.id,
            creator=other_user,
        )
        db_sess.add(recipe)
        db_sess.commit()

        response = admin_client.delete(f"/api/recipes/{recipe.id}")
        assert response.status_code == 204

        deleted_recipe = Recipe.get2(recipe.id, includeDeleted=True)
        assert deleted_recipe.deleted is True

    def test_create_recipe_invalid_status(self, authenticated_client, db_sess):
        """POST /api/recipes with invalid status returns 400."""
        admin = User.get_by_login(db_sess, "admin")
        category = RecipeCategory.new(name="Invalid Status Category", creator=admin)
        db_sess.add(category)
        db_sess.commit()

        response = authenticated_client.post("/api/recipes", json={
            "title": "Recipe",
            "description": "Desc",
            "active_time": 30,
            "total_time": 60,
            "difficulty": 3,
            "category_id": category.id,
            "status": "invalid_status"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert "status is not" in data.get("msg", "")

    def test_update_recipe_invalid_status(self, authenticated_client, db_sess):
        """PATCH /api/recipes/<id> with invalid status returns 400."""
        admin = User.get_by_login(db_sess, "admin")
        user = User.get_by_login(db_sess, "authuser")
        if not user:
            user = User.new(
                creator=admin,
                login="authuser",
                password="testpass",
                name="Auth User",
                roles=[Roles.user],
                db_sess=db_sess
            )
        category = RecipeCategory.new(name="Update Invalid Category", creator=admin)
        db_sess.add(category)
        db_sess.commit()

        recipe = Recipe.new(
            title="Recipe",
            description="Desc",
            active_time=10,
            total_time=20,
            difficulty=2,
            author=user,
            category_id=category.id,
            creator=admin,
        )
        db_sess.add(recipe)
        db_sess.commit()

        response = authenticated_client.patch(f"/api/recipes/{recipe.id}", json={
            "status": "invalid_status"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert "status is not" in data.get("msg", "")

    def test_update_recipe_forbidden(self, authenticated_client, db_sess):
        """User cannot update another user's recipe."""
        admin = User.get_by_login(db_sess, "admin")
        other_user = User.new(
            creator=admin,
            login="otheruser3",
            password="pass",
            name="Other User",
            roles=[Roles.user],
            db_sess=db_sess
        )
        category = RecipeCategory.new(name="Forbidden Category", creator=admin)
        db_sess.add(category)
        db_sess.commit()

        recipe = Recipe.new(
            title="Other's Recipe",
            description="Desc",
            active_time=10,
            total_time=20,
            difficulty=2,
            author=other_user,
            category_id=category.id,
            creator=admin,
        )
        db_sess.add(recipe)
        db_sess.commit()

        response = authenticated_client.patch(f"/api/recipes/{recipe.id}", json={
            "title": "Hacked"
        })
        assert response.status_code == 403
        data = response.get_json()
        assert "own recipes" in data.get("msg", "")

    def test_delete_recipe_forbidden(self, authenticated_client, db_sess):
        """User cannot delete another user's recipe."""
        admin = User.get_by_login(db_sess, "admin")
        other_user = User.new(
            creator=admin,
            login="otheruser4",
            password="pass",
            name="Other User",
            roles=[Roles.user],
            db_sess=db_sess
        )
        category = RecipeCategory.new(name="Forbidden Delete Category", creator=admin)
        db_sess.add(category)
        db_sess.commit()

        recipe = Recipe.new(
            title="Other's Recipe",
            description="Desc",
            active_time=10,
            total_time=20,
            difficulty=2,
            author=other_user,
            category_id=category.id,
            creator=admin,
        )
        db_sess.add(recipe)
        db_sess.commit()

        response = authenticated_client.delete(f"/api/recipes/{recipe.id}")
        assert response.status_code == 403
        data = response.get_json()
        assert "own recipes" in data.get("msg", "")
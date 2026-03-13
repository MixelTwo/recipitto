"""
Integration tests for auth blueprint.
"""
import pytest
from data.user import User
from data._roles import Roles
from bafser import UserBase


class TestAuth:
    """Test authentication endpoints."""

    def test_login_success(self, client, db_sess):
        """Test successful login."""
        # Create a user
        fake_creator = UserBase.get_fake_system()
        user = User.new(
            creator=fake_creator,
            login="testuser",
            password="testpass",
            name="Test User",
            roles=[Roles.user],
            db_sess=db_sess
        )
        # User.new already commits

        # Login request
        response = client.post("/api/auth", json={
            "login": "testuser",
            "password": "testpass"
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data["login"] == "testuser"
        assert "access_token_cookie" in response.headers.get("Set-Cookie", "")

    def test_login_wrong_password(self, client, db_sess):
        fake_creator = UserBase.get_fake_system()
        user = User.new(
            creator=fake_creator,
            login="testuser2",
            password="rightpass",
            name="Test User",
            roles=[Roles.user],
            db_sess=db_sess
        )
        # User.new already commits

        response = client.post("/api/auth", json={
            "login": "testuser2",
            "password": "wrongpass"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data["msg"] == "Неправильный логин или пароль"

    def test_login_nonexistent_user(self, client):
        response = client.post("/api/auth", json={
            "login": "nonexistent",
            "password": "any"
        })
        assert response.status_code == 400
        data = response.get_json()
        assert data["msg"] == "Неправильный логин или пароль"

    def test_logout(self, client, authenticated_client):
        """Logout should clear cookies."""
        # Use authenticated client to ensure we have a cookie
        response = authenticated_client.post("/api/logout")
        assert response.status_code == 200
        # Check that cookies are cleared
        cookie_header = response.headers.get("Set-Cookie")
        assert cookie_header is not None
        assert "access_token_cookie=;" in cookie_header

    def test_get_current_user(self, authenticated_client):
        """GET /api/user returns current user info."""
        response = authenticated_client.get("/api/user")
        assert response.status_code == 200
        data = response.get_json()
        assert data["login"] == "authuser"
        assert "roles" in data
        assert "operations" in data
"""
Pytest fixtures for Bafser-based Flask application.
"""
import pytest
import tempfile
import os
import sys
from datetime import timedelta

# Patch bafser_config before importing bafser
import bafser_config

# Set test-specific configuration
bafser_config.use_alembic = False
bafser_config.db_mysql = False
bafser_config.sql_echo = False

# db_dev_path will be set via environment variable DBPATH
# We'll set it in the app fixture

from bafser import create_app, AppConfig, db_session, Role, UserRole
from data.user import User
from data._roles import Roles
from data._operations import Operations

# Add missing operations to user role for testing
if hasattr(Roles, 'ROLES'):
    user_role = Roles.ROLES.get(Roles.user)
    if user_role:
        ops = user_role.get("operations", [])
        # Add missing operations that are needed for testing
        missing = [
            Operations.recipe_update,
            Operations.recipe_delete,
            Operations.recipe_category_create,
            Operations.recipe_category_update,
            Operations.recipe_category_delete,
            Operations.ingredient_category_create,
            Operations.ingredient_category_update,
            Operations.ingredient_category_delete,
            Operations.ingredient_create,
            Operations.ingredient_update,
            Operations.ingredient_delete,
            Operations.recipe_step_create,
            Operations.recipe_step_update,
            Operations.recipe_step_delete,
            Operations.recipe_ingredient_create,
            Operations.recipe_ingredient_update,
            Operations.recipe_ingredient_delete,
            Operations.recipe_image_create,
            Operations.recipe_image_delete,
            Operations.comment_create,
            Operations.comment_update,
            Operations.comment_delete,
            Operations.rating_create,
            Operations.rating_update,
            Operations.rating_delete,
            Operations.favorite_create,
            Operations.favorite_delete,
            Operations.search_recipes,
        ]
        for op in missing:
            if op not in ops:
                ops.append(op)
        user_role["operations"] = ops


@pytest.fixture(scope="session")
def app():
    """
    Create a Flask application instance for testing.
    Uses a temporary SQLite database.
    """
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.environ["DBPATH"] = db_path

    # Ensure bafser_config uses this path for dev
    bafser_config.db_dev_path = db_path

    # Create app with DEV_MODE=True and long JWT expiration for tests
    app, _ = create_app(
        __name__,
        AppConfig(DEV_MODE=True, JWT_ACCESS_TOKEN_EXPIRES=timedelta(days=365)),
    )
    app.config["JWT_COOKIE_SECURE"] = False
    app.config["TESTING"] = True

    # Initialize database (without alembic)
    # db_session.global_init will create tables because use_alembic=False
    db_session.global_init(dev=True)

    # Get the engine for later disposal
    from sqlalchemy.orm import Session
    session = db_session.create_session()
    engine = session.bind
    session.close()

    # Patch Log._serialize to handle Enum serialization
    from bafser.data.log import Log
    import datetime
    import enum
    original_serialize = Log._serialize
    def patched_serialize(v):
        if isinstance(v, datetime.datetime):
            return v.isoformat()
        if isinstance(v, enum.Enum):
            return v.value
        return v
    Log._serialize = staticmethod(patched_serialize)

    # Create default roles and admin user if needed
    with db_session.create_session() as sess:
        Role.update_roles_permissions(sess)
        # Ensure admin user exists (optional)
        admin = User.get_by_login(sess, "admin", includeDeleted=True)
        if not admin:
            admin = User.create_admin(sess)
        sess.close()

    yield app

    # Restore original serialize (optional)
    Log._serialize = staticmethod(original_serialize)

    # Teardown
    engine.dispose()
    os.close(db_fd)
    os.unlink(db_path)
    if "DBPATH" in os.environ:
        del os.environ["DBPATH"]


@pytest.fixture
def db_sess(app):
    """
    Provide a database session for each test.
    Automatically rolls back and closes after test.
    Runs within an app context and sets g.db_session.
    """
    with app.app_context():
        from flask import g
        session = db_session.create_session()
        g.db_session = session
        yield session
        session.rollback()
        session.close()
        # Remove to avoid leakage
        if hasattr(g, 'db_session'):
            del g.db_session


@pytest.fixture
def client(app):
    """Test client."""
    return app.test_client()


@pytest.fixture
def authenticated_client(client, db_sess):
    """
    Authenticated test client with a regular user (role user).
    """
    # Get or create a test user
    user = User.get_by_login(db_sess, "authuser", includeDeleted=True)
    if not user:
        from bafser import UserBase
        fake_creator = UserBase.get_fake_system()
        user = User.new(
            creator=fake_creator,
            login="authuser",
            password="testpass",
            name="Auth User",
            roles=[Roles.user],  # role id for user
            db_sess=db_sess
        )
        # User.new already commits

    # Generate JWT token
    from bafser import create_access_token
    # Debug: print JWT config
    token = create_access_token(user)
    # Set token in client's cookies (Bafser uses cookies)
    client.set_cookie("access_token_cookie", token)
    # Also set Authorization header for API endpoints that may use it
    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"

    yield client

    # Cleanup (user will be deleted because db_sess rolls back)
    # No need to explicitly delete


@pytest.fixture
def admin_client(client, db_sess):
    """
    Authenticated test client with an admin user.
    """
    # Get or create admin user
    admin = User.get_by_login(db_sess, "admin", includeDeleted=True)
    if not admin:
        admin = User.create_admin(db_sess)

    # Generate token
    from bafser import create_access_token
    token = create_access_token(admin)

    client.set_cookie("access_token_cookie", token)
    client.environ_base["HTTP_AUTHORIZATION"] = f"Bearer {token}"

    yield client
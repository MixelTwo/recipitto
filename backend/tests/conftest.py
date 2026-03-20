"""
Pytest fixtures for Bafser-based Flask application.
"""

import os
import tempfile
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Iterator

import pytest

if TYPE_CHECKING:
    from flask import Flask
    from flask.testing import FlaskClient
    from sqlalchemy.orm import Session

# Patch bafser_config before importing bafser
import bafser_config

# Set test-specific configuration
bafser_config.use_alembic = False
bafser_config.db_mysql = False
bafser_config.sql_echo = False

# db_dev_path will be set via environment variable DBPATH
# We'll set it in the app fixture

from bafser import AppConfig, Role, create_app, db_session

from data._roles import Roles
from data.user import User


@pytest.fixture(scope="session")
def app() -> Iterator["Flask"]:
    """
    Create a Flask application instance for testing.
    Uses a temporary SQLite database.
    """
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp(suffix=".db")

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
    from sqlalchemy.orm import Session  # pyright: ignore[reportUnusedImport]

    session = db_session.create_session()
    engine = session.bind
    session.close()

    # Patch Log._serialize to handle Enum serialization
    import datetime
    import enum

    from bafser.data.log import Log

    original_serialize = Log._serialize  # pyright: ignore[reportPrivateUsage]

    def patched_serialize(v: Any):
        if isinstance(v, datetime.datetime):
            return v.isoformat()
        if isinstance(v, enum.Enum):
            return v.value
        return v

    Log._serialize = staticmethod(patched_serialize)  # pyright: ignore[reportPrivateUsage]

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
    Log._serialize = staticmethod(original_serialize)  # pyright: ignore[reportPrivateUsage]

    # Teardown
    engine.dispose()  # type: ignore
    os.close(db_fd)
    os.unlink(db_path)
    if "DBPATH" in os.environ:
        del os.environ["DBPATH"]


@pytest.fixture
def db_sess(app: "Flask") -> Iterator["Session"]:
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
        if hasattr(g, "db_session"):
            del g.db_session


@pytest.fixture
def client(app: "Flask") -> "FlaskClient":
    """Test client."""
    return app.test_client()


@pytest.fixture
def authenticated_client(client: "FlaskClient", db_sess: "Session") -> Iterator["FlaskClient"]:
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
            db_sess=db_sess,
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
def admin_client(client: "FlaskClient", db_sess: "Session") -> Iterator["FlaskClient"]:
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

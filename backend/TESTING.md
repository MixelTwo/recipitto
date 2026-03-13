# Testing Guide

This document describes the testing setup, fixtures, and practices for the Bafser Recipe Backend.

## Test Structure

- **`tests/unit/`** – Unit tests for data models (CRUD, validation, relationships).
- **`tests/integration/`** – Integration tests for Flask blueprints (API endpoints).
- **`tests/conftest.py`** – Shared pytest fixtures.

## Fixtures

The test suite uses the following fixtures (defined in `conftest.py`):

### `app`
- **Scope**: session
- **Description**: Creates a Flask application with a temporary SQLite database.
- **Configuration**: Patches `bafser_config` to use a test database path and disables CSRF protection.

### `db_sess`
- **Scope**: function
- **Description**: Provides a fresh database session for each test, with automatic rollback after the test.
- **Dependencies**: `app` (ensures database is initialized).

### `client`
- **Scope**: function
- **Description**: Flask test client for making HTTP requests.

### `authenticated_client`
- **Scope**: function
- **Description**: Test client with a logged‑in regular user (role "user").
- **Creates**: A user with login `"test_user"` and sets a JWT token in cookies.

### `admin_client`
- **Scope**: function
- **Description**: Test client with a logged‑in admin user (role "admin").
- **Creates**: A user with login `"test_admin"` and admin permissions.

### `test_user` / `test_admin`
- **Scope**: function
- **Description**: The `User` objects created for the authenticated clients.

## Running Tests

### Basic Test Run
```bash
pytest
```

### With Coverage
```bash
pytest --cov=blueprints --cov=data --cov=utils --cov-report=term-missing
```

### Generate HTML Report
```bash
pytest --cov=blueprints --cov=data --cov=utils --cov-report=html
```
Open `htmlcov/index.html` in a browser.

### Run Only Unit Tests
```bash
pytest tests/unit/
```

### Run Only Integration Tests
```bash
pytest tests/integration/
```

### Run a Specific Test File
```bash
pytest tests/integration/test_auth.py -v
```

## Coverage Target

The project aims for **≥80% code coverage** across the `blueprints`, `data`, and `utils` modules.

Current coverage (as of latest run):
- **blueprints**: ~80%
- **data**: ~85%
- **utils**: ~90%

To see which lines are uncovered, run:
```bash
pytest --cov=blueprints --cov=data --cov=utils --cov-report=term-missing
```

## Writing New Tests

### Unit Tests
- Test model creation, updates, deletions, and validation.
- Use the `db_sess` fixture to interact with the database.
- Example:
```python
def test_recipe_creation(db_sess):
    recipe = Recipe.new(title="Test", ...)
    db_sess.add(recipe)
    db_sess.commit()
    assert recipe.id is not None
```

### Integration Tests
- Use `authenticated_client` or `admin_client` to make API requests.
- Assert HTTP status codes, response JSON, and side effects.
- Example:
```python
def test_create_recipe(authenticated_client):
    resp = authenticated_client.post("/api/recipes", json={...})
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["title"] == "Test"
```

## Mocking and Patching

- Use `unittest.mock` to patch external dependencies (e.g., `datetime.now`).
- For Bafser‑specific components (like `Roles.ROLES`), patch in `conftest.py` to ensure test‑friendly permissions.

## Database Isolation

Each test runs inside a transaction that is rolled back after the test, ensuring no cross‑test contamination. The database itself is a temporary SQLite file created once per test session.

## Linting and Type Checking in CI

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs three jobs:

1. **test** – Runs pytest with coverage.
2. **lint** – Runs black, isort, flake8.
3. **type‑check** – Runs pyright.

To run these locally:
```bash
black --check blueprints data utils
isort --check-only blueprints data utils
flake8 blueprints data utils
pyright blueprints data utils
```

## Troubleshooting

### "Operation not permitted" errors
- Ensure the test user has the required permissions. The `conftest.py` patches `Roles.ROLES` to grant all operations to the "user" role.

### Database session errors
- Use `db_sess` fixture; avoid mixing sessions from different fixtures.

### JWT token expiration
- Tokens are set with a long expiration for tests. If you encounter 401 errors, check that the token is being sent correctly (the fixture sets it in cookies).

### Coverage missing lines
- Some lines may be unreachable due to defensive coding (e.g., `JsonObj` validation preventing `ValueError`). These are acceptable as dead code.

## Further Reading

- [pytest documentation](https://docs.pytest.org/)
- [Bafser framework documentation](https://bafser.readthedocs.io/)
- [SQLAlchemy testing](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#joining-a-session-into-an-external-transaction)
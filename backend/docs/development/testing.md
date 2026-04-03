# Testing

The project includes a comprehensive test suite with unit and integration tests, achieving >80% code coverage.

## Running Tests

### Install Development Dependencies

Make sure you have installed the development dependencies:

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

To run the entire test suite with coverage:

```bash
pytest --cov=blueprints --cov=data --cov=utils --cov-report=term-missing
```

### Run Specific Test Categories

- **Unit tests** (data models):
  ```bash
  pytest tests/unit/
  ```

- **Integration tests** (API endpoints):
  ```bash
  pytest tests/integration/
  ```

- **Single test file**:
  ```bash
  pytest tests/integration/test_recipe.py
  ```

- **Single test class or method**:
  ```bash
  pytest tests/integration/test_recipe.py::TestRecipeEndpoints::test_list_recipes
  ```

## Test Structure

- `tests/unit/` – Unit tests for data models and business logic.
- `tests/integration/` – Integration tests that simulate HTTP requests to the API.
- `tests/conftest.py` – Shared pytest fixtures (database session, test client, authenticated clients).

## Coverage Report

The test suite aims to maintain high code coverage. To generate an HTML coverage report:

```bash
pytest --cov=blueprints --cov=data --cov=utils --cov-report=html
```

Open `htmlcov/index.html` in a browser to explore the coverage.

Current coverage targets (as of latest run):

- **blueprints**: ~80%
- **data**: ~85%
- **utils**: ~90%

## Writing Tests

### Unit Tests

Unit tests should focus on a single class or function. Example:

```python
def test_recipe_creation(db_sess):
    """Test that a recipe can be created."""
    user = User.get_by_login(db_sess, "admin")
    recipe = Recipe.new(
        title="Test Recipe",
        description="Test description",
        active_time=30,
        total_time=60,
        difficulty=3,
        author=user,
        category_id=1,
    )
    assert recipe.id is not None
    assert recipe.title == "Test Recipe"
```

### Integration Tests

Integration tests use the Flask test client to simulate HTTP requests. Example:

```python
def test_list_recipes(client, db_sess):
    """GET /api/recipes returns list."""
    # Create a recipe
    admin = User.get_by_login(db_sess, "admin")
    Recipe.new(
        title="Test Recipe",
        description="Test",
        active_time=30,
        total_time=60,
        difficulty=3,
        author=admin,
        category_id=1,
    )
    response = client.get("/api/recipes")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) >= 1
```

### Fixtures

Key fixtures available in `conftest.py`:

- `db_sess`: Database session (rolled back after each test).
- `client`: Flask test client (unauthenticated).
- `authenticated_client`: Test client with a logged‑in regular user.
- `admin_client`: Test client with a logged‑in admin user.

## Continuous Integration

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push and pull request, executing:

1. **Test**: Runs pytest with coverage.
2. **Lint**: Runs black, isort, flake8.
3. **Type Check**: Runs pyright.

Ensure all checks pass before merging.
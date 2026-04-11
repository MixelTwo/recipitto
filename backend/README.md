# Bafser Recipe Backend

A Flask-based backend for a recipe management application, built with the Bafser framework.

## Features

- User authentication (JWT)
- Recipe CRUD with categories, ingredients, steps, images
- Ratings, comments, favorites
- Search with filters
- Role-based permissions
- Soft delete and audit logging

## Development Setup

### Prerequisites

- Python 3.11+
- SQLite (development) or PostgreSQL (production)

### Installation

1. Clone the repository.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and adjust settings.
5. Initialize the database:
   ```bash
   python -m utils.init_db
   ```
6. Run the development server:
   ```bash
   python main.py
   ```

## Testing

The project includes a comprehensive test suite with unit and integration tests, achieving >80% code coverage.

### Running Tests

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run tests with coverage:

```bash
pytest --cov=blueprints --cov=data --cov=utils --cov-report=term-missing
```

To run specific test categories:

- Unit tests: `pytest tests/unit/`
- Integration tests: `pytest tests/integration/`

### Linting and Formatting

The project uses `black`, `isort`, `flake8`, and `pyright` for code quality.

- Format code: `black blueprints data utils`
- Sort imports: `isort blueprints data utils`
- Lint: `flake8 blueprints data utils`
- Type check: `pyright blueprints data utils`

Configuration is in `pyproject.toml`.

### Continuous Integration

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push and pull request, executing:

1. **Test**: Runs pytest with coverage.
2. **Lint**: Runs black, isort, flake8.
3. **Type Check**: Runs pyright.

## Project Structure

- `blueprints/` – Flask blueprints (API endpoints)
- `data/` – SQLAlchemy models and business logic
- `utils/` – Utilities (database initialization, search normalization)
- `tests/` – Test suite
  - `tests/unit/` – Unit tests for data models
  - `tests/integration/` – Integration tests for API endpoints
- `alembic/` – Database migrations (if used)

## Documentation

The project uses **MkDocs** with **mkdocstrings** for automatic API documentation generation.

### Building Documentation

Install documentation dependencies (already included in `requirements-dev.txt`):

```bash
pip install -r requirements-dev.txt
```

Build the static site:

```bash
mkdocs build
```

The generated HTML files will be placed in the `site/` directory.

### Serving Documentation Locally

To preview the documentation with live reload:

```bash
mkdocs serve
```

Then open `http://localhost:8000` in your browser.

### Documentation Structure

- **Home**: Overview and quick start.
- **API Reference**: Auto‑generated documentation for all blueprints and data models.
- **Development**: Setup, testing, and database guides.

The documentation source files are located in the `docs/` directory, and the configuration is in `mkdocs.yml`.

## Coverage Report

Current coverage (as of latest run):

- **blueprints**: ~80%
- **data**: ~85%
- **utils**: ~90%

To generate an HTML report:

```bash
pytest --cov=blueprints --cov=data --cov=utils --cov-report=html
```

Open `htmlcov/index.html` in a browser.

## Contributing

1. Write tests for new features.
2. Ensure all tests pass (`pytest`).
3. Format code with black and isort.
4. Verify linting and type checking.
5. Update documentation as needed.

## License

MIT
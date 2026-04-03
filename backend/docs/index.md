# Bafser Recipe Backend

A Flask-based backend for a recipe management application, built with the Bafser framework.

## Features

- User authentication (JWT)
- Recipe CRUD with categories, ingredients, steps, images
- Ratings, comments, favorites
- Search with filters
- Role-based permissions
- Soft delete and audit logging

## Quick Start

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

## Documentation Structure

This documentation is organized into the following sections:

- **API Reference**: Detailed documentation of all API endpoints and data models.
- **Development**: Guides for setting up the development environment, testing, and database management.

## API Overview

The backend provides a RESTful API with the following main resources:

- **Authentication**: Login, logout, and current user retrieval.
- **Recipes**: Full CRUD operations for recipes.
- **Users**: User profile management.
- **Comments**: Commenting on recipes.
- **Ratings**: Rating recipes (1‑5 stars).
- **Favorites**: Bookmarking recipes.
- **Search**: Searching recipes with filters.

All API endpoints are prefixed with `/api/` and return JSON responses.

## Technology Stack

- **Framework**: Flask with Bafser extensions
- **Database**: SQLAlchemy (SQLite for development, PostgreSQL for production)
- **Authentication**: JWT (JSON Web Tokens) with HTTP‑only cookies
- **Testing**: pytest with coverage
- **Documentation**: MkDocs with mkdocstrings (this site)

## Getting Help

If you encounter issues or have questions, please check the [GitHub repository](https://github.com/your-org/recipe-backend) or open an issue.

## License

MIT License
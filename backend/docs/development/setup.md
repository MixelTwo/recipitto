# Development Setup

This guide explains how to set up the development environment for the Bafser Recipe Backend.

## Prerequisites

- Python 3.11 or newer
- SQLite (for development) or PostgreSQL (for production)
- Git

## Step 1: Clone the Repository

```bash
git clone https://github.com/your-org/recipe-backend.git
cd recipe-backend
```

## Step 2: Create a Virtual Environment

### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux
```bash
python -m venv venv
source venv/bin/activate
```

## Step 3: Install Dependencies

Install the production dependencies:

```bash
pip install -r requirements.txt
```

For development, also install the development dependencies:

```bash
pip install -r requirements-dev.txt
```

## Step 4: Configure Environment Variables

Copy the example environment file:

```bash
copy .env.example .env   # Windows
cp .env.example .env     # macOS / Linux
```

Edit `.env` and adjust the settings as needed. The most important variables are:

- `DATABASE_URL`: Connection string for the database (defaults to SQLite)
- `SECRET_KEY`: Secret key for JWT signing
- `DEV_MODE`: Set to `true` for development

## Step 5: Initialize the Database

Run the database initialization script:

```bash
python -m utils.init_db
```

This creates the SQLite database file and populates it with initial data (admin user, categories, etc.).

## Step 6: Run the Development Server

Start the Flask development server:

```bash
python main.py
```

The server will be available at `http://localhost:5000`.

## Step 7: Verify Installation

Open your browser and navigate to `http://localhost:5000/api`. If the API is running, you should see a welcome message (in development mode) or a 404 (in production mode).

You can also test the API with curl:

```bash
curl http://localhost:5000/api/recipes
```

## Next Steps

- Read the [Testing](testing.md) guide to run the test suite.
- Explore the [API Reference](../api/blueprints/recipe.md) for endpoint documentation.
- Check the [Database](database.md) guide for migration and seeding information.
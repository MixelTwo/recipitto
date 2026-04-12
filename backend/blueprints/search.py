from typing import TypedDict

from bafser import doc_api, use_db_sess
from flask import Blueprint, request
from sqlalchemy import distinct, func
from sqlalchemy.orm import Session

from data.rating import Rating
from data.recipe import Recipe, RecipeDict, RecipeStatus
from data.recipe_ingredient import RecipeIngredient
from utils import normalize_for_search

bp = Blueprint("search", __name__)


class SearchRecipesResponse(TypedDict):
    """Response schema for recipe search.

    Attributes:
        total: Total number of matching recipes (ignoring pagination).
        page: Current page number (1‑based).
        per_page: Number of recipes per page.
        results: List of recipe objects for the current page.
    """

    total: int
    page: int
    per_page: int
    results: list[RecipeDict]


@bp.get("/api/search/recipes")
@doc_api(res=SearchRecipesResponse, desc="Search recipes with filters and sorting")
@use_db_sess
def search_recipes(db_sess: Session) -> SearchRecipesResponse:
    """Search published recipes with advanced filtering, sorting, and pagination.

    Supported query parameters:
        q (str): Text search in recipe titles (case‑insensitive substring).
        category_id (int): Filter by recipe category ID.
        author_id (int): Filter by author ID.
        difficulty (int): Filter by difficulty level (1‑5).
        max_active_time (int): Filter by maximum active preparation time (minutes).
        max_total_time (int): Filter by maximum total time (minutes).
        min_rating (float): Filter by minimum average rating (1.0‑5.0).
        ingredients_include (list[int]): Filter recipes that contain ALL of the given ingredient IDs.
        ingredients_exclude (list[int]): Exclude recipes that contain ANY of the given ingredient IDs.
        sort_by (str): Sort field: 'relevance', 'rating', 'date', 'active_time', 'total_time', 'difficulty'.
        sort_order (str): Sort direction: 'asc' or 'desc'.
        page (int): Page number (1‑based). Default 1.
        per_page (int): Number of recipes per page. Default 20.
        include_drafts (bool): If true, include draft recipes alongside published ones. Default false.

    Args:
        db_sess: Database session (injected by @use_db_sess).

    Returns:
        SearchRecipesResponse: Dictionary with total count, pagination metadata, and recipe results.

    Note:
        By default only recipes with status 'published' are returned.
        If include_drafts is true, both 'published' and 'draft' recipes are included.
        Relevance sorting currently defaults to recipe ID (placeholder).
    """
    # Parse query parameters
    query = request.args.get("q", "").strip()
    category_id = request.args.get("category_id", type=int)
    author_id = request.args.get("author_id", type=int)
    difficulty = request.args.get("difficulty", type=int)  # 1-5
    max_active_time = request.args.get("max_active_time", type=int)
    max_total_time = request.args.get("max_total_time", type=int)
    min_rating = request.args.get("min_rating", type=float)
    ingredients_include = request.args.getlist("ingredients_include")  # list of ingredient IDs
    ingredients_exclude = request.args.getlist("ingredients_exclude")
    sort_by = request.args.get("sort_by", "relevance")  # relevance, rating, date, active_time, total_time, difficulty
    sort_order = request.args.get("sort_order", "desc")  # asc, desc
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    include_drafts = request.args.get("include_drafts", default=False, type=bool)

    # Start building query
    if include_drafts:
        q = Recipe.query2().filter(Recipe.status.in_([RecipeStatus.PUBLISHED, RecipeStatus.DRAFT]))
    else:
        q = Recipe.query2().filter(Recipe.status == RecipeStatus.PUBLISHED)

    # Text search on title
    if query:
        normalized_query = normalize_for_search(query)
        like_pattern = f"%{normalized_query}%"
        q = q.filter(Recipe.title_normalized.like(like_pattern))

    # Filter by category
    if category_id:
        q = q.filter(Recipe.category_id == category_id)

    # Filter by author
    if author_id:
        q = q.filter(Recipe.author_id == author_id)

    # Filter by difficulty
    if difficulty:
        q = q.filter(Recipe.difficulty == difficulty)

    # Filter by active time
    if max_active_time:
        q = q.filter(Recipe.active_time <= max_active_time)

    # Filter by total time
    if max_total_time:
        q = q.filter(Recipe.total_time <= max_total_time)

    # Filter by rating (average rating)
    if min_rating:
        subq = (
            db_sess.query(Rating.recipe_id, func.avg(Rating.rating).label("avg_rating"))
            .group_by(Rating.recipe_id)
            .having(func.avg(Rating.rating) >= min_rating)
            .subquery()
        )
        q = q.join(subq, Recipe.id == subq.c.recipe_id)

    # Filter by ingredients (include)
    if ingredients_include:
        # Recipes that contain ALL of these ingredients
        ing_ids = [int(i) for i in ingredients_include]
        subq = (
            db_sess.query(RecipeIngredient.recipe_id)
            .filter(RecipeIngredient.ingredient_id.in_(ing_ids))
            .group_by(RecipeIngredient.recipe_id)
            .having(func.count(distinct(RecipeIngredient.ingredient_id)) == len(ing_ids))
            .subquery()
        )
        q = q.join(subq, Recipe.id == subq.c.recipe_id)

    # Filter by ingredients (exclude)
    if ingredients_exclude:
        ing_ids = [int(i) for i in ingredients_exclude]
        subq = db_sess.query(RecipeIngredient.recipe_id).filter(RecipeIngredient.ingredient_id.in_(ing_ids))
        q = q.filter(~Recipe.id.in_(subq))

    # Sorting
    if sort_by == "rating":
        # Need to join with ratings average
        subq = db_sess.query(Rating.recipe_id, func.avg(Rating.rating).label("avg_rating")).group_by(Rating.recipe_id).subquery()
        q = q.outerjoin(subq, Recipe.id == subq.c.recipe_id)
        order_col = subq.c.avg_rating
        if sort_order == "desc":
            q = q.order_by(order_col.desc().nulls_last())
        else:
            q = q.order_by(order_col.asc().nulls_last())
    elif sort_by == "date":
        order_col = Recipe.created_at
    elif sort_by == "active_time":
        order_col = Recipe.active_time
    elif sort_by == "total_time":
        order_col = Recipe.total_time
    elif sort_by == "difficulty":
        order_col = Recipe.difficulty
    else:  # relevance (default) - we'll sort by id as placeholder
        order_col = Recipe.id

    if sort_by != "rating":
        if sort_order == "desc":
            q = q.order_by(order_col.desc())
        else:
            q = q.order_by(order_col.asc())

    # Pagination
    total = q.count()
    q = q.offset((page - 1) * per_page).limit(per_page)

    recipes = q.all()

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "results": [recipe.get_dict() for recipe in recipes],
    }

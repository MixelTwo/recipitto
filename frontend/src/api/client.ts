import { query, QueryCache } from "./api.js";
import { fetchJsonPost, fetchJsonGet, fetchPost, fetchJsonDelete, fetchJsonPatch, FetchError } from "../littleLib.js";
import
{
    AuthRequest,
    User,
    RecipeDict,
    RecipeListResponse,
    RecipeRequest,
    RecipeResponse,
    RecipeUpdateRequest,
    CommentDict,
    CommentRequest,
    FavoriteDict,
    IngredientCategoryDict,
    IngredientCategoryRequest,
    IngredientDict,
    IngredientRequest,
    RecipeCategoryDict,
    RecipeCategoryRequest,
    RecipeImageDict,
    RecipeImageRequest,
    RecipeIngredientDict,
    RecipeIngredientRequest,
    RecipeIngredientUpdateRequest,
    RatingRequest,
    RatingResponse,
    RatingStatsResponse,
    RecipeStepDict,
    StepRequest,
    StepUpdateRequest,
    SearchQuery,
    SearchResponse,
    TRecipeStatus,
} from "./types.js";


// Auth
export const query_auth = () => query<User, [string, string]>(
    null,
    async (login: string, password: string) =>
    {
        const r = await fetchJsonPost<User>("/api/auth", { login, password });
        QueryCache.set("user", r);
        return r;
    }
);

export const query_logout = () => query<boolean, []>(
    null,
    async () =>
    {
        await fetchPost("/api/logout");
        QueryCache.del("user");
        return true;
    }
);

export const query_user = () => query<User, []>(
    "user",
    async () =>
    {
        const user = await fetchJsonGet<User>("/api/user");
        return user;
    },
    []
);

// Recipes
export const query_recipes = (params?: {
    category_id?: number;
    author_id?: number;
    difficulty?: number;
    max_active_time?: number;
    max_total_time?: number;
    min_rating?: number;
    sort_by?: "relevance" | "rating" | "date" | "active_time" | "total_time" | "difficulty";
    sort_order?: "asc" | "desc";
    page?: number;
    per_page?: number;
}) => query<RecipeListResponse, []>(
    "recipes",
    async () =>
    {
        const url = new URL("/api/recipes", window.location.origin);
        if (params)
        {
            const search = new URLSearchParams();
            if (params.category_id !== undefined) search.append("category_id", params.category_id.toString());
            if (params.author_id !== undefined) search.append("author_id", params.author_id.toString());
            if (params.difficulty !== undefined) search.append("difficulty", params.difficulty.toString());
            if (params.max_active_time !== undefined) search.append("max_active_time", params.max_active_time.toString());
            if (params.max_total_time !== undefined) search.append("max_total_time", params.max_total_time.toString());
            if (params.min_rating !== undefined) search.append("min_rating", params.min_rating.toString());
            if (params.sort_by) search.append("sort_by", params.sort_by);
            if (params.sort_order) search.append("sort_order", params.sort_order);
            if (params.page !== undefined) search.append("page", params.page.toString());
            if (params.per_page !== undefined) search.append("per_page", params.per_page.toString());
            url.search = search.toString();
        }
        const recipes = await fetchJsonGet<RecipeDict[]>(url.toString());
        return recipes;
    },
    []
);

export const query_recipe_by_id = (id: number) => query<RecipeResponse, []>(
    `recipe_${id}`,
    async () =>
    {
        const recipe = await fetchJsonGet<RecipeDict>(`/api/recipes/${id}`);
        return recipe;
    },
    []
);

export const mutate_create_recipe = () => query<RecipeResponse, [RecipeRequest]>(
    null,
    async (data: RecipeRequest) =>
    {
        const recipe = await fetchJsonPost<RecipeDict>("/api/recipes", data);
        return recipe;
    }
);

export const mutate_update_recipe = (id: number) => query<RecipeResponse, [RecipeUpdateRequest]>(
    null,
    async (data: RecipeUpdateRequest) =>
    {
        const res = await fetch(`/api/recipes/${id}`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        if (!res.ok)
        {
            let msg = "";
            try { msg = (await res.json() as { msg: string }).msg; } catch { }
            throw new FetchError(msg, res.status);
        }
        const recipe = await res.json() as RecipeDict;
        return recipe;
    }
);

export const mutate_delete_recipe = (id: number) => query<boolean, []>(
    null,
    async () =>
    {
        await fetchJsonDelete(`/api/recipes/${id}`);
        return true;
    }
);

// Recipe subresources

export const query_recipe_comments = (recipe_id: number) => query<CommentDict[], []>(
    `recipe_${recipe_id}_comments`,
    async () =>
    {
        const comments = await fetchJsonGet<CommentDict[]>(`/api/recipes/${recipe_id}/comments`);
        return comments;
    },
    []
);

export const mutate_create_comment = (recipe_id: number) => query<CommentDict, [string]>(
    null,
    async (text: string) =>
    {
        const comment = await fetchJsonPost<CommentDict>(`/api/recipes/${recipe_id}/comments`, { text });
        return comment;
    }
);

export const mutate_update_comment = (comment_id: number) => query<CommentDict, [string]>(
    null,
    async (text: string) =>
    {
        const comment = await fetchJsonPatch<CommentDict>(`/api/comments/${comment_id}`, { text });
        return comment;
    }
);

export const mutate_delete_comment = (comment_id: number) => query<boolean, []>(
    null,
    async () =>
    {
        await fetchJsonDelete(`/api/comments/${comment_id}`);
        return true;
    }
);

// Favorites
export const query_recipe_favorite = (recipe_id: number) => query<{ favorite: FavoriteDict | null; favorited: boolean }, []>(
    `recipe_${recipe_id}_favorite`,
    async () =>
    {
        const result = await fetchJsonGet<{ favorite: FavoriteDict | null; favorited: boolean }>(`/api/recipes/${recipe_id}/favorite`);
        return result;
    },
    []
);

export const mutate_add_favorite = (recipe_id: number) => query<FavoriteDict, []>(
    null,
    async () =>
    {
        const fav = await fetchJsonPost<FavoriteDict>(`/api/recipes/${recipe_id}/favorite`);
        return fav;
    }
);

export const mutate_remove_favorite = (recipe_id: number) => query<boolean, []>(
    null,
    async () =>
    {
        await fetchJsonDelete(`/api/recipes/${recipe_id}/favorite`);
        return true;
    }
);

// Categories
export const query_recipe_categories = () => query<RecipeCategoryDict[], []>(
    "recipe_categories",
    async () =>
    {
        const categories = await fetchJsonGet<RecipeCategoryDict[]>("/api/recipe-categories");
        return categories;
    },
    []
);

export const query_ingredient_categories = () => query<IngredientCategoryDict[], []>(
    "ingredient_categories",
    async () =>
    {
        const categories = await fetchJsonGet<IngredientCategoryDict[]>("/api/ingredient-categories");
        return categories;
    },
    []
);

// Ingredients
export const query_ingredients = () => query<IngredientDict[], []>(
    "ingredients",
    async () =>
    {
        const ingredients = await fetchJsonGet<IngredientDict[]>("/api/ingredients");
        return ingredients;
    },
    []
);

// Search
export const query_search_recipes = (params: SearchQuery) => query<SearchResponse, []>(
    "search_recipes",
    async () =>
    {
        const url = new URL("/api/search/recipes", window.location.origin);
        const search = new URLSearchParams();
        if (params.q !== undefined) search.append("q", params.q);
        if (params.category_id !== undefined) search.append("category_id", params.category_id.toString());
        if (params.author_id !== undefined) search.append("author_id", params.author_id.toString());
        if (params.difficulty !== undefined) search.append("difficulty", params.difficulty.toString());
        if (params.max_active_time !== undefined) search.append("max_active_time", params.max_active_time.toString());
        if (params.max_total_time !== undefined) search.append("max_total_time", params.max_total_time.toString());
        if (params.min_rating !== undefined) search.append("min_rating", params.min_rating.toString());
        if (params.ingredients_include)
        {
            params.ingredients_include.forEach(id => search.append("ingredients_include", id.toString()));
        }
        if (params.ingredients_exclude)
        {
            params.ingredients_exclude.forEach(id => search.append("ingredients_exclude", id.toString()));
        }
        if (params.sort_by) search.append("sort_by", params.sort_by);
        if (params.sort_order) search.append("sort_order", params.sort_order);
        if (params.page !== undefined) search.append("page", params.page.toString());
        if (params.per_page !== undefined) search.append("per_page", params.per_page.toString());
        url.search = search.toString();
        const response = await fetchJsonGet<SearchResponse>(url.toString());
        return response;
    },
    []
);

// Note: More endpoints can be added as needed.
import { query, QueryCache } from "./api.js";
import { mockFetch } from "../utils.js";
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

// Mock mapping of category_id to category name
const categoryMap: Record<number, string> = {
    1: "Завтраки",
    2: "Супы",
    3: "Основные блюда",
    4: "Салаты",
    5: "Выпечка",
    6: "Десерты",
    7: "Напитки",
    8: "Соусы",
};

// Helper to generate mock data based on endpoint
// For now, we'll use simple mocks; later can be replaced with real fetch.

// Auth
export const query_auth = () => query<User, [string, string]>(
    null,
    async (login: string, password: string) =>
    {
        const r = await mockFetch(
            "POST /api/auth",
            {
                avatar: null,
                id: 1,
                login: "user1",
                name: "Вася И.",
                operations: ["admin", "recipe_view", "recipe_create", "recipe_update", "recipe_delete", "recipe_manage_own", "recipe_step_view", "recipe_step_create", "recipe_step_update", "recipe_step_delete", "recipe_ingredient_view", "recipe_ingredient_create", "recipe_ingredient_update", "recipe_ingredient_delete", "recipe_image_view", "recipe_image_create", "recipe_image_delete", "comment_view", "comment_create", "comment_update", "comment_delete", "rating_view", "rating_create", "rating_update", "rating_delete", "favorite_view", "favorite_create", "favorite_delete", "search_recipes", "recipe_category_view", "ingredient_category_view", "ingredient_view"],
                reg_date: "08.03.2026T15:47:22",
                roles: ["user"]
            } as User,
            { login, password }
        );
        QueryCache.set("user", r);
        return r;
    }
);

export const query_logout = () => query<boolean, []>(
    null,
    async () =>
    {
        await mockFetch("POST /api/logout", {});
        QueryCache.del("user");
        return true;
    }
);

export const query_user = () => query<User, []>(
    "user",
    async () =>
    {
        await mockFetch("GET /api/user", {});
        // Simulate unauthorized
        throw new Error("Not authorized");
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
        // Mock data using images from wwwroot/mocks/
        const mockRecipes: RecipeDict[] = [
            {
                active_time: 30,
                author: "Chef John",
                category: "Основные блюда",
                created_at: "2026-03-20T10:00:00Z",
                description: "A delicious pasta dish with fresh tomatoes.",
                difficulty: 3,
                id: 1,
                main_image: "/mocks/margherita-pizza.jpg",
                published_at: "2026-03-20T10:00:00Z",
                rating: 4.5,
                status: "published",
                title: "Spaghetti Carbonara",
                total_time: 45,
                vote_count: 120,
            },
            {
                active_time: 15,
                author: "Jane Doe",
                category: "Салаты",
                created_at: "2026-03-21T12:00:00Z",
                description: "Fresh green salad with vinaigrette.",
                difficulty: 1,
                id: 2,
                main_image: "/mocks/quinoa-salad.jpg",
                published_at: "2026-03-21T12:00:00Z",
                rating: 4.2,
                status: "published",
                title: "Green Salad",
                total_time: 15,
                vote_count: 89,
            },
            {
                active_time: 10,
                author: "Breakfast Lover",
                category: "Завтраки",
                created_at: "2026-03-22T08:00:00Z",
                description: "Creamy avocado on toasted bread with a sprinkle of chili flakes.",
                difficulty: 1,
                id: 3,
                main_image: "/mocks/avocado-toast.jpg",
                published_at: "2026-03-22T08:00:00Z",
                rating: 4.8,
                status: "published",
                title: "Avocado Toast",
                total_time: 10,
                vote_count: 200,
            },
            {
                active_time: 45,
                author: "Dessert Master",
                category: "Десерты",
                created_at: "2026-03-22T14:00:00Z",
                description: "Light and airy chocolate soufflé with a molten center.",
                difficulty: 4,
                id: 4,
                main_image: "/mocks/chocolate-souffle.jpg",
                published_at: "2026-03-22T14:00:00Z",
                rating: 4.9,
                status: "published",
                title: "Chocolate Soufflé",
                total_time: 60,
                vote_count: 150,
            },
            {
                active_time: 40,
                author: "Thai Chef",
                category: "Основные блюда",
                created_at: "2026-03-22T18:00:00Z",
                description: "Aromatic green curry with coconut milk, vegetables, and chicken.",
                difficulty: 3,
                id: 5,
                main_image: "/mocks/thai-green-curry.jpg",
                published_at: "2026-03-22T18:00:00Z",
                rating: 4.7,
                status: "published",
                title: "Thai Green Curry",
                total_time: 50,
                vote_count: 180,
            },
            {
                active_time: 20,
                author: "Quick Cook",
                category: "Быстрые блюда",
                created_at: "2026-03-22T12:00:00Z",
                description: "Simple yet delicious pizza with fresh basil and mozzarella.",
                difficulty: 2,
                id: 6,
                main_image: null,
                published_at: "2026-03-22T12:00:00Z",
                rating: 4.3,
                status: "published",
                title: "Margherita Pizza",
                total_time: 30,
                vote_count: 95,
            },
        ];
        return mockRecipes;
    },
    []
);

export const query_recipe_by_id = (id: number) => query<RecipeResponse, []>(
    `recipe_${id}`,
    async () =>
    {
        // Mock recipes mapping
        const mockRecipes: Record<number, RecipeDict> = {
            1: {
                active_time: 30,
                author: "Chef John",
                category: "Основные блюда",
                created_at: "2026-03-20T10:00:00Z",
                description: "A delicious pasta dish with fresh tomatoes.",
                difficulty: 3,
                id: 1,
                main_image: "/mocks/margherita-pizza.jpg",
                published_at: "2026-03-20T10:00:00Z",
                rating: 4.5,
                status: "published",
                title: "Spaghetti Carbonara",
                total_time: 45,
                vote_count: 120,
            },
            2: {
                active_time: 15,
                author: "Jane Doe",
                category: "Салаты",
                created_at: "2026-03-21T12:00:00Z",
                description: "Fresh green salad with vinaigrette.",
                difficulty: 1,
                id: 2,
                main_image: "/mocks/quinoa-salad.jpg",
                published_at: "2026-03-21T12:00:00Z",
                rating: 4.2,
                status: "published",
                title: "Green Salad",
                total_time: 15,
                vote_count: 89,
            },
            3: {
                active_time: 10,
                author: "Breakfast Lover",
                category: "Завтраки",
                created_at: "2026-03-22T08:00:00Z",
                description: "Creamy avocado on toasted bread with a sprinkle of chili flakes.",
                difficulty: 1,
                id: 3,
                main_image: "/mocks/avocado-toast.jpg",
                published_at: "2026-03-22T08:00:00Z",
                rating: 4.8,
                status: "published",
                title: "Avocado Toast",
                total_time: 10,
                vote_count: 200,
            },
            4: {
                active_time: 45,
                author: "Dessert Master",
                category: "Десерты",
                created_at: "2026-03-22T14:00:00Z",
                description: "Light and airy chocolate soufflé with a molten center.",
                difficulty: 4,
                id: 4,
                main_image: "/mocks/chocolate-souffle.jpg",
                published_at: "2026-03-22T14:00:00Z",
                rating: 4.9,
                status: "published",
                title: "Chocolate Soufflé",
                total_time: 60,
                vote_count: 150,
            },
            5: {
                active_time: 40,
                author: "Thai Chef",
                category: "Основные блюда",
                created_at: "2026-03-22T18:00:00Z",
                description: "Aromatic green curry with coconut milk, vegetables, and chicken.",
                difficulty: 3,
                id: 5,
                main_image: "/mocks/thai-green-curry.jpg",
                published_at: "2026-03-22T18:00:00Z",
                rating: 4.7,
                status: "published",
                title: "Thai Green Curry",
                total_time: 50,
                vote_count: 180,
            },
            6: {
                active_time: 20,
                author: "Quick Cook",
                category: "Быстрые блюда",
                created_at: "2026-03-22T12:00:00Z",
                description: "Simple yet delicious pizza with fresh basil and mozzarella.",
                difficulty: 2,
                id: 6,
                main_image: null,
                published_at: "2026-03-22T12:00:00Z",
                rating: 4.3,
                status: "published",
                title: "Margherita Pizza",
                total_time: 30,
                vote_count: 95,
            },
        };
        const recipe = mockRecipes[id];
        if (!recipe)
        {
            // Fallback to a generic recipe
            return {
                active_time: 30,
                author: "Unknown Chef",
                category: "Основные блюда",
                created_at: "2026-03-20T10:00:00Z",
                description: "A generic recipe.",
                difficulty: 2,
                id,
                main_image: null,
                published_at: "2026-03-20T10:00:00Z",
                rating: 3.5,
                status: "published",
                title: "Unknown Recipe",
                total_time: 45,
                vote_count: 0,
            };
        }
        return recipe;
    },
    []
);

export const mutate_create_recipe = () => query<RecipeResponse, [RecipeRequest]>(
    null,
    async (data: RecipeRequest) =>
    {
        const status: TRecipeStatus = data.status || "draft";
        const category = categoryMap[data.category_id] || "Unknown";
        const newRecipe: RecipeDict = {
            active_time: data.active_time,
            author: "Current User",
            category,
            created_at: new Date().toISOString(),
            description: data.description,
            difficulty: data.difficulty,
            id: Math.floor(Math.random() * 1000),
            main_image: null,
            published_at: status === "published" ? new Date().toISOString() : null,
            rating: 0,
            status,
            title: data.title,
            total_time: data.total_time,
            vote_count: 0,
        };
        return newRecipe;
    }
);

export const mutate_update_recipe = (id: number) => query<RecipeResponse, [RecipeUpdateRequest]>(
    null,
    async (data: RecipeUpdateRequest) =>
    {
        // In real app, we would PATCH
        const existing = await query_recipe_by_id(id).v.fetch();
        if (!existing)
        {
            throw new Error("Recipe not found");
        }
        const updated: RecipeDict = {
            ...existing,
            active_time: data.active_time ?? existing.active_time,
            category: data.category_id ? categoryMap[data.category_id] || existing.category : existing.category,
            description: data.description ?? existing.description,
            difficulty: data.difficulty ?? existing.difficulty,
            main_image: data.main_image_id !== undefined ? null : existing.main_image, // simplified
            status: data.status ?? existing.status,
            title: data.title ?? existing.title,
            total_time: data.total_time ?? existing.total_time,
        };
        return updated;
    }
);

export const mutate_delete_recipe = (id: number) => query<boolean, []>(
    null,
    async () =>
    {
        await mockFetch(`DELETE /api/recipes/${id}`, {});
        return true;
    }
);

// Recipe subresources

export const query_recipe_comments = (recipe_id: number) => query<CommentDict[], []>(
    `recipe_${recipe_id}_comments`,
    async () =>
    {
        return [
            {
                created_at: "2026-03-21T14:30:00Z",
                id: 1,
                recipe_id,
                text: "Great recipe!",
                user_id: 2,
            },
            {
                created_at: "2026-03-21T15:00:00Z",
                id: 2,
                recipe_id,
                text: "I added extra cheese, turned out amazing.",
                user_id: 3,
            },
        ];
    },
    []
);

export const mutate_create_comment = (recipe_id: number) => query<CommentDict, [string]>(
    null,
    async (text: string) =>
    {
        const newComment: CommentDict = {
            created_at: new Date().toISOString(),
            id: Math.floor(Math.random() * 1000),
            recipe_id,
            text,
            user_id: 1, // current user
        };
        return newComment;
    }
);

export const mutate_update_comment = (comment_id: number) => query<CommentDict, [string]>(
    null,
    async (text: string) =>
    {
        // Mock
        return {
            created_at: new Date().toISOString(),
            id: comment_id,
            recipe_id: 1,
            text,
            user_id: 1,
        };
    }
);

export const mutate_delete_comment = (comment_id: number) => query<boolean, []>(
    null,
    async () =>
    {
        await mockFetch(`DELETE /api/comments/${comment_id}`, {});
        return true;
    }
);

// Favorites
export const query_recipe_favorite = (recipe_id: number) => query<{ favorite: FavoriteDict | null; favorited: boolean }, []>(
    `recipe_${recipe_id}_favorite`,
    async () =>
    {
        return {
            favorite: null,
            favorited: false,
        };
    },
    []
);

export const mutate_add_favorite = (recipe_id: number) => query<FavoriteDict, []>(
    null,
    async () =>
    {
        const fav: FavoriteDict = {
            added_at: new Date().toISOString(),
            recipe_id,
            user_id: 1,
        };
        return fav;
    }
);

export const mutate_remove_favorite = (recipe_id: number) => query<boolean, []>(
    null,
    async () =>
    {
        await mockFetch(`DELETE /api/recipes/${recipe_id}/favorite`, {});
        return true;
    }
);

// Categories
export const query_recipe_categories = () => query<RecipeCategoryDict[], []>(
    "recipe_categories",
    async () =>
    {
        return [
            { id: 1, name: "Завтраки" },
            { id: 2, name: "Супы" },
            { id: 3, name: "Основные блюда" },
            { id: 4, name: "Салаты" },
            { id: 5, name: "Выпечка" },
            { id: 6, name: "Десерты" },
            { id: 7, name: "Напитки" },
            { id: 8, name: "Соусы" },
        ];
    },
    []
);

export const query_ingredient_categories = () => query<IngredientCategoryDict[], []>(
    "ingredient_categories",
    async () =>
    {
        return [
            { id: 1, name: "Овощи" },
            { id: 2, name: "Фрукты" },
            { id: 3, name: "Мясо" },
            { id: 4, name: "Молочные продукты" },
            { id: 5, name: "Зерновые" },
        ];
    },
    []
);

// Ingredients
export const query_ingredients = () => query<IngredientDict[], []>(
    "ingredients",
    async () =>
    {
        return [
            { id: 1, name: "Помидор", category: "Овощи" },
            { id: 2, name: "Лук", category: "Овощи" },
            { id: 3, name: "Курица", category: "Мясо" },
            { id: 4, name: "Молоко", category: "Молочные продукты" },
            { id: 5, name: "Мука", category: "Зерновые" },
        ];
    },
    []
);

// Search
export const query_search_recipes = (params: SearchQuery) => query<SearchResponse, []>(
    "search_recipes",
    async () =>
    {
        // Mock search results using images from wwwroot/mocks/
        const results: RecipeDict[] = [
            {
                active_time: 30,
                author: "Chef John",
                category: "Основные блюда",
                created_at: "2026-03-20T10:00:00Z",
                description: "A delicious pasta dish with fresh tomatoes.",
                difficulty: 3,
                id: 1,
                main_image: "/mocks/margherita-pizza.jpg",
                published_at: "2026-03-20T10:00:00Z",
                rating: 4.5,
                status: "published",
                title: "Spaghetti Carbonara",
                total_time: 45,
                vote_count: 120,
            },
            {
                active_time: 15,
                author: "Jane Doe",
                category: "Салаты",
                created_at: "2026-03-21T12:00:00Z",
                description: "Fresh green salad with vinaigrette.",
                difficulty: 1,
                id: 2,
                main_image: "/mocks/quinoa-salad.jpg",
                published_at: "2026-03-21T12:00:00Z",
                rating: 4.2,
                status: "published",
                title: "Green Salad",
                total_time: 15,
                vote_count: 89,
            },
            {
                active_time: 10,
                author: "Breakfast Lover",
                category: "Завтраки",
                created_at: "2026-03-22T08:00:00Z",
                description: "Creamy avocado on toasted bread with a sprinkle of chili flakes.",
                difficulty: 1,
                id: 3,
                main_image: "/mocks/avocado-toast.jpg",
                published_at: "2026-03-22T08:00:00Z",
                rating: 4.8,
                status: "published",
                title: "Avocado Toast",
                total_time: 10,
                vote_count: 200,
            },
        ];
        // Simulate pagination
        const page = params.page || 1;
        const per_page = params.per_page || 20;
        const start = (page - 1) * per_page;
        const paginatedResults = results.slice(start, start + per_page);
        return {
            page,
            per_page,
            results: paginatedResults,
            total: results.length,
        };
    },
    []
);

// Note: More endpoints can be added as needed.
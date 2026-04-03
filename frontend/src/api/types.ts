// Generated from api.json

export interface CommentDict
{
	created_at: string;
	id: number;
	recipe_id: number;
	text: string;
	user_id: number;
}

export interface FavoriteDict
{
	added_at: string;
	recipe_id: number;
	user_id: number;
}

export interface FavoriteWithRecipeDict
{
	added_at: string;
	recipe: RecipeDict;
}

export interface ImageJson
{
	data: string;
	name: string;
}

export interface IngredientCategoryDict
{
	id: number;
	name: string;
}

export interface IngredientDict
{
	category: string;
	id: number;
	name: string;
}

export interface RecipeCategoryDict
{
	id: number;
	name: string;
}

export interface RecipeDict
{
	active_time: number;
	author: string;
	category: string;
	category_id: number;
	created_at: string;
	description: string;
	difficulty: number;
	id: number;
	main_image: string | null;
	published_at: string | null;
	rating: number;
	status: TRecipeStatus;
	title: string;
	total_time: number;
	vote_count: number;
}

export interface RecipeImageDict
{
	id: number;
	image_id: number;
	image_path: string;
	recipe_id: number;
}

export interface RecipeIngredientDict
{
	ingredient_id: number;
	ingredient_name: string;
	quantity: number;
	recipe_id: number;
	unit: string;
}

export interface RecipeStepDict
{
	id: number;
	image: string | null;
	recipe_id: number;
	step_number: number;
	text: string;
}

// Enums
export type TRecipeStatus = "draft" | "published" | "deleted";

export enum UserOperations
{
	recipe_create = "recipe_create"
}

// Request/Response types for each endpoint

export interface AuthRequest
{
	login: string;
	password: string;
}

export interface User
{
	avatar: string | null;
	id: number;
	login: string;
	name: string;
	operations: string[];
	reg_date: string;
	roles: string[];
}

export interface CommentRequest
{
	text?: string;
}

export interface CommentResponse extends CommentDict { }

export interface FavoriteResponse extends FavoriteDict { }

export interface IngredientCategoryRequest
{
	name: string;
}

export interface IngredientCategoryResponse extends IngredientCategoryDict { }

export interface IngredientRequest
{
	category_id: number;
	name: string;
}

export interface IngredientResponse extends IngredientDict { }

export interface RecipeCategoryRequest
{
	name: string;
}

export interface RecipeCategoryResponse extends RecipeCategoryDict { }

export interface RecipeListResponse extends Array<RecipeDict> { }

export interface RecipeRequest
{
	active_time: number;
	category_id: number;
	description: string;
	difficulty: number;
	main_image?: ImageJson | null;
	status?: TRecipeStatus;
	title: string;
	total_time: number;
}

export interface RecipeResponse extends RecipeDict { }

export interface RecipeUpdateRequest
{
	active_time?: number;
	category_id?: number;
	description?: string;
	difficulty?: number;
	main_image?: ImageJson | null;
	status?: TRecipeStatus;
	title?: string;
	total_time?: number;
}

export interface RecipeImageRequest
{
	image: ImageJson;
}

export interface RecipeImageResponse extends RecipeImageDict { }

export interface RecipeIngredientRequest
{
	ingredient_id: number;
	quantity: number;
	unit: string;
}

export interface RecipeIngredientResponse extends RecipeIngredientDict { }

export interface RecipeIngredientUpdateRequest
{
	quantity?: number;
	unit?: string;
}

export interface RatingRequest
{
	rating: number;
}

export interface RatingResponse
{
	rating: number;
	recipe_id: number;
	user_id: number;
}

export interface RatingStatsResponse
{
	average: number;
	count: number;
	distribution: { [key: string]: number };
	recipe_id: number;
}

export interface StepRequest
{
	image?: ImageJson | null;
	step_number: number;
	text: string;
}

export interface StepResponse extends RecipeStepDict { }

export interface StepUpdateRequest
{
	image?: ImageJson | null;
	step_number?: number;
	text?: string;
}

export interface SearchQuery
{
	q?: string;
	category_id?: number;
	author_id?: number;
	difficulty?: number; // 1-5
	max_active_time?: number;
	max_total_time?: number;
	min_rating?: number;
	ingredients_include?: number[];
	ingredients_exclude?: number[];
	sort_by?: "relevance" | "rating" | "date" | "active_time" | "total_time" | "difficulty";
	sort_order?: "asc" | "desc";
	page?: number;
	per_page?: number;
}

export interface SearchResponse
{
	page: number;
	per_page: number;
	results: RecipeDict[];
	total: number;
}
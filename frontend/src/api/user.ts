import { FetchError } from "../littleLib.js";
import { mockFetch } from "../utils.js";
import { query, QueryCache } from "./api.js";


export interface User
{
	id: number,
	name: string
}

export const query_login = () => query("user", (login: string, password: string) => mockFetch(
	"POST /api/auth",
	{
		avatar: null,
		id: 1,
		login: "user1",
		name: "Вася И.",
		operations: ["recipe_view", "recipe_create", "recipe_update", "recipe_delete", "recipe_manage_own", "recipe_step_view", "recipe_step_create", "recipe_step_update", "recipe_step_delete", "recipe_ingredient_view", "recipe_ingredient_create", "recipe_ingredient_update", "recipe_ingredient_delete", "recipe_image_view", "recipe_image_create", "recipe_image_delete", "comment_view", "comment_create", "comment_update", "comment_delete", "rating_view", "rating_create", "rating_update", "rating_delete", "favorite_view", "favorite_create", "favorite_delete", "search_recipes", "recipe_category_view", "ingredient_category_view", "ingredient_view",],
		reg_date: "08.03.2026T15:47:22",
		roles: ["user"]
	},
	{ login, password },
));

export const query_logout = () => query(null, async () =>
{
	await mockFetch("POST /api/logout", {});
	QueryCache.del("user");
	return true;
});

export const query_user = () => query("user", async () =>
{
	await mockFetch("GET /api/user", {})
	throw new FetchError("Not authorized", 403);
	return {} as User;
}, []);

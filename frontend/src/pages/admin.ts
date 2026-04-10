import Layout from "../layout.js";
import { $, Button, Div, H1, Input, Table, TR, TD, initEl, If } from "../littleLib.js";
import { setPageTitle } from "../utils.js";
import { query_recipes, query_recipe_categories, query_ingredients, mutate_delete_recipe } from "../api/client.js";
import Spinner from "../cmps/spinner.js";
import IngredientManager from "../cmps/ingredient-manager.js";

export default function render()
{
	setPageTitle("Админ-панель");

	const activeTab = $<"recipes" | "categories" | "ingredients" | "users">("recipes");
	const searchQuery = $("");

	const recipes = query_recipes();
	const categories = query_recipe_categories();
	const ingredients = query_ingredients();

	const handleDeleteRecipe = (id: number) =>
	{
		if (confirm("Удалить рецепт?"))
		{
			mutate_delete_recipe(id).v.fetch();
			// TODO: add error handling
			// In a real app we would invalidate cache
			recipes.v.refetch();
		}
	};

	Layout([
		Div("admin-page", [
			H1([], "Админ-панель"),
			Div("admin-page__tabs", [
				Button([], "Рецепты", () => activeTab.v = "recipes"),
				Button([], "Категории", () => activeTab.v = "categories"),
				Button([], "Ингредиенты", () => activeTab.v = "ingredients"),
				Button([], "Пользователи", () => activeTab.v = "users"),
			]),
			Div("admin-page__tab-content", [
				If($(activeTab, tab => tab === "recipes"),
					Div("admin-page__section", [
						initEl("h2", "admin-page__subtitle", "Управление рецептами"),
						Div("admin-page__search", [
							Input([], "text", "Поиск рецептов...", (el) =>
							{
								el.value = searchQuery.v;
								el.addEventListener("input", () => searchQuery.v = el.value);
							}),
							Button([], "Найти", () => { }),
						]),
						$(recipes, r => r.isLoading && Spinner()),
						$(recipes, r => r.error && Div("admin-page__error", "Ошибка загрузки рецептов")),
						$(recipes, r => r.data && (
							Table("admin-page__table", [
								initEl("thead", undefined, [
									TR(undefined, [
										initEl("th", [], "ID"),
										initEl("th", [], "Название"),
										initEl("th", [], "Автор"),
										initEl("th", [], "Категория"),
										initEl("th", [], "Статус"),
										initEl("th", [], "Действия"),
									]),
								]),
								initEl("tbody", undefined,
									r.data.map(recipe => TR(undefined, [
										TD([], String(recipe.id)),
										TD([], recipe.title),
										TD([], recipe.author),
										TD([], recipe.category),
										TD([], recipe.status === "published" ? "Опубликован" : "Черновик"),
										TD([], [
											Button([], "Просмотр", () => window.open(`/recipe/${recipe.id}`, "_blank")),
											Button([], "Удалить", () => handleDeleteRecipe(recipe.id)),
										]),
									]))
								),
							])
						)),
					])),
				If($(activeTab, tab => tab === "categories"),
					Div("admin-page__section", [
						initEl("h2", "admin-page__subtitle", "Управление категориями рецептов"),
						$(categories, c => c.isLoading && Spinner()),
						$(categories, c => c.error && Div("admin-page__error", "Ошибка загрузки категорий")),
						$(categories, c => c.data && (
							Table("admin-page__table", [
								initEl("thead", undefined, [
									TR(undefined, [
										initEl("th", [], "ID"),
										initEl("th", [], "Название"),
										initEl("th", [], "Действия"),
									]),
								]),
								initEl("tbody", undefined,
									c.data.map(cat => TR(undefined, [
										TD([], String(cat.id)),
										TD([], cat.name),
										TD([], [
											Button([], "Редактировать", () => { }),
											Button([], "Удалить", () => { }),
										]),
									]))
								),
							])
						)),
						Div("admin-page__form", [
							Input([], "text", "Новая категория..."),
							Button([], "Добавить", () => { }),
						]),
					])),
				If($(activeTab, tab => tab === "ingredients"),
					Div("admin-page__section", [
						initEl("h2", "admin-page__subtitle", "Управление ингредиентами"),
						IngredientManager(),
					])),
				If($(activeTab, tab => tab === "users"),
					Div("admin-page__section", [
						initEl("h2", "admin-page__subtitle", "Управление пользователями"),
						Div([], "Здесь будет таблица пользователей."),
					])),
			]),
		]),
	], "admin_page");
}
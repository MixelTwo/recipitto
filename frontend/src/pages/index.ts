import Layout from "../layout.js";
import { $, A, Button, Div, H1, Input, Span, initEl, If, type ElChildren } from "../littleLib.js";
import { toPage } from "../main.js";
import { setPageTitle } from "../utils.js";
import { query_recipes, query_recipe_categories } from "../api/client.js";
import Spinner from "../cmps/spinner.js";
import RatingStars from "../cmps/rating-stars.js";

/**
 * Home page component.
 * Displays hero section, search bar, popular recipes, and categories.
 *
 * @returns The rendered page content
 */
export default function render()
{
	setPageTitle("Recipitto — Домашняя кулинария");

	const recipes = query_recipes();
	const categories = query_recipe_categories();

	// Search text state for the hero search bar
	const searchText = $("");

	Layout([
		Div("index__hero", [
			H1([], "Recipitto"),
			initEl("p", "index__subtitle", "Найдите идеальный рецепт для любого случая"),
			Div("index__search-bar", [
				initEl("form", [], [
					Input([], "text", "Поиск рецептов...", (el) =>
					{
						el.value = searchText.v;
						el.addEventListener("input", () => searchText.v = el.value);
					}),
					Button([], "Найти", () => toPage("search", undefined, { q: searchText.v })),
				])
			]),
		]),
		Div("index__content", [
			Div("index__section", [
				initEl("h2", "index__section-title", "Популярные рецепты"),
				$(recipes, r => r.isLoading && Spinner()),
				$(recipes, r => r.error && Div("index__error", `Ошибка загрузки: ${r.error.msg || "Неизвестная ошибка"}`)),
				$(recipes, r => r.data && (
					Div("index__recipe-grid", r.data.map(recipe => (
						Div("recipe-card", [
							recipe.main_image
								? initEl("img", "recipe-card__image", undefined, (el: HTMLImageElement) =>
								{
									el.src = recipe.main_image!;
									el.alt = recipe.title;
								})
								: Div("recipe-card__image-placeholder", ""),
							Div("recipe-card__content", [
								initEl("h3", "recipe-card__title", recipe.title),
								initEl("p", "recipe-card__description", recipe.description),
								Div("recipe-card__meta", [
									Span([], `${recipe.active_time} мин активного времени`),
									Span([], `${recipe.difficulty}/5 сложность`),
									RatingStars({
										rating: recipe.rating,
										voteCount: recipe.vote_count,
										size: "small",
										showCount: true,
										showNumber: false,
									}),
								]),
								A([], "Подробнее", `/recipe/${recipe.id}`, () => toPage("recipe", { id: String(recipe.id) })),
							]),
						])
					)))
				)),
			]),
			Div("index__section", [
				initEl("h2", "index__section-title", "Категории рецептов"),
				$(categories, c => c.isLoading && Spinner()),
				$(categories, c => c.error && Div("index__error", `Ошибка загрузки категорий`)),
				$(categories, c => c.data && (
					Div("index__category-grid", c.data.map(cat => (
						A("category-card", cat.name, `/search?category=${cat.id}`, () => toPage("search", undefined, { category: cat.id }))
					)))
				)),
			]),
			Div("index__section", [
				initEl("h2", "index__section-title", "Почему Recipitto?"),
				initEl("p", "index__feature", "Более 10 000 проверенных рецептов от домашних кулинаров и шеф-поваров."),
				initEl("p", "index__feature", "Умный поиск по ингредиентам, времени приготовления и сложности."),
				initEl("p", "index__feature", "Сохраняйте любимые рецепты, комментируйте и ставьте оценки."),
				Button([], "Присоединиться", () => toPage("profile")),
			]),
		]),
	]);
}
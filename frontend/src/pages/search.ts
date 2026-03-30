import Layout from "../layout.js";
import { $, A, Button, Div, H1, Input, Span, initEl, If, type ElChildren, State } from "../littleLib.js";
import { toPage } from "../main.js";
import { setPageTitle } from "../utils.js";
import { query_search_recipes, query_recipe_categories } from "../api/client.js";
import Spinner from "../cmps/spinner.js";
import RatingStars from "../cmps/rating-stars.js";

export default function render()
{
	setPageTitle("Поиск рецептов");

	const categories = query_recipe_categories();

	// Search parameters state
	const searchText = $("");
	const selectedCategory = $<number | null>(null);
	const maxActiveTime = $<number | null>(null);
	const difficulty = $<number | null>(null);
	const sortBy = $<"relevance" | "rating" | "date">("relevance");
	const sortOrder = $<"asc" | "desc">("desc");

	// Function to build search query
	const buildSearchQuery = () => ({
		text: searchText.v || undefined,
		category_id: selectedCategory.v || undefined,
		max_active_time: maxActiveTime.v || undefined,
		difficulty: difficulty.v || undefined,
		sort_by: sortBy.v,
		sort_order: sortOrder.v,
		page: 1,
		per_page: 20,
	});

	// Perform search
	const searchQuery = $(buildSearchQuery());
	const searchResults = query_search_recipes(searchQuery.v);

	const performSearch = () =>
	{
		searchQuery.v = buildSearchQuery();
	};

	Layout([
		Div("search-page", [
			Div("search-page__sidebar", [
				initEl("h2", "search-page__sidebar-title", "Фильтры"),
				Div("search-filter", [
					initEl("label", "search-filter__label", "Поиск по тексту"),
					Input([], "text", "Название или ингредиент...", (el) =>
					{
						el.value = searchText.v;
						el.addEventListener("input", () => searchText.v = el.value);
					}),
				]),
				Div("search-filter", [
					initEl("label", "search-filter__label", "Категория"),
					initEl("select", "search-filter__select", undefined, (el: HTMLSelectElement) =>
					{
						el.innerHTML = `<option value="">Все категории</option>`;
						$(categories, c =>
						{
							if (c.data)
							{
								c.data.forEach(cat =>
								{
									const option = document.createElement("option");
									option.value = cat.id.toString();
									option.textContent = cat.name;
									el.appendChild(option);
								});
								if (selectedCategory.v)
								{
									el.value = selectedCategory.v.toString();
								}
							}
						});
						el.addEventListener("change", () =>
						{
							selectedCategory.v = el.value ? parseInt(el.value) : null;
						});
					}),
				]),
				Div("search-filter", [
					initEl("label", "search-filter__label", "Макс. активное время (мин)"),
					Input([], "number", "Не ограничено", (el) =>
					{
						el.value = maxActiveTime.v?.toString() || "";
						el.addEventListener("input", () =>
						{
							const val = el.value ? parseInt(el.value) : null;
							maxActiveTime.v = val && val > 0 ? val : null;
						});
					}),
				]),
				Div("search-filter", [
					initEl("label", "search-filter__label", "Сложность (1-5)"),
					initEl("select", "search-filter__select", undefined, (el: HTMLSelectElement) =>
					{
						const options = ["Любая", "1", "2", "3", "4", "5"];
						options.forEach((opt, idx) =>
						{
							const option = document.createElement("option");
							option.value = idx === 0 ? "" : idx.toString();
							option.textContent = opt;
							el.appendChild(option);
						});
						if (difficulty.v) el.value = difficulty.v.toString();
						el.addEventListener("change", () =>
						{
							difficulty.v = el.value ? parseInt(el.value) : null;
						});
					}),
				]),
				Div("search-filter", [
					initEl("label", "search-filter__label", "Сортировка"),
					initEl("select", "search-filter__select", undefined, (el: HTMLSelectElement) =>
					{
						const options = [
							{ value: "relevance", label: "По релевантности" },
							{ value: "rating", label: "По рейтингу" },
							{ value: "date", label: "По дате" },
						];
						options.forEach(opt =>
						{
							const option = document.createElement("option");
							option.value = opt.value;
							option.textContent = opt.label;
							el.appendChild(option);
						});
						el.value = sortBy.v;
						el.addEventListener("change", () =>
						{
							sortBy.v = el.value as any;
						});
					}),
					initEl("select", "search-filter__select", undefined, (el: HTMLSelectElement) =>
					{
						const options = [
							{ value: "desc", label: "По убыванию" },
							{ value: "asc", label: "По возрастанию" },
						];
						options.forEach(opt =>
						{
							const option = document.createElement("option");
							option.value = opt.value;
							option.textContent = opt.label;
							el.appendChild(option);
						});
						el.value = sortOrder.v;
						el.addEventListener("change", () =>
						{
							sortOrder.v = el.value as any;
						});
					}),
				]),
				Button([], "Применить фильтры", performSearch),
				Button([], "Сбросить", () =>
				{
					searchText.v = "";
					selectedCategory.v = null;
					maxActiveTime.v = null;
					difficulty.v = null;
					sortBy.v = "relevance";
					sortOrder.v = "desc";
					performSearch();
				}),
			]),
			Div("search-page__main", [
				H1([], "Результаты поиска"),
				Div("search-page__stats", [
					$(searchResults, r => r.data && Span([], `Найдено рецептов: ${r.data.total}`)),
				]),
				$(searchResults, r => r.isLoading && Spinner()),
				$(searchResults, r => r.error && Div("search-page__error", `Ошибка: ${r.error.msg || "Неизвестная ошибка"}`)),
				$(searchResults, r => r.data && (
					r.data.results.length === 0
						? Div("search-page__empty", "По вашему запросу ничего не найдено.")
						: Div("search-page__grid", r.data.results.map(recipe => (
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
		]),
	]);
}
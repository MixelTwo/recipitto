import Layout from "../layout.js";
import { $, A, Button, Div, H1, Input, Span, initEl, If, type ElChildren, State } from "../littleLib.js";
import { toPage } from "../main.js";
import { setPageTitle } from "../utils.js";
import { query_search_recipes, query_recipe_categories } from "../api/client.js";
import Spinner from "../cmps/spinner.js";
import RatingStars from "../cmps/rating-stars.js";
import IngredientFilter, { type IngredientFilterMode } from "../cmps/ingredient-filter.js";
import Pagination from "../cmps/pagination.js";

/**
 * Search page component with advanced filtering, sorting, and pagination.
 *
 * @returns The rendered search interface
 */
export default function render()
{
	setPageTitle("Поиск рецептов");

	// Parse query parameters from URL
	const urlParams = new URLSearchParams(window.location.search);
	const parseNumber = (key: string): number | null =>
	{
		const val = urlParams.get(key);
		if (val === null || val === "") return null;
		const num = parseInt(val);
		return isNaN(num) ? null : num;
	};
	const parseNumberArray = (key: string): number[] =>
	{
		return urlParams.getAll(key).map(v => parseInt(v)).filter(v => !isNaN(v));
	};

	const initialQ = urlParams.get("q") || "";
	const initialCategoryId = parseNumber("category_id") || parseNumber("category");
	const initialMaxActiveTime = parseNumber("max_active_time");
	const initialDifficulty = parseNumber("difficulty");
	const initialIngredientsInclude = parseNumberArray("ingredients_include");
	const initialIngredientsExclude = parseNumberArray("ingredients_exclude");
	const initialSortBy = (urlParams.get("sort_by") as "relevance" | "rating" | "date") || "relevance";
	const initialSortOrder = (urlParams.get("sort_order") as "asc" | "desc") || "desc";
	const initialPage = parseNumber("page") || 1;
	const initialPageSize = parseNumber("per_page") || 20;

	const categories = query_recipe_categories();

	// Search parameters state
	const searchText = $(initialQ);
	const selectedCategory = $<number | null>(initialCategoryId);
	const maxActiveTime = $<number | null>(initialMaxActiveTime);
	const difficulty = $<number | null>(initialDifficulty);
	const sortBy = $<"relevance" | "rating" | "date">(initialSortBy);
	const sortOrder = $<"asc" | "desc">(initialSortOrder);
	// Determine initial ingredient filter mode and selected IDs
	let initialIngredientFilterMode: IngredientFilterMode = "contains_any";
	let initialSelectedIngredientIds: number[] = [];
	if (initialIngredientsExclude.length > 0)
	{
		initialIngredientFilterMode = "excludes";
		initialSelectedIngredientIds = initialIngredientsExclude;
	} else if (initialIngredientsInclude.length > 0)
	{
		initialIngredientFilterMode = "contains_any";
		initialSelectedIngredientIds = initialIngredientsInclude;
	}

	// Ingredient filter state
	const ingredientsInclude = $<number[]>(initialIngredientsInclude);
	const ingredientsExclude = $<number[]>(initialIngredientsExclude);
	const ingredientFilterMode = $<IngredientFilterMode>(initialIngredientFilterMode);

	// Pagination state
	const currentPage = $(initialPage);
	const pageSize = $(initialPageSize);

	// Ingredient filter component instance
	const ingredientFilter = IngredientFilter({
		initialSelected: initialSelectedIngredientIds,
		onChange: (filter) =>
		{
			ingredientsInclude.v = filter.include;
			ingredientsExclude.v = filter.exclude;
			ingredientFilterMode.v = filter.mode;
		},
	});

	// Function to build search query for API
	const buildSearchQuery = () => ({
		q: searchText.v || undefined,
		category_id: selectedCategory.v || undefined,
		max_active_time: maxActiveTime.v || undefined,
		difficulty: difficulty.v || undefined,
		ingredients_include: ingredientsInclude.v.length > 0 ? ingredientsInclude.v : undefined,
		ingredients_exclude: ingredientsExclude.v.length > 0 ? ingredientsExclude.v : undefined,
		sort_by: sortBy.v,
		sort_order: sortOrder.v,
		page: currentPage.v,
		per_page: pageSize.v,
	});

	// Function to build query params for URL
	const buildUrlQueryParams = () =>
	{
		const params: Record<string, string | number | (string | number)[]> = {};
		if (searchText.v) params.q = searchText.v;
		if (selectedCategory.v !== null) params.category_id = selectedCategory.v;
		if (maxActiveTime.v !== null) params.max_active_time = maxActiveTime.v;
		if (difficulty.v !== null) params.difficulty = difficulty.v;
		if (ingredientsInclude.v.length > 0) params.ingredients_include = ingredientsInclude.v;
		if (ingredientsExclude.v.length > 0) params.ingredients_exclude = ingredientsExclude.v;
		if (sortBy.v !== "relevance") params.sort_by = sortBy.v;
		if (sortOrder.v !== "desc") params.sort_order = sortOrder.v;
		if (currentPage.v !== 1) params.page = currentPage.v;
		if (pageSize.v !== 20) params.per_page = pageSize.v;
		return params;
	};

	// Update URL with current filters (without page reload)
	const updateUrlFromState = () =>
	{
		const params = buildUrlQueryParams();
		const searchParams = new URLSearchParams();
		for (const [key, value] of Object.entries(params))
		{
			if (Array.isArray(value))
			{
				value.forEach(v => searchParams.append(key, v.toString()));
			} else
			{
				searchParams.set(key, value.toString());
			}
		}
		const newUrl = `${window.location.pathname}?${searchParams.toString()}`;
		window.history.replaceState(null, "", newUrl);
	};

	// Perform search
	const searchResults = query_search_recipes();

	const performSearch = () =>
	{
		searchResults.v.refetch(buildSearchQuery());
		updateUrlFromState();
	};
	performSearch();

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
					initEl("label", "search-filter__label", "Фильтр по ингредиентам"),
					ingredientFilter.el,
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
				Div("search-filter__submit", [

					Button([], "Сбросить", () =>
					{
						searchText.v = "";
						selectedCategory.v = null;
						maxActiveTime.v = null;
						difficulty.v = null;
						ingredientsInclude.v = [];
						ingredientsExclude.v = [];
						ingredientFilterMode.v = "contains_any";
						// Reset component internal state
						ingredientFilter.reset();
						sortBy.v = "relevance";
						sortOrder.v = "desc";
						performSearch();
					}),
					Button([], "Применить фильтры", performSearch),
				]),
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
						: [
							Div("search-page__grid", r.data.results.map(recipe => (
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
							))),
							$(searchResults, r => r.data && r.data.total > 0 ? Pagination({
								currentPage,
								totalItems: r.data.total,
								pageSize,
								onPageChange: (page) =>
								{
									currentPage.v = page;
									performSearch();
								},
								onPageSizeChange: (size) =>
								{
									pageSize.v = size;
									currentPage.v = 1;
									performSearch();
								},
								showPageSizeSelector: true,
								showFirstLast: true,
								showTotalInfo: true,
							}) : null),
						]
				)),
			]),
		]),
	]);
}
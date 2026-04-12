import { LayoutWithUser } from "../layout.js";
import { $, A, Button, Div, H1, Span, initEl, If, type ElChildren, State } from "../littleLib.js";
import { toPage } from "../main.js";
import { setPageTitle } from "../utils.js";
import { query_favorites, query_search_recipes } from "../api/client.js";
import Spinner from "../cmps/spinner.js";
import RatingStars from "../cmps/rating-stars.js";
import FavoriteRecipeCard from "../cmps/favorite-recipe-card.js";
import ProfileEditModal from "../cmps/profile-edit-modal.js";
import Pagination from "../cmps/pagination.js";

/**
 * User profile page with tabs for recipes, favorites, and settings.
 *
 * @returns The rendered profile page
 */
export default function render()
{
	setPageTitle("Мой профиль");

	LayoutWithUser(null, user =>
	{
		const recipes = query_search_recipes();
		const currentPage = $(1);
		const pageSize = $(20);
		const favorites = query_favorites();
		const activeTab = $<"recipes" | "favorites" | "settings">("recipes");
		const showEditModal = $(false);

		// Function to fetch recipes with current pagination
		const fetchRecipes = () =>
		{
			recipes.v.refetch({
				author_id: user.id,
				page: currentPage.v,
				per_page: pageSize.v,
				include_drafts: true,
			});
		};
		// Initial fetch
		fetchRecipes();

		return Div("profile-page", [
			If(showEditModal, () => ProfileEditModal({
				user,
				onSuccess: (updatedUser) =>
				{
					showEditModal.v = false;
				},
				onCancel: () => showEditModal.v = false,
			})),
			Div("profile-page__header", [
				Div("profile-page__avatar", user.avatar
					? initEl("img", "profile-page__avatar-img", undefined, (el: HTMLImageElement) =>
					{
						el.src = user.avatar!;
						el.alt = user.name;
					})
					: Div("profile-page__avatar-placeholder", user.name.slice(0, 1).toUpperCase())
				),
				Div("profile-page__info", [
					H1([], user.name),
					Div("profile-page__meta", [
						Span([], `Логин: ${user.login}`),
						Span([], `Дата регистрации: ${new Date(user.reg_date).toLocaleDateString("ru-RU")}`),
						Span([], `Роли: ${user.roles.join(", ")}`),
					]),
				]),
				Button([], "Редактировать профиль", () =>
				{
					showEditModal.v = true;
				}),
			]),
			Div("profile-page__tabs", [
				Button([], "Мои рецепты", () => activeTab.v = "recipes"),
				Button([], "Избранное", () => activeTab.v = "favorites"),
				Button([], "Настройки", () => activeTab.v = "settings"),
			]),
			Div("profile-page__tab-content", [
				If($(activeTab, tab => tab === "recipes"),
					Div("profile-page__recipes", [
						initEl("h2", "profile-page__subtitle", "Мои рецепты"),
						$(recipes, r => r.isLoading && Spinner()),
						$(recipes, r => r.error && Div("profile-page__error", "Ошибка загрузки рецептов")),
						$(recipes, r => r.data && (
							r.data.results.length === 0
								? Div("profile-page__empty", "У вас пока нет рецептов. " + A([], "Создать первый", "/recipe/new", () => toPage("recipe_create", {})))
								: [
									Div("profile-page__grid", r.data.results.map(recipe => (
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
													Span([], `${recipe.active_time} мин`),
													Span([], `${recipe.difficulty}/5`),
													RatingStars({
														rating: recipe.rating,
														size: "small",
														showCount: false,
														showNumber: false,
													}),
												]),
												A([], "Подробнее", `/recipe/${recipe.id}`, () => toPage("recipe", { id: String(recipe.id) })),
											]),
										])
									))),
									$(recipes, r => r.data && r.data.total > 0 ? Pagination({
										currentPage,
										totalItems: r.data.total,
										pageSize,
										onPageChange: (page) =>
										{
											currentPage.v = page;
											fetchRecipes();
										},
										onPageSizeChange: (size) =>
										{
											pageSize.v = size;
											currentPage.v = 1;
											fetchRecipes();
										},
										showPageSizeSelector: true,
										showFirstLast: true,
										showTotalInfo: true,
									}) : null),
								]
						)),
					])),
				$(activeTab, tab => tab === "favorites" && Div("profile-page__favorites", [
					initEl("h2", "profile-page__subtitle", "Избранное"),
					$(favorites, f => f.isLoading && Spinner()),
					$(favorites, f => f.error && Div("profile-page__error", "Ошибка загрузки избранного")),
					$(favorites, f => f.data && (
						f.data.length === 0
							? Div("profile-page__empty", "У вас пока нет избранных рецептов.")
							: Div("profile-page__grid", f.data.map(fav =>
								FavoriteRecipeCard({
									favorite: fav,
									onRemove: () => favorites.v.refetch()
								})
							))
					)),
				])),
				$(activeTab, tab => tab === "settings" && Div("profile-page__settings", [
					initEl("h2", "profile-page__subtitle", "Настройки аккаунта"),
					Div([], "Настройки будут доступны позже."),
				])),
			]),
		]);
	}
	);
}
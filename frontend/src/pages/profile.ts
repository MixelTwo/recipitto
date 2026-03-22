import Layout, { LayoutWithUser } from "../layout.js";
import { $, A, Button, Div, H1, Span, initEl, If, type ElChildren, State } from "../littleLib.js";
import { toPage } from "../main.js";
import { setPageTitle } from "../utils.js";
import { query_recipes, query_user } from "../api/client.js";
import Spinner from "../cmps/spinner.js";

export default function render()
{
	setPageTitle("Мой профиль");

	LayoutWithUser(null, user =>
	{
		const recipes = query_recipes({ author_id: user.id }); // mock filtering
		const activeTab = $<"recipes" | "favorites" | "settings">("recipes");

		return Div("profile-page", [
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
					// TODO: implement profile edit
					alert("Редактирование профиля пока недоступно");
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
							r.data.length === 0
								? Div("profile-page__empty", "У вас пока нет рецептов. " + A([], "Создать первый", "/recipe/new", () => toPage("recipe_create", {})))
								: Div("profile-page__grid", r.data.map(recipe => (
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
												Span([], `★ ${recipe.rating}`),
											]),
											A([], "Подробнее", `/recipe/${recipe.id}`, () => toPage("recipe", { id: String(recipe.id) })),
										]),
									])
								)))
						)),
					])),
				$(activeTab, tab => tab === "favorites" && Div("profile-page__favorites", [
					initEl("h2", "profile-page__subtitle", "Избранное"),
					Div([], "Здесь будут отображены ваши избранные рецепты."),
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
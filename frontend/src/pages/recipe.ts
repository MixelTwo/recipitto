import Layout from "../layout.js";
import { $, A, Button, Div, H1, Input, Span, initEl, If, type ElChildren, State } from "../littleLib.js";
import { toPage } from "../main.js";
import { setPageTitle } from "../utils.js";
import
{
	query_recipe_by_id,
	query_recipe_comments,
	query_recipe_favorite,
	query_recipe_ingredients,
	query_recipe_steps,
	query_recipe_images,
	mutate_add_favorite,
	mutate_remove_favorite,
	mutate_create_comment,
} from "../api/client.js";
import Spinner from "../cmps/spinner.js";
import IngredientList from "../cmps/ingredient-list.js";
import RecipeSteps from "../cmps/recipe-steps.js";
import RatingWidget from "../cmps/rating-widget.js";

export default function render({ id }: { id: string })
{
	const recipeId = parseInt(id);
	if (isNaN(recipeId))
	{
		setPageTitle("Рецепт не найден");
		Layout([
			H1([], "Ошибка"),
			Div([], "Некорректный идентификатор рецепта."),
		]);
		return;
	}

	const recipe = query_recipe_by_id(recipeId);
	const comments = query_recipe_comments(recipeId);
	const ingredients = query_recipe_ingredients(recipeId);
	const steps = query_recipe_steps(recipeId);
	const galleryImages = query_recipe_images(recipeId);
	const favorite = query_recipe_favorite(recipeId);

	const activeTab = $<"details" | "ingredients" | "steps" | "comments">("details");
	const newCommentText = $("");

	setPageTitle("Рецепт");

	const handleAddComment = () =>
	{
		if (!newCommentText.v.trim()) return;
		const mutate = mutate_create_comment(recipeId);
		// fetch returns a Promise, we ignore result for now
		mutate.v.fetch(newCommentText.v);
		newCommentText.v = "";
		// In a real app we would invalidate comments query
		comments.v.refetch();
	};

	const handleToggleFavorite = () =>
	{
		if (favorite.v.data?.favorited)
		{
			mutate_remove_favorite(recipeId).v.fetch();
		} else
		{
			mutate_add_favorite(recipeId).v.fetch();
		}
		favorite.v.refetch();
	};

	Layout([
		Div("recipe-page", [
			$(recipe, r => r.isLoading && Spinner()),
			$(recipe, r => r.error && Div("recipe-page__error", `Ошибка загрузки рецепта: ${r.error.msg || "Неизвестная ошибка"}`)),
			$(recipe, r => r.data && (() =>
			{
				const data = r.data!;
				return [
					Div("recipe-page__header", [
						Div("recipe-page__header-left", [
							H1([], data.title),
							Div("recipe-page__meta", [
								Span([], `Автор: ${data.author}`),
								Span([], `Категория: ${data.category}`),
								Span([], `Сложность: ${data.difficulty}/5`),
								Span([], `Активное время: ${data.active_time} мин`),
								Span([], `Общее время: ${data.total_time} мин`),
								RatingWidget({
									recipeId: recipeId,
									initialRating: data.rating,
									initialCount: data.vote_count,
									interactive: true,
								}),
								Span([], `Статус: ${data.status === "published" ? "Опубликован" : "Черновик"}`),
							]),
						]),
						Div("recipe-page__header-right", [
							Button([], $(favorite, f => f.data?.favorited ? "★ В избранном" : "☆ Добавить в избранное"), handleToggleFavorite),
							A([], "Редактировать", `/recipe/${recipeId}/edit`, () => toPage("recipe_edit", { id: String(recipeId) })),
						]),
					]),
					data.main_image && initEl("img", "recipe-page__image", undefined, (el: HTMLImageElement) =>
					{
						el.src = data.main_image!;
						el.alt = data.title;
					}),
					// Gallery images
					$(galleryImages, g => g.isLoading ? Spinner() : null),
					$(galleryImages, g => g.error ? Div("recipe-page__error", `Ошибка загрузки изображений: ${g.error.msg || "Неизвестная ошибка"}`) : null),
					$(galleryImages, g => g.data && g.data.length > 0 ? Div("recipe-page__gallery", [
						initEl("h3", "recipe-page__subtitle", "Галерея изображений"),
						Div("recipe-page__gallery-grid",
							g.data.map(img =>
								initEl("img", "recipe-page__gallery-image", [], (el: HTMLImageElement) =>
								{
									el.src = `/api/img/${img.image_id}`;
									el.alt = `Изображение ${img.id}`;
								})
							)
						),
					]) : null),
					Div("recipe-page__description", data.description),
					Div("recipe-page__tabs", [
						Button([], "Основное", () => activeTab.v = "details"),
						Button([], "Ингредиенты", () => activeTab.v = "ingredients"),
						Button([], "Шаги приготовления", () => activeTab.v = "steps"),
						Button([], "Комментарии", () => activeTab.v = "comments"),
					]),
					Div("recipe-page__tab-content", [
						$(activeTab, tab => tab === "details" && Div("recipe-page__details", [
							initEl("h2", "recipe-page__subtitle", "Дополнительная информация"),
							Div([], `Дата создания: ${new Date(data.created_at).toLocaleDateString("ru-RU")}`),
							Div([], `Дата публикации: ${data.published_at ? new Date(data.published_at).toLocaleDateString("ru-RU") : "Не опубликован"}`),
						])),
						$(activeTab, tab => tab === "ingredients" && Div("recipe-page__ingredients", [
							initEl("h2", "recipe-page__subtitle", "Ингредиенты"),
							$(ingredients, i => i.isLoading && Spinner()),
							$(ingredients, i => i.error && Div("recipe-page__error", `Ошибка загрузки ингредиентов: ${i.error.msg || "Неизвестная ошибка"}`)),
							$(ingredients, i => i.data && IngredientList({
								ingredients: i.data,
								showHeader: true,
								emptyMessage: "В этом рецепте пока нет ингредиентов."
							})),
						])),
						$(activeTab, tab => tab === "steps" && Div("recipe-page__steps", [
							initEl("h2", "recipe-page__subtitle", "Шаги приготовления"),
							$(steps, s => s.isLoading && Spinner()),
							$(steps, s => s.error && Div("recipe-page__error", `Ошибка загрузки шагов: ${s.error.msg || "Неизвестная ошибка"}`)),
							$(steps, s => s.data && RecipeSteps({
								steps: s.data,
								emptyMessage: "В этом рецепте пока нет шагов приготовления."
							})),
						])),
						If($(activeTab, tab => tab === "comments"),
							Div("recipe-page__comments", [
								initEl("h2", "recipe-page__subtitle", "Комментарии"),
								$(comments, c => c.isLoading && Spinner()),
								$(comments, c => c.error && Div("recipe-page__error", `Ошибка загрузки комментариев`)),
								$(comments, c => c.data && (
									c.data.length === 0
										? Div([], "Пока нет комментариев. Будьте первым!")
										: Div("recipe-page__comment-list", c.data.map(comment => (
											Div("comment", [
												Div("comment__header", [
													Span([], `Пользователь #${comment.user_id}`),
													Span([], new Date(comment.created_at).toLocaleDateString("ru-RU")),
												]),
												Div("comment__text", comment.text),
											])
										)))
								)),
								Div("recipe-page__add-comment", [
									initEl("h3", "recipe-page__subtitle", "Добавить комментарий"),
									initEl("textarea", "recipe-page__comment-input", undefined, (el: HTMLTextAreaElement) =>
									{
										el.placeholder = "Ваш комментарий...";
										el.value = newCommentText.v;
										el.addEventListener("input", () => newCommentText.v = el.value);
									}),
									Button([], "Отправить", handleAddComment),
								]),
							])),
					]),
				];
			})()),
		]),
	]);
}
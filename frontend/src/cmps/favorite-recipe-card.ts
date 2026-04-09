import { $, A, Button, Div, Span, initEl, injectStyles, type ElChildren } from "../littleLib.js";
import { toPage } from "../main.js";
import { mutate_remove_favorite } from "../api/client.js";
import { FavoriteWithRecipeDict } from "../api/types.js";
import RatingStars from "./rating-stars.js";

export interface FavoriteRecipeCardProps
{
	favorite: FavoriteWithRecipeDict;
	onRemove?: () => void;
}

export default function FavoriteRecipeCard(props: FavoriteRecipeCardProps): HTMLDivElement
{
	const { favorite, onRemove } = props;
	const recipe = favorite.recipe;

	const handleRemove = () =>
	{
		if (confirm("Удалить рецепт из избранного?"))
		{
			mutate_remove_favorite(recipe.id).v.fetch();
			if (onRemove) onRemove();
		}
	};

	return Div("recipe-card favorite-recipe-card", [
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
				Span([], `Сложность: ${recipe.difficulty}/5`),
				RatingStars({
					rating: recipe.rating,
					size: "small",
					showCount: false,
					showNumber: false,
				}),
			]),
			Div(styles.favoriteMeta, [
				Span([], `Добавлено: ${new Date(favorite.added_at).toLocaleDateString("ru-RU")}`),
			]),
			Div(styles.actions, [
				A([], "Подробнее", `/recipe/${recipe.id}`, () => toPage("recipe", { id: String(recipe.id) })),
				Button(styles.removeBtn, "Удалить из избранного", handleRemove),
			]),
		]),
	]);
}

const styles = injectStyles({
	favoriteMeta: {
		marginBottom: "1rem",
		fontSize: "0.9rem",
		color: "var(--primary-500)",
	},
	actions: {
		display: "flex",
		gap: "1rem",
		alignItems: "center",
	},
	removeBtn: {
		padding: "0.75rem 1.5rem",
		background: "#ffebee",
		color: "#c62828",
		border: "1px solid #ffcdd2",
		borderRadius: "2rem",
		fontWeight: "bold",
		cursor: "pointer",
		transition: "background 0.2s, color 0.2s",
		"&:hover": {
			background: "#ffcdd2",
			color: "#b71c1c",
		},
	},
});
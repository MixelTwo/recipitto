import { Div } from "../littleLib.js";
import { RecipeIngredientDict } from "../api/types.js";

export interface IngredientListProps
{
	ingredients: RecipeIngredientDict[];
	showHeader?: boolean;
	emptyMessage?: string;
}

export default function IngredientList(props: IngredientListProps): HTMLDivElement
{
	const { ingredients, showHeader = true, emptyMessage = "В этом рецепте пока нет ингредиентов." } = props;

	if (ingredients.length === 0)
	{
		return Div([], emptyMessage);
	}

	return Div("ingredient-list-container", [
		showHeader && Div("ingredient-list__header", [
			Div("ingredient-list__header-name", "Ингредиент"),
			Div("ingredient-list__header-quantity", "Количество"),
		]),
		Div("ingredient-list", ingredients.map(ing => (
			Div("ingredient-list__item", [
				Div("ingredient-list__name", ing.ingredient_name),
				Div("ingredient-list__quantity", `${ing.quantity} ${ing.unit}`),
			])
		))),
	]);
}
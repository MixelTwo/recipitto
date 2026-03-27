import { Div, injectStyles } from "../littleLib.js";
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

	return Div(styles.ingredientListContainer, [
		showHeader && Div(styles.ingredientListHeader, [
			Div(styles.ingredientListHeaderName, "Ингредиент"),
			Div(styles.ingredientListHeaderQuantity, "Количество"),
		]),
		Div(styles.ingredientList, ingredients.map(ing => (
			Div(styles.ingredientListItem, [
				Div(styles.ingredientListName, ing.ingredient_name),
				Div(styles.ingredientListQuantity, `${ing.quantity} ${ing.unit}`),
			])
		))),
	]);
}

const styles = injectStyles({
	ingredientListContainer: {
		// Container styles if needed
	},
	ingredientList: {
		display: "flex",
		flexDirection: "column",
		gap: "0.5rem",
	},
	ingredientListHeader: {
		display: "flex",
		justifyContent: "space-between",
		padding: "0.75rem 1rem",
		background: "var(--primary-100)",
		borderRadius: "0.5rem",
		fontWeight: 600,
		color: "var(--primary-700)",
		marginBottom: "0.5rem",
	},
	ingredientListHeaderName: {
		flex: 1,
	},
	ingredientListHeaderQuantity: {
		flex: 1,
		textAlign: "right",
	},
	ingredientListItem: {
		display: "flex",
		justifyContent: "space-between",
		alignItems: "center",
		padding: "1rem",
		background: "white",
		borderRadius: "0.5rem",
		border: "1px solid var(--primary-200)",
		transition: "background 0.2s",
	},
	"ingredientListItem:hover": {
		background: "var(--primary-50)",
	},
	ingredientListName: {
		flex: 1,
		fontWeight: 500,
		color: "var(--primary-800)",
	},
	ingredientListQuantity: {
		fontWeight: 500,
		color: "var(--primary-700)",
		background: "var(--primary-100)",
		padding: "0.5rem 1rem",
		borderRadius: "2rem",
	},
});
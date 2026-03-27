import { $, Div, Input, Button, Span, initEl, injectStyles, type ElChildren, State } from "../littleLib.js";
import { query_ingredients } from "../api/client.js";
import { IngredientDict, RecipeIngredientDict } from "../api/types.js";

export interface IngredientPickerProps
{
	/** Existing ingredients (for edit mode) */
	initialIngredients?: RecipeIngredientDict[];
	/** Callback when ingredients list changes */
	onChange?: (ingredients: RecipeIngredientDict[]) => void;
	/** Placeholder for search input */
	searchPlaceholder?: string;
	/** Whether to allow adding new ingredients (not implemented) */
	allowCreate?: boolean;
}

export default function IngredientPicker(props: IngredientPickerProps): HTMLDivElement
{
	const { initialIngredients = [], onChange, searchPlaceholder = "Поиск ингредиента..." } = props;

	// State
	const searchQuery = $("");
	const selectedIngredients = $<RecipeIngredientDict[]>([...initialIngredients]);
	const isDropdownOpen = $(false);
	const highlightedIndex = $(-1);

	// Fetch all ingredients
	const ingredientsQuery = query_ingredients();

	// Filter ingredients based on search query
	const filteredIngredients = $<IngredientDict[]>([]);

	const updateFiltered = () =>
	{
		const query = ingredientsQuery.v;
		if (!query.data)
		{
			filteredIngredients.v = [];
			return;
		}
		const q = searchQuery.v.trim().toLowerCase();
		if (q === "")
		{
			filteredIngredients.v = [];
		} else
		{
			const selectedIds = new Set(selectedIngredients.v.map(si => si.ingredient_id));
			filteredIngredients.v = query.data.filter(ing =>
				!selectedIds.has(ing.id) && (
					ing.name.toLowerCase().includes(q) ||
					ing.category.toLowerCase().includes(q)
				)
			).slice(0, 10); // limit to 10 results
		}
	};

	// React to changes in ingredients data
	$(ingredientsQuery, updateFiltered);
	// React to changes in search query
	$(searchQuery, updateFiltered);
	// React to changes in selected ingredients
	$(selectedIngredients, updateFiltered);

	// Open dropdown when there are filtered results
	$(filteredIngredients, (filtered) =>
	{
		isDropdownOpen.v = filtered.length > 0 && searchQuery.v.trim() !== "";
	});

	// Handle search input
	const handleSearchInput = (value: string) =>
	{
		searchQuery.v = value;
		highlightedIndex.v = -1;
	};

	// Handle ingredient selection
	const selectIngredient = (ingredient: IngredientDict) =>
	{
		// Check if already selected
		if (selectedIngredients.v.some(si => si.ingredient_id === ingredient.id))
		{
			// Maybe focus on existing item
			return;
		}
		// Add with default quantity and unit
		const newIng: RecipeIngredientDict = {
			ingredient_id: ingredient.id,
			ingredient_name: ingredient.name,
			quantity: 1,
			unit: "г",
			recipe_id: 0, // will be set by parent
		};
		selectedIngredients.v = [...selectedIngredients.v, newIng];
		searchQuery.v = "";
		highlightedIndex.v = -1;
		onChange?.(selectedIngredients.v);
	};

	// Remove ingredient
	const removeIngredient = (index: number) =>
	{
		const newList = [...selectedIngredients.v];
		newList.splice(index, 1);
		selectedIngredients.v = newList;
		onChange?.(newList);
	};

	// Update quantity/unit of an ingredient
	const updateIngredient = (index: number, field: "quantity" | "unit", value: string) =>
	{
		const newList = [...selectedIngredients.v];
		const ing = newList[index];
		if (!ing) return;
		if (field === "quantity")
		{
			const num = parseFloat(value);
			if (isNaN(num) || num <= 0) return;
			ing.quantity = num;
		} else
		{
			ing.unit = value;
		}
		selectedIngredients.v = newList;
		onChange?.(newList);
	};

	// Handle keyboard navigation
	const handleKeyDown = (e: KeyboardEvent) =>
	{
		if (!isDropdownOpen.v) return;
		const filtered = filteredIngredients.v;
		if (e.key === "ArrowDown")
		{
			e.preventDefault();
			highlightedIndex.v = (highlightedIndex.v + 1) % filtered.length;
		} else if (e.key === "ArrowUp")
		{
			e.preventDefault();
			highlightedIndex.v = highlightedIndex.v <= 0 ? filtered.length - 1 : highlightedIndex.v - 1;
		} else if (e.key === "Enter" && highlightedIndex.v >= 0)
		{
			e.preventDefault();
			const ingredient = filtered[highlightedIndex.v];
			if (ingredient) selectIngredient(ingredient);
		} else if (e.key === "Escape")
		{
			isDropdownOpen.v = false;
		}
	};

	// Render
	return Div(styles.container, [
		// Search input and dropdown
		Div(styles.searchSection, [
			Div(styles.searchWrapper, [
				Input([], "text", searchPlaceholder, (el) =>
				{
					searchQuery.w(v => el.value = v);
					el.addEventListener("input", () => handleSearchInput(el.value));
					el.addEventListener("keydown", handleKeyDown);
					el.addEventListener("focus", () =>
					{
						if (filteredIngredients.v.length > 0) isDropdownOpen.v = true;
					});
					el.addEventListener("blur", () =>
					{
						// Close dropdown after a short delay to allow click
						setTimeout(() => isDropdownOpen.v = false, 200);
					});
				}),
				$(isDropdownOpen, open => open && Div(styles.dropdown, filteredIngredients.v.map((ing, idx) =>
					initEl("div", [
						styles.dropdownItem,
						$(highlightedIndex, v => v === idx ? styles.dropdownItemHighlighted : "")
					], [
						Div(styles.dropdownItemName, ing.name),
						Div(styles.dropdownItemCategory, ing.category),
					], (el) =>
					{
						el.addEventListener("click", () => selectIngredient(ing));
					})
				))),
			]),
			$(ingredientsQuery, q => q.isLoading && Span(styles.loading, "Загрузка...")),
		]),

		// Selected ingredients list
		Div(styles.selectedList, [
			$(selectedIngredients, ingredients => ingredients.length === 0
				? Div(styles.emptyMessage, "Нет выбранных ингредиентов")
				: ingredients.map((ing, idx) =>
					Div(styles.selectedItem, [
						Div(styles.selectedItemName, ing.ingredient_name),
						Div(styles.selectedItemControls, [
							Input([], "number", "1", (el) =>
							{
								el.value = ing.quantity.toString();
								el.min = "0.01";
								el.step = "0.01";
								el.addEventListener("input", () => updateIngredient(idx, "quantity", el.value));
							}),
							Input([], "text", "г", (el) =>
							{
								el.value = ing.unit;
								el.placeholder = "ед.";
								el.addEventListener("input", () => updateIngredient(idx, "unit", el.value));
							}),
							Button([], "×", () => removeIngredient(idx)),
						]),
					])
				)
			),
		]),

		// Hint
		Div(styles.hint, "Начните вводить название ингредиента, выберите из списка, укажите количество и единицу измерения."),
	]);
}

const styles = injectStyles({
	container: {
		display: "flex",
		flexDirection: "column",
		gap: "1.5rem",
	},
	searchSection: {
		position: "relative",
	},
	searchWrapper: {
		position: "relative",
	},
	dropdown: {
		position: "absolute",
		top: "100%",
		left: 0,
		right: 0,
		background: "white",
		border: "1px solid var(--primary-300)",
		borderRadius: "0.5rem",
		boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
		zIndex: 100,
		maxHeight: "300px",
		overflowY: "auto",
		marginTop: "0.25rem",
	},
	dropdownItem: {
		padding: "0.75rem 1rem",
		cursor: "pointer",
		borderBottom: "1px solid var(--primary-100)",
		display: "flex",
		justifyContent: "space-between",
		alignItems: "center",
	},
	dropdownItemHighlighted: {
		background: "var(--primary-100)",
	},
	dropdownItemName: {
		fontWeight: 500,
		color: "var(--primary-800)",
	},
	dropdownItemCategory: {
		fontSize: "0.875rem",
		color: "var(--primary-600)",
		background: "var(--primary-100)",
		padding: "0.25rem 0.5rem",
		borderRadius: "0.25rem",
	},
	loading: {
		display: "block",
		marginTop: "0.5rem",
		color: "var(--primary-600)",
		fontSize: "0.875rem",
	},
	selectedList: {
		display: "flex",
		flexDirection: "column",
		gap: "1rem",
	},
	selectedItem: {
		display: "flex",
		justifyContent: "space-between",
		alignItems: "center",
		padding: "1rem",
		background: "var(--primary-50)",
		borderRadius: "0.5rem",
		border: "1px solid var(--primary-200)",
	},
	selectedItemName: {
		fontWeight: 500,
		color: "var(--primary-800)",
		flex: 1,
	},
	selectedItemControls: {
		display: "flex",
		gap: "0.5rem",
		alignItems: "center",
	},
	emptyMessage: {
		color: "var(--primary-500)",
		fontStyle: "italic",
		textAlign: "center",
		padding: "2rem",
	},
	hint: {
		fontSize: "0.875rem",
		color: "var(--primary-600)",
		textAlign: "center",
		padding: "0.5rem",
		borderTop: "1px dashed var(--primary-300)",
	},
});
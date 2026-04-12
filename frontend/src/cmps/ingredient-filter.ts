import { $, Div, Input, Button, Span, initEl, injectStyles } from "../littleLib.js";
import { query_ingredients } from "../api/client.js";
import { IngredientDict } from "../api/types.js";

export type IngredientFilterMode = "contains_all" | "contains_any" | "excludes";

export interface IngredientFilterProps
{
	/** Initial selected ingredient IDs */
	initialSelected?: number[];
	/** Callback when filter changes */
	onChange?: (filter: { include: number[]; exclude: number[]; mode: IngredientFilterMode }) => void;
	/** Placeholder for search input */
	searchPlaceholder?: string;
}

export interface IngredientFilterInstance
{
	el: HTMLDivElement;
	reset: () => void;
}

export default function IngredientFilter(props: IngredientFilterProps): IngredientFilterInstance
{
	const { initialSelected = [], onChange, searchPlaceholder = "Поиск ингредиента..." } = props;

	// State
	const searchQuery = $("");
	const selectedIds = $<number[]>([...initialSelected]);
	const mode = $<IngredientFilterMode>("contains_any");
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
			const selectedSet = new Set(selectedIds.v);
			filteredIngredients.v = query.data.filter(ing =>
				!selectedSet.has(ing.id) && (
					ing.name.toLowerCase().includes(q) ||
					ing.category.toLowerCase().includes(q)
				)
			).slice(0, 10); // limit to 10 results
		}
	};

	// React to changes
	$(ingredientsQuery, updateFiltered);
	$(searchQuery, updateFiltered);
	$(selectedIds, updateFiltered);

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
		if (selectedIds.v.includes(ingredient.id))
		{
			return;
		}
		selectedIds.v = [...selectedIds.v, ingredient.id];
		searchQuery.v = "";
		highlightedIndex.v = -1;
		notifyChange();
	};

	// Remove ingredient
	const removeIngredient = (id: number) =>
	{
		selectedIds.v = selectedIds.v.filter(selectedId => selectedId !== id);
		notifyChange();
	};

	// Handle mode change
	const setMode = (newMode: IngredientFilterMode) =>
	{
		mode.v = newMode;
		notifyChange();
	};

	// Notify parent about changes
	const notifyChange = () =>
	{
		if (!onChange) return;
		const selected = selectedIds.v;
		let include: number[] = [];
		let exclude: number[] = [];
		switch (mode.v)
		{
			case "contains_all":
			case "contains_any":
				include = selected;
				break;
			case "excludes":
				exclude = selected;
				break;
		}
		onChange({ include, exclude, mode: mode.v });
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

	// Get ingredient name by ID
	const getIngredientName = (id: number): string =>
	{
		const query = ingredientsQuery.v;
		if (!query.data) return `#${id}`;
		const ing = query.data.find(i => i.id === id);
		return ing ? ing.name : `#${id}`;
	};

	const el = Div(styles.container, [
		// Mode selector
		Div(styles.modeSelector, [
			initEl("span", styles.modeLabel, "Фильтр по ингредиентам:"),
			Div(styles.modeButtons, [
				Button([styles.modeButton, $(mode, m => m === "contains_any" ? styles.modeButtonActive : "")], "Содержит любой", () => setMode("contains_any")),
				Button([styles.modeButton, $(mode, m => m === "contains_all" ? styles.modeButtonActive : "")], "Содержит все", () => setMode("contains_all")),
				Button([styles.modeButton, $(mode, m => m === "excludes" ? styles.modeButtonActive : "")], "Исключает", () => setMode("excludes")),
			]),
		]),

		// Search input and dropdown
		Div(styles.searchSection, [
			Div(styles.searchWrapper, [
				Input([styles.searchInput], "text", searchPlaceholder, (el) =>
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
			$(ingredientsQuery, () => $(selectedIds, ids => ids.length === 0
				? Div(styles.emptyMessage, "Нет выбранных ингредиентов")
				: ids.map(id =>
					Div(styles.selectedItem, [
						Div(styles.selectedItemName, getIngredientName(id)),
						Button([styles.selectedItemRemove], "×", () => removeIngredient(id)),
					])
				)
			)),
		]),
	]);

	// Reset function
	const reset = () =>
	{
		selectedIds.v = [];
		mode.v = "contains_any";
		notifyChange();
	};

	return {
		el,
		reset,
	};
}


const styles = injectStyles({
	container: {
		display: "flex",
		flexDirection: "column",
		gap: "1.5rem",
	},
	modeSelector: {
		display: "flex",
		flexDirection: "column",
		gap: "0.75rem",
	},
	modeLabel: {
		fontWeight: "bold",
		color: "var(--text)",
	},
	modeButtons: {
		display: "flex",
		gap: "0.5rem",
		flexWrap: "wrap",
	},
	modeButton: {
		padding: "0.5rem 1rem",
		border: "1px solid var(--primary-300)",
		background: "white",
		color: "var(--text)",
		borderRadius: "0.5rem",
		cursor: "pointer",
		fontSize: "0.9rem",
		transition: "all 0.2s",
	},
	"modeButton:hover": {
		borderColor: "var(--accent-500)",
		background: "var(--accent-50)",
	},
	modeButtonActive: {
		background: "var(--accent-500)",
		color: "white",
		borderColor: "var(--accent-500)",
	},
	searchSection: {
		position: "relative",
	},
	searchWrapper: {
		position: "relative",
	},
	searchInput: {
		width: "100%",
		padding: "0.75rem 1rem",
		border: "1px solid var(--primary-300)",
		borderRadius: "0.5rem",
		fontSize: "1rem",
		background: "white",
		color: "var(--text)",
		transition: "border-color 0.2s, box-shadow 0.2s",
	},
	"searchInput:focus": {
		outline: "none",
		borderColor: "var(--accent-500)",
		boxShadow: "0 0 0 3px rgba(45, 210, 111, 0.2)",
	},
	dropdown: {
		position: "absolute",
		top: "100%",
		left: 0,
		right: 0,
		background: "white",
		border: "1px solid var(--primary-300)",
		borderRadius: "0.5rem",
		boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
		maxHeight: "300px",
		overflowY: "auto",
		zIndex: 100,
		marginTop: "0.25rem",
	},
	dropdownItem: {
		padding: "0.75rem 1rem",
		cursor: "pointer",
		borderBottom: "1px solid var(--primary-100)",
		display: "flex",
		justifyContent: "space-between",
		transition: "background-color 0.2s",
	},
	"dropdownItem:hover": {
		background: "var(--accent-50)",
	},
	"dropdownItem:last-child": {
		borderBottom: "none",
	},
	dropdownItemHighlighted: {
		background: "var(--primary-100)",
	},
	dropdownItemName: {
		fontWeight: "bold",
	},
	dropdownItemCategory: {
		color: "var(--primary-500)",
		fontSize: "0.9rem",
	},
	selectedList: {
		display: "flex",
		flexDirection: "column",
		gap: "0.5rem",
	},
	selectedItem: {
		display: "flex",
		justifyContent: "space-between",
		alignItems: "center",
		padding: "0.5rem 0.75rem",
		background: "var(--primary-50)",
		borderRadius: "0.5rem",
	},
	selectedItemName: {
		fontWeight: 500,
	},
	selectedItemRemove: {
		background: "none",
		border: "none",
		color: "var(--primary-500)",
		fontSize: "1.2rem",
		cursor: "pointer",
		padding: "0 0.5rem",
		transition: "color 0.2s",
	},
	"selectedItemRemove:hover": {
		color: "#c62828",
	},
	loading: {
		display: "block",
		marginTop: "0.5rem",
		color: "var(--primary-500)",
		fontSize: "0.9rem",
	},
	emptyMessage: {
		color: "#666",
		fontStyle: "italic",
		textAlign: "center",
		padding: "1rem",
	},
});
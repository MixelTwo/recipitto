import { $, Button, Div, Input, Table, TR, TD, initEl, injectStyles, Span, If } from "../littleLib.js";
import { query_ingredients, query_ingredient_categories, mutate_create_ingredient, mutate_update_ingredient, mutate_delete_ingredient } from "../api/client.js";
import { IngredientDict, IngredientCategoryDict, IngredientResponse } from "../api/types.js";
import Spinner from "./spinner.js";

export default function IngredientManager()
{
	// State
	const ingredients = query_ingredients();
	const categories = query_ingredient_categories();
	const newIngredientName = $("");
	const newIngredientCategoryId = $<number | "">("");
	const editingId = $<number | null>(null);
	const editingName = $("");
	const editingCategoryId = $<number | "">("");

	// Handlers
	const handleAdd = async () =>
	{
		if (!newIngredientName.v.trim() || newIngredientCategoryId.v === "") return;
		try
		{
			await (mutate_create_ingredient().v.fetch({
				name: newIngredientName.v.trim(),
				category_id: Number(newIngredientCategoryId.v)
			}) as any);
			newIngredientName.v = "";
			newIngredientCategoryId.v = "";
			ingredients.v.refetch();
		}
		catch (err: any)
		{
			console.error("Failed to create ingredient:", err);
		}
	};

	const startEdit = (ing: IngredientDict) =>
	{
		editingId.v = ing.id;
		editingName.v = ing.name;
		// Find category id by name (since IngredientDict only has category string)
		const cat = categories.v.data?.find(c => c.name === ing.category);
		editingCategoryId.v = cat ? cat.id : "";
	};

	const cancelEdit = () =>
	{
		editingId.v = null;
		editingName.v = "";
		editingCategoryId.v = "";
	};

	const saveEdit = async () =>
	{
		if (!editingName.v.trim() || editingCategoryId.v === "" || editingId.v === null) return;
		try
		{
			await (mutate_update_ingredient(editingId.v).v.fetch({
				name: editingName.v.trim(),
				category_id: Number(editingCategoryId.v)
			}) as any);
			ingredients.v.refetch();
			cancelEdit();
		}
		catch (err: any)
		{
			console.error("Failed to update ingredient:", err);
		}
	};

	const handleDelete = async (id: number) =>
	{
		if (!confirm("Удалить ингредиент?")) return;
		try
		{
			await (mutate_delete_ingredient(id).v.fetch() as any);
			ingredients.v.refetch();
		}
		catch (err: any)
		{
			console.error("Failed to delete ingredient:", err);
		}
	};

	return Div(styles.ingredientManager, [
		// Add form
		Div(styles.form, [
			Input(styles.input, "text", "Название ингредиента", (el) =>
			{
				el.value = newIngredientName.v;
				el.addEventListener("input", () => newIngredientName.v = el.value);
				newIngredientName.w(v => el.value = v);
			}),
			$(categories, cats => cats.data ? initEl("select", styles.select, undefined, (el: HTMLSelectElement) =>
			{
				el.innerHTML = "";
				const option = initEl("option", [], "Выберите категорию");
				option.value = "";
				el.appendChild(option);
				cats.data!.forEach(cat =>
				{
					const option = initEl("option", [], cat.name);
					option.value = cat.id.toString();
					el.appendChild(option);
				});
				el.value = newIngredientCategoryId.v.toString();
				el.addEventListener("change", () => newIngredientCategoryId.v = el.value === "" ? "" : Number(el.value));
				newIngredientCategoryId.w(v => el.value = v.toString());
			}) : Span([], "Загрузка категорий...")),
			Button(styles.button, "Добавить", handleAdd),
		]),

		// Loading/error states
		$(ingredients, i => i.isLoading && Div(styles.loading, [Spinner()])),
		$(ingredients, i => i.error && Div(styles.error, "Ошибка загрузки ингредиентов")),
		$(categories, c => c.error && Div(styles.error, "Ошибка загрузки категорий")),

		// Table
		$(ingredients, i => i.data && $(categories, c => c.data && $(editingId, () =>
			Table(styles.table, [
				initEl("thead", undefined, [
					TR(undefined, [
						initEl("th", styles.th, "ID"),
						initEl("th", styles.th, "Название"),
						initEl("th", styles.th, "Категория"),
						initEl("th", styles.th, "Действия"),
					]),
				]),
				initEl("tbody", undefined,
					i.data!.map(ing =>
					{
						const isEditing = editingId.v === ing.id;
						if (isEditing)
						{
							return TR(styles.editRow, [
								TD(styles.td, String(ing.id)),
								TD(styles.td, Input([], "text", "", (el) =>
								{
									el.value = editingName.v;
									el.addEventListener("input", () => editingName.v = el.value);
									editingName.w(v => el.value = v);
								})),
								TD(styles.td, initEl("select", [], undefined, (el: HTMLSelectElement) =>
								{
									el.innerHTML = "";
									c.data!.forEach(cat =>
									{
										const option = initEl("option", [], cat.name);
										option.value = cat.id.toString();
										el.appendChild(option);
									});
									el.value = editingCategoryId.v.toString();
									el.addEventListener("change", () => editingCategoryId.v = el.value === "" ? "" : Number(el.value));
									editingCategoryId.w(v => el.value = v.toString());
								})),
								TD(styles.td, [
									Button(styles.button, "Сохранить", saveEdit),
									Button([styles.button, styles.buttonSecondary], "Отмена", cancelEdit),
								]),
							]);
						}
						else
						{
							return TR([styles.trHover], [
								TD(styles.td, String(ing.id)),
								TD(styles.td, ing.name),
								TD(styles.td, ing.category),
								TD(styles.td, [
									Button([styles.button, styles.buttonSecondary], "Редактировать", () => startEdit(ing)),
									Button([styles.button, styles.buttonDanger], "Удалить", () => handleDelete(ing.id)),
								]),
							]);
						}
					})
				),
			])
		))),
	]);
}

const styles = injectStyles({
	ingredientManager: {
		maxWidth: "1000px",
		margin: "0 auto",
	},
	form: {
		display: "flex",
		gap: "12px",
		marginBottom: "24px",
		flexWrap: "wrap",
		alignItems: "flex-end",
	},
	input: {
		padding: "8px 12px",
		border: "1px solid #ccc",
		borderRadius: "4px",
		fontSize: "16px",
		minWidth: "200px",
	},
	select: {
		padding: "8px 12px",
		border: "1px solid #ccc",
		borderRadius: "4px",
		fontSize: "16px",
		minWidth: "200px",
	},
	button: {
		padding: "8px 16px",
		backgroundColor: "#007bff",
		color: "white",
		border: "none",
		borderRadius: "4px",
		cursor: "pointer",
		fontSize: "16px",
	},
	buttonSecondary: {
		backgroundColor: "#6c757d",
	},
	buttonDanger: {
		backgroundColor: "#dc3545",
	},
	table: {
		width: "100%",
		borderCollapse: "collapse",
		marginTop: "16px",
	},
	th: {
		border: "1px solid #ddd",
		padding: "12px",
		textAlign: "left",
		backgroundColor: "#f2f2f2",
		fontWeight: "bold",
	},
	td: {
		border: "1px solid #ddd",
		padding: "12px",
		textAlign: "left",
	},
	trHover: {
		"&:hover": {
			backgroundColor: "#f9f9f9",
		},
	},
	editRow: {
		backgroundColor: "#fff3cd",
	},
	actions: {
		display: "flex",
		gap: "8px",
	},
	error: {
		color: "#dc3545",
		padding: "12px",
		backgroundColor: "#f8d7da",
		borderRadius: "4px",
		marginBottom: "16px",
	},
	loading: {
		textAlign: "center",
		padding: "24px",
	},
});

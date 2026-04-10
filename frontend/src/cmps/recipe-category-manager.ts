import { $, Button, Div, Input, Table, TR, TD, initEl, injectStyles, Span, If } from "../littleLib.js";
import
{
	query_recipe_categories,
	mutate_create_recipe_category,
	mutate_update_recipe_category,
	mutate_delete_recipe_category
} from "../api/client.js";
import { RecipeCategoryDict } from "../api/types.js";
import Spinner from "./spinner.js";

export default function RecipeCategoryManager()
{
	// State
	const categories = query_recipe_categories();
	const newCategoryName = $("");
	const editingId = $<number | null>(null);
	const editingName = $("");

	// Validation
	const validateName = (name: string): string | null =>
	{
		const trimmed = name.trim();
		if (trimmed.length === 0) return "Название не может быть пустым";
		if (trimmed.length > 100) return "Название слишком длинное (максимум 100 символов)";
		return null;
	};

	// Loading states
	const addingLoading = $(false);
	const editingLoading = $(false);
	const deletingLoading = $<number | null>(null);

	// Handlers
	const handleAdd = async () =>
	{
		const validationError = validateName(newCategoryName.v);
		if (validationError)
		{
			alert(validationError);
			return;
		}

		addingLoading.v = true;
		try
		{
			await (mutate_create_recipe_category().v.fetch({
				name: newCategoryName.v.trim()
			}) as any);
			newCategoryName.v = "";
			categories.v.refetch();
		}
		catch (err: any)
		{
			console.error("Failed to create category:", err);
			alert("Ошибка при создании категории: " + (err.message || "неизвестная ошибка"));
		}
		finally
		{
			addingLoading.v = false;
		}
	};

	const startEdit = (cat: RecipeCategoryDict) =>
	{
		editingId.v = cat.id;
		editingName.v = cat.name;
	};

	const cancelEdit = () =>
	{
		editingId.v = null;
		editingName.v = "";
	};

	const saveEdit = async () =>
	{
		const validationError = validateName(editingName.v);
		if (validationError || editingId.v === null)
		{
			if (validationError) alert(validationError);
			return;
		}

		editingLoading.v = true;
		try
		{
			await (mutate_update_recipe_category(editingId.v).v.fetch({
				name: editingName.v.trim()
			}) as any);
			categories.v.refetch();
			cancelEdit();
		}
		catch (err: any)
		{
			console.error("Failed to update category:", err);
			alert("Ошибка при обновлении категории: " + (err.message || "неизвестная ошибка"));
		}
		finally
		{
			editingLoading.v = false;
		}
	};

	const handleDelete = async (id: number) =>
	{
		if (!confirm("Удалить категорию? Все рецепты в этой категории будут перемещены в категорию по умолчанию.")) return;

		deletingLoading.v = id;
		try
		{
			await (mutate_delete_recipe_category(id).v.fetch() as any);
			categories.v.refetch();
		}
		catch (err: any)
		{
			console.error("Failed to delete category:", err);
			alert("Ошибка при удалении категории: " + (err.message || "неизвестная ошибка"));
		}
		finally
		{
			deletingLoading.v = null;
		}
	};

	return Div(styles.categoryManager, [
		// Add form
		Div(styles.form, [
			Input(styles.input, "text", "Новая категория рецептов", (el) =>
			{
				el.value = newCategoryName.v;
				el.addEventListener("input", () => newCategoryName.v = el.value);
				newCategoryName.w(v => el.value = v);
			}),
			$(addingLoading, loading =>
				Button(styles.button, loading ? "Добавление..." : "Добавить", loading ? undefined : handleAdd, loading ? (el) => { el.disabled = true; } : undefined)
			),
		]),

		// Loading/error states
		$(categories, c => c.isLoading && Spinner()),
		$(categories, c => c.error && Div(styles.error, "Ошибка загрузки категорий")),

		// Categories table
		$(categories, c => c.data && (
			Table(styles.table, [
				initEl("thead", undefined, [
					TR(undefined, [
						initEl("th", [], "ID"),
						initEl("th", [], "Название"),
						initEl("th", [], "Действия"),
					]),
				]),
				initEl("tbody", undefined,
					c.data.map(cat =>
						If($(editingId, id => id === cat.id),
							// Edit mode
							TR(styles.editRow, [
								TD([], String(cat.id)),
								TD([], [
									Input(styles.editInput, "text", "", (el) =>
									{
										el.value = editingName.v;
										el.addEventListener("input", () => editingName.v = el.value);
										editingName.w(v => el.value = v);
									}),
								]),
								TD([], [
									$(editingLoading, loading =>
										Button(styles.smallButton, loading ? "Сохранение..." : "Сохранить", loading ? undefined : saveEdit, loading ? (el) => { el.disabled = true; } : undefined)
									),
									Button(styles.smallButton, "Отмена", cancelEdit),
								]),
							]),
							// View mode
							TR(undefined, [
								TD([], String(cat.id)),
								TD([], cat.name),
								TD([], [
									Button(styles.smallButton, "Редактировать", () => startEdit(cat)),
									$(deletingLoading, loadingId =>
										Button(styles.smallButton, loadingId === cat.id ? "Удаление..." : "Удалить", loadingId === cat.id ? undefined : () => handleDelete(cat.id), loadingId === cat.id ? (el) => { el.disabled = true; } : undefined)
									),
								]),
							])
						)
					)
				),
			])
		)),
	]);
}

const styles = injectStyles({
	categoryManager: {
		marginTop: "20px",
	},
	form: {
		display: "flex",
		gap: "10px",
		marginBottom: "20px",
		alignItems: "center",
	},
	input: {
		padding: "8px 12px",
		border: "1px solid #ccc",
		borderRadius: "4px",
		fontSize: "14px",
		minWidth: "300px",
	},
	editInput: {
		padding: "6px 10px",
		border: "1px solid #ccc",
		borderRadius: "4px",
		fontSize: "14px",
		width: "100%",
	},
	button: {
		padding: "8px 16px",
		backgroundColor: "#4CAF50",
		color: "white",
		border: "none",
		borderRadius: "4px",
		cursor: "pointer",
		fontSize: "14px",
		"&:hover": {
			backgroundColor: "#45a049",
		},
	},
	smallButton: {
		padding: "4px 8px",
		margin: "0 4px",
		fontSize: "12px",
		border: "1px solid #ccc",
		borderRadius: "3px",
		cursor: "pointer",
		backgroundColor: "#f5f5f5",
		"&:hover": {
			backgroundColor: "#e0e0e0",
		},
	},
	table: {
		width: "100%",
		borderCollapse: "collapse",
		"& th, & td": {
			border: "1px solid #ddd",
			padding: "8px",
			textAlign: "left",
		},
		"& th": {
			backgroundColor: "#f2f2f2",
			fontWeight: "bold",
		},
		"& tr:hover": {
			backgroundColor: "#f9f9f9",
		},
	},
	editRow: {
		backgroundColor: "#fffde7",
	},
	error: {
		color: "#d32f2f",
		padding: "10px",
		backgroundColor: "#ffebee",
		borderRadius: "4px",
		marginBottom: "10px",
	},
});
import Layout from "../layout.js";
import { $, Button, Div, H1, Input, Span, initEl, type ElChildren, State } from "../littleLib.js";
import { toPage } from "../main.js";
import { setPageTitle } from "../utils.js";
import { query_recipe_by_id, query_recipe_categories, mutate_create_recipe, mutate_update_recipe } from "../api/client.js";
import Spinner from "../cmps/spinner.js";

export default function render({ id }: { id?: string }) {
	const isNew = !id;
	const recipeId = id ? parseInt(id) : null;
	if (recipeId !== null && isNaN(recipeId)) {
		setPageTitle("Ошибка");
		Layout([
			H1([], "Ошибка"),
			Div([], "Некорректный идентификатор рецепта."),
		]);
		return;
	}

	const recipe = recipeId ? query_recipe_by_id(recipeId) : null;
	const categories = query_recipe_categories();

	// Form state
	const title = $("");
	const description = $("");
	const categoryId = $<number | null>(null);
	const difficulty = $<number>(3);
	const activeTime = $<number>(30);
	const totalTime = $<number>(60);
	const status = $<"draft" | "published">("draft");
	const errors = $<Record<string, string>>({});
	const isSubmitting = $(false);

	// Load existing recipe if editing
	if (recipe) {
		$(recipe, r => {
			if (r.data) {
				title.v = r.data.title;
				description.v = r.data.description;
				// category mapping by name? We'll need to map later
				categoryId.v = null; // placeholder
				difficulty.v = r.data.difficulty;
				activeTime.v = r.data.active_time;
				totalTime.v = r.data.total_time;
				status.v = r.data.status as any;
			}
		});
	}

	setPageTitle(isNew ? "Создание рецепта" : "Редактирование рецепта");

	const validate = (): boolean => {
		const err: Record<string, string> = {};
		if (!title.v.trim()) err.title = "Название обязательно";
		if (!description.v.trim()) err.description = "Описание обязательно";
		if (categoryId.v === null) err.category = "Выберите категорию";
		if (difficulty.v < 1 || difficulty.v > 5) err.difficulty = "Сложность от 1 до 5";
		if (activeTime.v <= 0) err.activeTime = "Активное время должно быть положительным";
		if (totalTime.v < activeTime.v) err.totalTime = "Общее время не может быть меньше активного";
		errors.v = err;
		return Object.keys(err).length === 0;
	};

	const handleSubmit = async () => {
		if (!validate()) return;
		isSubmitting.v = true;

		const data = {
			title: title.v,
			description: description.v,
			category_id: categoryId.v!,
			difficulty: difficulty.v,
			active_time: activeTime.v,
			total_time: totalTime.v,
			status: status.v,
			main_image_id: undefined as number | undefined,
		};

		try {
			if (isNew) {
				const result = await mutate_create_recipe().v.fetch(data);
				if (result) {
					toPage("recipe", { id: String((result as any).id) });
				}
			} else {
				if (!recipeId) return;
				const result = await mutate_update_recipe(recipeId).v.fetch(data);
				if (result) {
					toPage("recipe", { id: String(recipeId) });
				}
			}
		} catch {
			errors.v = { submit: "Ошибка при сохранении рецепта" };
		} finally {
			isSubmitting.v = false;
		}
	};

	Layout([
		Div("recipe-edit-page", [
			H1([], isNew ? "Создание нового рецепта" : "Редактирование рецепта"),
			recipe ? $(recipe, r => r.isLoading && Spinner()) : null,
			$(errors, e => e.submit && Div("recipe-edit__error", e.submit)),
			Div("recipe-edit__form", [
				Div("recipe-edit__field", [
					initEl("label", "recipe-edit__label", "Название рецепта *"),
					Input([], "text", "Введите название...", (el) => {
						el.value = title.v;
						el.addEventListener("input", () => title.v = el.value);
					}),
					$(errors, e => e.title && Span("recipe-edit__error-text", e.title)),
				]),
				Div("recipe-edit__field", [
					initEl("label", "recipe-edit__label", "Описание *"),
					initEl("textarea", "recipe-edit__textarea", undefined, (el: HTMLTextAreaElement) => {
						el.value = description.v;
						el.placeholder = "Опишите рецепт...";
						el.addEventListener("input", () => description.v = el.value);
					}),
					$(errors, e => e.description && Span("recipe-edit__error-text", e.description)),
				]),
				Div("recipe-edit__field", [
					initEl("label", "recipe-edit__label", "Категория *"),
					initEl("select", "recipe-edit__select", undefined, (el: HTMLSelectElement) => {
						el.innerHTML = `<option value="">Выберите категорию</option>`;
						$(categories, c => {
							if (c.data) {
								c.data.forEach(cat => {
									const option = document.createElement("option");
									option.value = cat.id.toString();
									option.textContent = cat.name;
									el.appendChild(option);
								});
								if (categoryId.v) {
									el.value = categoryId.v.toString();
								}
							}
						});
						el.addEventListener("change", () => {
							categoryId.v = el.value ? parseInt(el.value) : null;
						});
					}),
					$(errors, e => e.category && Span("recipe-edit__error-text", e.category)),
				]),
				Div("recipe-edit__row", [
					Div("recipe-edit__field", [
						initEl("label", "recipe-edit__label", "Сложность (1-5)"),
						Input([], "number", "3", (el) => {
							el.value = difficulty.v.toString();
							el.min = "1";
							el.max = "5";
							el.addEventListener("input", () => difficulty.v = parseInt(el.value) || 3);
						}),
						$(errors, e => e.difficulty && Span("recipe-edit__error-text", e.difficulty)),
					]),
					Div("recipe-edit__field", [
						initEl("label", "recipe-edit__label", "Активное время (мин)"),
						Input([], "number", "30", (el) => {
							el.value = activeTime.v.toString();
							el.min = "1";
							el.addEventListener("input", () => activeTime.v = parseInt(el.value) || 30);
						}),
						$(errors, e => e.activeTime && Span("recipe-edit__error-text", e.activeTime)),
					]),
					Div("recipe-edit__field", [
						initEl("label", "recipe-edit__label", "Общее время (мин)"),
						Input([], "number", "60", (el) => {
							el.value = totalTime.v.toString();
							el.min = "1";
							el.addEventListener("input", () => totalTime.v = parseInt(el.value) || 60);
						}),
						$(errors, e => e.totalTime && Span("recipe-edit__error-text", e.totalTime)),
					]),
				]),
				Div("recipe-edit__field", [
					initEl("label", "recipe-edit__label", "Статус"),
					initEl("select", "recipe-edit__select", undefined, (el: HTMLSelectElement) => {
						const options = [
							{ value: "draft", label: "Черновик" },
							{ value: "published", label: "Опубликован" },
						];
						options.forEach(opt => {
							const option = document.createElement("option");
							option.value = opt.value;
							option.textContent = opt.label;
							el.appendChild(option);
						});
						el.value = status.v;
						el.addEventListener("change", () => {
							status.v = el.value as any;
						});
					}),
				]),
				Div("recipe-edit__actions", [
					Button([], "Отмена", () => {
						if (recipeId) toPage("recipe", { id: String(recipeId) });
						else toPage("index");
					}),
					$(isSubmitting, submitting =>
						submitting
							? Button([], "Сохранение...", undefined)
							: Button([], isNew ? "Создать рецепт" : "Сохранить изменения", handleSubmit)
					),
				]),
			]),
		]),
	]);
}
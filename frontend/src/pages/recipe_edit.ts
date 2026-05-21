import Layout from "../layout.js";
import { $, Button, Div, H1, Input, Span, initEl, type ElChildren, State } from "../littleLib.js";
import { toPage } from "../main.js";
import { setPageTitle } from "../utils.js";
import
{
	query_recipe_by_id,
	query_recipe_categories,
	query_recipe_ingredients,
	query_recipe_images,
	mutate_create_recipe,
	mutate_update_recipe,
	mutate_add_recipe_ingredient,
	mutate_delete_recipe_ingredient,
	mutate_add_recipe_image,
	mutate_delete_recipe_image,
} from "../api/client.js";
import { RecipeIngredientDict, type ImageJson, type RecipeImageDict } from "../api/types.js";
import Spinner from "../cmps/spinner.js";
import IngredientPicker from "../cmps/ingredient-picker.js";
import ImageUpload from "../cmps/image-upload.js";

/**
 * Recipe creation/editing page with form for recipe metadata, ingredients, steps, and images.
 *
 * @param params - Object containing optional recipe ID (for editing) or empty for new recipe
 * @returns The rendered recipe editor
 */
export default function render({ id }: { id?: string })
{
	const isNew = !id;
	const recipeId = id ? parseInt(id) : null;
	if (recipeId !== null && isNaN(recipeId))
	{
		setPageTitle("Ошибка");
		Layout([
			H1([], "Ошибка"),
			Div([], "Некорректный идентификатор рецепта."),
		]);
		return;
	}

	const recipe = recipeId ? query_recipe_by_id(recipeId) : null;
	const categories = query_recipe_categories();
	const create_recipe = mutate_create_recipe();
	const update_recipe = mutate_update_recipe(recipeId || -1);

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
	const ingredients = $<RecipeIngredientDict[]>([]);
	const mainImage = $<ImageJson | null>(null);
	const galleryImages = $<RecipeImageDict[]>([]);
	const newGalleryImages = $<ImageJson[]>([]);
	const imagesToDelete = $<number[]>([]);

	// Load existing recipe if editing
	if (recipe)
	{
		$(recipe, r =>
		{
			if (r.data)
			{
				title.v = r.data.title;
				description.v = r.data.description;
				categoryId.v = r.data.category_id;
				difficulty.v = r.data.difficulty;
				activeTime.v = r.data.active_time;
				totalTime.v = r.data.total_time;
				status.v = r.data.status as any;
			}
		});
	}

	// Load existing ingredients if editing
	if (recipeId)
	{
		const existingIngredientsQuery = query_recipe_ingredients(recipeId);
		$(existingIngredientsQuery, q =>
		{
			if (q.data)
			{
				ingredients.v = q.data;
			}
		});

		// Load existing images if editing
		const existingImagesQuery = query_recipe_images(recipeId);
		$(existingImagesQuery, q =>
		{
			if (q.data)
			{
				galleryImages.v = q.data;
			}
		});
	}

	setPageTitle(isNew ? "Создание рецепта" : "Редактирование рецепта");

	const validate = (): boolean =>
	{
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

	const handleSubmit = async () =>
	{
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
			main_image: mainImage.v,
		};

		try
		{
			let savedRecipeId: number | null = null;
			if (isNew)
			{
				const result = await create_recipe.v.fetch(data);
				if (result)
				{
					savedRecipeId = (result as any).id;
				}
			} else
			{
				if (!recipeId) return;
				const result = await update_recipe.v.fetch(data);
				if (result)
				{
					savedRecipeId = recipeId;
				}
			}

			// Save ingredients if we have a recipe ID
			if (savedRecipeId !== null && ingredients.v.length > 0)
			{
				// For simplicity, we add each ingredient sequentially
				// In a real app you might want batch operations and error handling
				for (const ing of ingredients.v)
				{
					try
					{
						await mutate_add_recipe_ingredient(savedRecipeId).v.fetch({
							ingredient_id: ing.ingredient_id,
							quantity: ing.quantity,
							unit: ing.unit,
						});
					} catch (err)
					{
						console.error("Failed to save ingredient", ing, err);
						// Continue with other ingredients
					}
				}
			}

			// Save gallery images if we have a recipe ID
			if (savedRecipeId !== null)
			{
				// Delete images marked for removal
				for (const imageId of imagesToDelete.v)
				{
					try
					{
						await mutate_delete_recipe_image(savedRecipeId, imageId).v.fetch();
					} catch (err)
					{
						console.error("Failed to delete image", imageId, err);
					}
				}
				// Add new gallery images
				for (const image of newGalleryImages.v)
				{
					try
					{
						await mutate_add_recipe_image(savedRecipeId).v.fetch(image);
					} catch (err)
					{
						console.error("Failed to add image", image, err);
					}
				}
			}

			// Redirect to recipe page
			if (savedRecipeId !== null)
			{
				toPage("recipe", { id: String(savedRecipeId) });
			}
		} catch
		{
			errors.v = { submit: "Ошибка при сохранении рецепта" };
		} finally
		{
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
					Input([], "text", "Введите название...", (el) =>
					{
						title.w(v => el.value = v);
						el.addEventListener("input", () => title.v = el.value);
					}),
					$(errors, e => e.title && Span("recipe-edit__error-text", e.title)),
				]),
				Div("recipe-edit__field", [
					initEl("label", "recipe-edit__label", "Описание *"),
					initEl("textarea", "recipe-edit__textarea", undefined, (el: HTMLTextAreaElement) =>
					{
						description.w(v => el.value = v);
						el.placeholder = "Опишите рецепт...";
						el.addEventListener("input", () => description.v = el.value);
					}),
					$(errors, e => e.description && Span("recipe-edit__error-text", e.description)),
				]),
				Div("recipe-edit__field", [
					initEl("label", "recipe-edit__label", "Категория *"),
					initEl("select", "recipe-edit__select", undefined, (el: HTMLSelectElement) =>
					{
						el.innerHTML = `<option value="">Выберите категорию</option>`;
						$(categories, c =>
						{
							if (c.data)
							{
								c.data.forEach(cat =>
								{
									const option = document.createElement("option");
									option.value = cat.id.toString();
									option.textContent = cat.name;
									el.appendChild(option);
								});
								// Set initial value after options are added
								if (categoryId.v)
								{
									el.value = categoryId.v.toString();
								}
							}
						});
						// React to categoryId changes
						$(categoryId, id =>
						{
							if (id)
							{
								el.value = id.toString();
							}
							else
							{
								el.value = "";
							}
						});
						el.addEventListener("change", () =>
						{
							categoryId.v = el.value ? parseInt(el.value) : null;
						});
					}),
					$(errors, e => e.category && Span("recipe-edit__error-text", e.category)),
				]),
				Div("recipe-edit__row", [
					Div("recipe-edit__field", [
						initEl("label", "recipe-edit__label", "Сложность (1-5)"),
						Input([], "number", "3", (el) =>
						{
							difficulty.w(v => el.value = v.toString());
							el.min = "1";
							el.max = "5";
							el.addEventListener("input", () => difficulty.v = parseInt(el.value) || 3);
						}),
						$(errors, e => e.difficulty && Span("recipe-edit__error-text", e.difficulty)),
					]),
					Div("recipe-edit__field", [
						initEl("label", "recipe-edit__label", "Активное время (мин)"),
						Input([], "number", "30", (el) =>
						{
							activeTime.w(v => el.value = v.toString());
							el.min = "1";
							el.addEventListener("input", () => activeTime.v = parseInt(el.value) || 30);
						}),
						$(errors, e => e.activeTime && Span("recipe-edit__error-text", e.activeTime)),
					]),
					Div("recipe-edit__field", [
						initEl("label", "recipe-edit__label", "Общее время (мин)"),
						Input([], "number", "60", (el) =>
						{
							totalTime.w(v => el.value = v.toString());
							el.min = "1";
							el.addEventListener("input", () => totalTime.v = parseInt(el.value) || 60);
						}),
						$(errors, e => e.totalTime && Span("recipe-edit__error-text", e.totalTime)),
					]),
				]),
				Div("recipe-edit__field", [
					initEl("label", "recipe-edit__label", "Статус"),
					initEl("select", "recipe-edit__select", undefined, (el: HTMLSelectElement) =>
					{
						const options = [
							{ value: "draft", label: "Черновик" },
							{ value: "published", label: "Опубликован" },
						];
						options.forEach(opt =>
						{
							const option = document.createElement("option");
							option.value = opt.value;
							option.textContent = opt.label;
							el.appendChild(option);
						});
						status.w(v => el.value = v);
						el.addEventListener("change", () =>
						{
							status.v = el.value as any;
						});
					}),
				]),
				Div("recipe-edit__field", [
					initEl("label", "recipe-edit__label", "Главное изображение"),
					ImageUpload({
						multiple: false,
						label: "Загрузите главное изображение рецепта",
						onImagesChange: (images) =>
						{
							mainImage.v = images.length > 0 ? images[0]! : null;
						},
						showDropzone: true,
					}),
				]),
				Div("recipe-edit__field", [
					initEl("label", "recipe-edit__label", "Галерея изображений"),
					ImageUpload({
						multiple: true,
						label: "Загрузите дополнительные изображения для галереи",
						existingImages: galleryImages.v,
						onRemoveExisting: (id) =>
						{
							imagesToDelete.v = [...imagesToDelete.v, id];
							galleryImages.v = galleryImages.v.filter(img => img.id !== id);
						},
						onImagesChange: (images) =>
						{
							newGalleryImages.v = images;
						},
						showDropzone: true,
						maxFiles: 10,
					}),
				]),
				Div("recipe-edit__field", [
					initEl("label", "recipe-edit__label", "Ингредиенты"),
					$(ingredients, ingList => IngredientPicker({
						initialIngredients: ingList,
						onChange: (newIngredients) =>
						{
							ingredients.v = newIngredients;
						},
						searchPlaceholder: "Начните вводить название ингредиента...",
					})),
				]),
				$(create_recipe, e => e.error && Span("recipe-edit__error-text", e.error.msg)),
				$(update_recipe, e => e.error && Span("recipe-edit__error-text", e.error.msg)),
				Div("recipe-edit__actions", [
					Button([], "Отмена", () =>
					{
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
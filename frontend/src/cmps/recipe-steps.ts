import { Div, initEl, injectStyles } from "../littleLib.js";
import { RecipeStepDict } from "../api/types.js";

export interface RecipeStepsProps
{
	steps: RecipeStepDict[];
	emptyMessage?: string;
}

export default function RecipeSteps(props: RecipeStepsProps): HTMLDivElement
{
	const { steps, emptyMessage = "В этом рецепте пока нет шагов приготовления." } = props;

	if (steps.length === 0)
	{
		return Div([], emptyMessage);
	}

	return Div(styles.recipeStepsContainer, [
		Div(styles.recipeSteps, steps.map(step => (
			Div(styles.recipeStep, [
				Div(styles.recipeStepNumber, `Шаг ${step.step_number}`),
				Div(styles.recipeStepContent, [
					Div(styles.recipeStepText, step.text),
					step.image && initEl("img", styles.recipeStepImage, undefined, (el: HTMLImageElement) =>
					{
						el.src = step.image!;
						el.alt = `Иллюстрация шага ${step.step_number}`;
					}),
				]),
			])
		))),
	]);
}

const styles = injectStyles({
	recipeStepsContainer: {
		marginTop: "1rem",
	},
	recipeSteps: {
		display: "flex",
		flexDirection: "column",
		gap: "2rem",
	},
	recipeStep: {
		display: "flex",
		gap: "1.5rem",
		alignItems: "flex-start",
		padding: "1.5rem",
		background: "var(--primary-50)",
		borderRadius: "1rem",
		borderLeft: "4px solid var(--accent-500)",
	},
	recipeStepNumber: {
		flexShrink: 0,
		width: "3.5rem",
		height: "3.5rem",
		display: "flex",
		alignItems: "center",
		justifyContent: "center",
		background: "var(--accent-500)",
		color: "white",
		fontWeight: "bold",
		fontSize: "1.2rem",
		borderRadius: "50%",
	},
	recipeStepContent: {
		flex: 1,
		display: "flex",
		flexDirection: "column",
		gap: "1rem",
	},
	recipeStepText: {
		fontSize: "1.1rem",
		lineHeight: 1.6,
		color: "var(--primary-800)",
	},
	recipeStepImage: {
		maxWidth: "100%",
		maxHeight: "300px",
		objectFit: "cover",
		borderRadius: "0.75rem",
		boxShadow: "0 4px 8px rgba(0, 0, 0, 0.1)",
		alignSelf: "flex-start",
	},
});
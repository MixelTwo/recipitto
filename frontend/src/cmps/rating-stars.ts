import { Div, Span, injectStyles, type ElChildren } from "../littleLib.js";

export interface RatingStarsProps
{
	/** Average rating value (0-5) */
	rating: number;
	/** Number of votes (optional) */
	voteCount?: number;
	/** Size of stars (small, medium, large) */
	size?: "small" | "medium" | "large";
	/** Whether to show vote count text */
	showCount?: boolean;
	/** Whether to show rating number */
	showNumber?: boolean;
}

export default function RatingStars(props: RatingStarsProps): HTMLDivElement
{
	const { rating, voteCount, size = "medium", showCount = false, showNumber = false } = props;

	const starSize = {
		small: { fontSize: "0.9em", gap: "0.1em" },
		medium: { fontSize: "1.2em", gap: "0.15em" },
		large: { fontSize: "1.5em", gap: "0.2em" },
	}[size];

	// Render stars
	const stars: ElChildren[] = [];
	for (let i = 1; i <= 5; i++)
	{
		const isFilled = i <= Math.floor(rating);
		const isHalf = !isFilled && (i - 0.5 <= rating && rating < i);
		stars.push(
			Span([
				styles.star,
				isFilled && styles.starFilled,
				isHalf && styles.starHalf,
				{ fontSize: starSize.fontSize },
			], "★")
		);
	}

	const children: ElChildren[] = [
		Div([styles.starsContainer, { gap: starSize.gap }], stars as ElChildren),
	];

	if (showNumber)
	{
		children.push(Span(styles.ratingNumber, rating.toFixed(1)));
	}
	if (showCount && voteCount !== undefined)
	{
		children.push(Span(styles.voteCount, `(${voteCount})`));
	}

	return Div(styles.container, children as ElChildren);
}

const styles = injectStyles({
	container: {
		display: "flex",
		alignItems: "center",
		gap: "0.5em",
	},
	starsContainer: {
		display: "flex",
		alignItems: "center",
	},
	star: {
		color: "var(--gray-400)",
		lineHeight: "1",
	},
	starFilled: {
		color: "var(--primary-400)",
	},
	starHalf: {
		background: "linear-gradient(90deg, var(--primary-400) 50%, var(--gray-400) 50%)",
		WebkitBackgroundClip: "text",
		WebkitTextFillColor: "transparent",
	},
	ratingNumber: {
		fontSize: "0.9em",
		fontWeight: "bold",
		color: "var(--gray-700)",
	},
	voteCount: {
		fontSize: "0.85em",
		color: "var(--gray-600)",
	},
});
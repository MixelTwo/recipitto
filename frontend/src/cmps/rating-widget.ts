import { $, Div, Span, Button, injectStyles, type ElChildren, State } from "../littleLib.js";
import { query_recipe_ratings, query_my_rating, mutate_rate_recipe, mutate_delete_rating } from "../api/client.js";
import { RatingStatsResponse, RatingResponse } from "../api/types.js";

export interface RatingWidgetProps
{
    /** Recipe ID */
    recipeId: number;
    /** Initial average rating (optional, will be fetched if not provided) */
    initialRating?: number;
    /** Initial vote count (optional) */
    initialCount?: number;
    /** Whether the widget is interactive (user can rate) */
    interactive?: boolean;
    /** Callback when user rates (rating submitted) */
    onRate?: (rating: number) => void;
    /** Callback when user removes rating */
    onRemove?: () => void;
}

export default function RatingWidget(props: RatingWidgetProps): HTMLDivElement
{
    const { recipeId, interactive = true, onRate, onRemove } = props;

    // State for average rating and count
    const averageRating = $(props.initialRating ?? 0);
    const voteCount = $(props.initialCount ?? 0);
    // State for user's current rating (null if not rated)
    const userRating = $<number | null>(null);
    // State for hover preview
    const hoverRating = $<number | null>(null);

    // Fetch rating stats and user rating
    const ratingsQuery = query_recipe_ratings(recipeId);
    const myRatingQuery = query_my_rating(recipeId);

    // Update state when queries resolve
    $(ratingsQuery, (q) =>
    {
        if (q.data)
        {
            averageRating.v = q.data.average;
            voteCount.v = q.data.count;
        }
    });
    $(myRatingQuery, (q) =>
    {
        if (q.data)
        {
            userRating.v = q.data.rating;
        } else
        {
            userRating.v = null;
        }
    });

    // Handle star click
    const handleStarClick = (rating: number) =>
    {
        if (!interactive) return;
        if (userRating.v === rating)
        {
            // Remove rating if clicking same star
            const result = mutate_delete_rating(recipeId).v.fetch();
            if (result instanceof Promise)
            {
                result.then(() =>
                {
                    userRating.v = null;
                    ratingsQuery.v.refetch();
                    onRemove?.();
                });
            } else
            {
                userRating.v = null;
                ratingsQuery.v.refetch();
                onRemove?.();
            }
        } else
        {
            // Submit new rating
            const result = mutate_rate_recipe(recipeId).v.fetch({ rating });
            if (result instanceof Promise)
            {
                result.then(() =>
                {
                    userRating.v = rating;
                    ratingsQuery.v.refetch();
                    onRate?.(rating);
                });
            } else
            {
                userRating.v = rating;
                ratingsQuery.v.refetch();
                onRate?.(rating);
            }
        }
    };

    // Handle star hover
    const handleStarHover = (rating: number | null) =>
    {
        if (!interactive) return;
        hoverRating.v = rating;
    };

    // Reactive star rendering based on averageRating, userRating, and hoverRating
    const starElements = $(averageRating, (avg) =>
    {
        const rating = hoverRating.v ?? userRating.v ?? avg;
        const stars: ElChildren[] = [];
        for (let i = 1; i <= 5; i++)
        {
            const isFilled = i <= Math.floor(rating);
            const isHalf = !isFilled && (i - 0.5 <= rating && rating < i);
            stars.push(
                Button(
                    [
                        styles.star,
                        isFilled && styles.starFilled,
                        isHalf && styles.starHalf,
                        interactive && styles.starInteractive,
                    ],
                    "★",
                    () => handleStarClick(i),
                    (btn) =>
                    {
                        btn.addEventListener("mouseenter", () => handleStarHover(i));
                        btn.addEventListener("mouseleave", () => handleStarHover(null));
                        btn.title = `Rate ${i} star${i > 1 ? "s" : ""}`;
                    }
                )
            );
        }
        return Div(styles.starsContainer, stars as ElChildren);
    });

    // Reactive text
    const ratingText = $(voteCount, (count) =>
    {
        if (count === 0)
        {
            return Span(styles.text, "No ratings yet");
        }
        const avg = averageRating.v.toFixed(1);
        return Span(styles.text, `${avg} (${count} rating${count !== 1 ? "s" : ""})`);
    });

    // Reactive user rating indicator
    const userRatingIndicator = $(userRating, (ur) =>
    {
        if (!interactive || ur === null) return null;
        return Span(styles.userRating, `Your rating: ${ur} ★`);
    });

    return Div(styles.container, [
        starElements,
        Div(styles.infoContainer, [
            ratingText,
            userRatingIndicator,
        ]),
    ]);
}

const styles = injectStyles({
    container: {
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
        gap: "0.5em",
    },
    starsContainer: {
        display: "flex",
        gap: "0.25em",
    },
    star: {
        background: "none",
        border: "none",
        fontSize: "1.5em",
        color: "var(--gray-400)",
        cursor: "default",
        transition: "color 0.2s, transform 0.2s",
        padding: "0",
        lineHeight: "1",
    },
    starInteractive: {
        cursor: "pointer",
    },
    starFilled: {
        color: "var(--primary-400)",
    },
    starHalf: {
        background: "linear-gradient(90deg, var(--primary-400) 50%, var(--gray-400) 50%)",
        WebkitBackgroundClip: "text",
        WebkitTextFillColor: "transparent",
    },
    infoContainer: {
        display: "flex",
        flexDirection: "column",
        gap: "0.25em",
        fontSize: "0.9em",
        color: "var(--gray-600)",
    },
    text: {
        fontWeight: "500",
    },
    userRating: {
        fontSize: "0.85em",
        color: "var(--primary-500)",
        fontStyle: "italic",
    },
});
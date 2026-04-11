import { $, Button, Div, Span, initEl, injectStyles, type ElChildren, type State, If } from "../littleLib.js";

export interface PaginationProps
{
	/** Current page number (1-based) */
	currentPage: number | State<number>;
	/** Total number of items */
	totalItems: number | State<number>;
	/** Number of items per page */
	pageSize: number | State<number>;
	/** Available page size options */
	pageSizeOptions?: number[];
	/** Callback when page changes */
	onPageChange: (page: number) => void;
	/** Callback when page size changes */
	onPageSizeChange?: (pageSize: number) => void;
	/** Maximum number of page buttons to show (excluding first/last) */
	maxPageButtons?: number;
	/** Whether to show page size selector */
	showPageSizeSelector?: boolean;
	/** Whether to show first/last page buttons */
	showFirstLast?: boolean;
	/** Whether to show total items info */
	showTotalInfo?: boolean;
}

/**
 * Pagination component for navigating through paginated data.
 * Supports page size selection, first/last page buttons, and total items info.
 *
 * @param props - Configuration properties
 * @returns A div element containing the pagination controls
 */
export default function Pagination(props: PaginationProps): HTMLDivElement
{
	const {
		currentPage,
		totalItems,
		pageSize,
		pageSizeOptions = [10, 20, 50, 100],
		onPageChange,
		onPageSizeChange,
		maxPageButtons = 5,
		showPageSizeSelector = true,
		showFirstLast = true,
		showTotalInfo = true,
	} = props;

	// Convert props to State if they aren't already
	const currentPageState = typeof currentPage === "number" ? $(currentPage) : currentPage;
	const totalItemsState = typeof totalItems === "number" ? $(totalItems) : totalItems;
	const pageSizeState = typeof pageSize === "number" ? $(pageSize) : pageSize;

	// Helper to compute total pages
	const computeTotalPages = () =>
		Math.max(1, Math.ceil(totalItemsState.v / pageSizeState.v));

	const handlePageChange = (page: number) =>
	{
		const total = computeTotalPages();
		if (page < 1 || page > total) return;
		currentPageState.v = page;
		onPageChange(page);
	};

	const handlePageSizeChange = (size: number) =>
	{
		pageSizeState.v = size;
		// When page size changes, we might need to adjust current page
		const newTotalPages = Math.max(1, Math.ceil(totalItemsState.v / size));
		if (currentPageState.v > newTotalPages)
		{
			currentPageState.v = newTotalPages;
			onPageChange(newTotalPages);
		}
		if (onPageSizeChange) onPageSizeChange(size);
	};

	// Compute page range for buttons
	const getPageRange = (current: number, total: number) =>
	{
		if (total <= 1) return [];
		const half = Math.floor(maxPageButtons / 2);
		let start = Math.max(1, current - half);
		let end = Math.min(total, start + maxPageButtons - 1);

		// Adjust start if we're near the end
		if (end - start + 1 < maxPageButtons)
		{
			start = Math.max(1, end - maxPageButtons + 1);
		}

		const range: number[] = [];
		for (let i = start; i <= end; i++) range.push(i);
		return range;
	};

	return Div(styles.container, [
		// Left side: total info and page size selector
		Div(styles.leftSection, [
			// Total items info
			If($(showTotalInfo),
				() => $(totalItemsState, total => total > 0 ?
					Span(styles.totalInfo, $(totalItemsState, total =>
						$(pageSizeState, size =>
							$(currentPageState, page =>
							{
								const start = (page - 1) * size + 1;
								const end = Math.min(total, page * size);
								return `Показано ${start}-${end} из ${total}`;
							})
						)
					)) : null
				)
			),
			// Page size selector
			If($(showPageSizeSelector),
				() => Div(styles.pageSizeSelector, [
					Span(styles.pageSizeLabel, "На странице:"),
					initEl("select", styles.pageSizeSelect, undefined, (el: HTMLSelectElement) =>
					{
						// Populate options
						pageSizeOptions.forEach(opt =>
						{
							const option = document.createElement("option");
							option.value = opt.toString();
							option.textContent = opt.toString();
							el.appendChild(option);
						});
						// Set current value
						pageSizeState.w(v => el.value = v.toString());
						el.value = pageSizeState.v.toString();
						// Handle change
						el.addEventListener("change", () =>
						{
							const val = parseInt(el.value);
							if (!isNaN(val)) handlePageSizeChange(val);
						});
					}),
				])
			),
		]),

		// Center: page navigation
		Div(styles.centerSection, [
			// First page button
			If($(showFirstLast),
				() => Button([styles.navButton, $(currentPageState, page => page <= 1 ? styles.navButtonDisabled : "")],
					"«",
					() => handlePageChange(1),
					el => currentPageState.w(p => el.disabled = p <= 1)
				)
			),
			// Previous page button
			Button([styles.navButton, $(currentPageState, page => page <= 1 ? styles.navButtonDisabled : "")],
				"‹",
				() => handlePageChange(currentPageState.v - 1),
				el => currentPageState.w(p => el.disabled = p <= 1)
			),
			// Page number buttons - compute range reactively
			Div(styles.pageButtons, [
				$(currentPageState, current =>
					$(totalItemsState, totalItems =>
						$(pageSizeState, size =>
						{
							const totalPages = Math.max(1, Math.ceil(totalItems / size));
							const range = getPageRange(current, totalPages);
							return range.map(page =>
								Button([
									styles.pageButton,
									$(currentPageState, cp => cp === page ? styles.pageButtonActive : "")
								],
									page.toString(),
									() => handlePageChange(page)
								)
							);
						})
					)
				)
			]),
			// Next page button
			Button([styles.navButton, $(currentPageState, current =>
				$(totalItemsState, totalItems =>
					$(pageSizeState, size =>
					{
						const totalPages = Math.max(1, Math.ceil(totalItems / size));
						return current >= totalPages ? styles.navButtonDisabled : "";
					})
				)
			)],
				"›",
				() => handlePageChange(currentPageState.v + 1),
				el => currentPageState.w(current =>
					$(totalItemsState, totalItems =>
						$(pageSizeState, size =>
						{
							const totalPages = Math.max(1, Math.ceil(totalItems / size));
							el.disabled = current >= totalPages;
						})
					)
				)
			),
			// Last page button
			If($(showFirstLast),
				() => Button([styles.navButton, $(currentPageState, current =>
					$(totalItemsState, totalItems =>
						$(pageSizeState, size =>
						{
							const totalPages = Math.max(1, Math.ceil(totalItems / size));
							return current >= totalPages ? styles.navButtonDisabled : "";
						})
					)
				)],
					"»",
					() =>
					{
						const totalPages = computeTotalPages();
						handlePageChange(totalPages);
					},
					el => currentPageState.w(current =>
						$(totalItemsState, totalItems =>
							$(pageSizeState, size =>
							{
								const totalPages = Math.max(1, Math.ceil(totalItems / size));
								el.disabled = current >= totalPages;
							})
						)
					)
				)
			),
		]),

		// Right side: current page indicator
		Div(styles.rightSection, [
			Div(styles.pageIndicator, [
				Span(styles.pageIndicatorText, "Страница"),
				initEl("input", styles.pageInput, undefined, (el: HTMLInputElement) =>
				{
					el.type = "number";
					el.min = "1";
					// Set current value and max
					currentPageState.w(v => el.value = v.toString());
					// Update max when total pages changes
					const updateMax = () =>
					{
						const total = computeTotalPages();
						el.max = total.toString();
					};
					totalItemsState.w(updateMax);
					pageSizeState.w(updateMax);
					// Handle change on blur/enter
					const updatePage = () =>
					{
						const val = parseInt(el.value);
						const total = computeTotalPages();
						if (!isNaN(val) && val >= 1 && val <= total)
						{
							handlePageChange(val);
						}
						else
						{
							// Reset to current page if invalid
							currentPageState.w(v => el.value = v.toString());
						}
					};
					el.addEventListener("change", updatePage);
					el.addEventListener("keydown", (e) =>
					{
						if (e.key === "Enter") updatePage();
					});
				}),
				Span(styles.pageIndicatorText, $(totalItemsState, totalItems =>
					$(pageSizeState, size =>
					{
						const totalPages = Math.max(1, Math.ceil(totalItems / size));
						return ` из ${totalPages}`;
					})
				)),
			]),
		]),
	]);
}

const styles = injectStyles({
	container: {
		display: "flex",
		alignItems: "center",
		justifyContent: "space-between",
		flexWrap: "wrap",
		gap: "1rem",
		padding: "1rem 0",
		borderTop: "1px solid var(--border-color)",
		marginTop: "1rem",
	},
	leftSection: {
		display: "flex",
		alignItems: "center",
		gap: "1rem",
		flexWrap: "wrap",
	},
	centerSection: {
		display: "flex",
		alignItems: "center",
		gap: "0.25rem",
		flexWrap: "wrap",
		justifyContent: "center",
	},
	rightSection: {
		display: "flex",
		alignItems: "center",
		gap: "0.5rem",
		flexWrap: "wrap",
	},
	totalInfo: {
		fontSize: "0.9rem",
		color: "var(--text-secondary)",
	},
	pageSizeSelector: {
		display: "flex",
		alignItems: "center",
		gap: "0.5rem",
	},
	pageSizeLabel: {
		fontSize: "0.9rem",
		color: "var(--text-secondary)",
	},
	pageSizeSelect: {
		padding: "0.25rem 0.5rem",
		borderRadius: "0.25rem",
		border: "1px solid var(--border-color)",
		background: "var(--bg-primary)",
		color: "var(--text-primary)",
		fontSize: "0.9rem",
	},
	navButton: {
		padding: "0.375rem 0.75rem",
		borderRadius: "0.25rem",
		border: "1px solid var(--border-color)",
		background: "var(--bg-primary)",
		color: "var(--text-primary)",
		fontSize: "0.9rem",
		cursor: "pointer",
		transition: "background 0.2s, border-color 0.2s",
		"&:hover:not(:disabled)": {
			background: "var(--primary-100)",
			borderColor: "var(--primary-300)",
		},
		"&:disabled": {
			opacity: 0.5,
			cursor: "not-allowed",
		},
	},
	navButtonDisabled: {
		opacity: 0.5,
		cursor: "not-allowed",
	},
	pageButtons: {
		display: "flex",
		gap: "0.25rem",
	},
	pageButton: {
		minWidth: "2.25rem",
		padding: "0.375rem 0.5rem",
		borderRadius: "0.25rem",
		border: "1px solid var(--border-color)",
		background: "var(--bg-primary)",
		color: "var(--text-primary)",
		fontSize: "0.9rem",
		cursor: "pointer",
		transition: "background 0.2s, border-color 0.2s",
		"&:hover": {
			background: "var(--primary-100)",
			borderColor: "var(--primary-300)",
		},
	},
	pageButtonActive: {
		background: "var(--primary-400)",
		color: "white",
		borderColor: "var(--primary-400)",
		"&:hover": {
			background: "var(--primary-500)",
			borderColor: "var(--primary-500)",
		},
	},
	pageIndicator: {
		display: "flex",
		alignItems: "center",
		gap: "0.5rem",
	},
	pageIndicatorText: {
		fontSize: "0.9rem",
		color: "var(--text-secondary)",
	},
	pageInput: {
		width: "3rem",
		padding: "0.25rem 0.5rem",
		borderRadius: "0.25rem",
		border: "1px solid var(--border-color)",
		background: "var(--bg-primary)",
		color: "var(--text-primary)",
		fontSize: "0.9rem",
		textAlign: "center",
	},
});
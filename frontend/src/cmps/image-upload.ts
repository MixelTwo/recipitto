import { $, Button, Div, Span, Input, injectStyles, type ElChildren, type ElClasses, State } from "../littleLib.js";
import { type ImageJson, type RecipeImageDict } from "../api/types.js";

export interface ImageUploadProps
{
	/** Whether to allow multiple file selection */
	multiple?: boolean;
	/** Callback when images are added (returns ImageJson array) */
	onImagesChange?: (images: ImageJson[]) => void;
	/** Existing images to display as preview (for gallery) */
	existingImages?: RecipeImageDict[];
	/** Callback when an existing image is removed */
	onRemoveExisting?: (id: number) => void;
	/** Maximum number of files allowed (only for multiple) */
	maxFiles?: number;
	/** Label text */
	label?: string;
	/** Whether to show drag-and-drop area */
	showDropzone?: boolean;
	/** Accepted file types (default: image/*) */
	accept?: string;
}

export default function ImageUpload(props: ImageUploadProps): HTMLDivElement
{
	const files = $(<File[]>[]);
	const previews = $(<string[]>[]);
	const isDragging = $(false);
	const error = $(<string | null>(null));

	const readFileAsDataURL = (file: File): Promise<string> =>
	{
		return new Promise((resolve, reject) =>
		{
			const reader = new FileReader();
			reader.onload = () => resolve(reader.result as string);
			reader.onerror = reject;
			reader.readAsDataURL(file);
		});
	};

	const fileToImageJson = async (file: File): Promise<ImageJson> =>
	{
		const data = await readFileAsDataURL(file);
		return {
			name: file.name,
			data,
		};
	};

	const handleFiles = async (fileList: FileList) =>
	{
		const newFiles = Array.from(fileList);
		if (props.maxFiles && files.v.length + newFiles.length > props.maxFiles)
		{
			error.v = `Maximum ${props.maxFiles} files allowed`;
			return;
		}

		// Filter to images only
		const imageFiles = newFiles.filter(f => f.type.startsWith('image/'));
		if (imageFiles.length === 0)
		{
			error.v = "Please select image files only";
			return;
		}

		error.v = null;
		const newPreviews: string[] = [];
		const newImageJsons: ImageJson[] = [];

		for (const file of imageFiles)
		{
			const preview = URL.createObjectURL(file);
			newPreviews.push(preview);
			const imageJson = await fileToImageJson(file);
			newImageJsons.push(imageJson);
		}

		files.v = [...files.v, ...imageFiles];
		previews.v = [...previews.v, ...newPreviews];

		if (props.onImagesChange)
		{
			const allImages = await Promise.all(files.v.map(fileToImageJson));
			props.onImagesChange(allImages);
		}
	};

	const handleFileInput = (e: Event) =>
	{
		const input = e.target as HTMLInputElement;
		if (input.files)
		{
			handleFiles(input.files);
			input.value = ''; // Reset to allow selecting same file again
		}
	};

	const removeFile = (index: number) =>
	{
		const preview = previews.v[index];
		if (preview) URL.revokeObjectURL(preview); // Clean up object URL
		files.v.splice(index, 1);
		previews.v.splice(index, 1);
		files.v = [...files.v];
		previews.v = [...previews.v];
		if (props.onImagesChange)
		{
			Promise.all(files.v.map(fileToImageJson)).then(images =>
			{
				props.onImagesChange!(images);
			});
		}
	};

	const removeExisting = (id: number) =>
	{
		if (props.onRemoveExisting)
		{
			props.onRemoveExisting(id);
		}
	};

	// Drag and drop handlers
	const handleDragOver = (e: DragEvent) =>
	{
		e.preventDefault();
		isDragging.v = true;
	};

	const handleDragLeave = () =>
	{
		isDragging.v = false;
	};

	const handleDrop = (e: DragEvent) =>
	{
		e.preventDefault();
		isDragging.v = false;
		if (e.dataTransfer?.files)
		{
			handleFiles(e.dataTransfer.files);
		}
	};

	// Create file input element
	const fileInput = Input(styles.fileInput, "file", props.accept || "image/*", el =>
	{
		el.multiple = props.multiple || false;
		el.addEventListener("change", handleFileInput);
	});

	const dropzone = Div(
		$(isDragging, dragging => dragging ? styles.dropzoneDragging : styles.dropzone),
		[
			Div(styles.dropzoneContent, [
				Span(styles.dropzoneIcon, "📁"),
				Span(styles.dropzoneText, "Drop images here"),
				Span(styles.dropzoneHint, "or click to browse"),
			]),
			fileInput,
		],
		(el: HTMLDivElement) =>
		{
			el.addEventListener("dragover", handleDragOver);
			el.addEventListener("dragleave", handleDragLeave);
			el.addEventListener("drop", handleDrop);
			el.addEventListener("click", () => fileInput.click());
		}
	);

	const browseButton = Button(styles.browseButton, "Choose Images", () =>
	{
		const input = document.createElement('input');
		input.type = 'file';
		input.multiple = props.multiple || false;
		input.accept = props.accept || "image/*";
		input.addEventListener('change', handleFileInput);
		input.click();
	});

	return Div(styles.container, [
		props.label && Span(styles.label, props.label),
		props.showDropzone !== false ? dropzone : browseButton,
		$(error, err => err ? Div(styles.error, err) : null),
		// Preview of newly added files
		Div(styles.previewsContainer,
			...previews.v.map((preview, index) =>
				Div(styles.previewItem, [
					// Create img element manually
					(() =>
					{
						const img = document.createElement('img');
						img.className = styles.previewImage;
						img.src = preview;
						img.alt = files.v[index]?.name || 'Preview';
						return img;
					})(),
					Button(styles.removeButton, "×", () => removeFile(index)),
				])
			)
		),
		// Existing images (for gallery)
		props.existingImages && props.existingImages.length > 0 ? Div(styles.existingContainer, [
			Span(styles.existingLabel, "Existing images:"),
			Div(styles.existingGrid,
				...props.existingImages.map(img =>
					Div(styles.existingItem, [
						(() =>
						{
							const imgEl = document.createElement('img');
							imgEl.className = styles.existingImage;
							imgEl.src = `/api/img/${img.image_id}`;
							imgEl.alt = `Existing image ${img.id}`;
							return imgEl;
						})(),
						props.onRemoveExisting ? Button(styles.removeExistingButton, "Remove", () => removeExisting(img.id)) : null,
					])
				)
			),
		]) : null,
	]);
}

const styles = injectStyles({
	container: {
		marginBottom: "1.5rem",
	},
	label: {
		display: "block",
		marginBottom: "0.5rem",
		fontWeight: "600",
		fontSize: "0.875rem",
	},
	dropzone: {
		border: "2px dashed var(--primary-300)",
		borderRadius: "8px",
		padding: "2rem",
		textAlign: "center",
		backgroundColor: "var(--primary-50)",
		transition: "border-color 0.2s, background-color 0.2s",
		cursor: "pointer",
	},
	dropzoneDragging: {
		border: "2px dashed var(--primary-500)",
		borderRadius: "8px",
		padding: "2rem",
		textAlign: "center",
		backgroundColor: "var(--primary-100)",
		transition: "border-color 0.2s, background-color 0.2s",
		cursor: "pointer",
	},
	dropzoneContent: {
		display: "flex",
		flexDirection: "column",
		alignItems: "center",
		gap: "0.5rem",
	},
	dropzoneIcon: {
		fontSize: "2rem",
		marginBottom: "0.5rem",
	},
	dropzoneText: {
		fontSize: "1rem",
		fontWeight: "600",
	},
	dropzoneHint: {
		fontSize: "0.875rem",
		color: "var(--text-secondary)",
	},
	fileInput: {
		display: "none",
	},
	browseButton: {
		padding: "0.5rem 1rem",
		borderRadius: "0.25rem",
		backgroundColor: "var(--primary-500)",
		color: "white",
		fontWeight: "600",
		cursor: "pointer",
		border: "none",
		fontSize: "0.875rem",
	},
	"browseButton:hover": {
		backgroundColor: "var(--primary-600)",
	},
	error: {
		marginTop: "0.5rem",
		padding: "0.5rem",
		backgroundColor: "#ffebee",
		color: "#c62828",
		borderRadius: "0.25rem",
		fontSize: "0.875rem",
	},
	previewsContainer: {
		display: "flex",
		flexWrap: "wrap",
		gap: "1rem",
		marginTop: "1rem",
	},
	previewItem: {
		position: "relative",
		width: "100px",
		height: "100px",
	},
	previewImage: {
		width: "100%",
		height: "100%",
		objectFit: "cover",
		borderRadius: "0.25rem",
		border: "1px solid var(--primary-200)",
	},
	removeButton: {
		position: "absolute",
		top: "-0.5rem",
		right: "-0.5rem",
		width: "1.5rem",
		height: "1.5rem",
		borderRadius: "50%",
		backgroundColor: "#f44336",
		color: "white",
		border: "none",
		cursor: "pointer",
		fontSize: "0.75rem",
		display: "flex",
		alignItems: "center",
		justifyContent: "center",
		padding: 0,
	},
	existingContainer: {
		marginTop: "1.5rem",
	},
	existingLabel: {
		display: "block",
		marginBottom: "0.5rem",
		fontWeight: "600",
		fontSize: "0.875rem",
	},
	existingGrid: {
		display: "grid",
		gridTemplateColumns: "repeat(auto-fill, minmax(100px, 1fr))",
		gap: "1rem",
	},
	existingItem: {
		position: "relative",
		width: "100px",
		height: "100px",
	},
	existingImage: {
		width: "100%",
		height: "100%",
		objectFit: "cover",
		borderRadius: "0.25rem",
		border: "1px solid var(--primary-200)",
	},
	removeExistingButton: {
		position: "absolute",
		bottom: "0",
		left: "0",
		right: "0",
		padding: "0.25rem",
		backgroundColor: "rgba(0,0,0,0.7)",
		color: "white",
		border: "none",
		cursor: "pointer",
		fontSize: "0.75rem",
		borderRadius: "0 0 0.25rem 0.25rem",
	},
});
import { $, Button, Div, Input, Span, injectStyles, type ElChildren, initEl } from "../littleLib.js";
import { type User, type UserUpdateRequest, type ImageJson } from "../api/types.js";
import { mutate_update_user } from "../api/client.js";
import Spinner from "./spinner.js";
import ImageUpload from "./image-upload.js";

export interface ProfileEditModalProps
{
	user: User;
	onSuccess?: (updatedUser: User) => void;
	onCancel?: () => void;
}

export default function ProfileEditModal(props: ProfileEditModalProps): ElChildren
{
	const name = $(props.user.name);
	const avatar = $(<ImageJson | null>(null));
	const avatarPreview = $(props.user.avatar);
	const validationError = $(<string | null>(null));
	const updateMutation = mutate_update_user();

	const handleAvatarChange = (images: ImageJson[]) =>
	{
		if (images.length > 0 && images[0])
		{
			avatar.v = images[0];
			avatarPreview.v = images[0].data;
		}
		else
		{
			avatar.v = null;
			avatarPreview.v = null;
		}
	};

	const handleSubmit = async () =>
	{
		if (!name.v.trim())
		{
			validationError.v = "Введите имя";
			return;
		}
		validationError.v = null;

		// Build update request
		const updateData: UserUpdateRequest = {
			name: name.v !== props.user.name ? name.v : undefined,
			avatar: avatar.v !== null ? avatar.v : undefined,
		};

		// Call API mutation
		const result = updateMutation.v.fetch(updateData);
		const handleResult = (updatedUser: User | null) =>
		{
			if (updatedUser && !updateMutation.v.error && props.onSuccess)
			{
				props.onSuccess(updatedUser);
			}
		};
		if (result instanceof Promise)
		{
			result.then(handleResult);
		}
		else
		{
			// Synchronous result (cached)
			handleResult(result);
		}
	};

	const handleKeyPress = (e: KeyboardEvent) =>
	{
		if (e.key === "Enter")
		{
			handleSubmit();
		}
	};

	return [
		Div(styles.overlay, [
			$(updateMutation, m => m.isLoading && Spinner()),
			Div(styles.modal, [
				Div(styles.header, [
					Span(styles.title, "Редактировать профиль"),
					Button(styles.close, "×", () => props.onCancel?.()),
				]),
				Div([], [
					Div(styles.field, [
						Span(styles.label, "Аватар"),
						$(avatarPreview, preview =>
							preview
								? initEl("img", styles.avatarPreview, undefined, (el: HTMLImageElement) =>
								{
									el.src = preview;
									el.alt = "Аватар";
								})
								: Div(styles.avatarPlaceholder, props.user.name.slice(0, 1).toUpperCase())
						),
						ImageUpload({
							multiple: false,
							onImagesChange: handleAvatarChange,
							label: "Загрузить новый аватар",
							showDropzone: true,
							accept: "image/*",
						}),
					]),
					Div(styles.field, [
						Span(styles.label, "Имя"),
						Input(styles.input, "text", "Введите ваше имя", (el) =>
						{
							el.value = name.v;
							el.addEventListener("input", (e) =>
							{
								name.v = (e.target as HTMLInputElement).value;
							});
							el.addEventListener("keypress", handleKeyPress);
						}),
					]),
					$(validationError, err => err && Div(styles.error, err)),
					$(updateMutation, m => m.error && Div(styles.error, "Ошибка при сохранении: " + (m.error.msg || m.error.exc?.message || "Неизвестная ошибка"))),
					Div(styles.actions, [
						Button([styles.button, styles.buttonSecondary], "Отмена", () => props.onCancel?.()),
						Button([styles.button, styles.buttonPrimary], "Сохранить", handleSubmit),
					]),
				]),
			]),
		]),
	];
}

const styles = injectStyles({
	overlay: {
		position: "fixed",
		top: "0",
		left: "0",
		right: "0",
		bottom: "0",
		backgroundColor: "rgba(0, 0, 0, 0.5)",
		display: "flex",
		alignItems: "center",
		justifyContent: "center",
		zIndex: "1000",
	},
	modal: {
		backgroundColor: "var(--background)",
		borderRadius: "8px",
		boxShadow: "0 4px 20px rgba(0, 0, 0, 0.15)",
		width: "90%",
		maxWidth: "500px",
		maxHeight: "90vh",
		overflowY: "auto",
		padding: "24px",
		position: "relative",
	},
	header: {
		display: "flex",
		justifyContent: "space-between",
		alignItems: "center",
		marginBottom: "20px",
	},
	title: {
		fontSize: "1.5rem",
		fontWeight: "600",
		color: "var(--text-primary)",
	},
	close: {
		background: "none",
		border: "none",
		fontSize: "1.5rem",
		cursor: "pointer",
		color: "var(--text-secondary)",
		"&:hover": {
			color: "var(--text-primary)",
		},
	},
	field: {
		marginBottom: "16px",
	},
	label: {
		display: "block",
		marginBottom: "4px",
		fontSize: "0.875rem",
		color: "var(--text-secondary)",
	},
	input: {
		width: "100%",
		padding: "8px 12px",
		border: "1px solid var(--border)",
		borderRadius: "4px",
		fontSize: "1rem",
		backgroundColor: "var(--background)",
		color: "var(--text-primary)",
		"&:focus": {
			outline: "none",
			borderColor: "var(--primary)",
		},
	},
	avatarPreview: {
		width: "80px",
		height: "80px",
		borderRadius: "50%",
		objectFit: "cover",
		marginBottom: "12px",
		border: "2px solid var(--border)",
	},
	avatarPlaceholder: {
		width: "80px",
		height: "80px",
		borderRadius: "50%",
		backgroundColor: "var(--surface)",
		display: "flex",
		alignItems: "center",
		justifyContent: "center",
		fontSize: "1.5rem",
		color: "var(--text-secondary)",
		marginBottom: "12px",
	},
	actions: {
		display: "flex",
		justifyContent: "flex-end",
		gap: "12px",
		marginTop: "24px",
	},
	button: {
		padding: "8px 16px",
		borderRadius: "4px",
		fontSize: "0.875rem",
		fontWeight: "500",
		cursor: "pointer",
		border: "none",
		transition: "background-color 0.2s",
	},
	buttonPrimary: {
		backgroundColor: "var(--primary)",
		color: "white",
		"&:hover": {
			backgroundColor: "var(--primary-dark)",
		},
	},
	buttonSecondary: {
		backgroundColor: "var(--surface)",
		color: "var(--text-primary)",
		border: "1px solid var(--border)",
		"&:hover": {
			backgroundColor: "var(--background)",
		},
	},
	error: {
		color: "var(--error)",
		fontSize: "0.875rem",
		marginTop: "4px",
	},
});
import { query_auth } from "../api/client.js";
import { $, Button, Div, Input, Span, injectStyles, type ElChildren } from "../littleLib.js";
import Spinner from "./spinner.js";

export interface LoginFormProps
{
	/** Callback invoked after successful authentication */
	onSuccess?: () => void;
	/** Callback invoked when the user cancels the login form */
	onCancel?: () => void;
}

/**
 * Login form component with username/password fields, validation, and API integration.
 *
 * @param props - Configuration properties
 * @returns Form elements as ElChildren
 */
export default function LoginForm(props: LoginFormProps): ElChildren
{
	const login = query_auth();

	// Form state
	const username = $("");
	const password = $("");
	const validationError = $<string | null>(null);

	// Derived states
	const isLoading = $(login, state => state.isLoading);
	const error = $(login, state => state.error);

	const handleSubmit = () =>
	{
		// Basic validation
		if (!username.v.trim())
		{
			validationError.v = "Введите логин";
			return;
		}
		if (!password.v.trim())
		{
			validationError.v = "Введите пароль";
			return;
		}
		validationError.v = null;
		// Call login API
		const result = login.v.fetch(username.v, password.v);
		if (result instanceof Promise)
		{
			result.then(() =>
			{
				if (!login.v.error && props.onSuccess)
				{
					props.onSuccess();
				}
			});
		} else
		{
			// Synchronous result (cached)
			if (!login.v.error && props.onSuccess)
			{
				props.onSuccess();
			}
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
			$(login, v => v.isLoading && Spinner()),
			Div(styles.modal, [
				Div(styles.header, [
					Span(styles.title, "Вход в аккаунт"),
					Button(styles.close, "×", () => props.onCancel?.()),
				]),
				Div([], [
					Div([], [
						Div(styles.field, [
							Span(styles.label, "Логин"),
							Input(styles.input, "text", "Введите логин", (el) =>
							{
								el.value = username.v;
								el.addEventListener("input", (e) =>
								{
									username.v = (e.target as HTMLInputElement).value;
								});
								el.addEventListener("keypress", handleKeyPress);
							}),
						]),
						Div(styles.field, [
							Span(styles.label, "Пароль"),
							Input(styles.input, "password", "Введите пароль", (el) =>
							{
								el.value = password.v;
								el.addEventListener("input", (e) =>
								{
									password.v = (e.target as HTMLInputElement).value;
								});
								el.addEventListener("keypress", handleKeyPress);
							}),
						]),
						$(validationError, (err) =>
							err ? Div(styles.error, err) : null
						),
						$(error, (err) =>
							err ? Div(styles.error, err.msg) : null
						),
						Div(styles.actions, [
							Button([styles.button, styles.buttonCancel], "Отмена", () => props.onCancel?.()),
							Button(
								[styles.button, styles.buttonSubmit],
								$(isLoading, loading => loading ? "Загрузка..." : "Войти"),
								() => !isLoading.v && handleSubmit(),
								(btn) =>
								{
									// Update disabled state reactively
									isLoading.w(loading =>
									{
										btn.disabled = loading;
									});
								}
							),
						]),
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
		zIndex: "999",
	},
	modal: {
		backgroundColor: "var(--background)",
		borderRadius: "0.5rem",
		boxShadow: "0 4px 20px rgba(0, 0, 0, 0.2)",
		width: "100%",
		maxWidth: "400px",
		padding: "1.5rem",
	},
	header: {
		display: "flex",
		justifyContent: "space-between",
		alignItems: "center",
		marginBottom: "1.5rem",
	},
	title: {
		fontSize: "1.5rem",
		fontWeight: "bold",
	},
	close: {
		fontSize: "1.5rem",
		lineHeight: "1",
		padding: "0.25rem 0.5rem",
		borderRadius: "0.25rem",
		background: "none",
		color: "var(--text)",
	},
	"close:hover": {
		backgroundColor: "var(--primary-100)",
	},
	field: {
		marginBottom: "1rem",
	},
	label: {
		display: "block",
		marginBottom: "0.5rem",
		fontWeight: "600",
	},
	input: {
		width: "100%",
		padding: "0.5rem",
		border: "2px solid var(--primary-200)",
		borderRadius: "0.25rem",
		backgroundColor: "var(--primary-50)",
		color: "var(--text)",
		fontSize: "1rem",
	},
	"input:focus": {
		outline: "none",
		borderColor: "var(--primary-500)",
	},
	error: {
		marginTop: "0.5rem",
		padding: "0.5rem",
		backgroundColor: "#ffebee",
		color: "#c62828",
		borderRadius: "0.25rem",
		fontSize: "0.875rem",
	},
	actions: {
		display: "flex",
		justifyContent: "flex-end",
		gap: "0.5rem",
		marginTop: "1.5rem",
	},
	button: {
		padding: "0.5rem 1rem",
		borderRadius: "0.25rem",
		fontWeight: "600",
		cursor: "pointer",
		transition: "background-color 0.2s",
	},
	buttonCancel: {
		backgroundColor: "var(--primary-100)",
		color: "var(--text)",
	},
	"buttonCancel:hover": {
		backgroundColor: "var(--primary-200)",
	},
	buttonSubmit: {
		backgroundColor: "var(--primary-500)",
		color: "white",
	},
	"buttonSubmit:hover": {
		backgroundColor: "var(--primary-600)",
	},
	"buttonSubmit:disabled": {
		backgroundColor: "var(--primary-300)",
		cursor: "not-allowed",
	},
});